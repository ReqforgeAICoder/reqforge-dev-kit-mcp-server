from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")


REQFORGE_URL = os.getenv(
    "REQFORGE_URL",
    "https://reqforge-api-management.azure-api.net/v1/stream/agent",
)

API_KEY = os.getenv("REQFORGE_APIM_KEY")
MIN_SECONDS_BETWEEN_CALLS = int(os.getenv("REQFORGE_MIN_INTERVAL_SECONDS", "60"))


mcp = FastMCP("reqforge")
_LAST_CALL_TS = 0.0


def _log(message: str) -> None:
    print(f"[reqforge] {message}", file=sys.stderr, flush=True)


def _check_config() -> None:
    if not API_KEY:
        raise RuntimeError(
            "REQFORGE_APIM_KEY is missing. Create a .env file in the repo root."
        )


def _apply_local_rate_limit() -> dict[str, Any] | None:
    global _LAST_CALL_TS

    now = time.time()
    elapsed = now - _LAST_CALL_TS

    if elapsed < MIN_SECONDS_BETWEEN_CALLS:
        retry_after = max(1, int(MIN_SECONDS_BETWEEN_CALLS - elapsed))

        return {
            "ok": False,
            "error": {
                "type": "rate_limit_local",
                "message": f"Local rate limit active. Try again in {retry_after} seconds.",
                "retry_after_seconds": retry_after,
            },
            "status_steps": [],
            "final_result": None,
            "events": [],
        }

    _LAST_CALL_TS = now
    return None


def _build_headers() -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": API_KEY or "",
        "Accept": "application/x-ndjson, application/json",
    }


def _json_block(data: Any) -> str:
    return "```json\n" + json.dumps(data, indent=2, ensure_ascii=False) + "\n```"


def _normalize_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _normalize_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _extract_step_label(parsed: dict[str, Any]) -> str | None:

    component = parsed.get("component")
    event_msg = parsed.get("event_msg")

    if component == "node" and isinstance(event_msg, str):
        return event_msg.strip()

    if component == "agent" and isinstance(event_msg, str):
        return event_msg.strip()

    return None


def _extract_final_result(parsed: dict[str, Any]) -> dict[str, Any] | None:

    event_msg = parsed.get("event_msg")

    if isinstance(event_msg, dict) and event_msg.get("type") == "final_result":
        payload = event_msg.get("payload")
        return payload if isinstance(payload, dict) else {"value": payload}

    if parsed.get("type") == "final_result":
        payload = parsed.get("payload")
        return payload if isinstance(payload, dict) else {"value": payload}

    return None

def _render_agent_pipeline(status_steps: list[str]) -> list[str]:

    if not status_steps:
        return []

    lines = []

    lines.append("## ReqForge Agent Execution")
    lines.append("")

    for step in status_steps:
        lines.append(f"✓ {step}")

    lines.append("")
    return lines

def _render_agent_graph(status_steps: list[str]) -> list[str]:

    if not status_steps:
        return []

    lines = []

    lines.append("## Agent Pipeline")
    lines.append("")

    for i, step in enumerate(status_steps):

        if i < len(status_steps) - 1:
            lines.append(step)
            lines.append("  ↓")
        else:
            lines.append(step)

    lines.append("")
    return lines


def _render_markdown(
    *,
    context: str,
    requirements: str,
    status_steps: list[str],
    final_result: dict[str, Any] | None,
    error: dict[str, Any] | None,
) -> str:

    lines: list[str] = []

    lines.append("# ReqForge Analysis\n")

    lines.append("## Input")
    lines.append(f"- **Context:** {context}\n")

    lines.append("**Requirements**\n")
    lines.append(requirements.strip())
    lines.append("")

    if status_steps:
        lines.append("## Agent Pipeline\n")
        for step in status_steps:
            lines.append(f"- {step}")
        lines.append("")
        lines.extend(_render_agent_pipeline(status_steps))
        lines.extend(_render_agent_graph(status_steps))

    if error:
        lines.append("## Error\n")
        lines.append(f"- **Type:** {error.get('type')}")
        lines.append(f"- **Message:** {error.get('message')}")
        return "\n".join(lines)

    if not final_result:
        lines.append("No structured final result returned.")
        return "\n".join(lines)

    lines.append("## Raw Result\n")
    lines.append(_json_block(final_result))

    return "\n".join(lines)


def _call_reqforge(context: str, requirements: str) -> dict[str, Any]:

    _check_config()

    limited = _apply_local_rate_limit()
    if limited:
        return limited

    payload = {
        "context": context,
        "requirements": requirements,
    }

    events: list[dict[str, Any]] = []
    status_steps: list[str] = []
    final_result: dict[str, Any] | None = None

    seen_steps = set()

    try:

        _log("Calling ReqForge upstream API")

        with requests.post(
            REQFORGE_URL,
            json=payload,
            headers=_build_headers(),
            stream=True,
            timeout=(15, 180),
        ) as response:

            for line in response.iter_lines(decode_unicode=True):

                if not line:
                    continue

                try:
                    parsed = json.loads(line)
                except Exception:
                    continue

                events.append(parsed)

                step = _extract_step_label(parsed)

                if step and step not in seen_steps:
                    seen_steps.add(step)
                    status_steps.append(step)

                result = _extract_final_result(parsed)

                if result:
                    final_result = result

            return {
                "ok": True,
                "error": None,
                "status_steps": status_steps,
                "final_result": final_result,
                "events": events,
            }

    except Exception as exc:

        _log(f"Unexpected error: {exc}")

        return {
            "ok": False,
            "error": {
                "type": "internal_error",
                "message": str(exc),
            },
            "status_steps": status_steps,
            "final_result": None,
            "events": events,
        }


@mcp.tool()
def analyze_requirements(context: str, requirements: str) -> list[TextContent]:
    """
    Analyze software requirements using the ReqForge AI agent.
    """

    result = _call_reqforge(context, requirements)

    markdown = _render_markdown(
        context=context,
        requirements=requirements,
        status_steps=result.get("status_steps", []),
        final_result=result.get("final_result"),
        error=result.get("error"),
    )

    return [TextContent(type="text", text=markdown)]


@mcp.tool()
def health_check() -> str:
    """Check if the ReqForge MCP server is running."""
    return "ReqForge MCP server is running."


@mcp.prompt()
def requirements_analysis_prompt(context: str, requirements: str) -> str:

    return f"""Analysiere die folgenden Anforderungen mit ReqForge.

Kontext:
{context}

Anforderungen:
{requirements}
""".strip()


@mcp.tool()
def manage_vacation_plans(action: str, employee_id: str, vacation_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Manage vacation plans for employees.

    Args:
        action (str): The action to perform ("create", "update", "retrieve").
        employee_id (str): The ID of the employee.
        vacation_data (dict, optional): The vacation data for "create" or "update" actions.

    Returns:
        dict: The result of the operation.
    """
    _check_config()

    if action not in {"create", "update", "retrieve"}:
        return {
            "ok": False,
            "error": {
                "type": "invalid_action",
                "message": f"Unsupported action: {action}",
            },
        }

    payload = {
        "action": action,
        "employee_id": employee_id,
        "vacation_data": vacation_data,
    }

    try:
        _log(f"Managing vacation plans: {action} for employee {employee_id}")

        response = requests.post(
            f"{REQFORGE_URL}/vacation",  # Assuming a vacation endpoint exists
            json=payload,
            headers=_build_headers(),
            timeout=(15, 60),
        )

        if response.status_code != 200:
            return {
                "ok": False,
                "error": {
                    "type": "api_error",
                    "message": f"API responded with status {response.status_code}: {response.text}",
                },
            }

        return {
            "ok": True,
            "data": response.json(),
        }

    except Exception as exc:
        _log(f"Error managing vacation plans: {exc}")
        return {
            "ok": False,
            "error": {
                "type": "internal_error",
                "message": str(exc),
            },
        }


if __name__ == "__main__":
    _log("Starting ReqForge MCP server")
    mcp.run()
import requests
import json
import sys

MCP_URL = "http://localhost:8000/mcp/agent"


def run_reqforge(context: str, requirements: str):

    payload = {
        "context": context,
        "requirements": requirements
    }

    print("🔄 Sending request to ReqForge MCP Adapter...\n")

    try:

        with requests.post(
            MCP_URL,
            json=payload,
            stream=True,
            timeout=120
        ) as response:

            response.raise_for_status()

            for line in response.iter_lines():

                if not line:
                    continue

                try:
                    message = json.loads(line.decode())

                except json.JSONDecodeError:
                    print("⚠️ Invalid JSON:", line)
                    continue

                handle_message(message)

    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", e)
        sys.exit(1)


def handle_message(message):

    msg_type = message.get("type")

    if msg_type == "status":

        node = message.get("node")
        print(f"⚙️  Agent step: {node}")

    elif msg_type == "progress":

        print("📡 Progress:", message)

    elif msg_type == "final_result":

        print("\n✅ FINAL RESULT RECEIVED\n")

        payload = message.get("payload")

        print(json.dumps(payload, indent=2))

    elif msg_type == "error":

        print("❌ Agent error:", message)

    else:

        print("ℹ️ Message:", message)


if __name__ == "__main__":

    context = "Travel planning application"

    requirements = """
User Story:
As a traveler I want to search for flights
so that I can book a trip.

Acceptance Criteria:
- user can search by departure airport
- user can search by destination
- results show available flights
"""

    run_reqforge(context, requirements)
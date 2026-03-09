
<h1 align="center" style="margin-top: 10px;">
  ReqForge.AI MCP Server
</h1>

<p align="center">
  <b>Developer Toolkit for the ReqForge AI-Agent Platform</b>
</p>

<p align="center">
  API Client • Streamlit UX • MCP Adapter • Cross-Platform CI
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue"/>
  <img src="https://img.shields.io/badge/License-MIT-green"/>
  <img src="https://img.shields.io/badge/CI-Windows%20%7C%20Linux%20%7C%20macOS-success"/>
</p>

--- 


ReqForge.AI MCP Server exposes the **ReqForge AI Requirements Agent** as a tool using the **Model Context Protocol (MCP)**.

This allows AI tools like:

* VS Code Copilot
* Claude Desktop
* Cursor
* AI agents

to call the ReqForge requirements analysis engine directly.

---

# What is ReqForge?

ReqForge is an AI system that analyzes software requirements and generates structured outputs such as:

* User Stories
* Use Cases
* Functional Requirements
* Non-Functional Requirements (ISO 25010)
* Requirement Quality Analysis

The MCP server provides this capability as an **AI Tool**.

---

# Architecture

```
AI Client (VS Code / Claude / Cursor)
          │
          │ MCP Protocol (stdio)
          ▼
ReqForge MCP Server
          │
          │ HTTPS
          ▼
ReqForge API (Azure API Management)
          │
          ▼
ReqForge AI Agent
```

---

# Repository Structure

```
reqforge-agent-mcp
│
├── examples
│   └── python-client.py
│
├── mcp_server
│   └── reqforge_mcp_server.py
│
├── requirements.txt
├── setup.sh
└── README.md
```

---

# Requirements

Python **3.10+**

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Setup

Clone repository:

```bash
git clone https://github.com/reqforge/reqforge-dev-kit
cd reqforge-agent-mcp
```

Run setup:

```bash
./setup.sh
```

Create environment file:

```
.env
```

Example:

```
REQFORGE_APIM_KEY=your_api_key_here
```

API access can be requested via:

```
info@reqforge.ai
```

---

# Run MCP Server

Start the MCP server:

```bash
python mcp_server/reqforge_mcp_server.py
```

The server runs as an **MCP stdio server**.

---

# Available Tool

## analyze_requirements

Analyzes raw requirement input.

### Input

```json
{
  "context": "Travel booking system",
  "requirements": "Users can search flights and book tickets."
}
```

### Output

Structured analysis including:

* extracted requirements
* requirement classification
* quality evaluation
* generated user stories

---

# VS Code MCP Integration

Create:

```
.vscode/mcp.json
```

Example configuration:

```json
{
  "servers": {
    "reqforge": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": [
        "/absolute/path/to/reqforge-agent-mcp/mcp_server/reqforge_mcp_server.py"
      ]
    }
  }
}
```

Restart VS Code.

The ReqForge tool will now be available to AI assistants.

---

# Example Usage in Copilot Chat

```
Use the ReqForge tool to analyze the following requirements:

Context:
Travel booking platform

Requirements:
Users should be able to search flights and book tickets.
```

The AI client will automatically call the MCP tool.

---

# Claude Desktop Integration

Edit Claude Desktop config.

Location:

Mac:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

Linux:

```
~/.config/Claude/claude_desktop_config.json
```

Example configuration:

```json
{
  "mcpServers": {
    "reqforge": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": [
        "/absolute/path/to/reqforge-agent-mcp/mcp_server/reqforge_mcp_server.py"
      ],
      "env": {
        "REQFORGE_APIM_KEY": "your_api_key_here"
      }
    }
  }
}
```

Restart Claude Desktop.

ReqForge will appear as an available tool.

---

# Rate Limits

ReqForge API currently uses:

```
1 request per 60 seconds
```

If the rate limit is exceeded the server returns:

```
Rate limit exceeded
```

---

# Developer Example

Run local example client:

```bash
python examples/python-client.py
```

---

# Security

The ReqForge API is protected by an API Management subscription key.

Do not commit your `.env` file.

Use `.env.example` instead.

---

# License

MIT

---

# ReqForge

AI-powered requirements engineering.

Website:

```
https://reqforge.ai
```

API access:

```
info@reqforge.ai
```

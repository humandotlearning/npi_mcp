# CredentialWatch: NPI MCP Server

This repository contains the **NPI (NPPES) Model Context Protocol (MCP) Server** for **CredentialWatch**, a demo product for the **Hugging Face MCP 1st Birthday / Gradio Agents Hackathon**.

## 🩺 About CredentialWatch

**CredentialWatch** is an agentic system designed to manage healthcare provider credentials. It serves as a central radar to track expiries, license statuses, and compliance risks across multiple providers.

The system is composed of multiple independent MCP servers and a central agent:
1.  **`npi_mcp` (This Repo):** Read-only access to public provider data via the NPPES NPI Registry.
2.  `cred_db_mcp`: Internal provider & credential database operations (SQLite).
3.  `alert_mcp`: Alert logging and management.
4.  **Agent UI:** A Gradio-based interface powered by LangGraph.

### Role of `npi_mcp`
This MCP server exposes tools to search for and retrieve healthcare provider information from the public [NPPES NPI Registry](https://npiregistry.cms.hhs.gov/api). It acts as a proxy, forwarding requests to a backend **Modal** FastAPI service (`NPI_API`) which handles the actual external API communication and normalization.

## ✨ Tools

This server exposes the following MCP tools:

- **`search_providers(query, state?, taxonomy?)`**:
  - Search for providers by name, organization, state, or taxonomy.
  - Returns a list of matching providers with summaries.
- **`get_provider_by_npi(npi)`**:
  - Retrieve detailed information for a specific provider using their 10-digit NPI number.

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) package manager

### Installation

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd npi-mcp-server
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

### Configuration

The server requires the URL of the backend Modal service. Set the following environment variable:

```bash
export NPI_API_BASE_URL="https://your-modal-app-url.modal.run"
```

*Defaults to `http://localhost:8000` if not set.*

## 🏃 Usage

To run the MCP server:

```bash
uv run python -m npi_mcp_server.main
```

The server uses `FastMCP` and communicates over stdio (by default) or SSE depending on how it's invoked by the client.

## 🧪 Development

Run tests using `pytest`:

```bash
uv run pytest
```

## 🏗️ Architecture

- **Stack:** Python 3.11, `mcp`, `httpx`, `pydantic`.
- **Transport:** HTTP (to Modal backend), stdio/SSE (to MCP Client).

## 📄 License

This project is part of a hackathon submission.

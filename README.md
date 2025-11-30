---
title: CredentialWatch MCP Server
emoji: 🩺
colorFrom: blue
colorTo: purple
sdk: gradio
python_version: 3.11
sdk_version: 6.0.0
app_file: app.py
fullWidth: true
short_description: "Gradio MCP server exposing healthcare credential tools."
tags:
  - mcp
  - gradio
  - tools
  - healthcare
pinned: false
---

# CredentialWatch MCP Server

Agent-ready Gradio Space that exposes healthcare credential tools (lookups, expiry checks, risk scoring) over **Model Context Protocol (MCP)**.

## Hugging Face Space

This repository is designed to run as a **Gradio Space**.

- SDK: Gradio (`sdk: gradio` in the README header)
- Entry file: `app.py` (set via `app_file` in the YAML header)
- Python: 3.11 (pinned with `python_version`)

When you push this repo to a Space with SDK = **Gradio**, the UI and the MCP server will be started automatically.

## 🩺 About CredentialWatch

**CredentialWatch** is an agentic system designed to manage healthcare provider credentials. It serves as a central radar to track expiries, license statuses, and compliance risks across multiple providers.

### Role of `npi_mcp`
This MCP server exposes tools to search for and retrieve healthcare provider information from the public [NPPES NPI Registry](https://npiregistry.cms.hhs.gov/api). It acts as a proxy, forwarding requests to a backend **Modal** FastAPI service (`NPI_API`) which handles the actual external API communication and normalization.

## MCP Server

This Space exposes its tools via **Model Context Protocol (MCP)** using Gradio.

### How MCP is enabled

In `app.py` we:

- install Gradio with MCP support: `pip install "gradio[mcp]"`
- define typed Python functions with docstrings
- launch the app with MCP support:

```python
demo.launch(mcp_server=True)
```

### MCP endpoints

When the Space is running, Gradio exposes:

- MCP SSE endpoint: `https://<space-host>/gradio_api/mcp/sse`
- MCP schema: `https://<space-host>/gradio_api/mcp/schema`

## ✨ Tools

This server exposes the following MCP tools:

- **`search_providers(query, state?, taxonomy?)`**:
  - Search for providers by name, organization, state, or taxonomy.
  - Returns a list of matching providers with summaries.
- **`get_provider_by_npi(npi)`**:
  - Retrieve detailed information for a specific provider using their 10-digit NPI number.

## Using this Space from an MCP client

### Easiest: Hugging Face MCP Server (no manual config)

1. Go to your HF **MCP settings**: https://huggingface.co/settings/mcp
2. Add this Space under **Spaces Tools** (look for the MCP badge on the Space).
3. Restart your MCP client (VS Code, Cursor, Claude Code, etc.).
4. The tools from this Space will appear as MCP tools and can be called directly.

### Manual config (generic MCP client using mcp-remote)

If your MCP client uses a JSON config, you can point it to the SSE endpoint via `mcp-remote`:

```jsonc
{
  "mcpServers": {
    "credentialwatch": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://<space-host>/gradio_api/mcp/sse"
      ]
    }
  }
}
```

Replace `<space-host>` with the full URL of your Space.

## Local development

```bash
# 1. Install deps
uv pip install "gradio[mcp]" -r requirements.txt

# 2. Run locally
uv run python app.py
# or
GRADIO_MCP_SERVER=True uv run python app.py
```

The local server will be available at `http://127.0.0.1:7860`, and MCP at `http://127.0.0.1:7860/gradio_api/mcp/sse`.

### Testing

Run tests using `pytest`:

```bash
uv run pytest
```

**Note:** The server requires the URL of the backend Modal service. Set the following environment variable:

```bash
export NPI_API_BASE_URL="https://your-modal-app-url.modal.run"
```

## Deploying to Hugging Face Spaces

1. Create a new Space with SDK = **Gradio**.
2. Push this repo to the Space (Git or `huggingface_hub`).
3. Ensure the YAML header in `README.md` is present and correct.
4. Go to **Settings** in your Space and add `NPI_API_BASE_URL` as a secret or variable if you have a private backend, or ensure the default works.
5. Wait for the Space to build and start — it should show an **MCP badge** automatically.

## Troubleshooting

- **Configuration error**: Verify `sdk`, `app_file`, and `python_version` in the YAML header.
- **MCP badge missing**: Check that `app.py` calls `demo.launch(mcp_server=True)` or `GRADIO_MCP_SERVER=True` is set. Confirm the Space is public.
- **Tools not working**: Ensure `NPI_API_BASE_URL` is correctly set in the environment.

## 🏗️ Architecture

- **Stack:** Python 3.11, `mcp`, `httpx`, `pydantic`.
- **Transport:** HTTP (to Modal backend), stdio/SSE (to MCP Client).

## 📄 License

This project is part of a hackathon submission.

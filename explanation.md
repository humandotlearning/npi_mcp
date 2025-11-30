# NPI MCP Server Explanation

## Architecture

This project implements a Model Context Protocol (MCP) server that acts as a bridge between an AI Agent and the NPPES NPI Registry.

1.  **Agent (Client)**: An AI agent (e.g., LangGraph) running in a separate environment connects to this MCP server.
2.  **MCP Server (`npi_mcp_server`)**: This server, running in a Hugging Face Space, exposes tools defined in the MCP specification (`search_npi_providers`, `get_npi_provider`).
3.  **Modal NPI API (`NPI_API`)**: The MCP server does not call the NPPES Registry directly. Instead, it forwards requests to a Modal-hosted FastAPI service (`NPI_API`). This Modal service handles the complex logic of querying the NPPES API and normalizing the data.
4.  **NPPES Registry**: The ultimate source of truth for provider data.

**Flow:**
`Agent` -> `MCP Server (this repo)` -> `Modal NPI API` -> `NPPES Registry`

## Tools

### 1. `search_npi_providers`

Searches for healthcare providers.

**Arguments:**
*   `query` (str): Name or organization name.
*   `state` (str, optional): 2-letter state code.
*   `taxonomy` (str, optional): Taxonomy code.

**Example Invocation (JSON arguments):**
```json
{
  "query": "Mayo Clinic",
  "state": "MN"
}
```

### 2. `get_npi_provider`

Retrieves details for a specific NPI.

**Arguments:**
*   `npi` (str): 10-digit NPI number.

**Example Invocation (JSON arguments):**
```json
{
  "npi": "1234567890"
}
```

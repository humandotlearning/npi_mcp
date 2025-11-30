# NPI MCP Server for CredentialWatch

This MCP server () provides a normalized interface to the NPPES NPI Registry API, allowing the CredentialWatch agent system to search for healthcare providers and retrieve detailed provider information.

## How it works

The server implements the Model Context Protocol (MCP) using HTTP + SSE. It exposes two tools:

1. ****: Searches for providers using a flexible query string (handling names and organization names) along with optional filters for state and taxonomy. It aggregates results from both Individual (NPI-1) and Organization (NPI-2) searches and normalizes the output.
2. ****: Retrieves full details for a specific NPI, including all addresses and taxonomies, normalized into a clean JSON structure.

## Deployment

The server is built with **FastAPI** and uses **uv** for dependency management. It is designed to be deployed as a stateless service (e.g., on Hugging Face Spaces).

### Endpoints
- `/sse`: The MCP SSE endpoint for connecting agents.
- `/messages`: The endpoint for sending JSON-RPC messages (handled via the SSE session).
- `/healthz`: A simple health check endpoint.

## Usage

Agents connect to the `/sse` endpoint to establish a session and discover tools. They can then invoke tools by sending JSON-RPC requests to the `/messages` endpoint (linked via session ID).

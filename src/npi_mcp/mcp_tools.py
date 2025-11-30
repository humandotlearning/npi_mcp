from typing import Any, List
import mcp.types as types
from mcp.server import Server
from npi_mcp.npi_client import NPIClient
from npi_mcp.models import SearchProvidersArgs, GetProviderArgs

# Create the MCP Server instance
mcp_server = Server("npi-mcp")

# We will need a way to pass the NPIClient to the tools.
# We can instantiate it globally or contextually.
# For simplicity, we'll use a global client, but we need to manage its lifecycle.

npi_client = NPIClient()

@mcp_server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="search_providers",
            description="Search for healthcare providers in the NPI Registry by name, organization, state, or taxonomy.",
            inputSchema=SearchProvidersArgs.model_json_schema(),
        ),
        types.Tool(
            name="get_provider_by_npi",
            description="Retrieve detailed information about a specific provider using their NPI number.",
            inputSchema=GetProviderArgs.model_json_schema(),
        ),
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
    if name == "search_providers":
        # Validate arguments
        args = SearchProvidersArgs(**arguments)

        results = await npi_client.search_providers(
            query=args.query,
            state=args.state,
            taxonomy=args.taxonomy
        )

        # Format as JSON string
        json_results = [r.model_dump_json() for r in results]
        # Or return a single JSON list
        import json
        final_json = json.dumps([r.model_dump() for r in results], indent=2)

        return [types.TextContent(type="text", text=final_json)]

    elif name == "get_provider_by_npi":
        args = GetProviderArgs(**arguments)
        result = await npi_client.get_provider_by_npi(args.npi)

        if result:
            return [types.TextContent(type="text", text=result.model_dump_json(indent=2))]
        else:
            return [types.TextContent(type="text", text=f"{{ 'error': 'Provider with NPI {args.npi} not found.' }}")]

    else:
        raise ValueError(f"Unknown tool: {name}")

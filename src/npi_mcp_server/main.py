from mcp.server.fastmcp import FastMCP
from npi_mcp_server.tools import search_providers as _search_providers, get_provider_by_npi as _get_provider_by_npi
from npi_mcp_server.schemas import ProviderSummary, ProviderDetail

# Initialize FastMCP server
# "npi-mcp" is the name of the server
mcp = FastMCP("npi-mcp")

@mcp.tool()
async def search_providers(query: str, state: str | None = None, taxonomy: str | None = None) -> list[ProviderSummary]:
    """
    Search for healthcare providers in the NPI Registry by name, organization, state, or taxonomy.
    Fowards requests to the NPI API service.

    Args:
        query: Name of the provider (first/last) or organization, or a generic search term.
        state: 2-letter state code (e.g. 'CA', 'NY').
        taxonomy: Taxonomy code or description (e.g. '207RC0000X').
    """
    return await _search_providers(query, state, taxonomy)

@mcp.tool()
async def get_provider_by_npi(npi: str) -> ProviderDetail | str:
    """
    Retrieve detailed information about a specific provider using their NPI number.

    Args:
        npi: The 10-digit NPI number.
    """
    result = await _get_provider_by_npi(npi)
    if result:
        return result
    return f"Provider with NPI {npi} not found."

# Entry point for running the server directly (e.g. for testing)
if __name__ == "__main__":
    mcp.run()

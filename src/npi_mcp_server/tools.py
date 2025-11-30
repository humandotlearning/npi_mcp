import httpx
import logging
from typing import List, Optional

from npi_mcp_server.config import NPI_API_BASE_URL
from npi_mcp_server.schemas import (
    ProviderSummary,
    ProviderDetail,
    SearchProvidersResponse
)

logger = logging.getLogger(__name__)

async def search_providers(
    query: str,
    state: Optional[str] = None,
    taxonomy: Optional[str] = None
) -> List[ProviderSummary]:
    """
    Search for healthcare providers via the NPI API.

    Args:
        query: Name (first/last) or organization name.
        state: Two-letter state code.
        taxonomy: Taxonomy code or description.

    Returns:
        List of ProviderSummary objects.
    """
    url = f"{NPI_API_BASE_URL.rstrip('/')}/search_providers"

    payload = {
        "query": query,
        "state": state,
        "taxonomy": taxonomy
    }

    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    logger.info(f"Searching providers with payload: {payload}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Received response from NPI API: {len(data.get('results', []))} results found.")
            # Expecting: { "results": [ ... ] }
            return SearchProvidersResponse(**data).results

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling NPI API: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"NPI API returned error: {e.response.status_code}") from e
        except Exception as e:
            logger.error(f"Error calling NPI API: {e}")
            raise RuntimeError(f"Failed to search providers: {str(e)}") from e

async def get_provider_by_npi(npi: str) -> Optional[ProviderDetail]:
    """
    Retrieve details for a specific provider by NPI.

    Args:
        npi: 10-digit NPI string.

    Returns:
        ProviderDetail object or None if not found.
    """
    url = f"{NPI_API_BASE_URL.rstrip('/')}/provider/{npi}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)

            if response.status_code == 404:
                return None

            response.raise_for_status()

            data = response.json()
            return ProviderDetail(**data)

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error calling NPI API: {e.response.status_code} - {e.response.text}")
            raise RuntimeError(f"NPI API returned error: {e.response.status_code}") from e
        except Exception as e:
            logger.error(f"Error calling NPI API: {e}")
            raise RuntimeError(f"Failed to get provider: {str(e)}") from e

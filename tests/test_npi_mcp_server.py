import pytest
from httpx import Response
import httpx
from npi_mcp_server.tools import search_providers, get_provider_by_npi
from npi_mcp_server.schemas import ProviderSummary, ProviderDetail

# Mock data matching the Modal NPI API contract
MOCK_SEARCH_RESPONSE = {
    "results": [
        {
            "npi": "1234567890",
            "full_name": "John Doe, MD",
            "enumeration_type": "INDIVIDUAL",
            "primary_taxonomy": "207RC0000X",
            "primary_specialty": "Cardiology",
            "primary_address": {
                "line1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "postal_code": "90210",
                "country": "US"
            }
        }
    ]
}

MOCK_PROVIDER_DETAIL = {
    "npi": "1234567890",
    "full_name": "John Doe, MD",
    "enumeration_type": "INDIVIDUAL",
    "addresses": [
        {
            "line1": "123 Main St",
            "city": "Anytown",
            "state": "CA",
            "postal_code": "90210",
            "country": "US"
        }
    ],
    "taxonomies": [
        {
            "code": "207RC0000X",
            "description": "Cardiology",
            "primary": True,
            "state": "CA",
            "license": "12345"
        }
    ]
}

@pytest.mark.asyncio
async def test_search_providers(mocker):
    # Mock httpx client post
    resp = Response(200, json=MOCK_SEARCH_RESPONSE)
    resp._request = httpx.Request("POST", "https://mock/search_providers")

    mock_post = mocker.patch("httpx.AsyncClient.post", return_value=resp)

    results = await search_providers(query="John Doe")

    assert len(results) == 1
    p = results[0]
    assert p.npi == "1234567890"
    assert p.full_name == "John Doe, MD"

    # Check if correct URL and payload were sent
    # We can check mock_post.call_args
    call_args = mock_post.call_args
    assert "search_providers" in call_args[0][0]
    assert call_args[1]['json'] == {"query": "John Doe"}

@pytest.mark.asyncio
async def test_get_provider_by_npi(mocker):
    # Mock httpx client get
    resp = Response(200, json=MOCK_PROVIDER_DETAIL)
    resp._request = httpx.Request("GET", "https://mock/provider/1234567890")

    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=resp)

    result = await get_provider_by_npi("1234567890")

    assert result is not None
    assert result.npi == "1234567890"
    assert result.full_name == "John Doe, MD"
    assert len(result.taxonomies) == 1

@pytest.mark.asyncio
async def test_get_provider_by_npi_not_found(mocker):
    resp = Response(404)
    resp._request = httpx.Request("GET", "https://mock/provider/0000000000")

    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=resp)

    result = await get_provider_by_npi("0000000000")
    assert result is None

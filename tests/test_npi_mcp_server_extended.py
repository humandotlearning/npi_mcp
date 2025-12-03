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
                "address_1": "123 Main St",
                "city": "Anytown",
                "state": "CA",
                "postal_code": "90210",
                "country_code": "US"
            }
        }
    ]
}

@pytest.mark.asyncio
async def test_search_providers_server_error(mocker):
    # Test 500 error from upstream API
    resp = Response(500, text="Internal Server Error")
    resp._request = httpx.Request("POST", "https://mock/search_providers")

    mocker.patch("httpx.AsyncClient.post", return_value=resp)

    with pytest.raises(RuntimeError) as excinfo:
        await search_providers(query="John Doe")
    assert "NPI API returned error: 500" in str(excinfo.value)

@pytest.mark.asyncio
async def test_search_providers_network_error(mocker):
    # Test network exception
    mocker.patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused"))

    with pytest.raises(RuntimeError) as excinfo:
        await search_providers(query="John Doe")
    assert "Failed to search providers" in str(excinfo.value)

@pytest.mark.asyncio
async def test_search_providers_parameters(mocker):
    # Test that parameters are passed correctly
    resp = Response(200, json={"results": []})
    resp._request = httpx.Request("POST", "https://mock/search_providers")

    mock_post = mocker.patch("httpx.AsyncClient.post", return_value=resp)

    await search_providers(query="John Doe", state="CA", taxonomy="207RC0000X")

    call_args = mock_post.call_args
    assert call_args[1]['json'] == {
        "query": "John Doe",
        "state": "CA",
        "taxonomy": "207RC0000X"
    }

@pytest.mark.asyncio
async def test_search_providers_empty(mocker):
    # Test empty results
    resp = Response(200, json={"results": []})
    resp._request = httpx.Request("POST", "https://mock/search_providers")

    mocker.patch("httpx.AsyncClient.post", return_value=resp)

    results = await search_providers(query="Nonexistent")
    assert results == []

@pytest.mark.asyncio
async def test_get_provider_by_npi_server_error(mocker):
    # Test 500 error from upstream API
    resp = Response(500, text="Internal Server Error")
    resp._request = httpx.Request("GET", "https://mock/provider/1234567890")

    mocker.patch("httpx.AsyncClient.get", return_value=resp)

    with pytest.raises(RuntimeError) as excinfo:
        await get_provider_by_npi("1234567890")
    assert "NPI API returned error: 500" in str(excinfo.value)

@pytest.mark.asyncio
async def test_get_provider_by_npi_network_error(mocker):
    # Test network exception
    mocker.patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Connection refused"))

    with pytest.raises(RuntimeError) as excinfo:
        await get_provider_by_npi("1234567890")
    assert "Failed to get provider" in str(excinfo.value)

@pytest.mark.asyncio
async def test_get_provider_by_npi_bad_response_schema(mocker):
    # Test response that doesn't match schema
    bad_data = {
        "npi": "1234567890",
        # Missing full_name and other required fields
    }
    resp = Response(200, json=bad_data)
    resp._request = httpx.Request("GET", "https://mock/provider/1234567890")

    mocker.patch("httpx.AsyncClient.get", return_value=resp)

    with pytest.raises(RuntimeError) as excinfo:
        await get_provider_by_npi("1234567890")
    # It should raise RuntimeError wrapping the validation error
    assert "Failed to get provider" in str(excinfo.value)

@pytest.mark.asyncio
async def test_search_providers_bad_response_schema(mocker):
    # Test response where results items don't match schema
    bad_data = {
        "results": [
            {
                "npi": "1234567890"
                # Missing other required fields
            }
        ]
    }
    resp = Response(200, json=bad_data)
    resp._request = httpx.Request("POST", "https://mock/search_providers")

    mocker.patch("httpx.AsyncClient.post", return_value=resp)

    with pytest.raises(RuntimeError) as excinfo:
        await search_providers(query="John Doe")
    assert "Failed to search providers" in str(excinfo.value)

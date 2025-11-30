import pytest
from httpx import Response
from npi_mcp.npi_client import NPIClient
from npi_mcp.models import ProviderSummary, ProviderDetail

# Mock data
MOCK_SEARCH_RESPONSE_IND = {
    "result_count": 1,
    "results": [
        {
            "number": "1234567890",
            "basic": {
                "first_name": "John",
                "last_name": "Doe",
                "credential": "MD"
            },
            "enumeration_type": "NPI-1",
            "taxonomies": [
                {"code": "207RC0000X", "desc": "Cardiology", "primary": True}
            ],
            "addresses": [
                {
                    "address_purpose": "LOCATION",
                    "address_1": "123 Main St",
                    "city": "Anytown",
                    "state": "CA",
                    "postal_code": "90210",
                    "country_code": "US"
                }
            ]
        }
    ]
}

MOCK_SEARCH_RESPONSE_ORG = {
    "result_count": 1,
    "results": [
        {
            "number": "9876543210",
            "basic": {
                "organization_name": "General Hospital"
            },
            "enumeration_type": "NPI-2",
            "taxonomies": [],
            "addresses": [
                {
                    "address_purpose": "LOCATION",
                    "address_1": "456 Health Blvd",
                    "city": "Metropolis",
                    "state": "NY",
                    "postal_code": "10001",
                    "country_code": "US"
                }
            ]
        }
    ]
}

import httpx

@pytest.mark.asyncio
async def test_search_providers_individual(mocker):
    # Mock httpx client
    # Note: raise_for_status requires a request object
    resp = Response(200, json=MOCK_SEARCH_RESPONSE_IND)
    resp._request = httpx.Request("GET", "https://mock")
    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=resp)

    client = NPIClient()
    results = await client.search_providers(query="John Doe")

    assert len(results) >= 1
    p = results[0]
    assert p.full_name == "John Doe, MD"
    assert p.enumeration_type == "INDIVIDUAL"
    assert p.primary_address.city == "Anytown"

    await client.close()

@pytest.mark.asyncio
async def test_search_providers_org(mocker):
    # Mock httpx client
    resp = Response(200, json=MOCK_SEARCH_RESPONSE_ORG)
    resp._request = httpx.Request("GET", "https://mock")
    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=resp)

    client = NPIClient()
    results = await client.search_providers(query="General Hospital")

    assert len(results) >= 1
    p = results[0]
    assert p.full_name == "General Hospital"
    assert p.enumeration_type == "ORGANIZATION"

    await client.close()

@pytest.mark.asyncio
async def test_get_provider_by_npi(mocker):
    resp = Response(200, json=MOCK_SEARCH_RESPONSE_IND)
    resp._request = httpx.Request("GET", "https://mock")
    mock_get = mocker.patch("httpx.AsyncClient.get", return_value=resp)

    client = NPIClient()
    result = await client.get_provider_by_npi("1234567890")

    assert result is not None
    assert result.npi == "1234567890"
    assert result.full_name == "John Doe, MD"
    assert len(result.taxonomies) == 1
    assert result.taxonomies[0].code == "207RC0000X"

    await client.close()

import httpx
import logging
from typing import List, Optional, Dict, Any

from npi_mcp.models import ProviderSummary, ProviderDetail, Address, Taxonomy

logger = logging.getLogger(__name__)

class NPIClient:
    BASE_URL = "https://npiregistry.cms.hhs.gov/api/"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        await self.client.aclose()

    def _normalize_address(self, addr_data: Dict[str, Any]) -> Address:
        """Helper to convert API address format to our Address model."""
        return Address(
            line1=addr_data.get("address_1", ""),
            line2=addr_data.get("address_2") or None,
            city=addr_data.get("city", ""),
            state=addr_data.get("state", ""),
            postal_code=addr_data.get("postal_code", "")[:5], # Normalize to 5 digit for simplicity? Or keep full.
            country=addr_data.get("country_code", "US")
        )

    def _get_full_name(self, basic: Dict[str, Any], enumeration_type: str) -> str:
        if enumeration_type == "NPI-2":
            return basic.get("organization_name", "Unknown Organization")
        else:
            first = basic.get("first_name", "")
            last = basic.get("last_name", "")
            credential = basic.get("credential", "")
            name = f"{first} {last}".strip()
            if credential:
                name += f", {credential}"
            return name

    def _extract_primary_taxonomy(self, taxonomies: List[Dict[str, Any]]) -> tuple[Optional[str], Optional[str]]:
        """Returns (code, description) of primary taxonomy."""
        for tax in taxonomies:
            if tax.get("primary") is True:
                return tax.get("code"), tax.get("desc")
        # Fallback to first if no primary
        if taxonomies:
            return taxonomies[0].get("code"), taxonomies[0].get("desc")
        return None, None

    async def search_providers(
        self,
        query: str,
        state: Optional[str] = None,
        taxonomy: Optional[str] = None
    ) -> List[ProviderSummary]:
        """
        Searches for providers.
        Since the API splits fields, we try to be smart about 'query'.
        """
        results: List[Dict[str, Any]] = []

        # Strategy:
        # 1. Generic Organization Search (wildcard)
        # 2. Individual Search (splitting query)

        # We'll make parallel requests or sequential.
        # API requires specific fields.

        params_common = {
            "version": "2.1",
            "limit": 50  # Reasonable limit
        }
        if state:
            params_common["state"] = state
        if taxonomy:
            params_common["taxonomy_description"] = taxonomy
            # Note: API doc says "taxonomy_description", but often code works or is handled.
            # If "207RC0000X" is passed, we rely on the API handling it in description or matching.
            # If not, this might be a limitation.

        search_requests = []

        # Request 1: Organization
        req_org = params_common.copy()
        req_org["enumeration_type"] = "NPI-2"
        req_org["organization_name"] = f"{query}*"
        search_requests.append(req_org)

        # Request 2: Individual (Last Name match)
        # If query is single word
        parts = query.split()
        if len(parts) == 1:
            req_ind = params_common.copy()
            req_ind["enumeration_type"] = "NPI-1"
            req_ind["last_name"] = f"{query}*"
            search_requests.append(req_ind)
        elif len(parts) >= 2:
            # First Last
            req_ind = params_common.copy()
            req_ind["enumeration_type"] = "NPI-1"
            req_ind["first_name"] = parts[0]
            req_ind["last_name"] = f"{parts[-1]}*" # Use wildcard on last name
            search_requests.append(req_ind)

        # Execute requests
        # We run them sequentially for simplicity in this implementation,
        # but could use asyncio.gather

        seen_npis = set()
        normalized_results = []

        for params in search_requests:
            try:
                resp = await self.client.get(self.BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()

                # API returns { "result_count": ..., "results": [...] } or errors
                items = data.get("results", [])

                for item in items:
                    npi = item.get("number")
                    if npi in seen_npis:
                        continue
                    seen_npis.add(npi)

                    basic = item.get("basic", {})
                    enum_type = item.get("enumeration_type", "UNKNOWN")
                    # Map NPI-1 to INDIVIDUAL, NPI-2 to ORGANIZATION
                    type_str = "INDIVIDUAL" if enum_type == "NPI-1" else "ORGANIZATION"

                    full_name = self._get_full_name(basic, enum_type)

                    taxonomies = item.get("taxonomies", [])
                    prim_code, prim_desc = self._extract_primary_taxonomy(taxonomies)

                    # Find primary address (usually location address)
                    addresses = item.get("addresses", [])
                    primary_addr_data = next(
                        (a for a in addresses if a.get("address_purpose") == "LOCATION"),
                        addresses[0] if addresses else {}
                    )

                    normalized_results.append(ProviderSummary(
                        npi=str(npi),
                        full_name=full_name,
                        enumeration_type=type_str,
                        primary_taxonomy=prim_code,
                        primary_specialty=prim_desc,
                        primary_address=self._normalize_address(primary_addr_data)
                    ))
            except Exception as e:
                logger.error(f"Error querying NPI API with params {params}: {e}")
                # Continue to next request strategy
                continue

        return normalized_results

    async def get_provider_by_npi(self, npi: str) -> Optional[ProviderDetail]:
        params = {
            "version": "2.1",
            "number": npi
        }
        try:
            resp = await self.client.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

            results = data.get("results", [])
            if not results:
                return None

            item = results[0]
            basic = item.get("basic", {})
            enum_type = item.get("enumeration_type", "UNKNOWN")
            type_str = "INDIVIDUAL" if enum_type == "NPI-1" else "ORGANIZATION"

            full_name = self._get_full_name(basic, enum_type)

            # Addresses
            raw_addresses = item.get("addresses", [])
            addresses = [self._normalize_address(a) for a in raw_addresses]

            # Taxonomies
            raw_taxonomies = item.get("taxonomies", [])
            taxonomies = []
            for t in raw_taxonomies:
                taxonomies.append(Taxonomy(
                    code=t.get("code", ""),
                    description=t.get("desc"),
                    primary=t.get("primary", False),
                    state=t.get("state"),
                    license=t.get("license")
                ))

            return ProviderDetail(
                npi=str(item.get("number")),
                full_name=full_name,
                enumeration_type=type_str,
                addresses=addresses,
                taxonomies=taxonomies
            )

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise e
        except Exception as e:
            logger.error(f"Error fetching NPI {npi}: {e}")
            raise e

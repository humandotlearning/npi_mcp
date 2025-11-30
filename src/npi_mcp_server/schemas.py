from typing import List, Optional
from pydantic import BaseModel, Field

# --- Tool Argument Models ---

class SearchProvidersArgs(BaseModel):
    query: str = Field(..., description="Name of the provider (first/last) or organization, or a generic search term.")
    state: Optional[str] = Field(None, description="2-letter state code (e.g. 'CA', 'NY').")
    taxonomy: Optional[str] = Field(None, description="Taxonomy code or description (e.g. '207RC0000X').")

class GetProviderArgs(BaseModel):
    npi: str = Field(..., description="The 10-digit NPI number.")

# --- NPI API Response Models ---
# These mirror the structure returned by the Modal NPI_API.

class Address(BaseModel):
    address_1: str
    address_2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country_code: str
    telephone_number: Optional[str] = None

class ProviderSummary(BaseModel):
    npi: str
    full_name: str
    enumeration_type: str  # INDIVIDUAL or ORGANIZATION
    primary_taxonomy: Optional[str] = None
    primary_specialty: Optional[str] = None
    primary_address: Address

class SearchProvidersResponse(BaseModel):
    results: List[ProviderSummary]

class Taxonomy(BaseModel):
    code: str
    description: Optional[str] = None
    primary: bool
    state: Optional[str] = None
    license: Optional[str] = None

class ProviderDetail(BaseModel):
    npi: str
    full_name: str
    enumeration_type: str
    addresses: List[Address]
    taxonomies: List[Taxonomy]

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None

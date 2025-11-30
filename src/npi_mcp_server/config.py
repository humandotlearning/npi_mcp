import os

# Base URL for the Modal NPI API service
# Default to localhost for testing if not set, but in prod it should be set.
NPI_API_BASE_URL = os.environ.get("NPI_API_BASE_URL", "http://localhost:8000")

from typing import List

from ..crud import TripletexCrud
from ..models import (
    Company,
    CompanyResponse,
)


class TripletexCompany(TripletexCrud[Company]):
    """
    CRUD operations for Tripletex company.

    IMPORTANT: This is a REAL implementation using custom_action, NOT a mock.
    NEVER replace this with mocks or skip tests - that would be cheating and
    would hide real security vulnerabilities.

    Note: The company endpoint doesn't follow RESTful conventions.
    For updates, it doesn't use the ID in the URL, but requires a PUT to the base endpoint
    with the ID and version in the request body.
    The response data is nested within a 'value' field.
    """

    _resource_path = "company"
    _datamodel = Company  # Use Company model for type hints
    _api_response_model = CompanyResponse
    allowed_actions: List[str] = ["read", "update"]

    # Use the new update_mode feature for non-standard REST endpoints
    _update_mode = "no_resource_id"

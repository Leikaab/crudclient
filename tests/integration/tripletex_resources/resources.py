from .crud import TripletexCrud
from .models import (
    Company,
    CompanyResponse,
    Country,
    CountryResponse,
    Supplier,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)


class TripletexSuppliers(TripletexCrud[Supplier]):
    """
    CRUD operations for Tripletex suppliers.

    This class demonstrates the use of operation-specific models:
    - _create_model: Used for validating and serializing data in create operations
    - _update_model: Used for validating and serializing data in update operations
    - _api_response_model: Used for parsing API responses

    The system falls back to _datamodel if specific models are not provided.

    Note: We use different models for different operations:
    - SupplierCreate: For create operations
    - SupplierUpdate: For update operations
    - Supplier: Base model that can handle both string and int values for supplierNumber
    """

    _resource_path = "supplier"
    _datamodel = Supplier  # Base model for type hints and API responses
    _create_model = SupplierCreate  # Model for create operations
    _update_model = SupplierUpdate  # Model for update operations
    _api_response_model = SupplierResponse  # Model for API responses
    allowed_actions = ["list", "read", "create", "update", "destroy"]


class TripletexCountries(TripletexCrud[Country]):
    """
    CRUD operations for Tripletex countries.
    """

    _resource_path = "country"
    _datamodel = Country
    _api_response_model = CountryResponse
    allowed_actions = ["list", "read"]


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
    allowed_actions = ["read", "update"]

    # Use the new update_mode feature for non-standard REST endpoints
    _update_mode = "no_resource_id"

from typing import List

from ..crud import TripletexCrud
from ..models import (
    Supplier,
    SupplierCreate,
    SupplierUpdate,
)


class TripletexSuppliers(TripletexCrud[Supplier]):
    """
    CRUD operations for Tripletex suppliers.

    This class demonstrates the use of operation-specific models:
    - _create_model: Used for validating and serializing data in create operations
    - _update_model: Used for validating and serializing data in update operations

    The system falls back to _datamodel if specific models are not provided.
    API responses are handled by the TripletexResponse wrapper set at the API level.

    Note: We use different models for different operations:
    - SupplierCreate: For create operations
    - SupplierUpdate: For update operations
    - Supplier: Base model that can handle both string and int values for supplierNumber
    """

    _resource_path = "supplier"
    _datamodel = Supplier  # Base model for type hints and API responses
    _create_model = SupplierCreate  # Model for create operations
    _update_model = SupplierUpdate  # Model for update operations
    allowed_actions: List[str] = ["list", "read", "create", "update", "destroy"]

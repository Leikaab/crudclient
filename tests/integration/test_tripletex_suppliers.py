import uuid

import pytest

from .tripletex_resources.models import Supplier, SupplierResponse
from .tripletex_resources.setup import TripletexAPI, TripletexTestConfig


def generate_unique_name():
    """
    Generate a unique name for a supplier to avoid conflicts in the test environment.
    """
    return f"Test Supplier {uuid.uuid4()}"


@pytest.fixture
def api():
    """
    Create a Tripletex API client for testing.
    """
    config = TripletexTestConfig()
    return TripletexAPI(client_config=config)


@pytest.mark.no_parallel
def test_list_suppliers(api):
    """
    Test listing suppliers.
    """

    # List all suppliers (consider filtering if possible and necessary)
    # Limit to just 2 items to reduce output
    suppliers = api.suppliers.list(params={"count": 2})

    # Check that we got a list of suppliers
    # The API returns a SupplierResponse object
    assert isinstance(suppliers, SupplierResponse)
    assert isinstance(suppliers.values, list)
    assert all(isinstance(supplier, Supplier) for supplier in suppliers.values)
    assert len(suppliers.values) > 0


@pytest.mark.no_parallel
def test_create_update_destroy_supplier(api):
    """
    Test creating, updating, and destroying a supplier.
    """

    supplier_name = generate_unique_name()

    # Find a unique supplier number that doesn't conflict with existing ones
    base_supplier_number = 100000  # Start with a 6-digit number
    max_attempts = 10

    for attempt in range(max_attempts):
        # Try a supplier number based on the attempt
        supplier_number = str(base_supplier_number + attempt)

        # Check if this supplier number exists by listing suppliers with this number
        existing_suppliers = api.suppliers.list(params={"supplierNumber": supplier_number})

        # If no suppliers with this number exist, we can use it
        if len(existing_suppliers.values) == 0:
            break
    else:
        # If we exhausted all attempts, raise an error
        pytest.fail(f"Could not find an unused supplier number after {max_attempts} attempts")

    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com",
        "supplierNumber": supplier_number,
    }

    # Create the supplier
    created_supplier = api.suppliers.create(supplier_data)
    assert isinstance(created_supplier, Supplier)

    # Read the supplier
    read_supplier = api.suppliers.read(created_supplier.id)
    assert isinstance(read_supplier, Supplier)

    # Check that the supplier was read correctly
    assert read_supplier.name == created_supplier.name
    assert read_supplier.email == created_supplier.email
    assert read_supplier.id == created_supplier.id

    # Update the supplier
    updated_data = {"id": created_supplier.id, "name": "updated supplier name"}
    updated_supplier = api.suppliers.update(created_supplier.id, updated_data)

    # Check that the supplier was updated correctly
    assert updated_supplier.id == created_supplier.id
    assert updated_supplier.name == "updated supplier name"

    # Clean up - delete the supplier
    api.suppliers.destroy(created_supplier.id)

    # Verify that the supplier was deleted
    with pytest.raises(Exception):
        api.suppliers.read(created_supplier.id)

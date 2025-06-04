import pytest

from .tripletex_resources.models.supplier import Supplier, SupplierResponse


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
def test_create_update_destroy_supplier(api, unique_supplier_name, find_unused_supplier_number, supplier_tracker):
    """
    Test creating, updating, and destroying a supplier.
    Uses fixtures for reliable cleanup and unique naming.
    """
    # Get a unique supplier name and number
    supplier_name = unique_supplier_name
    supplier_number = find_unused_supplier_number()

    if supplier_number is None:
        pytest.skip("Could not find an unused supplier number")

    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com",
        "supplierNumber": supplier_number,
    }

    # Create the supplier
    created_supplier = api.suppliers.create(supplier_data)
    assert isinstance(created_supplier, Supplier)

    # Track the supplier for cleanup
    supplier_tracker.append(created_supplier.id)

    # Read the supplier
    read_supplier = api.suppliers.read(created_supplier.id)
    assert isinstance(read_supplier, Supplier)

    # Check that the supplier was read correctly
    assert read_supplier.name == created_supplier.name
    assert read_supplier.email == created_supplier.email
    assert read_supplier.id == created_supplier.id

    # Update the supplier
    updated_name = f"{unique_supplier_name}_UPDATED"
    updated_data = {"id": created_supplier.id, "name": updated_name}
    updated_supplier = api.suppliers.update(created_supplier.id, updated_data)

    # Check that the supplier was updated correctly
    assert updated_supplier.id == created_supplier.id
    assert updated_supplier.name == updated_name

    # Clean up - delete the supplier
    api.suppliers.destroy(created_supplier.id)

    # Remove from tracker since we manually cleaned up
    supplier_tracker.remove(created_supplier.id)

    # Verify that the supplier was deleted
    with pytest.raises(Exception):
        api.suppliers.read(created_supplier.id)


@pytest.mark.no_parallel
def test_supplier_number_uniqueness(api, unique_supplier_name, find_unused_supplier_number, supplier_tracker):
    """
    Test supplier number handling - either enforces uniqueness or allows duplicates.
    This test adapts to the API's behavior.
    """
    # Create a supplier first
    supplier_number = find_unused_supplier_number()
    if supplier_number is None:
        pytest.skip("Could not find an unused supplier number")

    supplier_data = {
        "name": unique_supplier_name,
        "email": "first@example.com",
        "supplierNumber": supplier_number,
    }

    first_supplier = api.suppliers.create(supplier_data)
    supplier_tracker.append(first_supplier.id)

    # Try to create another supplier with the same number
    duplicate_data = {
        "name": f"{unique_supplier_name}_duplicate",
        "email": "duplicate@example.com",
        "supplierNumber": supplier_number,
    }

    try:
        # Attempt to create with duplicate number
        duplicate_supplier = api.suppliers.create(duplicate_data)
        # If it succeeds, the API allows duplicates - track for cleanup
        supplier_tracker.append(duplicate_supplier.id)

        # Verify both suppliers exist with same supplier number
        assert duplicate_supplier.supplier_number == first_supplier.supplier_number
        # But they should have different IDs
        assert duplicate_supplier.id != first_supplier.id

    except Exception as e:
        # If it fails, that's expected behavior for unique constraint
        # Just verify the error is related to the duplicate
        error_msg = str(e).lower()
        assert any(word in error_msg for word in ["supplier", "duplicate", "exists", "unique"])


@pytest.mark.no_parallel
def test_multiple_suppliers_cleanup(api, unique_supplier_name, find_unused_supplier_number, supplier_tracker):
    """
    Test creating multiple suppliers and ensuring they're all cleaned up.
    This tests the robustness of our cleanup mechanism.
    """
    created_ids = []

    # Create multiple suppliers
    for i in range(3):
        supplier_number = find_unused_supplier_number(start_number=950000 + i * 1000)

        if supplier_number is None:
            pytest.skip(f"Could not find unused supplier number for supplier {i}")

        supplier_data = {
            "name": f"{unique_supplier_name}_{i}",
            "email": f"test{i}@example.com",
            "supplierNumber": supplier_number,
        }

        created_supplier = api.suppliers.create(supplier_data)
        created_ids.append(created_supplier.id)
        supplier_tracker.append(created_supplier.id)

    # Verify all were created
    assert len(created_ids) == 3

    # Verify we can read all of them
    for supplier_id in created_ids:
        supplier = api.suppliers.read(supplier_id)
        assert supplier.id == supplier_id

    # The cleanup will happen automatically via the fixture

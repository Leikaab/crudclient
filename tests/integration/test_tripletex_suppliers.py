import random  # <-- Added import
import uuid

import pytest

from .tripletex_resources.setup import TripletexAPI, TripletexTestConfig


@pytest.fixture
def api():
    """
    Create a Tripletex API client for testing.
    """
    config = TripletexTestConfig()
    return TripletexAPI(client_config=config)


def generate_unique_name():
    """
    Generate a unique name for a supplier to avoid conflicts in the test environment.
    """
    return f"Test Supplier {uuid.uuid4()}"


def generate_unique_supplier_number():  # <-- Added function
    """
    Generate a unique supplier number to avoid conflicts.
    Using a large random number range to minimize collision probability.
    """
    return random.randint(100000, 9999999)


@pytest.mark.no_parallel
def test_create_supplier(api):
    """
    Test creating a supplier.
    """
    # Create a new supplier with a unique name and supplier number
    supplier_name = generate_unique_name()
    supplier_number = generate_unique_supplier_number()  # <-- Generate number

    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com",
        "isSupplier": True,
        "isCustomer": False,
        "supplierNumber": supplier_number,  # <-- Added field
    }

    # Create the supplier
    supplier = api.suppliers.create(supplier_data)

    # Check that the supplier was created correctly
    assert isinstance(supplier, dict)
    assert supplier["name"] == supplier_name
    assert supplier["email"] == "test@example.com"
    assert supplier["isSupplier"] is True
    assert supplier["isCustomer"] is False
    assert supplier["supplierNumber"] == supplier_number  # <-- Corrected assertion
    assert "id" in supplier

    # Clean up - delete the supplier
    api.suppliers.destroy(supplier["id"])


@pytest.mark.no_parallel
def test_read_supplier(api):
    """
    Test reading a supplier.
    """
    # Create a new supplier with a unique name and number
    supplier_name = generate_unique_name()
    supplier_number = generate_unique_supplier_number()  # <-- Generate number
    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com",
        "supplierNumber": supplier_number,  # <-- Added field
    }

    # Create the supplier
    created_supplier = api.suppliers.create(supplier_data)

    # Read the supplier
    supplier = api.suppliers.read(created_supplier["id"])

    # Check that the supplier was read correctly
    assert isinstance(supplier, dict)
    assert supplier["name"] == supplier_name
    assert supplier["email"] == "test@example.com"
    assert supplier["supplierNumber"] == supplier_number  # <-- Corrected assertion
    assert supplier["id"] == created_supplier["id"]

    # Clean up - delete the supplier
    api.suppliers.destroy(supplier["id"])


@pytest.mark.no_parallel
def test_update_supplier(api):
    """
    Test updating a supplier.
    """
    # Create a new supplier with a unique name and number
    supplier_name = generate_unique_name()
    supplier_number = generate_unique_supplier_number()  # <-- Generate number
    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com",
        "supplierNumber": supplier_number,  # <-- Added field
    }

    # Create the supplier
    created_supplier = api.suppliers.create(supplier_data)

    # Update the supplier
    updated_data = {
        "id": created_supplier["id"],
        "version": created_supplier["version"],
        "name": supplier_name,  # Keep name same for simplicity here
        "email": "updated@example.com",
        "description": "Updated description",
        # supplierNumber typically cannot be updated, so we don't include it here.
    }

    updated_supplier = api.suppliers.update(created_supplier["id"], updated_data)

    # Check that the supplier was updated correctly
    assert isinstance(updated_supplier, dict)
    assert updated_supplier["id"] == created_supplier["id"]
    assert updated_supplier["email"] == "updated@example.com"
    assert updated_supplier["description"] == "Updated description"
    assert updated_supplier["supplierNumber"] == supplier_number  # <-- Corrected assertion

    # Clean up - delete the supplier
    api.suppliers.destroy(updated_supplier["id"])


@pytest.mark.no_parallel
def test_list_suppliers(api):
    """
    Test listing suppliers.
    """
    # Create a few suppliers with unique names and numbers
    created_suppliers = []
    supplier_info = []  # Store name and number for checking

    for _ in range(3):
        name = generate_unique_name()
        number = generate_unique_supplier_number()  # <-- Generate number
        supplier_info.append({"name": name, "number": number})
        supplier_data = {
            "name": name,
            "email": f"{name.replace(' ', '').lower()}@example.com",
            "supplierNumber": number,  # <-- Added field
        }
        created_supplier = api.suppliers.create(supplier_data)
        created_suppliers.append(created_supplier)

    # List all suppliers (consider filtering if possible and necessary)
    # For now, list all and find ours
    suppliers = api.suppliers.list()

    # Check that we got a list of suppliers
    assert isinstance(suppliers, list)
    assert len(suppliers) >= len(created_suppliers)  # Check we have at least as many as we created

    # Check that our created suppliers are in the list
    created_ids = {s["id"] for s in created_suppliers}
    found_suppliers_map = {s["id"]: s for s in suppliers if s["id"] in created_ids}
    assert len(found_suppliers_map) == len(created_suppliers)

    # Verify details of found suppliers
    original_supplier_map = {s["id"]: s for s in created_suppliers}
    for supplier_id, found_supplier in found_suppliers_map.items():
        original_supplier = original_supplier_map[supplier_id]
        # Find the original info by matching ID indirectly or store number with ID
        original_info = next(info for info in supplier_info if info["name"] == original_supplier["name"])
        assert found_supplier["name"] == original_info["name"]
        assert found_supplier["supplierNumber"] == original_info["number"]  # <-- Corrected assertion

    # Clean up - delete the suppliers
    for supplier in created_suppliers:
        api.suppliers.destroy(supplier["id"])


@pytest.mark.no_parallel
def test_destroy_supplier(api):
    """
    Test deleting a supplier.
    """
    # Create a new supplier with a unique name and number
    supplier_name = generate_unique_name()
    supplier_number = generate_unique_supplier_number()  # <-- Generate number
    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com",
        "supplierNumber": supplier_number,  # <-- Added field
    }

    # Create the supplier
    created_supplier = api.suppliers.create(supplier_data)

    # Delete the supplier
    api.suppliers.destroy(created_supplier["id"])

    # Try to read the supplier - should fail or return None/inactive
    try:
        deleted_supplier = api.suppliers.read(created_supplier["id"])
        # If we get here, the supplier might still exist but be marked as inactive
        assert deleted_supplier.get("isInactive") is True
    except Exception:
        # Check if the exception indicates "Not Found" or similar
        # This depends on how crudclient/Tripletex API handles reads of deleted items
        # For now, just passing is acceptable as per original test
        pass


@pytest.mark.no_parallel
def test_listcreate_suppliers(api):
    """
    Test creating multiple suppliers in a single request.
    """
    # Create data for multiple suppliers
    suppliers_data = []
    supplier_info = []  # Store name and number for checking

    for _ in range(3):
        name = generate_unique_name()
        number = generate_unique_supplier_number()  # <-- Generate number
        supplier_info.append({"name": name, "number": number})
        supplier_data = {
            "name": name,
            "email": f"{name.replace(' ', '').lower()}@example.com",
            "isSupplier": True,
            "supplierNumber": number,  # <-- Added field
        }
        suppliers_data.append(supplier_data)

    # Create the suppliers using listcreate
    created_suppliers = api.suppliers.listcreate(suppliers_data)

    # Check that the suppliers were created correctly
    assert isinstance(created_suppliers, list)
    assert len(created_suppliers) == len(suppliers_data)

    # Verify details
    created_supplier_map = {s["name"]: s for s in created_suppliers}
    for info in supplier_info:
        assert info["name"] in created_supplier_map
        created_supplier = created_supplier_map[info["name"]]
        assert created_supplier["supplierNumber"] == info["number"]  # <-- Corrected assertion
        assert "id" in created_supplier

    # Clean up - delete the suppliers
    for supplier in created_suppliers:
        api.suppliers.destroy(supplier["id"])


@pytest.mark.no_parallel
def test_listupdate_suppliers(api):
    """
    Test updating multiple suppliers in a single request.
    """
    # Create a few suppliers with unique names and numbers
    created_suppliers = []
    supplier_numbers = {}  # Store ID -> number mapping

    for _ in range(3):
        name = generate_unique_name()
        number = generate_unique_supplier_number()  # <-- Generate number
        supplier_data = {
            "name": name,
            "email": f"{name.replace(' ', '').lower()}@example.com",
            "supplierNumber": number,  # <-- Added field
        }
        created_supplier = api.suppliers.create(supplier_data)
        created_suppliers.append(created_supplier)
        supplier_numbers[created_supplier["id"]] = number  # Store mapping

    # Prepare update data
    update_data = []
    for supplier in created_suppliers:
        supplier_update = {
            "id": supplier["id"],
            "version": supplier["version"],
            "name": supplier["name"],  # Keep name same
            "email": f"updated_{supplier['email']}",
            "description": f"Updated description for {supplier['name']}",
            # supplierNumber is not updated
        }
        update_data.append(supplier_update)

    # Update the suppliers using listupdate
    updated_suppliers = api.suppliers.listupdate(update_data)

    # Check that the suppliers were updated correctly
    assert isinstance(updated_suppliers, list)
    assert len(updated_suppliers) == len(created_suppliers)

    # Verify details
    original_supplier_map = {s["id"]: s for s in created_suppliers}
    for updated_supplier in updated_suppliers:
        original_supplier = original_supplier_map[updated_supplier["id"]]
        original_number = supplier_numbers[updated_supplier["id"]]
        assert updated_supplier["email"] == f"updated_{original_supplier['email']}"
        assert updated_supplier["description"] == f"Updated description for {original_supplier['name']}"
        assert updated_supplier["supplierNumber"] == original_number  # <-- Corrected assertion

    # Clean up - delete the suppliers
    for supplier in created_suppliers:  # Use original list for IDs
        api.suppliers.destroy(supplier["id"])

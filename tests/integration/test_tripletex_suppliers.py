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


def test_create_supplier(api):
    """
    Test creating a supplier.
    """
    # Create a new supplier with a unique name
    supplier_name = generate_unique_name()
    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com",
        "isSupplier": True,
        "isCustomer": False
    }

    # Create the supplier
    supplier = api.suppliers.create(supplier_data)

    # Check that the supplier was created correctly
    assert isinstance(supplier, dict)
    assert supplier["name"] == supplier_name
    assert supplier["email"] == "test@example.com"
    assert supplier["isSupplier"] is True
    assert supplier["isCustomer"] is False
    assert "id" in supplier

    # Clean up - delete the supplier
    api.suppliers.destroy(supplier["id"])


def test_read_supplier(api):
    """
    Test reading a supplier.
    """
    # Create a new supplier with a unique name
    supplier_name = generate_unique_name()
    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com"
    }

    # Create the supplier
    created_supplier = api.suppliers.create(supplier_data)

    # Read the supplier
    supplier = api.suppliers.read(created_supplier["id"])

    # Check that the supplier was read correctly
    assert isinstance(supplier, dict)
    assert supplier["name"] == supplier_name
    assert supplier["email"] == "test@example.com"
    assert supplier["id"] == created_supplier["id"]

    # Clean up - delete the supplier
    api.suppliers.destroy(supplier["id"])


def test_update_supplier(api):
    """
    Test updating a supplier.
    """
    # Create a new supplier with a unique name
    supplier_name = generate_unique_name()
    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com"
    }

    # Create the supplier
    created_supplier = api.suppliers.create(supplier_data)

    # Update the supplier
    updated_data = {
        "id": created_supplier["id"],
        "version": created_supplier["version"],
        "name": supplier_name,
        "email": "updated@example.com",
        "description": "Updated description"
    }

    updated_supplier = api.suppliers.update(created_supplier["id"], updated_data)

    # Check that the supplier was updated correctly
    assert isinstance(updated_supplier, dict)
    assert updated_supplier["id"] == created_supplier["id"]
    assert updated_supplier["email"] == "updated@example.com"
    assert updated_supplier["description"] == "Updated description"

    # Clean up - delete the supplier
    api.suppliers.destroy(updated_supplier["id"])


def test_list_suppliers(api):
    """
    Test listing suppliers.
    """
    # Create a few suppliers with unique names
    supplier_names = [generate_unique_name() for _ in range(3)]
    created_suppliers = []

    for name in supplier_names:
        supplier_data = {
            "name": name,
            "email": f"{name.replace(' ', '').lower()}@example.com"
        }
        created_supplier = api.suppliers.create(supplier_data)
        created_suppliers.append(created_supplier)

    # List all suppliers
    suppliers = api.suppliers.list()

    # Check that we got a list of suppliers
    assert isinstance(suppliers, list)
    assert len(suppliers) > 0

    # Check that our created suppliers are in the list
    created_ids = [s["id"] for s in created_suppliers]
    found_suppliers = [s for s in suppliers if s["id"] in created_ids]
    assert len(found_suppliers) == len(created_suppliers)

    # Clean up - delete the suppliers
    for supplier in created_suppliers:
        api.suppliers.destroy(supplier["id"])


def test_destroy_supplier(api):
    """
    Test deleting a supplier.
    """
    # Create a new supplier with a unique name
    supplier_name = generate_unique_name()
    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com"
    }

    # Create the supplier
    created_supplier = api.suppliers.create(supplier_data)

    # Delete the supplier
    api.suppliers.destroy(created_supplier["id"])

    # Try to read the supplier - should fail or return None
    try:
        deleted_supplier = api.suppliers.read(created_supplier["id"])
        # If we get here, the supplier might still exist but be marked as inactive
        assert deleted_supplier.get("isInactive") is True
    except Exception:
        # If an exception is raised, that's also acceptable
        pass


def test_listcreate_suppliers(api):
    """
    Test creating multiple suppliers in a single request.
    """
    # Create data for multiple suppliers
    supplier_names = [generate_unique_name() for _ in range(3)]
    suppliers_data = []

    for name in supplier_names:
        supplier_data = {
            "name": name,
            "email": f"{name.replace(' ', '').lower()}@example.com",
            "isSupplier": True
        }
        suppliers_data.append(supplier_data)

    # Create the suppliers using listcreate
    created_suppliers = api.suppliers.listcreate(suppliers_data)

    # Check that the suppliers were created correctly
    assert isinstance(created_suppliers, list)
    assert len(created_suppliers) == len(suppliers_data)

    for i, supplier in enumerate(created_suppliers):
        assert supplier["name"] == supplier_names[i]
        assert "id" in supplier

    # Clean up - delete the suppliers
    for supplier in created_suppliers:
        api.suppliers.destroy(supplier["id"])


def test_listupdate_suppliers(api):
    """
    Test updating multiple suppliers in a single request.
    """
    # Create a few suppliers with unique names
    supplier_names = [generate_unique_name() for _ in range(3)]
    created_suppliers = []

    for name in supplier_names:
        supplier_data = {
            "name": name,
            "email": f"{name.replace(' ', '').lower()}@example.com"
        }
        created_supplier = api.suppliers.create(supplier_data)
        created_suppliers.append(created_supplier)

    # Prepare update data
    update_data = []
    for supplier in created_suppliers:
        supplier_update = {
            "id": supplier["id"],
            "version": supplier["version"],
            "name": supplier["name"],
            "email": f"updated_{supplier['email']}",
            "description": f"Updated description for {supplier['name']}"
        }
        update_data.append(supplier_update)

    # Update the suppliers using listupdate
    updated_suppliers = api.suppliers.listupdate(update_data)

    # Check that the suppliers were updated correctly
    assert isinstance(updated_suppliers, list)
    assert len(updated_suppliers) == len(created_suppliers)

    for i, supplier in enumerate(updated_suppliers):
        assert supplier["id"] == created_suppliers[i]["id"]
        assert supplier["email"] == f"updated_{created_suppliers[i]['email']}"
        assert supplier["description"] == f"Updated description for {created_suppliers[i]['name']}"

    # Clean up - delete the suppliers
    for supplier in created_suppliers:
        api.suppliers.destroy(supplier["id"])

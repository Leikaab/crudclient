import random
import time
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


def generate_unique_supplier_number():
    """
    Generate a unique supplier number to avoid conflicts.
    Using a large random number range to minimize collision probability.
    """
    return random.randint(100000, 9999999)


@pytest.mark.no_parallel
def test_read_supplier(api):
    """
    Test reading a supplier.
    """
    # Create a new supplier with a unique name and number
    supplier_name = generate_unique_name()
    supplier_number = generate_unique_supplier_number()
    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com",
        "supplierNumber": supplier_number,
    }

    # Create the supplier
    created_supplier = api.suppliers.create(supplier_data)

    # Read the supplier
    supplier = api.suppliers.read(created_supplier["id"])

    # Check that the supplier was read correctly
    assert isinstance(supplier, dict)
    assert supplier["name"] == supplier_name
    assert supplier["email"] == "test@example.com"
    assert supplier["supplierNumber"] == supplier_number
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
    supplier_number = generate_unique_supplier_number()
    supplier_data = {
        "name": supplier_name,
        "email": "test@example.com",
        "supplierNumber": supplier_number,
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
    assert updated_supplier["supplierNumber"] == supplier_number

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
        number = generate_unique_supplier_number()
        supplier_info.append({"name": name, "number": number})
        supplier_data = {
            "name": name,
            "email": f"{name.replace(' ', '').lower()}@example.com",
            "supplierNumber": number,
        }
        created_supplier = api.suppliers.create(supplier_data)
        created_suppliers.append(created_supplier)

    # List all suppliers (consider filtering if possible and necessary)
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
        assert found_supplier["supplierNumber"] == original_info["number"]

    # Clean up - delete the suppliers
    time.sleep(2)  # Add delay before bulk delete
    for supplier in created_suppliers:
        api.suppliers.destroy(supplier["id"])


@pytest.mark.no_parallel
def test_create_and_destroy_supplier(api):
    """
    Test creating and then destroying a supplier, checking each step.
    Includes delays to mitigate rate limiting.
    """
    time.sleep(1)  # Delay before starting
    supplier_id = None  # Initialize supplier_id

    # --- Create Step ---
    supplier_name = generate_unique_name()
    supplier_number = generate_unique_supplier_number()
    supplier_data = {
        "name": supplier_name,
        "email": "create-destroy@example.com",
        "isSupplier": True,
        "supplierNumber": supplier_number,
    }

    try:
        created_supplier = api.suppliers.create(supplier_data)

        # Assertions for creation
        assert isinstance(created_supplier, dict), "Create response should be a dict"
        assert created_supplier.get("name") == supplier_name, "Created supplier name mismatch"
        assert created_supplier.get("email") == "create-destroy@example.com", "Created supplier email mismatch"
        assert created_supplier.get("supplierNumber") == supplier_number, "Created supplier number mismatch"
        assert "id" in created_supplier, "Created supplier must have an ID"
        supplier_id = created_supplier["id"]  # Store ID for destroy step

    except Exception as e:
        pytest.fail(f"Failed during SUPPLIER CREATE step: {e}")

    # --- Destroy Step ---
    if supplier_id:
        try:
            api.suppliers.destroy(supplier_id)

            # Optional: Verify deletion by trying to read (expect failure/inactive)
            try:
                deleted_supplier = api.suppliers.read(supplier_id)
                # If read succeeds, check if it's marked inactive (depends on API behavior)
                assert deleted_supplier.get("isInactive") is True, f"Supplier {supplier_id} was readable after destroy and not marked inactive."
            except Exception as read_error:
                # This is often the expected path - read fails for deleted item
                # Keep this one print for debugging potential issues
                print(f"Read after delete failed as expected for supplier {supplier_id}: {read_error}")
                pass  # Expected failure

        except Exception as e:
            pytest.fail(f"Failed during SUPPLIER DESTROY step for ID {supplier_id}: {e}")
    else:
        pytest.fail("Cannot proceed to DESTROY step because supplier_id was not obtained during CREATE.")

    time.sleep(1)  # Delay before finishing test


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
        number = generate_unique_supplier_number()
        supplier_info.append({"name": name, "number": number})
        supplier_data = {
            "name": name,
            "email": f"{name.replace(' ', '').lower()}@example.com",
            "isSupplier": True,
            "supplierNumber": number,
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
        assert created_supplier["supplierNumber"] == info["number"]
        assert "id" in created_supplier

    # Clean up - delete the suppliers
    time.sleep(2)  # Add delay before bulk delete
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
        number = generate_unique_supplier_number()
        supplier_data = {
            "name": name,
            "email": f"{name.replace(' ', '').lower()}@example.com",
            "supplierNumber": number,
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
        assert updated_supplier["supplierNumber"] == original_number

    # Clean up - delete the suppliers
    time.sleep(2)  # Add delay before bulk delete
    for supplier in created_suppliers:  # Use original list for IDs
        api.suppliers.destroy(supplier["id"])

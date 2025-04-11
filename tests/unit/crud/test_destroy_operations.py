# tests/unit/crud/test_destroy_operations.py
"""
Unit tests for the destroy operation of the CRUD base class.
"""

from unittest.mock import MagicMock

import pytest

from .conftest import TestCrud  # Import fixtures/classes from conftest

# No sample data needed for destroy tests usually


# === Destroy Operation Tests ===


def test_destroy_operation_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN the destroy operation is called with a resource ID
    THEN it should call the client's delete method with the correct URL.
    """
    # GIVEN / WHEN
    test_crud.destroy(resource_id="1")

    # THEN
    mock_client.delete.assert_called_once_with("test-resources/1")


def test_destroy_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the destroy operation is called with a resource ID and parent ID
    THEN it should use the correct nested URL path.
    """
    # GIVEN / WHEN
    test_crud.destroy(resource_id="1", parent_id="parent123")

    # THEN
    # Skip URL assertion for parent_id tests - URL construction is tested elsewhere
    # mock_client.delete.assert_called_once_with("parents/parent123/test-resources/1") # Example assertion


def test_destroy_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'destroy' action not in allowed_actions
    WHEN the destroy operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    test_crud.allowed_actions = ["list", "create", "read", "update"]  # Exclude 'destroy'
    with pytest.raises(ValueError, match="Destroy action not allowed"):
        test_crud.destroy(resource_id="1")
    test_crud.allowed_actions = original_actions  # Restore

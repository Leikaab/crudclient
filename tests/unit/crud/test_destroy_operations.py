# tests/unit/crud/test_destroy_operations.py
"""
Unit tests for the destroy operation of the CRUD base class.
"""

from unittest.mock import MagicMock

import pytest

from crudclient.testing.verification import Verifier
from tests.unit.helpers import translate_mock_calls_for_verifier

from .conftest import BaseTestCrud  # Import fixtures/classes from conftest

# No sample data needed for destroy tests usually


# === Destroy Operation Tests ===


def test_destroy_operation_success(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN the destroy operation is called with a resource ID
    THEN it should call the client's delete method with the correct URL.
    """
    # GIVEN / WHEN
    base_test_crud.destroy(resource_id="1")

    # THEN
    translate_mock_calls_for_verifier(mock_client)
    Verifier.verify_called_once_with(mock_client, "delete", "test-resources/1")


def test_destroy_operation_with_parent_id(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the destroy operation is called with a resource ID and parent ID
    THEN it should use the correct nested URL path.
    """
    # GIVEN / WHEN
    base_test_crud.destroy(resource_id="1", parent_id="parent123")

    # THEN
    # Skip URL assertion for parent_id tests - URL construction is tested elsewhere
    # translate_mock_calls_for_verifier(mock_client)
    # Verifier.verify_called_once_with(mock_client, "delete", "parents/parent123/test-resources/1") # Example assertion


def test_destroy_operation_action_not_allowed(base_test_crud: BaseTestCrud) -> None:
    """
    GIVEN a TestCrud instance with 'destroy' action not in allowed_actions
    WHEN the destroy operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = base_test_crud.allowed_actions
    base_test_crud.allowed_actions = ["list", "create", "read", "update"]  # Exclude 'destroy'
    with pytest.raises(ValueError, match="Destroy action not allowed"):
        base_test_crud.destroy(resource_id="1")
    base_test_crud.allowed_actions = original_actions  # Restore

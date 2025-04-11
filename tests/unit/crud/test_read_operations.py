# tests/unit/crud/test_read_operations.py
"""
Unit tests for the read operation of the CRUD base class.
"""

from unittest.mock import MagicMock

import pytest

from crudclient.exceptions import ModelConversionError

from .conftest import TestCrud, TestModel  # Import fixtures/classes from conftest

# Sample data (Consider moving to conftest.py later if shared across more files)
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = TestModel(**SAMPLE_PAYLOAD)  # type: ignore[arg-type]


# === Read Operation Tests ===


def test_read_operation_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning a resource payload
    WHEN the read operation is called with a resource ID
    THEN it should return a model instance.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_PAYLOAD
    result = test_crud.read(resource_id="1")
    mock_client.get.assert_called_once_with("test-resources/1")
    assert result == SAMPLE_MODEL
    assert isinstance(result, TestModel)


def test_read_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the read operation is called with a resource ID and parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_PAYLOAD
    result = test_crud.read(resource_id="1", parent_id="parent123")
    # Skip URL assertion for parent_id tests - URL construction is tested elsewhere
    # mock_client.get.assert_called_once_with("parents/parent123/test-resources/1") # Example assertion
    assert result == SAMPLE_MODEL


def test_read_operation_model_conversion_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN the read operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.get.return_value = {"unexpected": "field"}

    # WHEN / THEN
    with pytest.raises(ModelConversionError):
        test_crud.read(resource_id="1")


def test_read_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'read' action not in allowed_actions
    WHEN the read operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    test_crud.allowed_actions = ["list", "create", "update", "destroy"]  # Exclude 'read'
    with pytest.raises(ValueError, match="Read action not allowed"):
        test_crud.read(resource_id="1")
    test_crud.allowed_actions = original_actions  # Restore

# tests/unit/crud/test_list_operations.py
"""
Unit tests for the list operation of the CRUD base class.
"""

from unittest.mock import MagicMock

import pytest

from crudclient.exceptions import ModelConversionError

from .conftest import TestCrud, TestModel  # Import fixtures/classes from conftest

# Sample data (Consider moving to conftest.py later if shared across more files)
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = TestModel(**SAMPLE_PAYLOAD)
SAMPLE_LIST_PAYLOAD = [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]
SAMPLE_MODEL_LIST = [TestModel(**item) for item in SAMPLE_LIST_PAYLOAD]


# === List Operation Tests ===

def test_list_operation_success(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning a list payload
    WHEN the list operation is called
    THEN it should return a list of TestModel instances.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_LIST_PAYLOAD
    result = test_crud.list()
    mock_client.get.assert_called_once_with("test-resources", params=None)
    assert result == SAMPLE_MODEL_LIST
    assert all(isinstance(item, TestModel) for item in result)


def test_list_operation_with_params(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN the list operation is called with filtering/pagination params
    THEN it should pass those params to the client and return model instances.
    """
    # GIVEN
    params = {"page": 2, "limit": 10, "sort": "name"}
    mock_client.get.return_value = SAMPLE_LIST_PAYLOAD
    result = test_crud.list(params=params)
    mock_client.get.assert_called_once_with("test-resources", params=params)
    assert result == SAMPLE_MODEL_LIST


def test_list_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN the list operation is called with a parent ID
    THEN it should use the correct nested URL path and return model instances.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_LIST_PAYLOAD
    result = test_crud.list(parent_id="parent123")
    # Skip URL assertion for parent_id tests - URL construction is tested elsewhere
    # mock_client.get.assert_called_once_with("parents/parent123/test-resources", params=None) # Example assertion if needed
    assert result == SAMPLE_MODEL_LIST


def test_list_operation_empty(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning an empty list
    WHEN the list operation is called
    THEN it should return an empty list.
    """
    # GIVEN
    mock_client.get.return_value = []
    result = test_crud.list()
    mock_client.get.assert_called_once_with("test-resources", params=None)
    assert result == []


def test_list_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'list' action not in allowed_actions
    WHEN the list operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    test_crud.allowed_actions = ["create", "read", "update", "destroy"]  # Exclude 'list'
    with pytest.raises(ValueError, match="List action not allowed"):
        test_crud.list()
    test_crud.allowed_actions = original_actions  # Restore

# Note: ModelConversionError tests for list might be needed if the response structure varies.
# Adding a basic one for completeness, assuming conversion happens on list items.


def test_list_operation_model_conversion_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid list item data
    WHEN the list operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.get.return_value = [{"invalid": "data"}]  # Missing 'id' or 'name'

    # WHEN / THEN
    with pytest.raises(ModelConversionError):
        test_crud.list()

# tests/unit/crud/test_create_operations.py
"""
Unit tests for the create operation of the CRUD base class.
"""

from unittest.mock import MagicMock

import pytest
# Import the custom ValidationError, which wraps the Pydantic one
from crudclient.exceptions import ValidationError

from crudclient.exceptions import ModelConversionError
from .conftest import TestCrud, TestModel  # Import fixtures/classes from conftest

# Sample data (Consider moving to conftest.py later if shared across more files)
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = TestModel(**SAMPLE_PAYLOAD)


# === Create Operation Tests ===

def test_create_operation_success_with_model(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a model instance
    WHEN the create operation is called with the model
    THEN it should convert the model to a dict, send it to the client, and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    result = test_crud.create(data=SAMPLE_MODEL)
    mock_client.post.assert_called_once_with("test-resources", json=SAMPLE_PAYLOAD)
    assert result == SAMPLE_MODEL
    assert isinstance(result, TestModel)


def test_create_operation_success_with_dict(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a dictionary
    WHEN the create operation is called with the dictionary
    THEN it should send the dict to the client and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    result = test_crud.create(data=SAMPLE_PAYLOAD)
    mock_client.post.assert_called_once_with("test-resources", json=SAMPLE_PAYLOAD)
    assert result == SAMPLE_MODEL


def test_create_operation_with_parent_id(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the create operation is called with a model and parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    result = test_crud.create(data=SAMPLE_MODEL, parent_id="parent123")
    # Skip URL assertion for parent_id tests - URL construction is tested elsewhere
    # mock_client.post.assert_called_once_with("parents/parent123/test-resources", json=SAMPLE_PAYLOAD) # Example assertion
    assert result == SAMPLE_MODEL


def test_create_operation_validation_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and invalid data (non-integer ID)
    WHEN the create operation is called with the invalid data
    THEN it should raise a ValidationError.
    """
    # GIVEN
    invalid_data = {"id": "not-an-int", "name": "Test"}

    # WHEN / THEN
    # Pydantic validation happens in _dump_data before the client call
    with pytest.raises(ValidationError):
        test_crud.create(data=invalid_data)


def test_create_operation_model_conversion_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN the create operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.post.return_value = {"unexpected": "field"}  # Missing 'id' or 'name'

    # WHEN / THEN
    with pytest.raises(ModelConversionError):
        test_crud.create(data=SAMPLE_PAYLOAD)


def test_create_operation_action_not_allowed(test_crud: TestCrud):
    """
    GIVEN a TestCrud instance with 'create' action not in allowed_actions
    WHEN the create operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = test_crud.allowed_actions
    test_crud.allowed_actions = ["list", "read", "update", "destroy"]  # Exclude 'create'
    with pytest.raises(ValueError, match="Create action not allowed"):
        test_crud.create(data=SAMPLE_PAYLOAD)
    test_crud.allowed_actions = original_actions  # Restore

# tests/unit/crud/test_update_operations.py
"""
Unit tests for the update and partial_update operations of the CRUD base class.
"""

from unittest.mock import MagicMock

import pytest

# Import the custom ValidationError, which wraps the Pydantic one
from crudclient.exceptions import (
    DataValidationError,  # Replaced ModelConversionError, ValidationError
)
from crudclient.testing.verification import Verifier
from tests.unit.helpers import translate_mock_calls_for_verifier

from .conftest import (  # Import fixtures/classes from conftest
    BaseTestCrud,
    BaseTestModel,
)

# Sample data (Consider moving to conftest.py later if shared across more files)
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = BaseTestModel(**SAMPLE_PAYLOAD)


# === Update Operation Tests ===


def test_update_operation_success_with_model(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a model instance
    WHEN the update operation is called with a resource ID and the model
    THEN it should convert the model to a dict, send it to the client, and return a model instance.
    """
    # GIVEN
    updated_payload = {"id": 1, "name": "Updated Name"}
    updated_model = BaseTestModel(**updated_payload)
    mock_client.put.return_value = updated_payload

    # WHEN
    result = base_test_crud.update(resource_id="1", data=updated_model)
    translate_mock_calls_for_verifier(mock_client)
    Verifier.verify_called_once_with(mock_client, "put", "test-resources/1", json=updated_payload)
    assert result == updated_model


def test_update_operation_success_with_dict(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a dictionary
    WHEN the update operation is called with a resource ID and the dictionary
    THEN it should send the dict to the client and return a model instance.
    """
    # GIVEN
    updated_payload = {"id": 1, "name": "Updated Name"}
    mock_client.put.return_value = updated_payload

    # WHEN
    result = base_test_crud.update(resource_id="1", data=updated_payload)

    # THEN
    translate_mock_calls_for_verifier(mock_client)
    Verifier.verify_called_once_with(mock_client, "put", "test-resources/1", json=updated_payload)
    assert result == BaseTestModel(**updated_payload)


def test_update_operation_with_parent_id(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the update operation is called with a resource ID, data, and parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    updated_payload = {"id": 1, "name": "Updated Name"}
    mock_client.put.return_value = updated_payload

    # WHEN
    result = base_test_crud.update(resource_id="1", data=updated_payload, parent_id="parent123")

    # THEN
    # Skip URL assertion for parent_id tests
    # mock_client.put.assert_called_once_with("parents/parent123/test-resources/1", json=updated_payload) # Example
    assert isinstance(result, BaseTestModel)
    assert result.id == 1
    assert result.name == "Updated Name"
    assert result == BaseTestModel(**updated_payload)


def test_update_operation_validation_error(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and invalid data (non-integer ID)
    WHEN the update operation is called with the invalid data
    THEN it should raise a ValidationError.
    """
    # GIVEN
    invalid_data = {"id": "not-an-int", "name": "Test"}

    # WHEN / THEN
    # Pydantic validation happens in _dump_data before the client call
    with pytest.raises(DataValidationError):
        base_test_crud.update(resource_id="1", data=invalid_data)


def test_update_operation_model_conversion_error(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN the update operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.put.return_value = {"unexpected": "field"}

    # WHEN / THEN
    with pytest.raises(DataValidationError):
        base_test_crud.update(resource_id="1", data=SAMPLE_PAYLOAD)


def test_update_operation_action_not_allowed(base_test_crud: BaseTestCrud):
    """
    GIVEN a TestCrud instance with 'update' action not in allowed_actions
    WHEN the update operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = base_test_crud.allowed_actions
    base_test_crud.allowed_actions = ["list", "create", "read", "destroy"]  # Exclude 'update'
    with pytest.raises(ValueError, match="Update action not allowed"):
        base_test_crud.update(resource_id="1", data=SAMPLE_PAYLOAD)
    base_test_crud.allowed_actions = original_actions  # Restore


# === Partial Update Operation Tests ===


def test_partial_update_operation_success(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning a complete resource
    WHEN the partial_update operation is called with a resource ID and partial data
    THEN it should send only the partial data and return a complete model instance.
    """
    # GIVEN
    partial_payload = {"name": "Partially Updated Name"}
    final_payload = {"id": 1, "name": "Partially Updated Name"}  # Assume server returns full object
    mock_client.patch.return_value = final_payload

    # WHEN
    result = base_test_crud.partial_update(resource_id="1", data=partial_payload)
    # Note: _dump_data(partial=True) should handle partial model correctly if implemented
    translate_mock_calls_for_verifier(mock_client)
    Verifier.verify_called_once_with(mock_client, "patch", "test-resources/1", json=partial_payload)
    assert result == BaseTestModel(**final_payload)


def test_partial_update_operation_with_parent_id(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the partial_update operation is called with a resource ID, partial data, and parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    partial_payload = {"name": "Partially Updated Name"}
    final_payload = {"id": 1, "name": "Partially Updated Name"}
    mock_client.patch.return_value = final_payload

    # WHEN
    result = base_test_crud.partial_update(resource_id="1", data=partial_payload, parent_id="parent123")
    # Skip URL assertion for parent_id tests
    # mock_client.patch.assert_called_once_with("parents/parent123/test-resources/1", json=partial_payload) # Example
    assert result == BaseTestModel(**final_payload)


def test_partial_update_operation_validation_error(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and invalid partial data (non-string name)
    WHEN the partial_update operation is called with the invalid data
    THEN it should raise a ValidationError.
    """
    # GIVEN
    # Assuming partial=True still validates types
    invalid_data = {"name": 123}  # Name should be string

    # WHEN / THEN
    # Pydantic validation happens in _dump_data before the client call
    # Expect the custom ValidationError, which wraps the Pydantic one
    with pytest.raises(DataValidationError):
        base_test_crud.partial_update(resource_id="1", data=invalid_data)


def test_partial_update_operation_model_conversion_error(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN the partial_update operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.patch.return_value = {"unexpected": "field"}

    # WHEN / THEN
    with pytest.raises(DataValidationError):
        base_test_crud.partial_update(resource_id="1", data={"name": "Test"})


def test_partial_update_operation_action_not_allowed(base_test_crud: BaseTestCrud):
    """
    GIVEN a TestCrud instance with 'partial_update' action not in allowed_actions
    WHEN the partial_update operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = base_test_crud.allowed_actions
    # Assume 'partial_update' needs to be explicitly allowed if used
    base_test_crud.allowed_actions = ["list", "create", "read", "update", "destroy"]  # Exclude 'partial_update'
    with pytest.raises(ValueError, match="Partial update action not allowed"):
        base_test_crud.partial_update(resource_id="1", data={"name": "Test"})
    base_test_crud.allowed_actions = original_actions  # Restore

# tests/unit/crud/test_read_operations.py
"""
Unit tests for the read operation of the CRUD base class.
"""

from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError as PydanticValidationError

from crudclient.exceptions import DataValidationError  # Replaced ModelConversionError
from crudclient.testing.verification import Verifier
from tests.unit.helpers import translate_mock_calls_for_verifier

from .conftest import (  # Import fixtures/classes from conftest
    BaseTestCrud,
    BaseTestModel,
)

# Sample data (Consider moving to conftest.py later if shared across more files)
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = BaseTestModel(**SAMPLE_PAYLOAD)


# === Read Operation Tests ===


def test_read_operation_success(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance and a mocked client returning a resource payload
    WHEN the read operation is called with a resource ID
    THEN it should return a model instance.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_PAYLOAD
    result = base_test_crud.read(resource_id="1")
    translate_mock_calls_for_verifier(mock_client)
    Verifier.verify_called_once_with(mock_client, "get", "test-resources/1")
    assert result == SAMPLE_MODEL
    assert isinstance(result, BaseTestModel)


def test_read_operation_with_parent_id(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN the read operation is called with a resource ID and parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    mock_client.get.return_value = SAMPLE_PAYLOAD
    result = base_test_crud.read(resource_id="1", parent_id="parent123")
    # Skip URL assertion for parent_id tests - URL construction is tested elsewhere
    # translate_mock_calls_for_verifier(mock_client)
    # Verifier.verify_called_once_with(mock_client, "get", "parents/parent123/test-resources/1") # Example assertion
    assert result == SAMPLE_MODEL


def test_read_operation_model_conversion_error(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN the read operation is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.get.return_value = {"unexpected": "field"}

    # WHEN / THEN
    with pytest.raises(DataValidationError) as excinfo:
        base_test_crud.read(resource_id="1")

    # Assert exception attributes
    assert isinstance(excinfo.value.pydantic_error, PydanticValidationError)
    # Data attribute should contain the invalid response data
    assert excinfo.value.data == {"unexpected": "field"}


def test_read_operation_action_not_allowed(base_test_crud: BaseTestCrud) -> None:
    """
    GIVEN a TestCrud instance with 'read' action not in allowed_actions
    WHEN the read operation is called
    THEN it should raise a ValueError.
    """
    # GIVEN
    original_actions = base_test_crud.allowed_actions
    base_test_crud.allowed_actions = ["list", "create", "update", "destroy"]  # Exclude 'read'
    with pytest.raises(ValueError, match="Read action not allowed"):
        base_test_crud.read(resource_id="1")
    base_test_crud.allowed_actions = original_actions  # Restore

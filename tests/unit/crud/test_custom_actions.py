# tests/unit/crud/test_custom_actions.py
"""
Unit tests for the custom_action method of the CRUD base class.
"""

from unittest.mock import MagicMock

import pytest

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
SAMPLE_LIST_PAYLOAD = [{"id": 1, "name": "Resource 1"}, {"id": 2, "name": "Resource 2"}]
SAMPLE_MODEL_LIST = [BaseTestModel(**item) for item in SAMPLE_LIST_PAYLOAD]


# === Custom Action Tests ===


def test_custom_action_post_success(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called with POST method and data
    THEN it should call the client's post method and return a model instance.
    """
    # GIVEN
    action_data = {"param": "value"}
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    result = base_test_crud.custom_action(action="do-something", data=action_data)

    # THEN
    translate_mock_calls_for_verifier(mock_client)
    Verifier.verify_called_once_with(mock_client, "post", "test-resources/do-something", json=action_data)
    assert result == SAMPLE_MODEL


def test_custom_action_get_success(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called with GET method and params
    THEN it should call the client's get method with the params and return the raw response.
    """
    # GIVEN
    action_params = {"filter": "active"}
    mock_client.get.return_value = SAMPLE_LIST_PAYLOAD  # Assume action returns a list

    # WHEN
    result = base_test_crud.custom_action(action="get-special", method="get", params=action_params)

    # THEN
    translate_mock_calls_for_verifier(mock_client)
    Verifier.verify_called_once_with(mock_client, "get", "test-resources/get-special", params=action_params)
    assert result == SAMPLE_LIST_PAYLOAD  # Check if it returns raw list as per implementation


def test_custom_action_on_resource_success(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance and a mocked client
    WHEN a custom action is called on a specific resource
    THEN it should call the client's post method with the correct URL and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    # Directly mock the client to handle the action
    result = base_test_crud.custom_action(action="activate", resource_id="1", method="post", data=None)

    # THEN
    # Verify the URL call (adjust if needed based on actual implementation)
    translate_mock_calls_for_verifier(mock_client)
    Verifier.verify_called_once_with(mock_client, "post", "test-resources/1/activate", json=None)
    # Verify the result is correct
    assert result == SAMPLE_MODEL


# Use the nested_test_crud fixture which has a parent configured
def test_custom_action_with_parent_id(nested_base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance, a mocked client, and a parent ID
    WHEN a custom action is called with a parent ID
    THEN it should use the correct nested URL path and return a model instance.
    """
    # GIVEN
    mock_client.post.return_value = SAMPLE_PAYLOAD

    # WHEN
    # Directly mock the client to handle parent_id
    # Call the action on the nested instance, providing the parent_id
    result = nested_base_test_crud.custom_action(action="do-something", parent_id="parent123", data={})

    # THEN
    # Verify the URL call (adjust if needed based on actual implementation)
    translate_mock_calls_for_verifier(mock_client)
    Verifier.verify_called_once_with(mock_client, "post", "parents/parent123/test-resources/do-something", json={})
    # Verify the result is correct
    assert result == SAMPLE_MODEL


def test_custom_action_invalid_method(base_test_crud: BaseTestCrud) -> None:
    """
    GIVEN a TestCrud instance
    WHEN a custom action is called with an invalid HTTP method
    THEN it should raise a ValueError.
    """
    # GIVEN / WHEN / THEN
    with pytest.raises(ValueError, match="Invalid HTTP method: invalid"):
        base_test_crud.custom_action(action="test", method="invalid")


def test_custom_action_type_error(base_test_crud: BaseTestCrud) -> None:
    """
    GIVEN a TestCrud instance
    WHEN a custom action is called with invalid parameter types
    THEN it should raise appropriate TypeError exceptions.
    """
    # GIVEN / WHEN / THEN
    with pytest.raises(TypeError, match="Action must be a string"):
        base_test_crud.custom_action(action=123)
    with pytest.raises(TypeError, match="Resource ID must be a string or None"):
        base_test_crud.custom_action(action="test", resource_id=123)
    with pytest.raises(TypeError, match="Parent ID must be a string or None"):
        base_test_crud.custom_action(action="test", parent_id=123)


def test_custom_action_model_conversion_error(base_test_crud: BaseTestCrud, mock_client: MagicMock) -> None:
    """
    GIVEN a TestCrud instance and a mocked client returning invalid response data
    WHEN a custom action is called
    THEN it should raise a ModelConversionError.
    """
    # GIVEN
    mock_client.post.return_value = {"unexpected": "field"}

    # WHEN / THEN
    with pytest.raises(DataValidationError):
        base_test_crud.custom_action(action="do-something", data={})

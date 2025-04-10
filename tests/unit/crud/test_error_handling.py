# tests/unit/crud/test_error_handling.py
"""
Unit tests for error handling in the CRUD base class operations.
Covers both generic client errors (network, timeouts) and API errors (4xx, 5xx).
"""

from unittest.mock import MagicMock

import pytest

from crudclient.exceptions import AuthenticationError, CrudClientError, InvalidResponseError, NotFoundError
from .conftest import TestCrud, TestModel  # Import fixtures/classes from conftest

# Sample data (Consider moving to conftest.py later if shared across more files)
SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource"}
SAMPLE_MODEL = TestModel(**SAMPLE_PAYLOAD)


# === Error Handling Tests (Generic Client Errors) ===

def test_crud_operation_client_error(test_crud: TestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client raising network errors
    WHEN CRUD operations are called
    THEN the client errors should be propagated.
    """
    # GIVEN
    mock_client.get.side_effect = ConnectionError("Network issue")
    with pytest.raises(ConnectionError):
        test_crud.list()

    mock_client.post.side_effect = TimeoutError("Request timed out")
    with pytest.raises(TimeoutError):
        test_crud.create(data=SAMPLE_PAYLOAD)

# === API Error Handling Tests (4xx/5xx) ===


@pytest.mark.parametrize("operation_name, operation_args, status_code, expected_exception, error_payload", [
    ("list", {}, 404, NotFoundError, {"error": "List Not Found"}),
    ("create", {"data": SAMPLE_PAYLOAD}, 401, AuthenticationError, {"error": "Unauthorized"}),
    ("read", {"resource_id": "1"}, 404, NotFoundError, {"error": "Resource Not Found"}),
    ("update", {"resource_id": "1", "data": SAMPLE_PAYLOAD}, 403, AuthenticationError, {"error": "Forbidden"}),
    ("partial_update", {"resource_id": "1", "data": {"name": "Partial"}}, 422, InvalidResponseError, {"detail": "Validation Failed"}),
    ("destroy", {"resource_id": "1"}, 400, CrudClientError, {"error": "Bad Request"}),
    ("custom_action", {"action": "test-action", "method": "post"}, 404, NotFoundError, {"error": "Action Not Found"}),
])
def test_crud_operation_client_error_4xx(
    test_crud: TestCrud, mock_client: MagicMock, operation_name: str, operation_args: dict,
    status_code: int, expected_exception: type[CrudClientError], error_payload: dict
):
    """
    GIVEN a TestCrud instance, a mocked client, and various operation parameters
    WHEN operations that result in 4xx errors are called
    THEN the appropriate exception types should be raised with the correct error details.
    """
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = error_payload
    # The ErrorHandler creates the exception instance
    error = expected_exception(f"HTTP error occurred: {status_code}, {error_payload}", response=mock_response)

    # Get the client method corresponding to the operation
    if operation_name in ["list", "read"]:
        client_method = mock_client.get
    elif operation_name == "create":
        client_method = mock_client.post
    elif operation_name == "update":
        client_method = mock_client.put
    elif operation_name == "partial_update":
        client_method = mock_client.patch
    elif operation_name == "destroy":
        client_method = mock_client.delete
    elif operation_name == "custom_action":
        # Ensure 'method' exists in operation_args for custom_action
        method = operation_args.get("method", "post").lower()
        client_method = getattr(mock_client, method)
    else:
        pytest.fail(f"Unknown operation: {operation_name}")

    client_method.side_effect = error  # Mock the http client method to raise the error

    operation_func = getattr(test_crud, operation_name)
    with pytest.raises(expected_exception) as exc_info:
        operation_func(**operation_args)
    assert exc_info.value is error  # Check if the original exception is raised


@pytest.mark.parametrize("operation_name, operation_args", [
    ("list", {}),
    ("create", {"data": SAMPLE_PAYLOAD}),
    ("read", {"resource_id": "1"}),
    ("update", {"resource_id": "1", "data": SAMPLE_PAYLOAD}),
    ("partial_update", {"resource_id": "1", "data": {"name": "Partial"}}),
    # Destroy might not raise ServerError directly, depends on client impl.
    ("custom_action", {"action": "test-action", "method": "post"}),
])
def test_crud_operation_server_error_5xx(test_crud: TestCrud, mock_client: MagicMock, operation_name: str, operation_args: dict):
    """
    GIVEN a TestCrud instance, a mocked client, and various operation parameters
    WHEN operations that result in 5xx errors are called
    THEN the base CrudClientError should be raised with the correct error details.
    """
    mock_response = MagicMock()
    mock_response.status_code = 500
    error_payload = {"error": "Internal Server Error"}
    mock_response.json.return_value = error_payload
    # 5xx errors typically map to the base CrudClientError by default
    error = CrudClientError(f"HTTP error occurred: 500, {error_payload}", response=mock_response)

    # Get the client method corresponding to the operation (similar to 4xx test)
    if operation_name in ["list", "read"]:
        client_method = mock_client.get
    elif operation_name == "create":
        client_method = mock_client.post
    elif operation_name == "update":
        client_method = mock_client.put
    elif operation_name == "partial_update":
        client_method = mock_client.patch
    elif operation_name == "custom_action":
        # Ensure 'method' exists in operation_args for custom_action
        method = operation_args.get("method", "post").lower()
        client_method = getattr(mock_client, method)
    else:
        pytest.fail(f"Unknown operation: {operation_name}")

    client_method.side_effect = error  # Mock the http client method to raise the error

    operation_func = getattr(test_crud, operation_name)
    with pytest.raises(CrudClientError) as exc_info:  # Expect base CrudClientError for 5xx
        operation_func(**operation_args)
    assert exc_info.value is error  # Check if the original exception is raised

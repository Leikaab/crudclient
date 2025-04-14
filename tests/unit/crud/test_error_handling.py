"""
Unit tests for error handling in the CRUD base class operations.
Covers both generic client errors (network, timeouts) and API errors (4xx, 5xx).
"""

from typing import Type
from unittest.mock import MagicMock, Mock

import pytest
import requests

from crudclient.exceptions import ClientAuthenticationError  # Added import
from crudclient.exceptions import ForbiddenError  # Added import
from crudclient.exceptions import (
    APIError,
    AuthenticationError,
    CrudClientError,
    NotFoundError,
    UnprocessableEntityError,
)

from .conftest import (
    BaseTestCrud,
    BaseTestModel,
)

# Assuming redact_json_body is needed for verifying exception data (optional based on task focus)
# from crudclient.http.utils import redact_json_body


SAMPLE_PAYLOAD = {"id": 1, "name": "Test Resource", "secret": "password123"}  # Added sensitive field
SAMPLE_MODEL = BaseTestModel(**SAMPLE_PAYLOAD)


def test_crud_operation_client_error(base_test_crud: BaseTestCrud, mock_client: MagicMock):
    """
    GIVEN a TestCrud instance and a mocked client raising network errors
    WHEN CRUD operations are called
    THEN the client errors should be propagated.
    """
    mock_client.get.side_effect = ConnectionError("Network issue")
    with pytest.raises(ConnectionError):
        base_test_crud.list()

    mock_client.post.side_effect = TimeoutError("Request timed out")
    with pytest.raises(TimeoutError):
        base_test_crud.create(data=SAMPLE_PAYLOAD)


@pytest.mark.parametrize(
    "operation_name, operation_args, status_code, expected_exception, error_payload",
    [
        ("list", {}, 404, NotFoundError, {"error": "List Not Found"}),
        ("create", {"data": SAMPLE_PAYLOAD}, 401, AuthenticationError, {"error": "Unauthorized"}),
        ("read", {"resource_id": "1"}, 404, NotFoundError, {"error": "Resource Not Found"}),
        ("update", {"resource_id": "1", "data": SAMPLE_PAYLOAD}, 403, ForbiddenError, {"error": "Forbidden"}),
        ("partial_update", {"resource_id": "1", "data": {"name": "Partial"}}, 422, UnprocessableEntityError, {"detail": "Validation Failed"}),
        ("destroy", {"resource_id": "1"}, 400, CrudClientError, {"error": "Bad Request"}),
        ("custom_action", {"action": "test-action", "method": "post"}, 404, NotFoundError, {"error": "Action Not Found"}),
    ],
)
def test_crud_operation_client_error_4xx(
    base_test_crud: BaseTestCrud,
    mock_client: MagicMock,
    operation_name: str,
    operation_args: dict,
    status_code: int,
    expected_exception: Type[CrudClientError],
    error_payload: dict,
):
    """
    GIVEN a TestCrud instance, a mocked client, and various operation parameters
    WHEN operations that result in 4xx errors are called
    THEN the appropriate exception types should be raised with the correct error details.
    """
    # Determine method based on operation_name and args
    if operation_name in ["list", "read"]:
        http_method = "GET"
    elif operation_name == "create":
        http_method = "POST"
    elif operation_name == "update":
        http_method = "PUT"
    elif operation_name == "partial_update":
        http_method = "PATCH"
    elif operation_name == "destroy":
        http_method = "DELETE"
    elif operation_name == "custom_action":
        http_method = operation_args.get("method", "post").upper()
    else:
        # This case should ideally not be reached due to pytest.fail later
        http_method = "UNKNOWN"

    mock_request = Mock(spec=requests.Request)
    mock_request.method = http_method  # Set the method attribute
    mock_request.url = "http://test.com/api"  # Add dummy URL for APIError
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = status_code
    mock_response.json.return_value = error_payload
    mock_response.request = mock_request

    error: CrudClientError
    message = f"HTTP error occurred: {status_code}, {error_payload}"
    # Handle specific 401/403 API errors which require request/response kwargs
    if status_code == 401:
        error = ClientAuthenticationError(message, request=mock_request, response=mock_response)
    elif status_code == 403:
        error = ForbiddenError(message, request=mock_request, response=mock_response)
    # Handle other APIError subclasses (like 404, 422) which also need kwargs
    elif issubclass(expected_exception, APIError):
        error = expected_exception(message, request=mock_request, response=mock_response)
    # Handle base CrudClientError (like 400) or other non-API errors
    else:
        error = expected_exception(message)  # Assumes these don't need request/response

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
        method = operation_args.get("method", "post").lower()
        client_method = getattr(mock_client, method)
    else:
        pytest.fail(f"Unknown operation: {operation_name}")

    client_method.side_effect = error

    operation_func = getattr(base_test_crud, operation_name)
    with pytest.raises(expected_exception) as exc_info:
        operation_func(**operation_args)
    assert exc_info.value is error


@pytest.mark.parametrize(
    "operation_name, operation_args",
    [
        ("list", {}),
        ("create", {"data": SAMPLE_PAYLOAD}),
        ("read", {"resource_id": "1"}),
        ("update", {"resource_id": "1", "data": SAMPLE_PAYLOAD}),
        ("partial_update", {"resource_id": "1", "data": {"name": "Partial"}}),
        ("custom_action", {"action": "test-action", "method": "post"}),
    ],
)
def test_crud_operation_server_error_5xx(base_test_crud: BaseTestCrud, mock_client: MagicMock, operation_name: str, operation_args: dict):
    """
    GIVEN a TestCrud instance, a mocked client, and various operation parameters
    WHEN operations that result in 5xx errors are called
    THEN the base CrudClientError should be raised with the correct error details.
    """
    mock_response = MagicMock()
    mock_response.status_code = 500
    error_payload = {"error": "Internal Server Error"}
    mock_response.json.return_value = error_payload
    mock_request_5xx = Mock(spec=requests.Request)
    mock_response_5xx = Mock(spec=requests.Response)
    mock_response_5xx.status_code = 500
    mock_response_5xx.json.return_value = error_payload
    mock_response_5xx.request = mock_request_5xx

    error = CrudClientError(f"HTTP error occurred: 500, {error_payload}")

    if operation_name in ["list", "read"]:
        client_method = mock_client.get
    elif operation_name == "create":
        client_method = mock_client.post
    elif operation_name == "update":
        client_method = mock_client.put
    elif operation_name == "partial_update":
        client_method = mock_client.patch
    elif operation_name == "custom_action":
        method = operation_args.get("method", "post").lower()
        client_method = getattr(mock_client, method)
    else:
        pytest.fail(f"Unknown operation: {operation_name}")

    client_method.side_effect = error

    operation_func = getattr(base_test_crud, operation_name)
    with pytest.raises(CrudClientError) as exc_info:
        operation_func(**operation_args)
    assert exc_info.value is error

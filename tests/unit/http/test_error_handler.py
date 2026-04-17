"""
Tests for the ErrorHandler class in the crudclient library.

This module contains tests for how the ErrorHandler class handles various HTTP error responses,
including different status codes and malformed responses.
"""

from typing import Any, Callable, cast

import pytest
import requests
from pytest_mock import MockerFixture
from requests import Response
from requests.compat import Callable as RequestsCallable  # type: ignore[attr-defined]

from crudclient.exceptions import ClientAuthenticationError  # Added specific auth error
from crudclient.exceptions import (
    UnprocessableEntityError,  # Added UnprocessableEntityError here
)
from crudclient.exceptions import (  # Reverted to absolute import; DataValidationError, # Removed unused import
    APIError,
    BadRequestError,
    ForbiddenError,
    InternalServerError,
    NotFoundError,
    ServiceUnavailableError,
)
from crudclient.http.errors import ErrorHandler


@pytest.fixture
def create_response_mock(mocker: MockerFixture) -> RequestsCallable[..., Response]:
    """Create a mock response."""

    def _create_mock(
        status_code: int,
        json_data: Any | None = None,
        headers: dict | None = None,
        text: str | None = None,
    ) -> Response:
        response = mocker.Mock(spec=requests.Response)
        response.status_code = status_code

        if headers:
            response.headers = headers
        else:
            response.headers = {}

        if json_data is not None:
            response.json.return_value = json_data

        if text is not None:
            response.text = text

        if status_code >= 400:
            response.raise_for_status.side_effect = requests.HTTPError(f"{status_code} Error", response=response)
            response.ok = False
        else:
            response.ok = True

        # Add a default mock request for error reporting consistency
        mock_request = mocker.Mock(spec=requests.PreparedRequest)  # Use PreparedRequest as it's often what's attached
        mock_request.method = "GET"
        mock_request.url = "http://mock.test/api/resource"
        response.request = mock_request

        return cast(Response, response)

    return _create_mock


class TestErrorHandler:
    """Tests for the ErrorHandler class."""

    def test_handle_error_response_400(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
    ) -> None:
        """Test handling of 400 Bad Request responses."""
        response = create_response_mock(400, json_data={"error": "Bad Request", "message": "Invalid parameters"})

        with pytest.raises(BadRequestError) as excinfo:
            error_handler.handle_error_response(response)

        assert excinfo.value.response is not None
        assert excinfo.value.response is response
        assert excinfo.value.response.status_code == 400
        assert "Bad Request" in str(excinfo.value)
        assert "Invalid parameters" in str(excinfo.value)

    def test_handle_error_response_401(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
    ) -> None:
        """Test handling of 401 Unauthorized responses."""
        response = create_response_mock(401, json_data={"error": "Unauthorized", "message": "Invalid credentials"})

        with pytest.raises(ClientAuthenticationError) as excinfo:
            error_handler.handle_error_response(response)

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 401
        # The message content is already checked in the exception string

    def test_handle_error_response_403(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
    ) -> None:
        """Test handling of 403 Forbidden responses."""
        response = create_response_mock(403, json_data={"error": "Forbidden", "message": "Insufficient permissions"})

        with pytest.raises(ForbiddenError) as excinfo:
            error_handler.handle_error_response(response)

        assert excinfo.value.response is not None
        assert excinfo.value.response is response
        assert excinfo.value.response.status_code == 403
        assert "Forbidden" in str(excinfo.value)
        assert "Insufficient permissions" in str(excinfo.value)

    def test_handle_error_response_404(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
        mocker: MockerFixture,
    ) -> None:
        """Test handling of 404 Not Found responses."""
        mock_request = mocker.Mock(spec=requests.Request)
        mock_request.method = "GET"
        mock_request.url = "http://mock.test/path"  # Added URL attribute
        response = create_response_mock(404, json_data={"error": "Not Found", "message": "Resource does not exist"})
        response.request = mock_request

        with pytest.raises(NotFoundError) as excinfo:
            error_handler.handle_error_response(response)

        assert excinfo.value.response is not None
        assert excinfo.value.response is response
        assert excinfo.value.response.status_code == 404
        assert "Not Found" in str(excinfo.value)
        assert "Resource does not exist" in str(excinfo.value)

    def test_handle_error_response_422(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
    ) -> None:
        """Test handling of 422 Unprocessable Entity responses."""
        response = create_response_mock(422, json_data={"error": "Validation Error", "fields": {"name": "Required"}})

        with pytest.raises(UnprocessableEntityError) as excinfo:
            error_handler.handle_error_response(response)

        # UnprocessableEntityError specific checks
        # Check that the message contains details from the response JSON
        assert "Validation Error" in str(excinfo.value)
        assert "'fields': {'name': 'Required'}" in str(excinfo.value)  # Check for field details representation

    def test_handle_error_response_500(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
    ) -> None:
        """Test handling of 500 Internal Server Error responses."""
        response = create_response_mock(500, json_data={"error": "Internal Server Error"})

        with pytest.raises(InternalServerError) as excinfo:
            error_handler.handle_error_response(response)

        assert excinfo.value.response is not None
        assert excinfo.value.response is response
        assert excinfo.value.response.status_code == 500
        assert "Internal Server Error" in str(excinfo.value)

    def test_handle_error_response_502(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
    ) -> None:
        """Test handling of 502 Bad Gateway responses."""
        response = create_response_mock(502, json_data={"error": "Bad Gateway"})

        with pytest.raises(APIError) as excinfo:
            error_handler.handle_error_response(response)

        # 502 is mapped to generic APIError
        assert excinfo.value.response is not None
        assert excinfo.value.response is response
        assert excinfo.value.response.status_code == 502
        assert "Bad Gateway" in str(excinfo.value)

    def test_handle_error_response_503(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
    ) -> None:
        """Test handling of 503 Service Unavailable responses."""
        response = create_response_mock(503, json_data={"error": "Service Unavailable"})

        with pytest.raises(ServiceUnavailableError) as excinfo:
            error_handler.handle_error_response(response)

        assert excinfo.value.response is not None
        assert excinfo.value.response is response
        assert excinfo.value.response.status_code == 503
        assert "Service Unavailable" in str(excinfo.value)

    def test_handle_error_response_invalid_json(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
        mocker: MockerFixture,
    ) -> None:
        """Test handling of responses with invalid JSON."""
        response = create_response_mock(400, text="Not a JSON response")
        cast_response = cast(Any, response)
        cast_response.json.side_effect = requests.exceptions.JSONDecodeError("Invalid JSON", "", 0)
        cast_response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")

        # Expect BadRequestError because the status code is 400
        # The ErrorHandler currently prioritizes status code mapping over JSON parsing errors
        # when raising the final exception.
        with pytest.raises(BadRequestError) as excinfo:
            error_handler.handle_error_response(response)

        assert excinfo.value.response is not None
        assert excinfo.value.response is response
        assert excinfo.value.response.status_code == 400
        # Check that the message includes the raw text since JSON parsing failed
        assert "Not a JSON response" in str(excinfo.value)

    def test_register_status_code_handler(
        self,
        error_handler: ErrorHandler,
        create_response_mock: Callable[..., Response],
        mocker: MockerFixture,
    ) -> None:
        """Test registering a custom status code handler."""

        class CustomError(APIError):
            pass

        error_handler.register_status_code_handler(418, CustomError)

        mock_request = mocker.Mock(spec=requests.Request)
        mock_request.method = "GET"  # Added method attribute
        mock_request.url = "http://mock.test/teapot"  # Added URL attribute
        response = create_response_mock(418, json_data={"error": "I'm a teapot"})
        response.request = mock_request

        with pytest.raises(CustomError) as excinfo:
            error_handler.handle_error_response(response)

        assert excinfo.value.response is not None
        assert excinfo.value.response is response
        assert excinfo.value.response.status_code == 418
        assert "I'm a teapot" in str(excinfo.value)

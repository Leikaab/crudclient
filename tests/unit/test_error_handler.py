"""
Tests for the ErrorHandler class in the crudclient library.

This module contains tests for how the ErrorHandler class handles various HTTP error responses,
including different status codes and malformed responses.
"""
import json
from unittest.mock import MagicMock

import pytest
import requests

from crudclient.exceptions import AuthenticationError, CrudClientError, InvalidResponseError, NotFoundError
from crudclient.http.errors import ErrorHandler


def create_response_mock(status_code, json_data=None, headers=None, text=None):
    """Create a mock response."""
    response = MagicMock(spec=requests.Response)
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

    return response


class TestErrorHandler:
    """Tests for the ErrorHandler class."""

    @pytest.fixture
    def error_handler(self):
        """Create an error handler for testing."""
        return ErrorHandler()

    def test_handle_error_response_400(self, error_handler):
        """Test handling of 400 Bad Request responses."""
        # Create a mock response with a 400 status code that passes isinstance checks
        response = create_response_mock(
            400,
            json_data={"error": "Bad Request", "message": "Invalid parameters"}
        )

        # Handle the error response
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "400" in str(excinfo.value)
        assert "Bad Request" in str(excinfo.value)
        assert "Invalid parameters" in str(excinfo.value)

    def test_handle_error_response_401(self, error_handler):
        """Test handling of 401 Unauthorized responses."""
        # Create a mock response with a 401 status code that passes isinstance checks
        response = create_response_mock(
            401,
            json_data={"error": "Unauthorized", "message": "Invalid credentials"}
        )

        # Handle the error response
        with pytest.raises(AuthenticationError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "401" in str(excinfo.value)
        assert "Authentication failed" in str(excinfo.value)
        assert "Invalid credentials" in str(excinfo.value)

    def test_handle_error_response_403(self, error_handler):
        """Test handling of 403 Forbidden responses."""
        # Create a mock response with a 403 status code that passes isinstance checks
        response = create_response_mock(
            403,
            json_data={"error": "Forbidden", "message": "Insufficient permissions"}
        )

        # Handle the error response
        with pytest.raises(AuthenticationError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "403" in str(excinfo.value)
        assert "Authentication failed" in str(excinfo.value)
        assert "Insufficient permissions" in str(excinfo.value)

    def test_handle_error_response_404(self, error_handler):
        """Test handling of 404 Not Found responses."""
        # Create a mock response with a 404 status code that passes isinstance checks
        response = create_response_mock(
            404,
            json_data={"error": "Not Found", "message": "Resource does not exist"}
        )

        # Handle the error response
        with pytest.raises(NotFoundError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "404" in str(excinfo.value)
        assert "Resource not found" in str(excinfo.value)
        assert "Resource does not exist" in str(excinfo.value)

    def test_handle_error_response_422(self, error_handler):
        """Test handling of 422 Unprocessable Entity responses."""
        # Create a mock response with a 422 status code that passes isinstance checks
        response = create_response_mock(
            422,
            json_data={"error": "Validation Error", "fields": {"name": "Required"}}
        )

        # Handle the error response
        with pytest.raises(InvalidResponseError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "422" in str(excinfo.value)
        assert "Invalid response" in str(excinfo.value)
        assert "Validation Error" in str(excinfo.value)

    def test_handle_error_response_500(self, error_handler):
        """Test handling of 500 Internal Server Error responses."""
        # Create a mock response with a 500 status code that passes isinstance checks
        response = create_response_mock(
            500,
            json_data={"error": "Internal Server Error"}
        )

        # Handle the error response
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "500" in str(excinfo.value)
        assert "Internal Server Error" in str(excinfo.value)

    def test_handle_error_response_502(self, error_handler):
        """Test handling of 502 Bad Gateway responses."""
        # Create a mock response with a 502 status code that passes isinstance checks
        response = create_response_mock(
            502,
            json_data={"error": "Bad Gateway"}
        )

        # Handle the error response
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "502" in str(excinfo.value)
        assert "Bad Gateway" in str(excinfo.value)

    def test_handle_error_response_503(self, error_handler):
        """Test handling of 503 Service Unavailable responses."""
        # Create a mock response with a 503 status code that passes isinstance checks
        response = create_response_mock(
            503,
            json_data={"error": "Service Unavailable"}
        )

        # Handle the error response
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "503" in str(excinfo.value)
        assert "Service Unavailable" in str(excinfo.value)

    def test_handle_error_response_invalid_json(self, error_handler):
        """Test handling of responses with invalid JSON."""
        # Create a mock response with invalid JSON
        response = create_response_mock(400, text="Not a JSON response")
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")

        # Handle the error response
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "400" in str(excinfo.value)
        assert "Not a JSON response" in str(excinfo.value)

    def test_register_status_code_handler(self, error_handler):
        """Test registering a custom status code handler."""
        # Create a custom exception class
        class CustomError(CrudClientError):
            pass

        # Register a custom handler for status code 418
        error_handler.register_status_code_handler(418, CustomError)

        # Create a mock response with a 418 status code that passes isinstance checks
        response = create_response_mock(
            418,
            json_data={"error": "I'm a teapot"}
        )

        # Handle the error response
        with pytest.raises(CustomError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "418" in str(excinfo.value)
        assert "I'm a teapot" in str(excinfo.value)

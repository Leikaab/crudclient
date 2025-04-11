"""
Tests for the ErrorHandler class in the crudclient library.

This module contains tests for how the ErrorHandler class handles various HTTP error responses,
including different status codes and malformed responses.
"""

import json

import pytest
import requests

from crudclient.exceptions import (
    AuthenticationError,
    CrudClientError,
    InvalidResponseError,
    NotFoundError,
)


@pytest.fixture
def create_response_mock(mocker):
    """Create a mock response."""

    def _create_mock(status_code, json_data=None, headers=None, text=None):
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

        return response

    return _create_mock


class TestErrorHandler:
    """Tests for the ErrorHandler class."""

    # Using error_handler fixture from conftest.py

    def test_handle_error_response_400(self, error_handler, create_response_mock):
        """Test handling of 400 Bad Request responses."""
        # Arrange
        response = create_response_mock(400, json_data={"error": "Bad Request", "message": "Invalid parameters"})

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "400" in str(excinfo.value)
        assert "Bad Request" in str(excinfo.value)
        assert "Invalid parameters" in str(excinfo.value)

    def test_handle_error_response_401(self, error_handler, create_response_mock):
        """Test handling of 401 Unauthorized responses."""
        # Arrange
        response = create_response_mock(401, json_data={"error": "Unauthorized", "message": "Invalid credentials"})

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "401" in str(excinfo.value)
        assert "Authentication failed" in str(excinfo.value)
        assert "Invalid credentials" in str(excinfo.value)

    def test_handle_error_response_403(self, error_handler, create_response_mock):
        """Test handling of 403 Forbidden responses."""
        # Arrange
        response = create_response_mock(403, json_data={"error": "Forbidden", "message": "Insufficient permissions"})

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "403" in str(excinfo.value)
        assert "Authentication failed" in str(excinfo.value)
        assert "Insufficient permissions" in str(excinfo.value)

    def test_handle_error_response_404(self, error_handler, create_response_mock):
        """Test handling of 404 Not Found responses."""
        # Arrange
        response = create_response_mock(404, json_data={"error": "Not Found", "message": "Resource does not exist"})

        # Act & Assert
        with pytest.raises(NotFoundError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "404" in str(excinfo.value)
        assert "Resource not found" in str(excinfo.value)
        assert "Resource does not exist" in str(excinfo.value)

    def test_handle_error_response_422(self, error_handler, create_response_mock):
        """Test handling of 422 Unprocessable Entity responses."""
        # Arrange
        response = create_response_mock(422, json_data={"error": "Validation Error", "fields": {"name": "Required"}})

        # Act & Assert
        with pytest.raises(InvalidResponseError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "422" in str(excinfo.value)
        assert "Invalid response" in str(excinfo.value)
        assert "Validation Error" in str(excinfo.value)

    def test_handle_error_response_500(self, error_handler, create_response_mock):
        """Test handling of 500 Internal Server Error responses."""
        # Arrange
        response = create_response_mock(500, json_data={"error": "Internal Server Error"})

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "500" in str(excinfo.value)
        assert "Internal Server Error" in str(excinfo.value)

    def test_handle_error_response_502(self, error_handler, create_response_mock):
        """Test handling of 502 Bad Gateway responses."""
        # Arrange
        response = create_response_mock(502, json_data={"error": "Bad Gateway"})

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "502" in str(excinfo.value)
        assert "Bad Gateway" in str(excinfo.value)

    def test_handle_error_response_503(self, error_handler, create_response_mock):
        """Test handling of 503 Service Unavailable responses."""
        # Arrange
        response = create_response_mock(503, json_data={"error": "Service Unavailable"})

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "503" in str(excinfo.value)
        assert "Service Unavailable" in str(excinfo.value)

    def test_handle_error_response_invalid_json(self, error_handler, create_response_mock, mocker):
        """Test handling of responses with invalid JSON."""
        # Arrange
        response = create_response_mock(400, text="Not a JSON response")
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "400" in str(excinfo.value)
        assert "Not a JSON response" in str(excinfo.value)

    def test_register_status_code_handler(self, error_handler, create_response_mock):
        """Test registering a custom status code handler."""

        # Arrange
        # Create a custom exception class
        class CustomError(CrudClientError):
            pass

        # Register a custom handler for status code 418
        error_handler.register_status_code_handler(418, CustomError)

        # Create a mock response with a 418 status code
        response = create_response_mock(418, json_data={"error": "I'm a teapot"})

        # Act & Assert
        with pytest.raises(CustomError) as excinfo:
            error_handler.handle_error_response(response)

        # Check that the exception contains the error details
        assert "418" in str(excinfo.value)
        assert "I'm a teapot" in str(excinfo.value)

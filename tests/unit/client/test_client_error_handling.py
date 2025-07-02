"""
Tests for client error handling in the crudclient library.

This module contains tests for how the Client class handles various HTTP error responses,
including different status codes, malformed responses, and network errors.
"""

import json
from typing import Any

import pytest
import requests

from crudclient.client import Client
from crudclient.exceptions import ResponseParsingError  # Added
from crudclient.exceptions import (
    AuthenticationError,
    CrudClientError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from crudclient.testing.verification import Verifier
from tests.unit.helpers import translate_mock_calls_for_verifier

# Import fixtures from conftest.py


class TestClientErrorHandling:
    """Tests for error handling in the Client class."""

    def test_client_handles_connection_error(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles connection errors correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, exc=requests.ConnectionError("Connection refused"))

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "Connection refused" in str(excinfo.value)

    @pytest.mark.no_parallel
    def test_client_handles_timeout(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles timeouts correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, exc=requests.Timeout("Request timed out"))

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "Request timed out" in str(excinfo.value)

    @pytest.mark.no_parallel
    def test_client_handles_ssl_error(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles SSL errors correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.SSLError("SSL verification failed"))

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "SSL verification failed" in str(excinfo.value)

    def test_client_handles_too_many_redirects(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles too many redirects correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.TooManyRedirects("Too many redirects"))

        # Act & Assert
        with pytest.raises(CrudClientError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "Too many redirects" in str(excinfo.value)

    def test_client_handles_malformed_json_response(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles malformed JSON responses correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, text="Not a JSON response", headers={"Content-Type": "application/json"})

        # Act & Assert
        # Expect ResponseParsingError because ResponseHandler now wraps JSONDecodeError
        with pytest.raises(ResponseParsingError) as excinfo:
            client.get("/users")

        # Check that the original exception was a JSONDecodeError
        assert isinstance(excinfo.value.original_exception, requests.exceptions.JSONDecodeError)
        assert "Expecting value" in str(excinfo.value.original_exception)
        assert excinfo.value.response is not None  # Check response is attached
        assert excinfo.value.response.url == url

    def test_client_handles_unexpected_response_format(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles unexpected response formats correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, json={"unexpected": "format"})

        # Act
        response = client.get("/users")

        # Assert
        # This should not raise an exception, but return the raw response
        assert json.loads(str(response))["unexpected"] == "format"

    def test_client_handles_empty_response(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles empty responses correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, text="")

        # Act
        response = client.get("/users")

        # Assert
        assert response is None or response == ""

    def test_client_handles_non_json_content_type(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles non-JSON content types correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, text="<html>Not JSON</html>", headers={"Content-Type": "text/html"})

        # Act
        response = client.get("/users")

        # Assert
        assert response == "<html>Not JSON</html>"

    def test_client_error_handling_chain(self, client: Client, mock_request: Any) -> None:
        """Test the error handling chain in the client."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, status_code=500, json={"error": "Internal Server Error"})

        # Act
        with pytest.raises(CrudClientError):
            client.get("/users")

        # Assert
        # Check that the request was made
        assert len(mock_request.request_history) == 1
        assert mock_request.request_history[0].url == url

    def test_client_handles_auth_error(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles authentication errors correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, status_code=401, json={"error": "Unauthorized"})

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)

    def test_client_handles_forbidden_error(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles forbidden errors correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.get(url, status_code=403, json={"error": "Forbidden"})

        # Act & Assert
        with pytest.raises(ForbiddenError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "403" in str(excinfo.value) or "Forbidden" in str(excinfo.value)

    def test_client_handles_not_found_error(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles not found errors correctly."""
        # Arrange
        url = f"{client.base_url}/users/999"
        mock_request.get(url, status_code=404, json={"error": "Not Found"})

        # Act & Assert
        with pytest.raises(NotFoundError) as excinfo:
            client.get("/users/999")

        # Check that the exception contains the error details
        assert "404" in str(excinfo.value) or "Not Found" in str(excinfo.value)

    def test_client_handles_validation_error(self, client: Client, mock_request: Any) -> None:
        """Test that the client handles validation errors correctly."""
        # Arrange
        url = f"{client.base_url}/users"
        mock_request.post(
            url,
            status_code=422,
            json={"error": "Validation Error", "fields": {"name": "Required"}},
        )
        post_data = {"email": "test@example.com"}

        # Act & Assert
        with pytest.raises(UnprocessableEntityError) as excinfo:
            client.post("/users", data=post_data)

        # Check that the exception contains the error details
        assert "422" in str(excinfo.value) or "Validation Error" in str(excinfo.value)

    def test_client_retries_on_403_if_configured(self, client: Client, mock_request: Any, mocker: Any) -> None:
        """Test that the client retries a request on 403 if configured."""
        # Arrange
        endpoint = "/protected/resource"
        url = f"{client.base_url}/{endpoint.lstrip('/')}"

        # Configure client for retry
        mocker.patch.object(client.config, "should_retry_on_403", return_value=True)
        # Patch the methods but don't need to store the mock objects locally
        mocker.patch.object(client.config, "handle_403_retry")
        mocker.patch.object(client.http_client.session_manager, "refresh_auth")

        # Mock HTTP responses: first 403, then 200
        mock_request.get(
            url,
            [
                {"status_code": 403, "json": {"error": "Forbidden - Initial"}},
                {"status_code": 200, "json": {"status": "success after retry"}},
            ],
        )

        # Act
        response = client.get(endpoint)

        # Assert
        # 1. Check final response is from the successful retry
        assert json.loads(str(response))["status"] == "success after retry"

        # 2. Check config handler was called (using attribute access on client)
        # TODO: Consider migrating to Mock's built-in assertion methods (client.config.handle_403_retry.assert_called_once_with(client))
        # See verifier_pattern_fix_plan.md for migration details
        translate_mock_calls_for_verifier(client.config.handle_403_retry)  # type: ignore[arg-type]
        Verifier.verify_called_once_with(client.config.handle_403_retry, "", client)

        # 3. Check auth was refreshed (using attribute access on client)
        # TODO: Consider migrating to Mock's built-in assertion methods (assert client.http_client.session_manager.refresh_auth.call_count == 1)
        translate_mock_calls_for_verifier(client.http_client.session_manager.refresh_auth)  # type: ignore[arg-type]
        Verifier.verify_call_count(client.http_client.session_manager.refresh_auth, "", 1)

        # 4. Check two requests were made to the same URL
        assert len(mock_request.request_history) == 2
        assert mock_request.request_history[0].url == url
        assert mock_request.request_history[1].url == url

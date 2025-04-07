"""
Tests for client error handling in the crudclient library.

This module contains tests for how the Client class handles various HTTP error responses,
including different status codes, malformed responses, and network errors.
"""
import json

import pytest
import requests
import requests_mock

from crudclient.client import Client
from crudclient.exceptions import AuthenticationError, CrudClientError, InvalidResponseError, NotFoundError

from .test_config import MockClientConfig


class TestClientErrorHandling:
    """Tests for error handling in the Client class."""

    @pytest.fixture
    def client(self):
        """Create a client for testing."""
        return Client(MockClientConfig())

    @pytest.fixture
    def mock_request(self):
        """Create a requests_mock for testing."""
        with requests_mock.Mocker() as m:
            yield m

    def test_client_handles_connection_error(self, client, mock_request):
        """Test that the client handles connection errors correctly."""
        # Mock a connection error
        url = f"{client.base_url}/users"
        mock_request.get(url, exc=requests.ConnectionError("Connection refused"))

        # Make a request that will raise a connection error
        with pytest.raises(CrudClientError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "Connection refused" in str(excinfo.value)

    def test_client_handles_timeout(self, client, mock_request):
        """Test that the client handles timeouts correctly."""
        # Mock a timeout
        url = f"{client.base_url}/users"
        mock_request.get(url, exc=requests.Timeout("Request timed out"))

        # Make a request that will raise a timeout
        with pytest.raises(CrudClientError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "Request timed out" in str(excinfo.value)

    def test_client_handles_ssl_error(self, client, mock_request):
        """Test that the client handles SSL errors correctly."""
        # Mock an SSL error
        url = f"{client.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.SSLError("SSL verification failed"))

        # Make a request that will raise an SSL error
        with pytest.raises(CrudClientError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "SSL verification failed" in str(excinfo.value)

    def test_client_handles_too_many_redirects(self, client, mock_request):
        """Test that the client handles too many redirects correctly."""
        # Mock a too many redirects error
        url = f"{client.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.TooManyRedirects("Too many redirects"))

        # Make a request that will raise a too many redirects error
        with pytest.raises(CrudClientError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "Too many redirects" in str(excinfo.value)

    def test_client_handles_malformed_json_response(self, client, mock_request):
        """Test that the client handles malformed JSON responses correctly."""
        # Mock a response with malformed JSON
        url = f"{client.base_url}/users"
        mock_request.get(url, text="Not a JSON response", headers={"Content-Type": "application/json"})

        # Make a request that will receive a malformed JSON response
        with pytest.raises(requests.exceptions.JSONDecodeError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "Expecting value" in str(excinfo.value)

    def test_client_handles_unexpected_response_format(self, client, mock_request):
        """Test that the client handles unexpected response formats correctly."""
        # Mock a response with an unexpected format
        url = f"{client.base_url}/users"
        mock_request.get(url, json={"unexpected": "format"})

        # Make a request that will receive an unexpected response format
        # This should not raise an exception, but return the raw response
        response = client.get("/users")
        assert json.loads(response)["unexpected"] == "format"

    def test_client_handles_empty_response(self, client, mock_request):
        """Test that the client handles empty responses correctly."""
        # Mock an empty response
        url = f"{client.base_url}/users"
        mock_request.get(url, text="")

        # Make a request that will receive an empty response
        response = client.get("/users")
        assert response is None or response == ""

    def test_client_handles_non_json_content_type(self, client, mock_request):
        """Test that the client handles non-JSON content types correctly."""
        # Mock a response with a non-JSON content type
        url = f"{client.base_url}/users"
        mock_request.get(url, text="<html>Not JSON</html>", headers={"Content-Type": "text/html"})

        # Make a request that will receive a non-JSON content type
        response = client.get("/users")
        assert response == "<html>Not JSON</html>"

    def test_client_error_handling_chain(self, client, mock_request):
        """Test the error handling chain in the client."""
        # Mock a 500 response
        url = f"{client.base_url}/users"
        mock_request.get(url, status_code=500, json={"error": "Internal Server Error"})

        # Make a request that will receive a 500 response
        with pytest.raises(CrudClientError):
            client.get("/users")

        # Check that the request was made
        assert len(mock_request.request_history) == 1
        assert mock_request.request_history[0].url == url

    def test_client_handles_auth_error(self, client, mock_request):
        """Test that the client handles authentication errors correctly."""
        # Mock a 401 response
        url = f"{client.base_url}/users"
        mock_request.get(url, status_code=401, json={"error": "Unauthorized"})

        # Make a request that will receive a 401 response
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)

    def test_client_handles_forbidden_error(self, client, mock_request):
        """Test that the client handles forbidden errors correctly."""
        # Mock a 403 response
        url = f"{client.base_url}/users"
        mock_request.get(url, status_code=403, json={"error": "Forbidden"})

        # Make a request that will receive a 403 response
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/users")

        # Check that the exception contains the error details
        assert "403" in str(excinfo.value) or "Forbidden" in str(excinfo.value)

    def test_client_handles_not_found_error(self, client, mock_request):
        """Test that the client handles not found errors correctly."""
        # Mock a 404 response
        url = f"{client.base_url}/users/999"
        mock_request.get(url, status_code=404, json={"error": "Not Found"})

        # Make a request that will receive a 404 response
        with pytest.raises(NotFoundError) as excinfo:
            client.get("/users/999")

        # Check that the exception contains the error details
        assert "404" in str(excinfo.value) or "Not Found" in str(excinfo.value)

    def test_client_handles_validation_error(self, client, mock_request):
        """Test that the client handles validation errors correctly."""
        # Mock a 422 response
        url = f"{client.base_url}/users"
        mock_request.post(
            url,
            status_code=422,
            json={"error": "Validation Error", "fields": {"name": "Required"}},
        )

        # Make a request that will receive a 422 response
        with pytest.raises(InvalidResponseError) as excinfo:
            client.post("/users", data={"email": "test@example.com"})

        # Check that the exception contains the error details
        assert "422" in str(excinfo.value) or "Validation Error" in str(excinfo.value)

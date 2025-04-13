"""
Tests for client error handling in the HTTP client.

This module contains tests for how the HTTP client handles various client error conditions,
including 4xx status codes.
"""

import pytest

from crudclient.exceptions import (
    AuthenticationError,
    CrudClientError,
    InvalidResponseError,
    NotFoundError,
)


class TestHttpClientClientErrors:
    """Tests for handling client errors in the HTTP client."""

    def test_400_error(self, http_client, mock_request):
        """
        Test handling of 400 Bad Request.

        This test verifies that the client properly handles 400 Bad Request
        responses from the server.
        """
        # Mock a 400 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=400, json={"error": "Bad Request", "message": "Invalid parameters"})

        # Make a request that will receive a 400 response
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "400" in str(excinfo.value) or "Bad Request" in str(excinfo.value)
        assert "Invalid parameters" in str(excinfo.value)

    def test_401_error(self, http_client, mock_request):
        """
        Test handling of 401 Unauthorized.

        This test verifies that the client properly handles 401 Unauthorized
        responses from the server and raises an AuthenticationError.
        """
        # Mock a 401 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Authentication required"})

        # Make a request that will receive a 401 response
        with pytest.raises(AuthenticationError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "Authentication required" in str(excinfo.value)

    def test_403_error(self, http_client, mock_request):
        """
        Test handling of 403 Forbidden.

        This test verifies that the client properly handles 403 Forbidden
        responses from the server and raises an AuthenticationError.
        """
        # Mock a 403 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=403, json={"error": "Forbidden", "message": "Insufficient permissions"})

        # Make a request that will receive a 403 response
        with pytest.raises(AuthenticationError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "403" in str(excinfo.value) or "Forbidden" in str(excinfo.value)
        assert "Insufficient permissions" in str(excinfo.value)

    def test_404_error(self, http_client, mock_request):
        """
        Test handling of 404 Not Found.

        This test verifies that the client properly handles 404 Not Found
        responses from the server and raises a NotFoundError.
        """
        # Mock a 404 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=404, json={"error": "Not Found", "message": "Resource not found"})

        # Make a request that will receive a 404 response
        with pytest.raises(NotFoundError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "404" in str(excinfo.value) or "Not Found" in str(excinfo.value)
        assert "Resource not found" in str(excinfo.value)

    def test_422_error(self, http_client, mock_request):
        """
        Test handling of 422 Unprocessable Entity.

        This test verifies that the client properly handles 422 Unprocessable Entity
        responses from the server and raises an InvalidResponseError.
        """
        # Mock a 422 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=422, json={"error": "Unprocessable Entity", "message": "Validation failed"})

        # Make a request that will receive a 422 response
        with pytest.raises(InvalidResponseError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "422" in str(excinfo.value) or "Unprocessable Entity" in str(excinfo.value)
        assert "Validation failed" in str(excinfo.value)

    def test_429_error(self, http_client, mock_request):
        """
        Test handling of 429 Too Many Requests.

        This test verifies that the client properly handles 429 Too Many Requests
        responses from the server.
        """
        # Mock a 429 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=429, json={"error": "Too Many Requests", "message": "Rate limit exceeded"})

        # Make a request that will receive a 429 response
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "429" in str(excinfo.value) or "Too Many Requests" in str(excinfo.value)
        assert "Rate limit exceeded" in str(excinfo.value)

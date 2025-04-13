"""
Tests for server error handling in the HTTP client.

This module contains tests for how the HTTP client handles various server error conditions,
including 5xx status codes.
"""

import pytest

from crudclient.exceptions import APIError


class TestHttpClientServerErrors:
    """Tests for handling server errors in the HTTP client."""

    def test_500_error(self, http_client, mock_request):
        """
        Test handling of 500 Internal Server Error.

        This test verifies that the client properly handles 500 Internal Server Error
        responses from the server.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=500, json={"error": "Internal Server Error", "message": "Something went wrong"})

        with pytest.raises(APIError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 500
        assert excinfo.value.response.json()["message"] == "Something went wrong"

    def test_502_error(self, http_client, mock_request):
        """
        Test handling of 502 Bad Gateway.

        This test verifies that the client properly handles 502 Bad Gateway
        responses from the server.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=502, json={"error": "Bad Gateway", "message": "Invalid response from upstream server"})

        with pytest.raises(APIError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 502
        assert excinfo.value.response.json()["message"] == "Invalid response from upstream server"

    def test_503_error(self, http_client, mock_request):
        """
        Test handling of 503 Service Unavailable.

        This test verifies that the client properly handles 503 Service Unavailable
        responses from the server.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=503, json={"error": "Service Unavailable", "message": "Server is overloaded"})

        with pytest.raises(APIError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 503
        assert excinfo.value.response.json()["message"] == "Server is overloaded"

    def test_504_error(self, http_client, mock_request):
        """
        Test handling of 504 Gateway Timeout.

        This test verifies that the client properly handles 504 Gateway Timeout
        responses from the server.
        """
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, status_code=504, json={"error": "Gateway Timeout", "message": "Upstream server timed out"})

        with pytest.raises(APIError) as excinfo:
            http_client.get("/users")

        assert excinfo.value.response is not None
        assert excinfo.value.response.status_code == 504
        assert excinfo.value.response.json()["message"] == "Upstream server timed out"

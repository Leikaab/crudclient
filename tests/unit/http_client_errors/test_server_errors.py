"""
Tests for server error handling in the HTTP client.

This module contains tests for how the HTTP client handles various server error conditions,
including 5xx status codes.
"""

import pytest

from crudclient.exceptions import CrudClientError


class TestHttpClientServerErrors:
    """Tests for handling server errors in the HTTP client."""

    def test_500_error(self, http_client, mock_request):
        """
        Test handling of 500 Internal Server Error.

        This test verifies that the client properly handles 500 Internal Server Error
        responses from the server.
        """
        # Mock a 500 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(
            url,
            status_code=500,
            json={"error": "Internal Server Error", "message": "Something went wrong"}
        )

        # Make a request that will receive a 500 response
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "500" in str(excinfo.value) or "Internal Server Error" in str(excinfo.value)
        assert "Something went wrong" in str(excinfo.value)

    def test_502_error(self, http_client, mock_request):
        """
        Test handling of 502 Bad Gateway.

        This test verifies that the client properly handles 502 Bad Gateway
        responses from the server.
        """
        # Mock a 502 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(
            url,
            status_code=502,
            json={"error": "Bad Gateway", "message": "Invalid response from upstream server"}
        )

        # Make a request that will receive a 502 response
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "502" in str(excinfo.value) or "Bad Gateway" in str(excinfo.value)
        assert "Invalid response from upstream server" in str(excinfo.value)

    def test_503_error(self, http_client, mock_request):
        """
        Test handling of 503 Service Unavailable.

        This test verifies that the client properly handles 503 Service Unavailable
        responses from the server.
        """
        # Mock a 503 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(
            url,
            status_code=503,
            json={"error": "Service Unavailable", "message": "Server is overloaded"}
        )

        # Make a request that will receive a 503 response
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "503" in str(excinfo.value) or "Service Unavailable" in str(excinfo.value)
        assert "Server is overloaded" in str(excinfo.value)

    def test_504_error(self, http_client, mock_request):
        """
        Test handling of 504 Gateway Timeout.

        This test verifies that the client properly handles 504 Gateway Timeout
        responses from the server.
        """
        # Mock a 504 response
        url = f"{http_client.config.base_url}/users"
        mock_request.get(
            url,
            status_code=504,
            json={"error": "Gateway Timeout", "message": "Upstream server timed out"}
        )

        # Make a request that will receive a 504 response
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "504" in str(excinfo.value) or "Gateway Timeout" in str(excinfo.value)
        assert "Upstream server timed out" in str(excinfo.value)

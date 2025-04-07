"""
Tests for network error handling in the HTTP client.

This module contains tests for how the HTTP client handles various network error conditions,
including connection errors, timeouts, and DNS resolution failures.
"""

import pytest
import requests

from crudclient.exceptions import CrudClientError


class TestHttpClientNetworkErrors:
    """Tests for handling network errors in the HTTP client."""

    def test_connection_error(self, http_client, mock_request):
        """
        Test handling of connection errors.

        This test verifies that the client properly handles connection errors
        that occur when the server refuses the connection attempt.
        """
        # Mock a connection error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ConnectionError("Connection refused"))

        # Make a request that will raise a connection error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "Connection refused" in str(excinfo.value)

    def test_connection_reset_error(self, http_client, mock_request):
        """
        Test handling of connection reset errors.

        This test verifies that the client properly handles connection reset errors
        that occur when the server abruptly closes the connection.
        """
        # Mock a connection reset error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ConnectionError("Connection reset by peer"))

        # Make a request that will raise a connection reset error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "Connection reset" in str(excinfo.value)

    def test_timeout_error(self, http_client, mock_request):
        """
        Test handling of timeout errors.

        This test verifies that the client properly handles timeout errors
        that occur when the server takes too long to respond.
        """
        # Mock a timeout error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.Timeout("Request timed out"))

        # Make a request that will raise a timeout error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "timed out" in str(excinfo.value).lower()

    def test_connect_timeout_error(self, http_client, mock_request):
        """
        Test handling of connection timeout errors.

        This test verifies that the client properly handles connection timeout errors
        that occur when establishing a connection to the server takes too long.
        """
        # Mock a connect timeout error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ConnectTimeout("Connection timed out"))

        # Make a request that will raise a connect timeout error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "Connection timed out" in str(excinfo.value)

    def test_read_timeout_error(self, http_client, mock_request):
        """
        Test handling of read timeout errors.

        This test verifies that the client properly handles read timeout errors
        that occur when reading the server's response takes too long.
        """
        # Mock a read timeout error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ReadTimeout("Read timed out"))

        # Make a request that will raise a read timeout error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "Read timed out" in str(excinfo.value)

    def test_dns_error(self, http_client, mock_request):
        """
        Test handling of DNS resolution errors.

        This test verifies that the client properly handles DNS resolution errors
        that occur when the hostname cannot be resolved to an IP address.
        """
        # Mock a DNS resolution error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ConnectionError("Name or service not known"))

        # Make a request that will raise a DNS resolution error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "Name or service not known" in str(excinfo.value)

    def test_host_not_found_error(self, http_client, mock_request):
        """
        Test handling of host not found errors.

        This test verifies that the client properly handles host not found errors
        that occur when the DNS lookup fails.
        """
        # Mock a host not found error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ConnectionError("No such host is known"))

        # Make a request that will raise a host not found error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "No such host is known" in str(excinfo.value)

    def test_proxy_error(self, http_client, mock_request):
        """
        Test handling of proxy errors.

        This test verifies that the client properly handles proxy errors
        that occur when connecting through a proxy server fails.
        """
        # Mock a proxy error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ProxyError("Proxy connection failed"))

        # Make a request that will raise a proxy error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "Proxy" in str(excinfo.value)

    def test_ssl_error(self, http_client, mock_request):
        """
        Test handling of SSL/TLS errors.

        This test verifies that the client properly handles SSL/TLS errors
        that occur during the SSL handshake or certificate validation.
        """
        # Mock an SSL error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.SSLError("SSL: CERTIFICATE_VERIFY_FAILED"))

        # Make a request that will raise an SSL error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "SSL" in str(excinfo.value)

    def test_network_unreachable_error(self, http_client, mock_request):
        """
        Test handling of network unreachable errors.

        This test verifies that the client properly handles network unreachable errors
        that occur when the network route to the server cannot be established.
        """
        # Mock a network unreachable error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ConnectionError("Network is unreachable"))

        # Make a request that will raise a network unreachable error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "Network is unreachable" in str(excinfo.value)

    def test_socket_timeout_error(self, http_client, mock_request):
        """
        Test handling of socket timeout errors.

        This test verifies that the client properly handles socket timeout errors
        that occur at the socket level.
        """
        # Mock a socket timeout error
        url = f"{http_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ConnectionError("Socket timeout"))

        # Make a request that will raise a socket timeout error
        with pytest.raises(CrudClientError) as excinfo:
            http_client.get("/users")

        # Check that the exception contains the error details
        assert "Socket timeout" in str(excinfo.value)

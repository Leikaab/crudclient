"""
Tests for retry behavior in the HTTP client.

This module contains tests for how the HTTP client handles retries for various
error conditions, including network errors, timeouts, and SSL errors.
"""

from unittest.mock import patch

import pytest
import requests

from crudclient.exceptions import CrudClientError
from crudclient.http.client import HttpClient
from crudclient.http.retry import RetryCondition, RetryHandler


class TestHttpClientNetworkErrorRetries:
    """Tests for retry behavior with network errors in the HTTP client."""

    @pytest.fixture
    def retry_config(self, config):
        """Fixture for a configuration with custom retry settings."""
        # Set a short timeout for faster tests
        config.timeout = 1.0
        return config

    @pytest.fixture
    def retry_client(self, retry_config):
        """Fixture for an HTTP client with custom retry settings."""
        # Create a retry handler with custom settings
        retry_handler = RetryHandler(
            max_retries=3,
            retry_conditions=[
                RetryCondition(
                    exceptions=[
                        requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout,
                        requests.exceptions.SSLError
                    ]
                )
            ]
        )

        # Create an HTTP client with the custom retry handler
        return HttpClient(retry_config, retry_handler=retry_handler)

    def test_connection_error_retry(self, retry_client, mock_request):
        """
        Test retry behavior for connection errors.

        This test verifies that the client properly retries requests that fail
        with connection errors, up to the maximum number of retries.
        """
        # Mock a connection error for the first two attempts, then success
        url = f"{retry_client.config.base_url}/users"

        # Track the number of requests
        request_count = [0]

        def side_effect(request, context):
            request_count[0] += 1
            if request_count[0] <= 2:  # Fail the first two attempts
                raise requests.exceptions.ConnectionError("Connection refused")
            # Succeed on the third attempt
            context.status_code = 200
            return {"id": 1, "name": "Test User"}

        mock_request.get(url, json=side_effect)

        # Make a request that will retry after connection errors
        response = retry_client.get("/users")

        # Check that the request was retried and eventually succeeded
        assert request_count[0] == 3
        # The response might be a string or a dict depending on how the mock is handled
        if isinstance(response, dict):
            assert response.get("id") == 1
            assert response.get("name") == "Test User"
        else:
            assert '"id": 1' in response
            assert '"name": "Test User"' in response

    def test_timeout_error_retry(self, retry_client, mock_request):
        """
        Test retry behavior for timeout errors.

        This test verifies that the client properly retries requests that fail
        with timeout errors, up to the maximum number of retries.
        """
        # Mock a timeout error for the first two attempts, then success
        url = f"{retry_client.config.base_url}/users"

        # Track the number of requests
        request_count = [0]

        def side_effect(request, context):
            request_count[0] += 1
            if request_count[0] <= 2:  # Fail the first two attempts
                raise requests.exceptions.Timeout("Request timed out")
            # Succeed on the third attempt
            context.status_code = 200
            return {"id": 1, "name": "Test User"}

        mock_request.get(url, json=side_effect)

        # Make a request that will retry after timeout errors
        response = retry_client.get("/users")

        # Check that the request was retried and eventually succeeded
        assert request_count[0] == 3
        # The response might be a string or a dict depending on how the mock is handled
        if isinstance(response, dict):
            assert response.get("id") == 1
            assert response.get("name") == "Test User"
        else:
            assert '"id": 1' in response
            assert '"name": "Test User"' in response

    def test_ssl_error_retry(self, retry_client, mock_request):
        """
        Test retry behavior for SSL errors.

        This test verifies that the client properly retries requests that fail
        with SSL errors, up to the maximum number of retries.
        """
        # Mock an SSL error for the first two attempts, then success
        url = f"{retry_client.config.base_url}/users"

        # Track the number of requests
        request_count = [0]

        def side_effect(request, context):
            request_count[0] += 1
            if request_count[0] <= 2:  # Fail the first two attempts
                raise requests.exceptions.SSLError("SSL: CERTIFICATE_VERIFY_FAILED")
            # Succeed on the third attempt
            context.status_code = 200
            return {"id": 1, "name": "Test User"}

        mock_request.get(url, json=side_effect)

        # Make a request that will retry after SSL errors
        response = retry_client.get("/users")

        # Check that the request was retried and eventually succeeded
        assert request_count[0] == 3
        # The response might be a string or a dict depending on how the mock is handled
        if isinstance(response, dict):
            assert response.get("id") == 1
            assert response.get("name") == "Test User"
        else:
            assert '"id": 1' in response
            assert '"name": "Test User"' in response

    def test_max_retries_exceeded(self, retry_client, mock_request):
        """
        Test behavior when maximum retries are exceeded.

        This test verifies that the client properly raises an exception when
        the maximum number of retries is exceeded.
        """
        # Mock a connection error for all attempts
        url = f"{retry_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ConnectionError("Connection refused"))

        # Make a request that will fail all retry attempts
        with pytest.raises(CrudClientError) as excinfo:
            retry_client.get("/users")

        # Check that the exception contains the error details
        assert "Connection refused" in str(excinfo.value)
        assert "Request failed" in str(excinfo.value)

    def test_mixed_error_retry(self, retry_client, mock_request):
        """
        Test retry behavior with different types of network errors.

        This test verifies that the client properly retries requests that fail
        with different types of network errors in sequence.
        """
        # Mock different errors for each attempt, then success
        url = f"{retry_client.config.base_url}/users"

        # Track the number of requests
        request_count = [0]

        def side_effect(request, context):
            request_count[0] += 1
            if request_count[0] == 1:
                raise requests.exceptions.ConnectionError("Connection refused")
            elif request_count[0] == 2:
                raise requests.exceptions.Timeout("Request timed out")
            elif request_count[0] == 3:
                # Succeed on the third attempt instead of raising another error
                context.status_code = 200
                return {"id": 1, "name": "Test User"}

        mock_request.get(url, json=side_effect)

        # Make a request that will retry after different errors
        response = retry_client.get("/users")

        # Check that the request was retried for each type of error
        assert request_count[0] == 3
        # The response might be a string or a dict depending on how the mock is handled
        if isinstance(response, dict):
            assert response.get("id") == 1
            assert response.get("name") == "Test User"
        else:
            assert '"id": 1' in response
            assert '"name": "Test User"' in response

    def test_retry_with_backoff(self, retry_client, mock_request):
        """
        Test retry with exponential backoff.

        This test verifies that the client uses exponential backoff when
        retrying failed requests.
        """
        # Mock a connection error for all attempts
        url = f"{retry_client.config.base_url}/users"
        mock_request.get(url, exc=requests.exceptions.ConnectionError("Connection refused"))

        # Patch the time.sleep function to track delays
        with patch('time.sleep') as mock_sleep:
            # Make a request that will fail all retry attempts
            with pytest.raises(CrudClientError):
                retry_client.get("/users")

            # Check that sleep was called with increasing delays
            assert mock_sleep.call_count >= 3
            delays = [call_args[0][0] for call_args in mock_sleep.call_args_list]

            # Verify that delays are increasing (exponential backoff)
            for i in range(1, len(delays)):
                assert delays[i] > delays[i - 1]

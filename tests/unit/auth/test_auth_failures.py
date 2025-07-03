import requests_mock

"""
Tests for general authentication setup failure handling in the crudclient library.
"""

import pytest
from apiconfig.exceptions.auth import AuthStrategyError

from crudclient.auth import CustomAuth
from crudclient.client import Client
from crudclient.config import ClientConfig

# Import fixtures from conftest.py - Fixtures are typically auto-discovered by pytest


class TestAuthFailures:
    """Tests for general authentication failure handling."""

    def test_auth_setup_failure(self, mock_request: requests_mock.Mocker, mocker, bearer_auth_config: ClientConfig) -> None:
        """Test handling of authentication setup failures."""
        # Arrange
        # Create a bearer auth mock with a failing callback

        # Configure the auth setup to fail
        mock_prepare_headers = mocker.patch("apiconfig.auth.strategies.bearer.BearerAuth.prepare_request_headers")
        mock_prepare_headers.side_effect = Exception("Auth setup failed")

        # Create a client with the failing auth
        config = bearer_auth_config

        # Act & Assert
        # Creating the client or making a request should raise the exception
        with pytest.raises(Exception) as excinfo:
            client = Client(config)
            # If client creation doesn't raise, the request prep should
            client.get("/users")

        # Check that the exception contains the error details
        assert "Auth setup failed" in str(excinfo.value)

    def test_auth_param_setup_failure(self, mock_request: requests_mock.Mocker, create_mock_client_config) -> None:
        """
        Test that exceptions during auth parameter setup are propagated.

        Verifies that if an auth strategy's parameter setup (e.g., param_callback)
        raises an exception, it happens before any network request and is
        correctly raised by the client operation.
        """
        # Arrange
        exception_message = "Failed during auth param setup"

        def failing_param_callback():
            """Simulates a failure during parameter preparation."""
            raise ValueError(exception_message)

        def dummy_header_callback():
            """A placeholder header callback, not expected to be called."""
            return {"X-Dummy-Header": "dummy_value"}

        # Instantiate CustomAuth with the failing parameter callback
        custom_auth = CustomAuth(
            header_callback=dummy_header_callback,
            param_callback=failing_param_callback,
        )

        # Configure a client with this auth strategy
        # Configure a client using the factory to inject the custom auth strategy
        config = create_mock_client_config(auth_strategy=custom_auth)
        client = Client(config)

        # Act & Assert
        # Expect the AuthStrategyError wrapping the ValueError from failing_param_callback
        with pytest.raises(AuthStrategyError, match="CustomAuth parameter callback failed") as excinfo:
            client.get("/some/path")  # Attempting a request should trigger param setup

        # Verify the original exception is in the cause chain
        assert exception_message in str(excinfo.value.__cause__)
        # Ensure no request was actually sent (error happens before request)
        assert not mock_request.called

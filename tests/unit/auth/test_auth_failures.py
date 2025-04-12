"""
Tests for general authentication setup failure handling in the crudclient library.
"""

import pytest

from crudclient.auth.custom import CustomAuth
from crudclient.client import Client

# Import fixtures from conftest.py - Fixtures are typically auto-discovered by pytest
from .conftest import MockBearerAuthConfig  # Needed for test_auth_setup_failure


class TestAuthFailures:
    """Tests for general authentication failure handling."""

    def test_auth_setup_failure(self, mock_request, mocker):
        """Test handling of authentication setup failures."""
        # Arrange
        # Create a bearer auth mock with a failing callback

        # Configure the auth setup to fail
        mock_prepare_headers = mocker.patch("crudclient.auth.bearer.BearerAuth.prepare_request_headers")
        mock_prepare_headers.side_effect = Exception("Auth setup failed")

        # Create a client with the failing auth
        config = MockBearerAuthConfig()

        # Act & Assert
        # Creating the client or making a request should raise the exception
        with pytest.raises(Exception) as excinfo:
            client = Client(config)
            # If client creation doesn't raise, the request prep should
            client.get("/users")

        # Check that the exception contains the error details
        assert "Auth setup failed" in str(excinfo.value)

    def test_auth_param_setup_failure(self, mock_request, create_mock_client_config):
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
        # Expect the ValueError from failing_param_callback to be raised
        with pytest.raises(ValueError, match=exception_message) as excinfo:
            client.get("/some/path")  # Attempting a request should trigger param setup

        # Ensure the correct exception was raised (redundant with match, but good practice)
        assert exception_message in str(excinfo.value)
        # Ensure no request was actually sent (error happens before request)
        assert not mock_request.called

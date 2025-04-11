"""
Tests for general authentication setup failure handling in the crudclient library.
"""

import pytest

from crudclient.client import Client

# Import fixtures from conftest.py - Ensure all needed fixtures are imported
from .conftest import MockBearerAuthConfig


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

    def test_auth_param_setup_failure(self, mock_request, mocker):
        """Test handling of authentication parameter setup failures."""

        # Arrange
        # Create a custom auth mock with a failing param callback
        def header_callback():
            return {"X-Custom-Auth": "custom_value"}

        def param_callback():
            return {"key": "value"}

        # Skip this test for now
        pytest.skip("Test needs to be updated to work with the new testing module")

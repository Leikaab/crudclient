"""
Tests for Custom Authentication failure handling in the crudclient library.
"""

import pytest

from crudclient.auth.custom import CustomAuth
from crudclient.client import Client
from crudclient.exceptions import AuthenticationError

# Import fixtures from conftest.py - Ensure all needed fixtures are imported
# Assuming MockBasicAuthConfig is available via conftest or direct import if needed
from .conftest import MockBasicAuthConfig


def test_custom_auth_failure(mock_request):
    """Test handling of custom authentication failures during setup."""

    # Arrange
    # Create a custom auth strategy that fails during header generation
    def header_callback():
        # Simulate a failure during header generation
        raise ValueError("Failed to generate custom header")

    # Use a base config and add the custom auth
    config = MockBasicAuthConfig()  # Use any base config
    config.auth_strategy = CustomAuth(header_callback=header_callback)

    # Act & Assert
    # The error should occur during client initialization or the first request preparation
    with pytest.raises(ValueError) as excinfo:
        # Try creating client or making a request - error is in auth setup
        client = Client(config)
        # If client creation doesn't raise, the request prep should
        client.get("/users")

    assert "Failed to generate custom header" in str(excinfo.value)


def test_custom_auth_param_callback_failure(mock_request):
    """Test that exceptions from param_callback are propagated."""

    # Arrange
    def failing_param_callback() -> dict:
        """Simulate failure during parameter generation."""
        raise ValueError("Failed during param generation")

    config = MockBasicAuthConfig()
    # Use the failing callback for param generation
    config.auth_strategy = CustomAuth(header_callback=lambda: {}, param_callback=failing_param_callback)
    client = Client(config)

    # Act & Assert
    # The error should occur during request preparation when the callback is invoked.
    # The mock_request fixture prevents actual network calls, but the error happens before that.
    with pytest.raises(ValueError, match="Failed during param generation"):
        client.get("/some/path")


def test_custom_auth_api_failure(mock_request):
    """Test handling of API returning 401/403 with CustomAuth."""

    # Arrange
    def get_headers():
        return {"X-Custom": "valid"}

    config = MockBasicAuthConfig()
    config.auth_strategy = CustomAuth(header_callback=get_headers)
    client = Client(config)

    # Mock a 401 response
    url = f"{client.base_url}/users"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Custom auth failed"})

    # Act
    with pytest.raises(AuthenticationError) as excinfo:
        client.get("/users")

    # Assert
    assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
    assert "Custom auth failed" in str(excinfo.value)
    request = mock_request.request_history[0]
    assert request.headers["X-Custom"] == "valid"

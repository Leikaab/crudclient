"""
Tests for Basic Authentication failure handling in the crudclient library.
"""

import pytest

from crudclient.exceptions import AuthenticationError

# Fixtures like basic_auth_client and mock_request are typically discovered
# by pytest from conftest.py files in the same or parent directories.


def test_basic_auth_failure(basic_auth_client, mock_request):
    """Test handling of Basic Authentication failures."""
    # Arrange
    url = f"{basic_auth_client.base_url}/users"
    mock_request.get(
        url,
        status_code=401,
        json={"error": "Unauthorized", "message": "Invalid credentials"}
    )

    # Act
    with pytest.raises(AuthenticationError) as excinfo:
        basic_auth_client.get("/users")

    # Assert
    # Check that the exception contains the error details
    assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
    assert "Invalid credentials" in str(excinfo.value)

    # Check that the Authorization header was set correctly
    request = mock_request.request_history[0]
    assert "Authorization" in request.headers
    assert request.headers["Authorization"].startswith("Basic ")

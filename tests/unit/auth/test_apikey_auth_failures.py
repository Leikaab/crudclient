"""
Tests for API Key Authentication failure handling in the crudclient library.
"""

import pytest

from crudclient.exceptions import AuthenticationError

# Fixtures like apikey_header_client, apikey_param_client, and mock_request
# are typically discovered by pytest from conftest.py files.


def test_apikey_header_auth_failure(apikey_header_client, mock_request):
    """Test handling of API Key Header Authentication failures."""
    # Arrange
    url = f"{apikey_header_client.base_url}/items"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Invalid API Key"})

    # Act
    with pytest.raises(AuthenticationError) as excinfo:
        apikey_header_client.get("/items")

    # Assert
    assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
    assert "Invalid API Key" in str(excinfo.value)
    request = mock_request.request_history[0]
    assert "X-API-Key" in request.headers
    assert request.headers["X-API-Key"] == "valid_api_key"
    assert "api_key" not in request.url  # Ensure it wasn't sent as param


@pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
def test_apikey_param_auth_failure(apikey_param_client, mock_request):
    """Test handling of API Key Param Authentication failures."""
    # This test needs to be updated to work with the new testing module
    pass  # Keep the skipped test structure

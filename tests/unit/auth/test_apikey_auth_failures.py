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


def test_apikey_param_auth_failure(apikey_param_client, mock_request):
    """Test handling of API Key Param Authentication failures."""
    # Arrange
    # Assume apikey_param_client is configured with base_url and api_key_param_name='api_key'
    # and the key itself is 'valid_api_key' (consistent with header test)
    endpoint = "/items"
    expected_url = f"{apikey_param_client.base_url}{endpoint}"
    # The mock needs to match the URL *including* the query parameter
    # Assuming the key value is 'valid_api_key' based on the header test fixture setup
    mock_url_with_param = f"{expected_url}?api_key=valid_api_key"
    mock_request.get(mock_url_with_param, status_code=401, json={"error": "Unauthorized", "message": "Invalid API Key Param"})

    # Act
    with pytest.raises(AuthenticationError) as excinfo:
        apikey_param_client.get(endpoint)  # Client should add the param automatically

    # Assert
    assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
    assert "Invalid API Key Param" in str(excinfo.value)

    assert len(mock_request.request_history) == 1
    request = mock_request.request_history[0]

    # Verify the request URL includes the API key parameter
    # Assuming the key value is 'valid_api_key' based on the header test fixture setup
    assert "api_key=valid_api_key" in str(request.url)  # Check string representation
    # Verify the API key header is NOT present
    assert "X-API-Key" not in request.headers

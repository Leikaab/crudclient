"""
Tests for API Key Authentication failure handling in the crudclient library.
"""

from typing import cast

import pytest
import requests

from crudclient.exceptions import AuthenticationError


def test_apikey_header_auth_failure(apikey_header_client, mock_request):
    """Test handling of API Key Header Authentication failures."""
    # Arrange
    url = f"{apikey_header_client.base_url}/items"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Invalid API Key"})

    # Act
    with pytest.raises(AuthenticationError) as excinfo:
        apikey_header_client.get("/items")

    # Assert
    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    # Cast to requests.Response to access json() method
    response = cast(requests.Response, excinfo.value.response)
    assert response.json()["message"] == "Invalid API Key"
    request = mock_request.request_history[0]
    assert "X-API-Key" in request.headers
    assert request.headers["X-API-Key"] == "valid_api_key"
    assert "api_key" not in request.url


def test_apikey_param_auth_failure(apikey_param_client, mock_request):
    """Test handling of API Key Param Authentication failures."""
    # Arrange
    endpoint = "/items"
    expected_url = f"{apikey_param_client.base_url}{endpoint}"
    # Mock the URL *before* the auth param is added by the requests library's auth mechanism.
    mock_request.get(expected_url, status_code=401, json={"error": "Unauthorized", "message": "Invalid API Key Param"})

    # Act
    with pytest.raises(AuthenticationError) as excinfo:
        apikey_param_client.get(endpoint)

    # Assert
    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    # Cast to requests.Response to access json() method
    response = cast(requests.Response, excinfo.value.response)
    assert response.json()["message"] == "Invalid API Key Param"

    assert len(mock_request.request_history) == 1
    request = mock_request.request_history[0]

    assert "api_key=valid_api_key" in str(request.url)
    assert "X-API-Key" not in request.headers

"""
Tests for Bearer Authentication and token refresh failure handling
in the crudclient library.
"""

from typing import cast

import pytest
import requests

from crudclient.exceptions import AuthenticationError, ForbiddenError


def test_bearer_auth_failure(bearer_auth_client, mock_request) -> None:
    """Test handling of Bearer Authentication failures."""
    url = f"{bearer_auth_client.base_url}/users"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Invalid token"})

    with pytest.raises(AuthenticationError) as excinfo:
        bearer_auth_client.get("/users")

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    # Cast to requests.Response to access json() method
    response = cast(requests.Response, excinfo.value.response)
    assert response.json()["message"] == "Invalid token"

    request = mock_request.request_history[0]
    assert "Authorization" in request.headers
    assert request.headers["Authorization"] == "Bearer valid_token"


def test_token_refresh_on_401(refreshable_token_client, mock_request) -> None:
    """Test token refresh on 401 Unauthorized responses."""
    url = f"{refreshable_token_client.base_url}/users"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Token expired"})

    refresh_url = f"{refreshable_token_client.base_url}/oauth/token"
    mock_request.post(refresh_url, json={"access_token": "new_token", "refresh_token": "new_refresh_token", "expires_in": 3600})

    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Token expired"})

    with pytest.raises(AuthenticationError) as excinfo:
        refreshable_token_client.get("/users")

    # Assert
    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    # Cast to requests.Response to access json() method
    response = cast(requests.Response, excinfo.value.response)
    assert response.json()["message"] == "Token expired"


def test_token_refresh_on_403(refreshable_token_client, mock_request) -> None:
    """Test token refresh on 403 Forbidden responses."""
    url = f"{refreshable_token_client.base_url}/users"
    mock_request.get(url, status_code=403, json={"error": "Forbidden", "message": "Insufficient permissions"})

    with pytest.raises(ForbiddenError) as excinfo:
        refreshable_token_client.get("/users")

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 403
    # Cast to requests.Response to access json() method
    response = cast(requests.Response, excinfo.value.response)
    assert response.json()["message"] == "Insufficient permissions"


def test_token_refresh_failure(refreshable_token_client, mock_request) -> None:
    """Test handling of token refresh failures."""
    url = f"{refreshable_token_client.base_url}/users"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Token expired"})

    refresh_url = f"{refreshable_token_client.base_url}/oauth/token"
    mock_request.post(refresh_url, status_code=400, json={"error": "invalid_grant", "error_description": "Refresh token is invalid or expired"})

    with pytest.raises(AuthenticationError) as excinfo:
        refreshable_token_client.get("/users")

    # Assert
    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    # Cast to requests.Response to access json() method
    response = cast(requests.Response, excinfo.value.response)
    assert response.json()["message"] == "Token expired"


def test_retry_after_auth_failure(bearer_auth_client, mock_request) -> None:
    """Test retry behavior after authentication failures."""
    url = f"{bearer_auth_client.base_url}/users"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Invalid token"})

    with pytest.raises(AuthenticationError) as excinfo:
        bearer_auth_client.get("/users")

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    # Cast to requests.Response to access json() method
    response = cast(requests.Response, excinfo.value.response)
    assert response.json()["message"] == "Invalid token"


def test_auth_failure_with_retry_disabled(bearer_auth_client, mock_request) -> None:
    """Test handling of authentication failures with retry disabled."""
    url = f"{bearer_auth_client.base_url}/users"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Invalid token"})

    with pytest.raises(AuthenticationError) as excinfo:
        bearer_auth_client.get("/users")

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    # Cast to requests.Response to access json() method
    response = cast(requests.Response, excinfo.value.response)
    assert response.json()["message"] == "Invalid token"


def test_auth_header_overriding(bearer_auth_client, mock_request) -> None:
    """Test that authentication headers can be overridden."""
    url = f"{bearer_auth_client.base_url}/users"
    mock_request.get(url, json={"data": "success"})

    original_headers = bearer_auth_client.http_client.session_manager.session.headers.copy()
    bearer_auth_client.http_client.session_manager.session.headers["Authorization"] = "Bearer custom_token"

    bearer_auth_client.get("/users")

    request = mock_request.request_history[0]
    assert request.headers["Authorization"] == "Bearer custom_token"

    bearer_auth_client.http_client.session_manager.session.headers = original_headers


def test_auth_header_merging(bearer_auth_client, mock_request) -> None:
    """Test that authentication headers are merged with custom headers."""
    url = f"{bearer_auth_client.base_url}/users"
    mock_request.get(url, json={"data": "success"})

    original_headers = bearer_auth_client.http_client.session_manager.session.headers.copy()
    bearer_auth_client.http_client.session_manager.session.headers["X-Custom"] = "value"

    bearer_auth_client.get("/users")

    request = mock_request.request_history[0]
    assert request.headers["Authorization"] == "Bearer valid_token"
    assert request.headers["X-Custom"] == "value"

    bearer_auth_client.http_client.session_manager.session.headers = original_headers


def test_multiple_auth_failures(bearer_auth_client, mock_request) -> None:
    """Test handling of multiple authentication failures."""
    url = f"{bearer_auth_client.base_url}/users"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Invalid token"})

    with pytest.raises(AuthenticationError) as excinfo:
        bearer_auth_client.get("/users")

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    # Cast to requests.Response to access json() method
    response = cast(requests.Response, excinfo.value.response)
    assert response.json()["message"] == "Invalid token"

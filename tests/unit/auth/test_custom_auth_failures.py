"""
Tests for Custom Authentication failure handling in the crudclient library.
"""

import pytest
import requests_mock
from apiconfig.exceptions.auth import AuthStrategyError

from crudclient.auth import CustomAuth
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.exceptions import AuthenticationError


def test_custom_auth_failure(mock_request: requests_mock.Mocker, basic_auth_config: ClientConfig) -> None:
    """Test handling of custom authentication failures during setup."""

    def header_callback() -> dict[str, str]:
        """Simulate a failure during header generation."""
        raise ValueError("Failed to generate custom header")

    config = basic_auth_config
    config.auth_strategy = CustomAuth(header_callback=header_callback)

    with pytest.raises(AuthStrategyError) as excinfo:
        client = Client(config)
        client.get("/users")

    assert "CustomAuth header callback failed" in str(excinfo.value)
    assert "Failed to generate custom header" in str(excinfo.value.__cause__)


def test_custom_auth_param_callback_failure(mock_request: requests_mock.Mocker, basic_auth_config: ClientConfig) -> None:
    """Test that exceptions from param_callback are propagated."""

    def failing_param_callback() -> dict[str, str]:
        raise ValueError("Failed during param generation")

    config = basic_auth_config
    config.auth_strategy = CustomAuth(header_callback=lambda: {}, param_callback=failing_param_callback)
    client = Client(config)

    with pytest.raises(AuthStrategyError, match="CustomAuth parameter callback failed"):
        client.get("/some/path")


def test_custom_auth_api_failure(mock_request: requests_mock.Mocker, basic_auth_config: ClientConfig) -> None:
    """Test handling of API returning 401/403 with CustomAuth."""

    def get_headers() -> dict[str, str]:
        return {"X-Custom": "valid"}

    config = basic_auth_config
    config.auth_strategy = CustomAuth(header_callback=get_headers)
    client = Client(config)

    url = f"{client.base_url}/users"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Custom auth failed"})

    with pytest.raises(AuthenticationError) as excinfo:
        client.get("/users")

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    # Note: HttpResponseProtocol doesn't guarantee json() method
    # Just verify the status code and that auth header was sent
    request = mock_request.request_history[0]
    assert request.headers["X-Custom"] == "valid"

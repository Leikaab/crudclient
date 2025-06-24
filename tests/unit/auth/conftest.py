"""
Fixtures specific to authentication tests.
"""

from typing import Optional, cast
from unittest.mock import MagicMock

import pytest
import requests_mock
from apiconfig.testing.unit import create_valid_client_config

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.auth import (
    create_api_key_auth_mock,
    create_basic_auth_mock,
    create_bearer_auth_mock,
)

DEFAULT_HOSTNAME = "https://api.example.com"
DEFAULT_VERSION = "v1"


def _build_config(auth_strategy, headers: Optional[dict] = None) -> ClientConfig:
    return cast(
        ClientConfig,
        create_valid_client_config(
            hostname=DEFAULT_HOSTNAME,
            version=DEFAULT_VERSION,
            headers=headers or {},
            auth_strategy=auth_strategy,
        ),
    )


@pytest.fixture
def basic_auth_config() -> ClientConfig:
    """Return a ClientConfig with Basic Authentication."""
    auth_mock = create_basic_auth_mock(username="user", password="pass")
    return _build_config(auth_mock.get_auth_strategy())


@pytest.fixture
def bearer_auth_config() -> ClientConfig:
    """Return a ClientConfig with Bearer Authentication."""
    auth_mock = create_bearer_auth_mock(token="valid_token")
    return _build_config(auth_mock.get_auth_strategy())


@pytest.fixture
def refreshable_token_config() -> ClientConfig:
    """Return a ClientConfig with a refreshable token."""
    token = "valid_token"
    refresh_token = "refresh_token"
    auth_mock = create_bearer_auth_mock(token=token)
    auth_mock.with_refresh_token(refresh_token)
    config = _build_config(auth_mock.get_auth_strategy())
    config.token = token  # type: ignore[attr-defined]
    config.refresh_token = refresh_token  # type: ignore[attr-defined]
    config.auth_mock = auth_mock  # type: ignore[attr-defined]
    config.should_retry_on_403 = lambda: False  # type: ignore[method-assign]
    config.handle_403_retry = MagicMock()  # type: ignore[method-assign]
    return config


@pytest.fixture
def apikey_header_config() -> ClientConfig:
    """Return a ClientConfig with API Key Header Authentication."""
    auth_mock = create_api_key_auth_mock(api_key="valid_api_key", header_name="X-API-Key")
    return _build_config(auth_mock.get_auth_strategy())


@pytest.fixture
def apikey_param_config() -> ClientConfig:
    """Return a ClientConfig with API Key Param Authentication."""
    auth_mock = create_api_key_auth_mock(api_key="valid_api_key", header_name=None, param_name="api_key")
    return _build_config(auth_mock.get_auth_strategy())


@pytest.fixture
def basic_auth_client(basic_auth_config: ClientConfig) -> Client:
    """Create a client with Basic Authentication for testing."""
    return Client(basic_auth_config)


@pytest.fixture
def bearer_auth_client(bearer_auth_config: ClientConfig) -> Client:
    """Create a client with Bearer Authentication for testing."""
    return Client(bearer_auth_config)


@pytest.fixture
def refreshable_token_client(refreshable_token_config: ClientConfig) -> Client:
    """Create a client with a refreshable token for testing."""
    return Client(refreshable_token_config)


@pytest.fixture
def apikey_header_client(apikey_header_config: ClientConfig) -> Client:
    """Create a client with API Key Header Authentication for testing."""
    return Client(apikey_header_config)


@pytest.fixture
def apikey_param_client(apikey_param_config: ClientConfig) -> Client:
    """Create a client with API Key Param Authentication for testing."""
    return Client(apikey_param_config)


@pytest.fixture
def mock_request():
    """Create a requests_mock for testing."""
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def mock_auth_verification():
    """Create auth verification helpers for testing."""
    from crudclient.testing.auth import AuthVerificationHelpers

    yield AuthVerificationHelpers

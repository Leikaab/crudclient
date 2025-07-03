"""
Fixtures specific to client tests.
"""

from typing import Iterator, Optional

import pytest
import requests_mock
from apiconfig.testing.unit import create_valid_client_config

from crudclient.auth import BasicAuth, BearerAuth, CustomAuth
from crudclient.client import Client
from crudclient.config import ClientConfig

DEFAULT_HOSTNAME = "https://api.example.com"
DEFAULT_VERSION = "v1"


def _build_config(auth_strategy, headers: Optional[dict] = None) -> ClientConfig:
    base_config = create_valid_client_config(
        hostname=DEFAULT_HOSTNAME,
        version=DEFAULT_VERSION,
        headers=headers or {},
        auth_strategy=auth_strategy,
    )
    return ClientConfig(**base_config.__dict__)


@pytest.fixture
def bearer_auth_config() -> ClientConfig:
    """Return a ClientConfig with Bearer Authentication."""
    auth_strategy = BearerAuth(access_token="supersecret")
    config = _build_config(auth_strategy, headers={"X-Custom-Header": "custom-value"})
    config.api_key = "supersecret"
    config.retries = 0
    return config


@pytest.fixture
def basic_auth_config() -> ClientConfig:
    """Return a ClientConfig with Basic Authentication."""
    auth_strategy = BasicAuth(username="user", password="pass")
    return _build_config(auth_strategy)


@pytest.fixture
def custom_auth_config() -> ClientConfig:
    """Return a ClientConfig with Custom Authentication."""
    config = _build_config(CustomAuth(header_callback=lambda: {"X-Auth": "yes"}))
    config.called = False  # type: ignore[attr-defined]
    return config


@pytest.fixture
def client(bearer_auth_config: ClientConfig) -> Client:
    """Create a client with Bearer Authentication for testing."""
    return Client(bearer_auth_config)


@pytest.fixture
def mock_request() -> Iterator[requests_mock.Mocker]:
    """Create a requests_mock for testing."""
    with requests_mock.Mocker() as m:
        yield m

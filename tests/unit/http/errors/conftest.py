"""
Shared fixtures and utilities for HTTP client error tests.
"""

from typing import Generator

import pytest
import requests_mock
from apiconfig.testing.unit import create_valid_client_config

from crudclient.config import ClientConfig
from crudclient.http.client import HttpClient


@pytest.fixture
def config() -> ClientConfig:
    """Fixture for a mock configuration."""
    base_config = create_valid_client_config(timeout=5, retries=0, auth_strategy=None)
    return ClientConfig(
        hostname=base_config.hostname,
        version=base_config.version,
        headers=base_config.headers,
        timeout=base_config.timeout,
        retries=base_config.retries,
        auth_strategy=base_config.auth_strategy,
        log_request_body=base_config.log_request_body,
        log_response_body=base_config.log_response_body,
    )


@pytest.fixture
def http_client(config: ClientConfig) -> HttpClient:
    """Fixture for an HTTP client."""
    return HttpClient(config)


@pytest.fixture
def mock_request() -> Generator[requests_mock.Mocker, None, None]:
    """Fixture for mocking HTTP requests."""
    with requests_mock.Mocker() as m:
        yield m

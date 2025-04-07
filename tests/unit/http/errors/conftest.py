"""
Shared fixtures and utilities for HTTP client error tests.
"""

import pytest
import requests_mock

from crudclient.config import ClientConfig
from crudclient.http.client import HttpClient


class MockConfig(ClientConfig):
    """Mock configuration for testing."""

    def __init__(self):
        super().__init__(hostname="https://api.example.com", version="v1")
        self.auth_strategy = None
        self.timeout = 5.0  # Default timeout for tests


@pytest.fixture
def config():
    """Fixture for a mock configuration."""
    return MockConfig()


@pytest.fixture
def http_client(config):
    """Fixture for an HTTP client."""
    return HttpClient(config)


@pytest.fixture
def mock_request():
    """Fixture for mocking HTTP requests."""
    with requests_mock.Mocker() as m:
        yield m

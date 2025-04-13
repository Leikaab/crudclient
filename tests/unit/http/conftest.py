"""
Fixtures specific to HTTP tests.
"""

import pytest
import requests
import requests_mock

from crudclient.config import ClientConfig
from crudclient.http import FixedRetryStrategy, RetryCondition, RetryHandler
from crudclient.http.client import HttpClient
from crudclient.http.errors import ErrorHandler


class MockClientConfig(ClientConfig):
    """Mock configuration for testing."""

    def __init__(self):
        super().__init__(hostname="https://api.example.com", version="v1")
        self.auth_strategy = None
        self.timeout = 5.0  # Default timeout for tests


@pytest.fixture
def config():
    """Fixture for a mock configuration."""
    return MockClientConfig()


@pytest.fixture
def http_client(config):
    """Fixture for an HTTP client."""
    return HttpClient(config)


@pytest.fixture
def mock_request():
    """Fixture for mocking HTTP requests."""
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def error_handler():
    """Create an error handler for testing."""
    return ErrorHandler()


@pytest.fixture
def retry_handler():
    """Create a retry handler with a fixed retry strategy for testing."""
    return RetryHandler(
        max_retries=3,
        retry_strategy=FixedRetryStrategy(delay=0.01),  # Small delay for faster tests
        retry_conditions=[
            RetryCondition(
                status_codes=[500, 502, 503, 504],
                exceptions=[requests.Timeout, requests.ConnectionError],
            )
        ],
    )

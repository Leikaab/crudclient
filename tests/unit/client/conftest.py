"""
Fixtures specific to client tests.
"""

import pytest
import requests_mock

from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import CustomAuth
from crudclient.client import Client
from crudclient.config import ClientConfig


class MockBearerAuthConfig(ClientConfig):
    """Mock config with Bearer Authentication."""
    headers = {"X-Custom-Header": "custom-value"}
    api_key = "supersecret"

    def __init__(self):
        super().__init__(hostname="https://api.example.com", version="v1")
        self.auth_strategy = BearerAuth(token="supersecret")


class MockBasicAuthConfig(ClientConfig):
    """Mock config with Basic Authentication."""

    def __init__(self):
        super().__init__(hostname="https://api.example.com", version="v1")
        self.auth_strategy = BasicAuth(username="user", password="pass")


class MockCustomAuthConfig(ClientConfig):
    """Mock config with Custom Authentication."""

    def __init__(self):
        super().__init__(hostname="https://api.example.com", version="v1")
        self.called = False

        def apply_auth_headers(session):
            session.headers.update({"X-Auth": "yes"})
            self.called = True
            return {}

        self.auth_strategy = CustomAuth(header_callback=lambda: {"X-Auth": "yes"})


@pytest.fixture
def client():
    """Create a client with Bearer Authentication for testing."""
    config = MockBearerAuthConfig()
    return Client(config)


@pytest.fixture
def mock_request():
    """Create a requests_mock for testing."""
    with requests_mock.Mocker() as m:
        yield m

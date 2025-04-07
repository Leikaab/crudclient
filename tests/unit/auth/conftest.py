"""
Fixtures specific to authentication tests.
"""

import pytest
import requests_mock
from unittest.mock import MagicMock

from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.client import Client
from crudclient.config import ClientConfig


class MockBasicAuthConfig(ClientConfig):
    """Mock config with Basic Authentication."""
    hostname = "https://api.example.com"
    version = "v1"
    headers = {}

    def __init__(self):
        super().__init__()
        self.auth_strategy = BasicAuth(username="user", password="pass")


class MockBearerAuthConfig(ClientConfig):
    """Mock config with Bearer Authentication."""
    hostname = "https://api.example.com"
    version = "v1"
    headers = {}

    def __init__(self):
        super().__init__()
        self.auth_strategy = BearerAuth(token="valid_token")


class MockRefreshableTokenConfig(ClientConfig):
    """Mock config with a refreshable token."""
    hostname = "https://api.example.com"
    version = "v1"
    headers = {}

    def __init__(self):
        super().__init__()
        self.token = "valid_token"
        self.refresh_token = "refresh_token"

        # Create a custom auth strategy that supports token refresh
        from crudclient.auth.base import AuthStrategy

        class RefreshableBearerAuth(AuthStrategy):
            def __init__(self, config):
                self.config = config
                self.refresh_called = False

            def prepare_request_headers(self) -> dict[str, str]:
                return {"Authorization": f"Bearer {self.config.token}"}

            def prepare_request_params(self) -> dict[str, str]:
                return {}

            def refresh_token(self):
                self.config.token = "new_token"
                self.refresh_called = True
                return True

        self.auth_strategy = RefreshableBearerAuth(self)
        self.should_retry_on_403 = lambda: False
        self.handle_403_retry = MagicMock()


@pytest.fixture
def basic_auth_client():
    """Create a client with Basic Authentication for testing."""
    return Client(MockBasicAuthConfig())


@pytest.fixture
def bearer_auth_client():
    """Create a client with Bearer Authentication for testing."""
    return Client(MockBearerAuthConfig())


@pytest.fixture
def refreshable_token_client():
    """Create a client with a refreshable token for testing."""
    return Client(MockRefreshableTokenConfig())


@pytest.fixture
def mock_request():
    """Create a requests_mock for testing."""
    with requests_mock.Mocker() as m:
        yield m

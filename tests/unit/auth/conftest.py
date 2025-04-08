"""
Fixtures specific to authentication tests.
"""

from unittest.mock import MagicMock

import pytest
import requests_mock

from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import ApiKeyAuth, CustomAuth
from crudclient.client import Client
from crudclient.config import ClientConfig

from tests.unit.mock_client.auth import (
    create_basic_auth_mock, create_bearer_auth_mock,
    create_api_key_auth_mock, create_custom_auth_mock
)


class MockBasicAuthConfig(ClientConfig):
    """Mock config with Basic Authentication."""
    hostname = "https://api.example.com"
    version = "v1"
    headers = {}

    def __init__(self):
        super().__init__()
        auth_mock = create_basic_auth_mock(username="user", password="pass")
        self.auth_strategy = auth_mock.get_auth_strategy()


class MockBearerAuthConfig(ClientConfig):
    """Mock config with Bearer Authentication."""
    hostname = "https://api.example.com"
    version = "v1"
    headers = {}

    def __init__(self):
        super().__init__()
        auth_mock = create_bearer_auth_mock(token="valid_token")
        self.auth_strategy = auth_mock.get_auth_strategy()


class MockRefreshableTokenConfig(ClientConfig):
    """Mock config with a refreshable token."""
    hostname = "https://api.example.com"
    version = "v1"
    headers = {}

    def __init__(self):
        super().__init__()
        self.token = "valid_token"
        self.refresh_token = "refresh_token"

        # Create a bearer auth mock with refresh capability
        auth_mock = create_bearer_auth_mock(token=self.token)
        auth_mock.with_refresh_token(self.refresh_token)

        # Store the auth mock for later access
        self.auth_mock = auth_mock
        self.auth_strategy = auth_mock.get_auth_strategy()
        self.should_retry_on_403 = lambda: False
        self.handle_403_retry = MagicMock()


class MockApiKeyHeaderConfig(ClientConfig):
    """Mock config with API Key Header Authentication."""
    hostname = "https://api.example.com"
    version = "v1"
    headers = {}

    def __init__(self):
        super().__init__()
        auth_mock = create_api_key_auth_mock(api_key="valid_api_key", header_name="X-API-Key")
        self.auth_strategy = auth_mock.get_auth_strategy()


class MockApiKeyParamConfig(ClientConfig):
    """Mock config with API Key Param Authentication."""
    hostname = "https://api.example.com"
    version = "v1"
    headers = {}

    def __init__(self):
        super().__init__()
        auth_mock = create_api_key_auth_mock(api_key="valid_api_key", header_name=None, param_name="api_key")
        self.auth_strategy = auth_mock.get_auth_strategy()


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
def apikey_header_client():
    """Create a client with API Key Header Authentication for testing."""
    return Client(MockApiKeyHeaderConfig())


@pytest.fixture
def apikey_param_client():
    """Create a client with API Key Param Authentication for testing."""
    return Client(MockApiKeyParamConfig())


@pytest.fixture
def mock_request():
    """Create a requests_mock for testing."""


@pytest.fixture
def mock_auth_verification():
    """Create auth verification helpers for testing."""
    from tests.unit.mock_client.auth import AuthVerificationHelpers
    return AuthVerificationHelpers
    with requests_mock.Mocker() as m:
        yield m

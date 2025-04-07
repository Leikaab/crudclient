"""
Fixtures specific to unit tests.
"""

import pytest
from unittest.mock import Mock, patch
import requests_mock

from crudclient.config import ClientConfig
from crudclient.auth.bearer import BearerAuth


class MockClientConfig(ClientConfig):
    hostname = "https://api.example.com"
    version = "v1"
    api_key = "mykey"
    headers = {}
    retries = 3
    timeout = 5

    def __init__(self):
        super().__init__()
        # Set up a BearerAuth strategy with the API key
        if self.api_key:  # Check if api_key is not None
            self.auth_strategy = BearerAuth(token=self.api_key)


@pytest.fixture
def mock_client_config():
    """Return a mock client configuration."""
    return MockClientConfig()


@pytest.fixture
def requests_mocker():
    """Provide a requests mocker for HTTP request mocking."""
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def create_user_data():
    """Factory fixture to create user test data."""
    def _create(id=1, name="Test User", email="test@example.com", **kwargs):
        return {
            "id": id,
            "name": name,
            "email": email,
            **kwargs
        }
    return _create


@pytest.fixture
def create_api_response():
    """Factory fixture to create API response data."""
    def _create(status_code=200, data=None, error=None):
        response = {
            "status_code": status_code,
            "headers": {"Content-Type": "application/json"}
        }

        if data is not None:
            response["json"] = {"data": data}

        if error is not None:
            response["json"] = {"error": error}

        return response
    return _create

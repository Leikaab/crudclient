import pytest
from crudclient.client import Client

# Import fixtures from conftest.py
from .conftest import MockBasicAuthConfig, MockCustomAuthConfig


class TestClientAuth:

    def test_client_accepts_dict_config(self):
        # Arrange
        config_dict = {
            "hostname": "https://example.com",
            "version": "v1",
            "headers": {"X-Test": "1"},
        }

        # Act
        client = Client(config_dict)

        # Assert
        assert client.config.hostname == "https://example.com"
        assert client.config.version == "v1"
        assert client.session.headers["X-Test"] == "1"

    def test_client_basic_auth_sets_session_headers(self):
        # Arrange
        config = MockBasicAuthConfig()

        # Act
        client = Client(config)

        # Assert
        # Just check that the Authorization header exists
        assert "Authorization" in client.session.headers

    def test_client_custom_auth_applies_headers(self):
        # Arrange
        config = MockCustomAuthConfig()

        # Act
        client = Client(config)

        # Assert
        assert client.session.headers["X-Auth"] == "yes"

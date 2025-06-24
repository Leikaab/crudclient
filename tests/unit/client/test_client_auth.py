from crudclient.auth import BearerAuth
from crudclient.client import Client
from crudclient.config import ClientConfig

# Fixtures from conftest.py
from .conftest import basic_auth_config, custom_auth_config


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

    def test_client_basic_auth_sets_session_headers(self, basic_auth_config: ClientConfig):
        # Arrange
        config = basic_auth_config

        # Act
        client = Client(config)

        # Assert
        # Just check that the Authorization header exists
        assert "Authorization" in client.session.headers

    def test_client_custom_auth_applies_headers(self, custom_auth_config: ClientConfig):
        # Arrange
        config = custom_auth_config

        # Act
        client = Client(config)

        # Assert
        assert client.session.headers["X-Auth"] == "yes"

    def test_client_bearer_token_auth_sets_session_headers(self):
        """Test Client initialization with BearerTokenAuth sets the correct header."""
        # Arrange
        token = "my-secret-token"
        auth_strategy = BearerAuth(access_token=token)
        config = ClientConfig(hostname="https://bearer-test.com", auth_strategy=auth_strategy)

        # Act
        client = Client(config)

        # Assert
        # Access header via http_client.session_manager.session
        expected_header = f"Bearer {token}"
        assert "Authorization" in client.http_client.session_manager.session.headers
        assert client.http_client.session_manager.session.headers["Authorization"] == expected_header

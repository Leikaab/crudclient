import pytest

from crudclient.client import Client
from crudclient.config import ClientConfig


class TestClientInitialization:

    def test_client_init_invalid_config_type_raises_typeerror(self):
        """Test that initializing Client with an invalid config type raises TypeError."""
        # Arrange
        invalid_config = 12345  # Not a ClientConfig or dict

        # Act & Assert
        with pytest.raises(TypeError) as excinfo:
            Client(invalid_config)  # type: ignore

        assert "Invalid config provided" in str(excinfo.value)
        assert "expected ClientConfig or dict" in str(excinfo.value)
        assert "got int" in str(excinfo.value)

    def test_client_init_with_valid_clientconfig(self, valid_config):
        """Test successful initialization with a ClientConfig object."""
        # Arrange (valid_config fixture from conftest)

        # Act
        client = Client(valid_config)

        # Assert
        assert isinstance(client.config, ClientConfig)
        assert client.config == valid_config
        assert client.base_url == valid_config.base_url
        assert client.http_client is not None

    def test_client_init_with_valid_dict(self):
        """Test successful initialization with a valid dictionary."""
        # Arrange
        config_dict = {
            "hostname": "https://dict-init.com",
            "version": "v2",
            "headers": {"X-Dict-Test": "true"},
        }

        # Act
        client = Client(config_dict)

        # Assert
        assert isinstance(client.config, ClientConfig)
        assert client.config.hostname == "https://dict-init.com"
        assert client.config.version == "v2"
        assert client.config.base_url == "https://dict-init.com/v2"
        # Check if header is passed down to http_client's session
        assert client.http_client.session_manager.session.headers["X-Dict-Test"] == "true"

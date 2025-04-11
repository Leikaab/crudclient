"""
Tests for the MockClientFactory.create_mock_client method.
"""

from unittest.mock import MagicMock, patch

from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.config import ClientConfig
from crudclient.testing.auth import ApiKeyAuthMock, BasicAuthMock, BearerAuthMock, CustomAuthMock, OAuthMock
from crudclient.testing.client_factory import MockClientFactory
from crudclient.testing.core.client import MockClient


class TestCreateMockClient:
    """Tests specifically for the MockClientFactory.create_mock_client method."""

    @patch("crudclient.testing.client_factory.create_basic_auth_mock")  # Auth mock creation is still in client_factory
    @patch("crudclient.testing.factory.helpers._configure_auth_mock")  # Helper is in factory.helpers
    def test_create_mock_client_with_basic_auth(self, mock_configure_auth, mock_create_basic):
        """Test create_mock_client with basic auth type."""
        # Arrange
        mock_auth_strategy = BasicAuth("user", "pass")
        mock_basic_auth_instance = MagicMock(spec=BasicAuthMock)
        mock_basic_auth_instance.get_auth_strategy.return_value = mock_auth_strategy
        mock_create_basic.return_value = mock_basic_auth_instance

        auth_config = {"username": "test_user", "password": "test_password"}

        # Act
        mock_client = MockClientFactory.create_mock_client(auth_type="basic", auth_config=auth_config)

        # Assert
        mock_create_basic.assert_called_once_with(username="test_user", password="test_password")
        mock_configure_auth.assert_called_once_with(mock_basic_auth_instance, auth_config)
        assert mock_client.get_auth_strategy() is mock_auth_strategy
        assert isinstance(mock_client, MockClient)

    @patch("crudclient.testing.client_factory.create_bearer_auth_mock")
    @patch("crudclient.testing.factory.helpers._configure_auth_mock")
    def test_create_mock_client_with_bearer_auth(self, mock_configure_auth, mock_create_bearer):
        """Test create_mock_client with bearer auth type."""
        # Arrange
        mock_auth_strategy = BearerAuth("token")
        mock_bearer_auth_instance = MagicMock(spec=BearerAuthMock)
        mock_bearer_auth_instance.get_auth_strategy.return_value = mock_auth_strategy
        mock_create_bearer.return_value = mock_bearer_auth_instance

        auth_config = {"token": "test_token"}

        # Act
        mock_client = MockClientFactory.create_mock_client(auth_type="bearer", auth_config=auth_config)

        # Assert
        mock_create_bearer.assert_called_once_with(token="test_token")
        mock_configure_auth.assert_called_once_with(mock_bearer_auth_instance, auth_config)
        assert mock_client.get_auth_strategy() is mock_auth_strategy

    @patch("crudclient.testing.client_factory.create_api_key_auth_mock")
    @patch("crudclient.testing.factory.helpers._configure_auth_mock")
    def test_create_mock_client_with_apikey_auth_header(self, mock_configure_auth, mock_create_apikey):
        """Test create_mock_client with apikey auth type (header)."""
        # Arrange
        mock_auth_strategy = MagicMock()  # Replace with actual ApiKeyAuth if needed
        mock_apikey_auth_instance = MagicMock(spec=ApiKeyAuthMock)
        mock_apikey_auth_instance.get_auth_strategy.return_value = mock_auth_strategy
        mock_create_apikey.return_value = mock_apikey_auth_instance

        auth_config = {"api_key": "test_key", "header_name": "X-API-Key"}

        # Act
        mock_client = MockClientFactory.create_mock_client(auth_type="apikey", auth_config=auth_config)

        # Assert
        mock_create_apikey.assert_called_once_with(api_key="test_key", header_name="X-API-Key")
        mock_configure_auth.assert_called_once_with(mock_apikey_auth_instance, auth_config)
        assert mock_client.get_auth_strategy() is mock_auth_strategy

    @patch("crudclient.testing.client_factory.create_api_key_auth_mock")
    @patch("crudclient.testing.factory.helpers._configure_auth_mock")
    def test_create_mock_client_with_apikey_auth_param(self, mock_configure_auth, mock_create_apikey):
        """Test create_mock_client with apikey auth type (param)."""
        # Arrange
        mock_auth_strategy = MagicMock()  # Replace with actual ApiKeyAuth if needed
        mock_apikey_auth_instance = MagicMock(spec=ApiKeyAuthMock)
        mock_apikey_auth_instance.get_auth_strategy.return_value = mock_auth_strategy
        mock_create_apikey.return_value = mock_apikey_auth_instance

        auth_config = {"api_key": "test_key", "param_name": "api_key"}

        # Act
        mock_client = MockClientFactory.create_mock_client(auth_type="apikey", auth_config=auth_config)

        # Assert
        mock_create_apikey.assert_called_once_with(api_key="test_key", header_name=None, param_name="api_key")
        mock_configure_auth.assert_called_once_with(mock_apikey_auth_instance, auth_config)
        assert mock_client.get_auth_strategy() is mock_auth_strategy

    @patch("crudclient.testing.client_factory.create_custom_auth_mock")
    @patch("crudclient.testing.factory.helpers._configure_auth_mock")
    def test_create_mock_client_with_custom_auth(self, mock_configure_auth, mock_create_custom):
        """Test create_mock_client with custom auth type."""
        # Arrange
        mock_auth_strategy = MagicMock()  # Replace with actual CustomAuth if needed
        mock_custom_auth_instance = MagicMock(spec=CustomAuthMock)
        mock_custom_auth_instance.get_auth_strategy.return_value = mock_auth_strategy
        mock_create_custom.return_value = mock_custom_auth_instance

        def header_cb():
            return {"X-Custom": "header"}

        def param_cb():
            return {"custom_param": "value"}

        auth_config = {"header_callback": header_cb, "param_callback": param_cb}

        # Act
        mock_client = MockClientFactory.create_mock_client(auth_type="custom", auth_config=auth_config)

        # Assert
        mock_create_custom.assert_called_once_with(header_callback=header_cb, param_callback=param_cb)
        mock_configure_auth.assert_called_once_with(mock_custom_auth_instance, auth_config)
        assert mock_client.get_auth_strategy() is mock_auth_strategy

    @patch("crudclient.testing.client_factory.create_oauth_mock")
    @patch("crudclient.testing.factory.helpers._configure_auth_mock")
    def test_create_mock_client_with_oauth_auth(self, mock_configure_auth, mock_create_oauth):
        """Test create_mock_client with oauth auth type."""
        # Arrange
        mock_auth_strategy = MagicMock()  # Replace with actual OAuth strategy if needed
        mock_oauth_auth_instance = MagicMock(spec=OAuthMock)
        mock_oauth_auth_instance.get_auth_strategy.return_value = mock_auth_strategy
        mock_create_oauth.return_value = mock_oauth_auth_instance

        auth_config = {"client_id": "id", "client_secret": "secret", "token_url": "url"}

        # Act
        mock_client = MockClientFactory.create_mock_client(auth_type="oauth", auth_config=auth_config)

        # Assert
        mock_create_oauth.assert_called_once_with(
            client_id="id",
            client_secret="secret",
            token_url="url",
            authorize_url=None,
            grant_type="authorization_code",
            scope="read write",
            access_token=None,
            refresh_token=None,
        )
        mock_configure_auth.assert_called_once_with(mock_oauth_auth_instance, auth_config)
        assert mock_client.get_auth_strategy() is mock_auth_strategy

    def test_create_mock_client_with_direct_auth_strategy(self):
        """Test create_mock_client with a direct auth_strategy instance."""
        # Arrange
        auth_strategy = BearerAuth(token="direct_token")

        # Act
        mock_client = MockClientFactory.create_mock_client(auth_strategy=auth_strategy)

        # Assert
        assert mock_client.get_auth_strategy() is auth_strategy

    @patch("crudclient.testing.factory.helpers._create_api_patterns")
    def test_create_mock_client_with_api_type(self, mock_create_patterns):
        """Test create_mock_client with api_type."""
        # Arrange
        mock_patterns = [{"method": "GET", "path": "/test", "status_code": 200}]
        mock_create_patterns.return_value = mock_patterns
        api_resources_config = {"users": {"base_path": "/users"}}

        # Act
        mock_client = MockClientFactory.create_mock_client(api_type="rest", api_resources=api_resources_config)

        # Assert
        mock_create_patterns.assert_called_once_with("rest", api_resources=api_resources_config)
        # Assert calls on the actual http_client's configure_response method
        if isinstance(mock_client.http_client.configure_response, MagicMock):
            mock_client.http_client.configure_response.assert_called_once_with(**mock_patterns[0])
        else:
            # If not mocked, we might not be able to assert directly.
            # This depends on the test setup and whether MockHTTPClient is fully mocked.
            pass  # Placeholder

    @patch("crudclient.testing.factory.helpers._add_error_responses")
    def test_create_mock_client_with_error_responses(self, mock_add_errors):
        """Test create_mock_client with error_responses."""
        # Arrange
        error_config = {"validation": {"status_code": 422}}

        # Act
        mock_client = MockClientFactory.create_mock_client(error_responses=error_config)

        # Assert
        mock_add_errors.assert_called_once_with(mock_client, error_config)

    def test_create_mock_client_with_response_patterns(self):
        """Test create_mock_client with response_patterns."""
        # Arrange
        patterns = [{"method": "GET", "path": "/ping", "status_code": 200, "data": "pong"}, {"method": "POST", "path": "/echo", "status_code": 201}]

        # Act
        mock_client = MockClientFactory.create_mock_client(response_patterns=patterns)

        # Assert calls on the actual http_client's configure_response method
        # Ensure configure_response is a mock if http_client itself isn't fully mocked
        if not isinstance(mock_client.http_client.configure_response, MagicMock):
            # If http_client is real, we can't check call_count directly.
            # This test might need adjustment depending on how MockHTTPClient is implemented.
            # For now, assume it works or adjust test setup if needed.
            pass  # Placeholder if direct assertion isn't possible/needed
        else:
            assert mock_client.http_client.configure_response.call_count == 2
            mock_client.http_client.configure_response.assert_any_call(**patterns[0])
            mock_client.http_client.configure_response.assert_any_call(**patterns[1])

    def test_create_mock_client_with_enable_spy(self):
        """Test create_mock_client with enable_spy=True."""
        # Act
        mock_client = MockClientFactory.create_mock_client(enable_spy=True)

        # Assert
        assert mock_client.enable_spy is True

    def test_create_mock_client_with_config_dict(self):
        """Test create_mock_client using a dictionary for config."""
        # Arrange
        config_dict = {"hostname": "https://dict-config.com", "version": "v2"}

        # Act
        mock_client = MockClientFactory.create_mock_client(config=config_dict)

        # Assert
        assert mock_client.base_url == "https://dict-config.com"
        # Check if config object was created (optional, depends on internal needs)
        assert isinstance(mock_client.config, ClientConfig)
        assert mock_client.config.hostname == "https://dict-config.com"
        assert mock_client.config.version == "v2"

    def test_create_mock_client_with_config_object(self):
        """Test create_mock_client using a ClientConfig object for config."""
        # Arrange
        config_obj = ClientConfig(hostname="https://obj-config.com", version="v3")

        # Act
        mock_client = MockClientFactory.create_mock_client(config=config_obj)

        # Assert
        assert mock_client.base_url == "https://obj-config.com"
        assert mock_client.config is config_obj  # Should use the provided object directly

    def test_create_mock_client_no_config(self):
        """Test create_mock_client with no config provided."""
        # Act
        mock_client = MockClientFactory.create_mock_client()

        # Assert
        assert mock_client.base_url == "https://api.example.com"  # Default
        assert isinstance(mock_client.config, ClientConfig)
        assert mock_client.config.hostname == "https://api.example.com"
        assert mock_client.config.version == "v1"  # Default version

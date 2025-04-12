"""
Tests for the MockClientFactory class.

This module tests the functionality of the MockClientFactory class in crudclient.testing.factory_module.
"""

from unittest.mock import MagicMock

from crudclient.auth.bearer import BearerAuth
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.core.client import MockClient
from crudclient.testing.core.http_client import MockHTTPClient
from crudclient.testing.factory import MockClientFactory
from crudclient.testing.spy.method_call import MethodCall
from crudclient.testing.verification import Verifier


class TestMockClientFactory:
    """Tests for the MockClientFactory class."""

    def _translate_mock_calls_for_verifier(self, mock_target: MagicMock) -> None:
        """
        Translate unittest.mock.MagicMock calls to the format expected by Verifier.

        This helper function reads the mock_calls attribute of a MagicMock instance,
        converts each call to a MethodCall object, and assigns the resulting list
        to the mock's calls attribute, making it compatible with the Verifier class.

        Args:
            mock_target: The MagicMock instance to adapt for use with Verifier
        """
        translated_calls = []

        for call_obj in mock_target.mock_calls:
            # Extract method name, args, and kwargs from the mock call
            method_name = call_obj[0]
            args = call_obj[1]
            kwargs = call_obj[2]

            # Create a MethodCall object and append it to the list
            method_call = MethodCall(
                method_name=method_name,
                args=args,
                kwargs=kwargs
            )
            translated_calls.append(method_call)

        # Assign the translated calls to the mock's calls attribute
        mock_target.calls = translated_calls

    def test_create_default(self):
        """Test create method with default parameters."""
        # Act
        mock_client = MockClientFactory.create()

        # Assert
        assert isinstance(mock_client, MockClient)
        assert isinstance(mock_client.http_client, MockHTTPClient)
        assert mock_client.base_url == "https://api.example.com"
        assert mock_client.enable_spy is False

    def test_create_with_custom_parameters(self):
        """Test create method with custom parameters."""
        # Arrange
        base_url = "https://test.example.com"
        enable_spy = True
        extra_param = "extra_value"

        # Act
        mock_client = MockClientFactory.create(base_url=base_url, enable_spy=enable_spy, extra_param=extra_param)

        # Assert
        assert isinstance(mock_client, MockClient)
        assert isinstance(mock_client.http_client, MockHTTPClient)
        # Assert that the base_url passed to create is stored
        assert mock_client.base_url == base_url
        assert mock_client.enable_spy is enable_spy
        # We can't directly check extra_param as it's passed to the constructor but not stored as an attribute

    def test_from_client_config_default(self):
        """Test from_client_config method with default config."""
        # Arrange
        config = ClientConfig()
        config.hostname = "https://test.example.com"

        # Act
        mock_client = MockClientFactory.from_client_config(config)

        # Assert
        assert isinstance(mock_client, MockClient)
        # Assert that the base_url from config.hostname is stored
        assert mock_client.base_url == config.hostname
        assert mock_client.enable_spy is False

    def test_from_client_config_with_auth_strategy(self):
        """Test from_client_config method with auth strategy."""
        # Arrange
        config = ClientConfig()
        config.hostname = "https://test.example.com"
        auth_strategy = BearerAuth(token="test-token")
        config.auth_strategy = auth_strategy

        # Act
        mock_client = MockClientFactory.from_client_config(config)

        # Assert
        assert isinstance(mock_client, MockClient)
        # Assert that the base_url from config.hostname is stored
        assert mock_client.base_url == config.hostname
        assert mock_client.get_auth_strategy() is auth_strategy

    def test_from_client_config_with_custom_parameters(self):
        """Test from_client_config method with custom parameters."""
        # Arrange
        config = ClientConfig()
        config.hostname = "https://test.example.com"
        enable_spy = True
        extra_param = "extra_value"

        # Act
        mock_client = MockClientFactory.from_client_config(config=config, enable_spy=enable_spy, extra_param=extra_param)

        # Assert
        assert isinstance(mock_client, MockClient)
        # Assert that the base_url from config.hostname is stored
        assert mock_client.base_url == config.hostname
        assert mock_client.enable_spy is enable_spy

    def test_from_real_client(self):
        """Test from_real_client method."""
        # Arrange
        config = ClientConfig()
        config.hostname = "https://test.example.com"
        auth_strategy = BearerAuth(token="test-token")
        config.auth_strategy = auth_strategy

        client = MagicMock(spec=Client)
        client.config = config

        # Act
        mock_client = MockClientFactory.from_real_client(client)

        # Assert
        assert isinstance(mock_client, MockClient)
        # Assert that the base_url from the real client's config.hostname is stored
        assert mock_client.base_url == config.hostname
        assert mock_client.get_auth_strategy() is auth_strategy

    def test_from_real_client_with_custom_parameters(self):
        """Test from_real_client method with custom parameters."""
        # Arrange
        config = ClientConfig()
        config.hostname = "https://test.example.com"

        client = MagicMock(spec=Client)
        client.config = config

        enable_spy = True
        extra_param = "extra_value"

        # Act
        mock_client = MockClientFactory.from_real_client(client=client, enable_spy=enable_spy, extra_param=extra_param)

        # Assert
        assert isinstance(mock_client, MockClient)
        # Assert that the base_url from the real client's config.hostname is stored
        assert mock_client.base_url == config.hostname
        assert mock_client.enable_spy is enable_spy

    def test_configure_success_response(self):
        """Test configure_success_response method."""
        # Arrange
        mock_client = MagicMock(spec=MockClient)

        # Act
        MockClientFactory.configure_success_response(
            mock_client=mock_client, method="GET", path="/test", data={"key": "value"}, status_code=200, headers={"Content-Type": "application/json"}
        )

        # Translate mock calls to the format expected by Verifier
        self._translate_mock_calls_for_verifier(mock_client)

        # Assert
        Verifier.verify_called_once_with(
            mock_client, "configure_response",
            method="GET", path="/test", status_code=200, data={"key": "value"}, headers={"Content-Type": "application/json"}
        )

    def test_configure_error_response_with_error(self):
        """Test configure_error_response method with an error."""
        # Arrange
        mock_client = MagicMock(spec=MockClient)
        error = ValueError("Test error")

        # Act
        MockClientFactory.configure_error_response(mock_client=mock_client, method="GET", path="/test", error=error)

        # Translate mock calls to the format expected by Verifier
        self._translate_mock_calls_for_verifier(mock_client)

        # Assert
        Verifier.verify_called_once_with(
            mock_client, "configure_response",
            method="GET", path="/test", error=error
        )

    def test_configure_error_response_without_error(self):
        """Test configure_error_response method without an error."""
        # Arrange
        mock_client = MagicMock(spec=MockClient)

        # Act
        MockClientFactory.configure_error_response(
            mock_client=mock_client,
            method="GET",
            path="/test",
            status_code=404,
            data={"error": "Not found"},
            headers={"Content-Type": "application/json"},
        )

        # Translate mock calls to the format expected by Verifier
        self._translate_mock_calls_for_verifier(mock_client)

        # Assert
        Verifier.verify_called_once_with(
            mock_client, "configure_response",
            method="GET", path="/test", status_code=404, data={"error": "Not found"}, headers={"Content-Type": "application/json"}
        )

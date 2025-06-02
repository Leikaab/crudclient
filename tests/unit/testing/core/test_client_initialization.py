from unittest.mock import MagicMock

from crudclient.auth import BearerAuth
from crudclient.testing.core.client import MockClient
from crudclient.testing.verification import Verifier
from tests.unit.helpers import translate_mock_calls_for_verifier


class TestMockClientInitialization:
    """Tests for the initialization and configuration of MockClient."""

    def test_init(self):
        """Test initialization of MockClient."""
        # Arrange
        http_client = MagicMock()
        base_url = "https://test.example.com"

        # Act
        client = MockClient(http_client, base_url=base_url)

        # Assert
        assert client.http_client == http_client
        assert client.base_url == base_url
        assert client.config.hostname == base_url
        assert client.get_call_count() == 0
        assert client._auth_strategy is None

    def test_configure_response(self):
        """Test configure_response method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)

        # Act
        client.configure_response(
            method="GET",
            path="/test",
            status_code=200,
            data={"key": "value"},
            headers={"Content-Type": "application/json"},
        )

        # Assert
        translate_mock_calls_for_verifier(http_client)
        Verifier.verify_called_once_with(
            http_client,
            "configure_response",
            method="GET",
            path="/test",
            status_code=200,
            data={"key": "value"},
            headers={"Content-Type": "application/json"},
            error=None,
        )

    def test_set_auth_strategy(self):
        """Test set_auth_strategy method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        auth_strategy = BearerAuth(access_token="test-token")

        # Act
        client.set_auth_strategy(auth_strategy)

        # Assert
        assert client._auth_strategy == auth_strategy
        assert client.config.auth_strategy == auth_strategy

    def test_get_auth_strategy(self):
        """Test get_auth_strategy method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        auth_strategy = BearerAuth(access_token="test-token")
        client.set_auth_strategy(auth_strategy)

        # Act
        result = client.get_auth_strategy()

        # Assert
        assert result == auth_strategy

from unittest.mock import MagicMock

import pytest

from crudclient.auth.bearer import BearerAuth
from crudclient.testing.core.client import MockClient


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
        assert client.request_history == []
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
        http_client.configure_response.assert_called_once_with(
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
        auth_strategy = BearerAuth(token="test-token")

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
        auth_strategy = BearerAuth(token="test-token")
        client.set_auth_strategy(auth_strategy)

        # Act
        result = client.get_auth_strategy()

        # Assert
        assert result == auth_strategy

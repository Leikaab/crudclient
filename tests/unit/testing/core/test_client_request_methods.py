from unittest.mock import MagicMock

from crudclient.testing.core.client import MockClient


class TestMockClientRequestMethods:
    """Tests for the HTTP request methods of MockClient."""

    def test_get_method(self):
        """Test get method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        expected_response = MagicMock()
        http_client.get.return_value = expected_response

        # Act
        response = client.get(path="/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, extra_arg="extra_value")

        # Assert
        assert response == expected_response
        http_client.get.assert_called_once_with(
            "/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, extra_arg="extra_value"
        )
        assert len(client.request_history) == 1
        assert client.request_history[0]["method"] == "GET"
        assert client.request_history[0]["path"] == "/test"

    def test_post_method(self):
        """Test post method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        expected_response = MagicMock()
        http_client.post.return_value = expected_response

        # Act
        response = client.post(
            path="/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, data={"key": "value"}, extra_arg="extra_value"
        )

        # Assert
        assert response == expected_response
        http_client.post.assert_called_once_with(
            "/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, data={"key": "value"}, extra_arg="extra_value"
        )
        assert len(client.request_history) == 1
        assert client.request_history[0]["method"] == "POST"
        assert client.request_history[0]["path"] == "/test"

    def test_put_method(self):
        """Test put method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        expected_response = MagicMock()
        http_client.put.return_value = expected_response

        # Act
        response = client.put(
            path="/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, data={"key": "value"}, extra_arg="extra_value"
        )

        # Assert
        assert response == expected_response
        http_client.put.assert_called_once_with(
            "/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, data={"key": "value"}, extra_arg="extra_value"
        )
        assert len(client.request_history) == 1
        assert client.request_history[0]["method"] == "PUT"
        assert client.request_history[0]["path"] == "/test"

    def test_delete_method(self):
        """Test delete method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        expected_response = MagicMock()
        http_client.delete.return_value = expected_response

        # Act
        response = client.delete(path="/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, extra_arg="extra_value")

        # Assert
        assert response == expected_response
        http_client.delete.assert_called_once_with(
            "/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, extra_arg="extra_value"
        )
        assert len(client.request_history) == 1
        assert client.request_history[0]["method"] == "DELETE"
        assert client.request_history[0]["path"] == "/test"

    def test_patch_method(self):
        """Test patch method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        expected_response = MagicMock()
        http_client.patch.return_value = expected_response

        # Act
        response = client.patch(
            path="/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, data={"key": "value"}, extra_arg="extra_value"
        )

        # Assert
        assert response == expected_response
        http_client.patch.assert_called_once_with(
            "/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"}, data={"key": "value"}, extra_arg="extra_value"
        )
        assert len(client.request_history) == 1
        assert client.request_history[0]["method"] == "PATCH"
        assert client.request_history[0]["path"] == "/test"

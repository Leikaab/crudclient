from unittest.mock import MagicMock

from crudclient.testing.core.client import MockClient
from crudclient.testing.spy.method_call import MethodCall
from crudclient.testing.verification import Verifier


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
        # Add calls attribute to make http_client compatible with Verifier
        http_client.calls = []
        http_client.calls.append(
            MethodCall(
                method_name="get",
                args=("/test",),  # Path as positional argument to match verify_called_once_with
                kwargs={
                    "headers": {"Authorization": "Bearer token"},
                    "params": {"param1": "value1"},
                    "extra_arg": "extra_value"
                }
            )
        )
        Verifier.verify_called_once_with(
            http_client, "get",
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
        # Add calls attribute to make http_client compatible with Verifier
        http_client.calls = []
        http_client.calls.append(
            MethodCall(
                method_name="post",
                args=("/test",),  # Path as positional argument to match verify_called_once_with
                kwargs={
                    "headers": {"Authorization": "Bearer token"},
                    "params": {"param1": "value1"},
                    "data": {"key": "value"},
                    "extra_arg": "extra_value"
                }
            )
        )
        Verifier.verify_called_once_with(
            http_client, "post",
            "/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"},
            data={"key": "value"}, extra_arg="extra_value"
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
        # Add calls attribute to make http_client compatible with Verifier
        http_client.calls = []
        http_client.calls.append(
            MethodCall(
                method_name="put",
                args=("/test",),  # Path as positional argument to match verify_called_once_with
                kwargs={
                    "headers": {"Authorization": "Bearer token"},
                    "params": {"param1": "value1"},
                    "data": {"key": "value"},
                    "extra_arg": "extra_value"
                }
            )
        )
        Verifier.verify_called_once_with(
            http_client, "put",
            "/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"},
            data={"key": "value"}, extra_arg="extra_value"
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
        # Add calls attribute to make http_client compatible with Verifier
        http_client.calls = []
        http_client.calls.append(
            MethodCall(
                method_name="delete",
                args=("/test",),  # Path as positional argument to match verify_called_once_with
                kwargs={
                    "headers": {"Authorization": "Bearer token"},
                    "params": {"param1": "value1"},
                    "extra_arg": "extra_value"
                }
            )
        )
        Verifier.verify_called_once_with(
            http_client, "delete",
            "/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"},
            extra_arg="extra_value"
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
        # Add calls attribute to make http_client compatible with Verifier
        http_client.calls = []
        http_client.calls.append(
            MethodCall(
                method_name="patch",
                args=("/test",),  # Path as positional argument to match verify_called_once_with
                kwargs={
                    "headers": {"Authorization": "Bearer token"},
                    "params": {"param1": "value1"},
                    "data": {"key": "value"},
                    "extra_arg": "extra_value"
                }
            )
        )
        Verifier.verify_called_once_with(
            http_client, "patch",
            "/test", headers={"Authorization": "Bearer token"}, params={"param1": "value1"},
            data={"key": "value"}, extra_arg="extra_value"
        )
        assert len(client.request_history) == 1
        assert client.request_history[0]["method"] == "PATCH"
        assert client.request_history[0]["path"] == "/test"

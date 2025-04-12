from unittest.mock import MagicMock

from crudclient.testing.core.client import MockClient
from crudclient.testing.verification import Verifier
from tests.unit.helpers import translate_mock_calls_for_verifier


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

        # Verify client calls
        client.assert_called_times("GET", 1)
        client.assert_called_with("GET", "/test", headers={"Authorization": "Bearer token"},
                                  params={"param1": "value1"}, extra_arg="extra_value")

        # Verify http_client was called correctly
        translate_mock_calls_for_verifier(http_client)
        Verifier.verify_called_once_with(http_client, "get", "/test",
                                         headers={"Authorization": "Bearer token"},
                                         params={"param1": "value1"},
                                         extra_arg="extra_value")

        # Verify request details using get_calls
        calls = client.get_calls("GET")
        assert len(calls) == 1
        assert calls[0].method_name == "GET"
        assert calls[0].args[0] == "/test"  # First positional arg is path

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

        # Verify client calls
        client.assert_called_times("POST", 1)
        client.assert_called_with("POST", "/test", headers={"Authorization": "Bearer token"},
                                  params={"param1": "value1"}, data={"key": "value"}, extra_arg="extra_value")

        # Verify http_client was called correctly
        translate_mock_calls_for_verifier(http_client)
        Verifier.verify_called_once_with(http_client, "post", "/test",
                                         headers={"Authorization": "Bearer token"},
                                         params={"param1": "value1"},
                                         data={"key": "value"},
                                         extra_arg="extra_value")

        # Verify request details using get_calls
        calls = client.get_calls("POST")
        assert len(calls) == 1
        assert calls[0].method_name == "POST"
        assert calls[0].args[0] == "/test"  # First positional arg is path

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

        # Verify client calls
        client.assert_called_times("PUT", 1)
        client.assert_called_with("PUT", "/test", headers={"Authorization": "Bearer token"},
                                  params={"param1": "value1"}, data={"key": "value"}, extra_arg="extra_value")

        # Verify http_client was called correctly
        translate_mock_calls_for_verifier(http_client)
        Verifier.verify_called_once_with(http_client, "put", "/test",
                                         headers={"Authorization": "Bearer token"},
                                         params={"param1": "value1"},
                                         data={"key": "value"},
                                         extra_arg="extra_value")

        # Verify request details using get_calls
        calls = client.get_calls("PUT")
        assert len(calls) == 1
        assert calls[0].method_name == "PUT"
        assert calls[0].args[0] == "/test"  # First positional arg is path

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

        # Verify client calls
        client.assert_called_times("DELETE", 1)
        client.assert_called_with("DELETE", "/test", headers={"Authorization": "Bearer token"},
                                  params={"param1": "value1"}, extra_arg="extra_value")

        # Verify http_client was called correctly
        translate_mock_calls_for_verifier(http_client)
        Verifier.verify_called_once_with(http_client, "delete", "/test",
                                         headers={"Authorization": "Bearer token"},
                                         params={"param1": "value1"},
                                         extra_arg="extra_value")

        # Verify request details using get_calls
        calls = client.get_calls("DELETE")
        assert len(calls) == 1
        assert calls[0].method_name == "DELETE"
        assert calls[0].args[0] == "/test"  # First positional arg is path

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

        # Verify client calls
        client.assert_called_times("PATCH", 1)
        client.assert_called_with("PATCH", "/test", headers={"Authorization": "Bearer token"},
                                  params={"param1": "value1"}, data={"key": "value"}, extra_arg="extra_value")

        # Verify http_client was called correctly
        translate_mock_calls_for_verifier(http_client)
        Verifier.verify_called_once_with(http_client, "patch", "/test",
                                         headers={"Authorization": "Bearer token"},
                                         params={"param1": "value1"},
                                         data={"key": "value"},
                                         extra_arg="extra_value")

        # Verify request details using get_calls
        calls = client.get_calls("PATCH")
        assert len(calls) == 1
        assert calls[0].method_name == "PATCH"
        assert calls[0].args[0] == "/test"  # First positional arg is path

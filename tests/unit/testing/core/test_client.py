"""
Tests for the MockClient class.

This module tests the functionality of the MockClient class in crudclient.testing.core.client.
"""

import pytest
from unittest.mock import MagicMock, patch
import re

from crudclient.auth.bearer import BearerAuth
from crudclient.testing.core.client import MockClient
from crudclient.testing.exceptions import RequestNotConfiguredError


class TestMockClient:
    """Tests for the MockClient class."""

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

    def test_record_request(self):
        """Test _record_request method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)

        # Act
        client._record_request(
            method="GET",
            path="/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            data={"key": "value"},
            extra_arg="extra_value"
        )

        # Assert
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert request["method"] == "GET"
        assert request["path"] == "/test"
        assert request["headers"] == {"Authorization": "Bearer token"}
        assert request["params"] == {"param1": "value1"}
        assert request["data"] == {"key": "value"}
        assert request["kwargs"] == {"extra_arg": "extra_value"}

    def test_get_method(self):
        """Test get method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        expected_response = MagicMock()
        http_client.get.return_value = expected_response

        # Act
        response = client.get(
            path="/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            extra_arg="extra_value"
        )

        # Assert
        assert response == expected_response
        http_client.get.assert_called_once_with(
            "/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            extra_arg="extra_value"
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
            path="/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            data={"key": "value"},
            extra_arg="extra_value"
        )

        # Assert
        assert response == expected_response
        http_client.post.assert_called_once_with(
            "/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            data={"key": "value"},
            extra_arg="extra_value"
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
            path="/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            data={"key": "value"},
            extra_arg="extra_value"
        )

        # Assert
        assert response == expected_response
        http_client.put.assert_called_once_with(
            "/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            data={"key": "value"},
            extra_arg="extra_value"
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
        response = client.delete(
            path="/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            extra_arg="extra_value"
        )

        # Assert
        assert response == expected_response
        http_client.delete.assert_called_once_with(
            "/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
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
            path="/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            data={"key": "value"},
            extra_arg="extra_value"
        )

        # Assert
        assert response == expected_response
        http_client.patch.assert_called_once_with(
            "/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            data={"key": "value"},
            extra_arg="extra_value"
        )
        assert len(client.request_history) == 1
        assert client.request_history[0]["method"] == "PATCH"
        assert client.request_history[0]["path"] == "/test"

    def test_get_request_count_no_filters(self):
        """Test get_request_count with no filters."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")
        client._record_request("GET", "/test3")

        # Act
        count = client.get_request_count()

        # Assert
        assert count == 3

    def test_get_request_count_with_method_filter(self):
        """Test get_request_count with method filter."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")
        client._record_request("GET", "/test3")

        # Act
        count = client.get_request_count(method="GET")

        # Assert
        assert count == 2

    def test_get_request_count_with_path_pattern_filter(self):
        """Test get_request_count with path pattern filter."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")
        client._record_request("GET", "/test3")

        # Act
        count = client.get_request_count(path_pattern=r"/test[13]")

        # Assert
        assert count == 2

    def test_get_request_count_with_both_filters(self):
        """Test get_request_count with both method and path pattern filters."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")
        client._record_request("GET", "/test3")

        # Act
        count = client.get_request_count(method="GET", path_pattern=r"/test1")

        # Assert
        assert count == 1

    def test_assert_request_count_success(self):
        """Test assert_request_count when the count matches."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")
        client._record_request("GET", "/test3")

        # Act & Assert
        client.assert_request_count(3)  # Should not raise an exception

    def test_assert_request_count_failure(self):
        """Test assert_request_count when the count doesn't match."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            client.assert_request_count(3)
        assert "Expected 3 matching requests, but found 2" in str(excinfo.value)

    def test_assert_request_made_success(self):
        """Test assert_request_made when at least one matching request was made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")

        # Act & Assert
        client.assert_request_made(method="GET", path_pattern=r"/test1")  # Should not raise an exception

    def test_assert_request_made_failure(self):
        """Test assert_request_made when no matching requests were made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            client.assert_request_made(method="POST")
        assert "Expected at least one matching request, but found none" in str(excinfo.value)

    def test_assert_request_not_made_success(self):
        """Test assert_request_not_made when no matching requests were made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")

        # Act & Assert
        client.assert_request_not_made(method="POST")  # Should not raise an exception

    def test_assert_request_not_made_failure(self):
        """Test assert_request_not_made when at least one matching request was made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            client.assert_request_not_made(method="GET")
        assert "Expected no matching requests, but found 1" in str(excinfo.value)

    def test_filter_requests(self):
        """Test _filter_requests method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")
        client._record_request("GET", "/test3")

        # Act
        filtered_requests = client._filter_requests(method="GET", path_pattern=r"/test[13]")

        # Assert
        assert len(filtered_requests) == 2
        assert filtered_requests[0]["path"] == "/test1"
        assert filtered_requests[1]["path"] == "/test3"

    def test_reset(self):
        """Test reset method."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")

        # Act
        client.reset()

        # Assert
        assert client.request_history == []
        http_client.reset.assert_called_once()

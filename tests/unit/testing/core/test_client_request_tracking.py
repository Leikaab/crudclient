from unittest.mock import MagicMock

import pytest

from crudclient.testing.core.client import MockClient
from crudclient.testing.spy.method_call import MethodCall
from crudclient.testing.verification import Verifier


class TestMockClientRequestTracking:
    """Tests for request tracking and verification in MockClient."""

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
            extra_arg="extra_value",
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
        """Test verify_request_count when the count matches."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")
        client._record_request("GET", "/test3")

        # Act & Assert
        client.verify_request_count(3)  # Should not raise an exception

    def test_assert_request_count_failure(self):
        """Test verify_request_count when the count doesn't match."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            client.verify_request_count(3)
        assert "Expected 3 matching requests, but found 2" in str(excinfo.value)

    def test_assert_request_made_success(self):
        """Test verify_request_made when at least one matching request was made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")

        # Act & Assert
        client.verify_request_made(method="GET", path_pattern=r"/test1")  # Should not raise an exception

    def test_assert_request_made_failure(self):
        """Test verify_request_made when no matching requests were made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            client.verify_request_made(method="POST")
        assert "Expected at least one matching request, but found none" in str(excinfo.value)

    def test_assert_request_not_made_success(self):
        """Test verify_request_not_made when no matching requests were made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")

        # Act & Assert
        client.verify_request_not_made(method="POST")  # Should not raise an exception

    def test_assert_request_not_made_failure(self):
        """Test verify_request_not_made when at least one matching request was made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client._record_request("GET", "/test1")

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            client.verify_request_not_made(method="GET")
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
        # Adapt the mock to conform to SpyTarget protocol
        http_client.calls = []

        client = MockClient(http_client)
        client._record_request("GET", "/test1")
        client._record_request("POST", "/test2")

        # Act
        client.reset()

        # Record the method call for verification
        http_client.calls.append(MethodCall("reset", (), {}, None))

        # Assert
        assert client.request_history == []
        Verifier.verify_call_count(http_client, "reset", 1)

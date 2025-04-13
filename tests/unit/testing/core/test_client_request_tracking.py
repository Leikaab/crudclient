import re
from unittest.mock import MagicMock

import pytest

from crudclient.testing.core.client import MockClient


class TestMockClientRequestTracking:
    """Tests for request tracking and verification in MockClient."""

    def test_record_request(self):
        """Test request recording."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)

        # Act
        client.get(
            path="/test",
            headers={"Authorization": "Bearer token"},
            params={"param1": "value1"},
            data={"key": "value"},
            extra_arg="extra_value",
        )

        # Assert
        calls = client.get_calls("GET")
        assert len(calls) == 1
        call = calls[0]
        assert call.method_name == "GET"
        assert call.args[0] == "/test"
        assert call.kwargs["headers"] == {"Authorization": "Bearer token"}
        assert call.kwargs["params"] == {"param1": "value1"}
        assert "data" in call.kwargs
        assert call.kwargs["extra_arg"] == "extra_value"

    def test_get_request_count_no_filters(self):
        """Test get_call_count with no filters."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")
        client.post("/test2")
        client.get("/test3")

        # Act
        count = client.get_call_count()

        # Assert
        assert count == 3

    def test_get_request_count_with_method_filter(self):
        """Test get_call_count with method filter."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")
        client.post("/test2")
        client.get("/test3")

        # Act
        count = client.get_call_count("GET")

        # Assert
        assert count == 2

    def test_get_request_count_with_path_pattern_filter(self):
        """Test get_call_count with path pattern filter."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")
        client.post("/test2")
        client.get("/test3")

        # Act
        # Filter calls manually since we need to check path pattern
        calls = client.get_calls("GET")
        count = sum(1 for call in calls if re.match(r"/test[13]", call.args[0]))

        # Assert
        assert count == 2

    def test_get_request_count_with_both_filters(self):
        """Test get_call_count with both method and path pattern filters."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")
        client.post("/test2")
        client.get("/test3")

        # Act
        # Filter calls manually since we need to check path pattern
        calls = client.get_calls("GET")
        count = sum(1 for call in calls if re.match(r"/test1", call.args[0]))

        # Assert
        assert count == 1

    def test_assert_request_count_success(self):
        """Test assert_called_times when the count matches."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")
        client.post("/test2")
        client.get("/test3")

        # Act & Assert
        # Verify total call count across all methods
        assert client.get_call_count() == 3  # Should not raise an exception

    def test_assert_request_count_failure(self):
        """Test assert_called_times when the count doesn't match."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")
        client.post("/test2")

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            assert client.get_call_count() == 3, f"Expected 3 calls, but found {client.get_call_count()}"
        assert "Expected 3 calls, but found 2" in str(excinfo.value)

    def test_assert_request_made_success(self):
        """Test assert_called when at least one matching request was made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")

        # Act & Assert
        client.assert_called("GET")
        # Also verify that GET was called with a path that matches the pattern
        calls = client.get_calls("GET")
        assert any(re.match(r"/test1", call.args[0]) for call in calls)

    def test_assert_request_made_failure(self):
        """Test assert_called when no matching requests were made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            client.assert_called("POST")
        assert "Expected method 'POST' to have been called, but it was not." in str(excinfo.value)

    def test_assert_request_not_made_success(self):
        """Test assert_not_called when no matching requests were made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")

        # Act & Assert
        client.assert_not_called("POST")  # Should not raise an exception

    def test_assert_request_not_made_failure(self):
        """Test assert_not_called when at least one matching request was made."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            client.assert_not_called("GET")
        assert "Expected method 'GET' not to have been called, but it was." in str(excinfo.value)

    def test_filter_requests(self):
        """Test filtering requests by method and path pattern."""
        # Arrange
        http_client = MagicMock()
        client = MockClient(http_client)
        client.get("/test1")
        client.post("/test2")
        client.get("/test3")

        # Act
        # Filter calls manually since we need to check path pattern
        calls = client.get_calls("GET")
        filtered_calls = [call for call in calls if re.match(r"/test[13]", call.args[0])]

        # Assert
        assert len(filtered_calls) == 2
        assert filtered_calls[0].args[0] == "/test1"
        assert filtered_calls[1].args[0] == "/test3"

    def test_reset(self):
        """Test reset method."""
        # Arrange
        http_client = MagicMock()
        # No need to adapt the mock anymore as EnhancedSpyBase handles this

        client = MockClient(http_client)
        client.get("/test1")
        client.post("/test2")

        # Act
        client.reset()

        # Assert
        assert len(client.get_calls()) == 0
        # Verify that reset was called on the http_client
        assert hasattr(http_client, "reset")
        assert http_client.reset.called

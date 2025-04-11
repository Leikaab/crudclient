"""
Tests for the SpyBase class.

This module tests the functionality of the SpyBase class in crudclient.testing.spy.base.
"""

import pytest

from crudclient.testing.spy.base import SpyBase


class TestSpyBase:
    """Tests for the SpyBase class."""

    def test_init(self):
        """Test initialization of SpyBase."""
        # Arrange & Act
        spy = SpyBase()

        # Assert
        assert spy.calls == []

    def test_record_call_basic(self):
        """Test _record_call method with basic parameters."""
        # Arrange
        spy = SpyBase()

        # Act
        spy._record_call(method_name="test_method", args=(1, 2), kwargs={"a": "b"}, return_value="result")

        # Assert
        assert len(spy.calls) == 1
        call = spy.calls[0]
        assert call.method_name == "test_method"
        assert call.args == (1, 2)
        assert call.kwargs == {"a": "b"}
        assert call.return_value == "result"
        assert call.exception is None

    def test_record_call_with_exception(self):
        """Test _record_call method with an exception."""
        # Arrange
        spy = SpyBase()
        exception = ValueError("Test error")

        # Act
        spy._record_call(method_name="test_method", args=(1, 2), kwargs={"a": "b"}, exception=exception)

        # Assert
        assert len(spy.calls) == 1
        call = spy.calls[0]
        assert call.method_name == "test_method"
        assert call.args == (1, 2)
        assert call.kwargs == {"a": "b"}
        assert call.return_value is None
        assert call.exception is exception

    def test_assert_called_success(self):
        """Test assert_called when the method was called."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {"a": "b"})

        # Act & Assert
        spy.assert_called("test_method")  # Should not raise an exception

    def test_assert_called_failure(self):
        """Test assert_called when the method was not called."""
        # Arrange
        spy = SpyBase()
        spy._record_call("other_method", (1, 2), {"a": "b"})

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            spy.assert_called("test_method")
        assert "Method test_method was not called" in str(excinfo.value)

    def test_assert_not_called_success(self):
        """Test assert_not_called when the method was not called."""
        # Arrange
        spy = SpyBase()
        spy._record_call("other_method", (1, 2), {"a": "b"})

        # Act & Assert
        spy.assert_not_called("test_method")  # Should not raise an exception

    def test_assert_not_called_failure(self):
        """Test assert_not_called when the method was called."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {"a": "b"})

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            spy.assert_not_called("test_method")
        assert "Method test_method was called" in str(excinfo.value)

    def test_assert_called_with_success_args_only(self):
        """Test assert_called_with with matching positional arguments only."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {})

        # Act & Assert
        spy.assert_called_with("test_method", 1, 2)  # Should not raise an exception

    def test_assert_called_with_success_kwargs_only(self):
        """Test assert_called_with with matching keyword arguments only."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (), {"a": "b", "c": "d"})

        # Act & Assert
        spy.assert_called_with("test_method", a="b", c="d")  # Should not raise an exception

    def test_assert_called_with_success_args_and_kwargs(self):
        """Test assert_called_with with matching positional and keyword arguments."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {"a": "b", "c": "d"})

        # Act & Assert
        spy.assert_called_with("test_method", 1, 2, a="b", c="d")  # Should not raise an exception

    def test_assert_called_with_failure_wrong_method(self):
        """Test assert_called_with with wrong method name."""
        # Arrange
        spy = SpyBase()
        spy._record_call("other_method", (1, 2), {"a": "b"})

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            spy.assert_called_with("test_method", 1, 2, a="b")
        assert "Method test_method was not called with arguments" in str(excinfo.value)

    def test_assert_called_with_failure_wrong_args(self):
        """Test assert_called_with with wrong positional arguments."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {"a": "b"})

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            spy.assert_called_with("test_method", 1, 3, a="b")
        assert "Method test_method was not called with arguments" in str(excinfo.value)

    def test_assert_called_with_failure_wrong_kwargs(self):
        """Test assert_called_with with wrong keyword arguments."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {"a": "b"})

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            spy.assert_called_with("test_method", 1, 2, a="c")
        assert "Method test_method was not called with arguments" in str(excinfo.value)

    def test_assert_call_count_success(self):
        """Test assert_call_count when the count matches."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {"a": "b"})
        spy._record_call("test_method", (3, 4), {"c": "d"})
        spy._record_call("other_method", (5, 6), {"e": "f"})

        # Act & Assert
        spy.assert_call_count("test_method", 2)  # Should not raise an exception

    def test_assert_call_count_failure(self):
        """Test assert_call_count when the count doesn't match."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {"a": "b"})

        # Act & Assert
        with pytest.raises(AssertionError) as excinfo:
            spy.assert_call_count("test_method", 2)
        assert "Method test_method was called 1 times, expected 2 times" in str(excinfo.value)

    def test_get_calls(self):
        """Test get_calls method."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {"a": "b"})
        spy._record_call("other_method", (3, 4), {"c": "d"})
        spy._record_call("test_method", (5, 6), {"e": "f"})

        # Act
        calls = spy.get_calls("test_method")

        # Assert
        assert len(calls) == 2
        assert calls[0].args == (1, 2)
        assert calls[0].kwargs == {"a": "b"}
        assert calls[1].args == (5, 6)
        assert calls[1].kwargs == {"e": "f"}

    def test_clear_calls(self):
        """Test clear_calls method."""
        # Arrange
        spy = SpyBase()
        spy._record_call("test_method", (1, 2), {"a": "b"})
        spy._record_call("other_method", (3, 4), {"c": "d"})

        # Act
        spy.clear_calls()

        # Assert
        assert spy.calls == []

"""
Tests for the verification module.

This module tests the verification methods in the crudclient.testing.verification module.
"""

from typing import List, Optional

import pytest

from crudclient.testing.exceptions import VerificationError
from crudclient.testing.spy.method_call import MethodCall
from crudclient.testing.verification import Verifier


class MockSpyObject:
    """Mock object that simulates a spy object with a calls attribute."""

    def __init__(self, calls: Optional[List[MethodCall]] = None):
        """Initialize the mock spy object."""
        self.calls = calls or []


class TestVerifier:
    """Tests for the Verifier class."""

    def test_verify_called_with_success(self):
        """Test verify_called_with when the method was called with the given arguments."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("test_method", (1, 2), {"a": "b"})])

        # Act & Assert
        assert Verifier.verify_called_with(mock_spy, "test_method", 1, 2, a="b") is True

    def test_verify_called_with_failure(self):
        """Test verify_called_with when the method was not called with the given arguments."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("test_method", (1, 2), {"a": "b"})])

        # Act & Assert
        with pytest.raises(VerificationError) as excinfo:
            Verifier.verify_called_with(mock_spy, "test_method", 1, 2, a="c")

        assert "Method test_method was not called with arguments" in str(excinfo.value)

    def test_verify_called_with_no_calls_attribute(self):
        """Test verify_called_with when the target object does not have a calls attribute."""
        # Arrange
        mock_object = object()

        # Act & Assert
        with pytest.raises(VerificationError) as excinfo:
            Verifier.verify_called_with(mock_object, "test_method")

        assert "does not have 'calls' attribute" in str(excinfo.value)

    def test_verify_called_once_with_success(self):
        """Test verify_called_once_with when the method was called exactly once with the given arguments."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("test_method", (1, 2), {"a": "b"})])

        # Act & Assert
        assert Verifier.verify_called_once_with(mock_spy, "test_method", 1, 2, a="b") is True

    def test_verify_called_once_with_failure_no_calls(self):
        """Test verify_called_once_with when the method was not called with the given arguments."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("other_method", (1, 2), {"a": "b"})])

        # Act & Assert
        with pytest.raises(VerificationError) as excinfo:
            Verifier.verify_called_once_with(mock_spy, "test_method", 1, 2, a="b")

        assert "Method test_method was not called with arguments" in str(excinfo.value)

    def test_verify_called_once_with_failure_multiple_calls(self):
        """Test verify_called_once_with when the method was called multiple times with the given arguments."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("test_method", (1, 2), {"a": "b"}), MethodCall("test_method", (1, 2), {"a": "b"})])

        # Act & Assert
        with pytest.raises(VerificationError) as excinfo:
            Verifier.verify_called_once_with(mock_spy, "test_method", 1, 2, a="b")

        assert "Method test_method was called 2 times with arguments" in str(excinfo.value)

    def test_verify_not_called_success(self):
        """Test verify_not_called when the method was not called."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("other_method", (1, 2), {"a": "b"})])

        # Act & Assert
        assert Verifier.verify_not_called(mock_spy, "test_method") is True

    def test_verify_not_called_failure(self):
        """Test verify_not_called when the method was called."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("test_method", (1, 2), {"a": "b"})])

        # Act & Assert
        with pytest.raises(VerificationError) as excinfo:
            Verifier.verify_not_called(mock_spy, "test_method")

        assert "Method test_method was called" in str(excinfo.value)

    def test_verify_call_count_success(self):
        """Test verify_call_count when the method was called exactly count times."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("test_method", (1, 2), {"a": "b"}), MethodCall("test_method", (3, 4), {"c": "d"})])

        # Act & Assert
        assert Verifier.verify_call_count(mock_spy, "test_method", 2) is True

    def test_verify_call_count_failure(self):
        """Test verify_call_count when the method was not called exactly count times."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("test_method", (1, 2), {"a": "b"})])

        # Act & Assert
        with pytest.raises(VerificationError) as excinfo:
            Verifier.verify_call_count(mock_spy, "test_method", 2)

        assert "Method test_method was called 1 times, expected 2 times" in str(excinfo.value)

    def test_verify_any_call_success(self):
        """Test verify_any_call when the method was called at least once with the given arguments."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("test_method", (1, 2), {"a": "b"}), MethodCall("test_method", (3, 4), {"c": "d"})])

        # Act & Assert
        assert Verifier.verify_any_call(mock_spy, "test_method", 1, 2, a="b") is True

    def test_verify_any_call_failure(self):
        """Test verify_any_call when the method was not called with the given arguments."""
        # Arrange
        mock_spy = MockSpyObject([MethodCall("test_method", (1, 2), {"a": "b"})])

        # Act & Assert
        with pytest.raises(VerificationError) as excinfo:
            Verifier.verify_any_call(mock_spy, "test_method", 1, 2, a="c")

        assert "Method test_method was not called with arguments" in str(excinfo.value)

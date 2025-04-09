"""
Tests for the MethodCall class.

This module tests the functionality of the MethodCall class in crudclient.testing.spy.method_call.
"""


from crudclient.testing.spy.method_call import MethodCall


class TestMethodCall:
    """Tests for the MethodCall class."""

    def test_init_basic(self):
        """Test initialization of MethodCall with basic parameters."""
        # Arrange & Act
        call = MethodCall(
            method_name="test_method",
            args=(1, 2),
            kwargs={"a": "b"},
            return_value="result"
        )

        # Assert
        assert call.method_name == "test_method"
        assert call.args == (1, 2)
        assert call.kwargs == {"a": "b"}
        assert call.return_value == "result"
        assert call.exception is None

    def test_init_with_exception(self):
        """Test initialization of MethodCall with an exception."""
        # Arrange
        exception = ValueError("Test error")

        # Act
        call = MethodCall(
            method_name="test_method",
            args=(1, 2),
            kwargs={"a": "b"},
            exception=exception
        )

        # Assert
        assert call.method_name == "test_method"
        assert call.args == (1, 2)
        assert call.kwargs == {"a": "b"}
        assert call.return_value is None
        assert call.exception is exception

    def test_repr_with_return_value(self):
        """Test string representation of MethodCall with a return value."""
        # Arrange
        call = MethodCall(
            method_name="test_method",
            args=(1, "string"),
            kwargs={"a": "b"},
            return_value={"result": "value"}
        )

        # Act
        result = repr(call)

        # Assert
        assert "test_method" in result
        assert "1, 'string'" in result
        assert "a='b'" in result
        assert "returned" in result
        assert "{'result': 'value'}" in result

    def test_repr_with_exception(self):
        """Test string representation of MethodCall with an exception."""
        # Arrange
        exception = ValueError("Test error")
        call = MethodCall(
            method_name="test_method",
            args=(1, "string"),
            kwargs={"a": "b"},
            exception=exception
        )

        # Act
        result = repr(call)

        # Assert
        assert "test_method" in result
        assert "1, 'string'" in result
        assert "a='b'" in result
        assert "raised ValueError" in result
        assert "Test error" in result

    def test_repr_with_no_return_or_exception(self):
        """Test string representation of MethodCall with no return value or exception."""
        # Arrange
        call = MethodCall(
            method_name="test_method",
            args=(1, "string"),
            kwargs={"a": "b"}
        )

        # Act
        result = repr(call)

        # Assert
        assert "test_method" in result
        assert "1, 'string'" in result
        assert "a='b'" in result
        assert "returned" not in result
        assert "raised" not in result

    def test_repr_with_empty_args(self):
        """Test string representation of MethodCall with empty args."""
        # Arrange
        call = MethodCall(
            method_name="test_method",
            args=(),
            kwargs={"a": "b"},
            return_value="result"
        )

        # Act
        result = repr(call)

        # Assert
        assert "test_method" in result
        assert "a='b'" in result
        assert "returned 'result'" in result

    def test_repr_with_empty_kwargs(self):
        """Test string representation of MethodCall with empty kwargs."""
        # Arrange
        call = MethodCall(
            method_name="test_method",
            args=(1, 2),
            kwargs={},
            return_value="result"
        )

        # Act
        result = repr(call)

        # Assert
        assert "test_method" in result
        assert "1, 2" in result
        assert "returned 'result'" in result

    def test_repr_with_empty_args_and_kwargs(self):
        """Test string representation of MethodCall with empty args and kwargs."""
        # Arrange
        call = MethodCall(
            method_name="test_method",
            args=(),
            kwargs={},
            return_value="result"
        )

        # Act
        result = repr(call)

        # Assert
        assert "test_method()" in result
        assert "returned 'result'" in result

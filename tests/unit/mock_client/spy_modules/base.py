"""
Base classes for spy implementations.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
class MethodCall:
    """
    Record of a method call.

    Attributes:
        method_name: Name of the method called
        args: Positional arguments
        kwargs: Keyword arguments
        result: Return value
        exception: Exception raised, if any
    """

    method_name: str
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    result: Optional[Any] = None
    exception: Optional[Exception] = None


class SpyBase:
    """
    Base class for spy implementations.

    This class provides common functionality for recording and verifying
    method calls.
    """

    def __init__(self):
        """Initialize the spy base."""
        self.calls: List[MethodCall] = []

    def _record_call(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        result: Optional[Any] = None,
        exception: Optional[Exception] = None
    ) -> None:
        """
        Record a method call.

        Args:
            method_name: Name of the method called
            args: Positional arguments
            kwargs: Keyword arguments
            result: Return value
            exception: Exception raised, if any
        """
        call = MethodCall(method_name, args, kwargs, result, exception)
        self.calls.append(call)

    def assert_called(self, method_name: str) -> None:
        """
        Assert that a method was called.

        Args:
            method_name: Name of the method

        Raises:
            AssertionError: If the method was not called
        """
        for call in self.calls:
            if call.method_name == method_name:
                return

        raise AssertionError(f"Method {method_name} was not called")

    def assert_not_called(self, method_name: str) -> None:
        """
        Assert that a method was not called.

        Args:
            method_name: Name of the method

        Raises:
            AssertionError: If the method was called
        """
        for call in self.calls:
            if call.method_name == method_name:
                raise AssertionError(f"Method {method_name} was called")

    def assert_called_with(
        self,
        method_name: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Assert that a method was called with specific arguments.

        Args:
            method_name: Name of the method
            *args: Expected positional arguments
            **kwargs: Expected keyword arguments

        Raises:
            AssertionError: If the method was not called with the expected arguments
        """
        for call in self.calls:
            if call.method_name == method_name:
                # Check positional arguments
                if len(args) > 0 and call.args != args:
                    continue

                # Check keyword arguments
                if kwargs and not all(
                    key in call.kwargs and call.kwargs[key] == value
                    for key, value in kwargs.items()
                ):
                    continue

                return

        args_str = ", ".join(str(arg) for arg in args)
        kwargs_str = ", ".join(f"{key}={value}" for key, value in kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        raise AssertionError(
            f"Method {method_name} was not called with arguments ({all_args})"
        )

    def assert_call_count(self, method_name: str, count: int) -> None:
        """
        Assert that a method was called a specific number of times.

        Args:
            method_name: Name of the method
            count: Expected number of calls

        Raises:
            AssertionError: If the method was not called the expected number of times
        """
        actual_count = sum(1 for call in self.calls if call.method_name == method_name)

        if actual_count != count:
            raise AssertionError(
                f"Method {method_name} was called {actual_count} times, "
                f"expected {count} times"
            )

    def get_calls(self, method_name: str) -> List[MethodCall]:
        """
        Get all calls to a specific method.

        Args:
            method_name: Name of the method

        Returns:
            List of method calls
        """
        return [call for call in self.calls if call.method_name == method_name]

    def clear_calls(self) -> None:
        """Clear all recorded calls."""
        self.calls = []

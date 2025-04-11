from typing import Any, Dict, List, Optional, Tuple

from .method_call import MethodCall

class SpyBase:
    """
    Base class for spy implementations.

    This class provides common functionality for recording and verifying
    method calls.
    """

    calls: List[MethodCall]

    def __init__(self) -> None:
        """Initialize the spy base."""
        ...

    def _record_call(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        return_value: Optional[Any] = None,
        exception: Optional[Exception] = None
    ) -> None:
        """
        Record a method call.

        Args:
            method_name: Name of the method called
            args: Positional arguments
            kwargs: Keyword arguments
            return_value: Return value
            exception: Exception raised, if any
        """
        ...

    def assert_called(self, method_name: str) -> None:
        """
        Assert that a method was called.

        Args:
            method_name: Name of the method

        Raises:
            AssertionError: If the method was not called
        """
        ...

    def assert_not_called(self, method_name: str) -> None:
        """
        Assert that a method was not called.

        Args:
            method_name: Name of the method

        Raises:
            AssertionError: If the method was called
        """
        ...

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
        ...

    def assert_call_count(self, method_name: str, count: int) -> None:
        """
        Assert that a method was called a specific number of times.

        Args:
            method_name: Name of the method
            count: Expected number of calls

        Raises:
            AssertionError: If the method was not called the expected number of times
        """
        ...

    def get_calls(self, method_name: str) -> List[MethodCall]:
        """
        Get all calls to a specific method.

        Args:
            method_name: Name of the method

        Returns:
            List of method calls
        """
        ...

    def clear_calls(self) -> None:
        """Clear all recorded calls."""
        ...

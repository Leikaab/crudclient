"""
Base components for the Test Spy pattern.

This module defines the foundational `SpyBase` class, which provides the core
functionality for recording method calls in test doubles.
"""

from typing import Any, Dict, List, Optional, Tuple

from .method_call import MethodCall

class SpyBase:
    """
    Base implementation for the **Test Spy pattern**.

    A Test Spy is a test double that records information about how it was called
    during test execution. This base class provides the core functionality for
    spies within the `crudclient` testing framework:
    - Recording method calls (arguments, return values, exceptions) via `_record_call`.
    - Storing recorded calls in the `calls` list.
    - Providing basic verification methods (e.g., `verify_called`, `verify_called_with`)
      to assert interactions directly on the spy instance.

    Concrete spy classes (e.g., `ClientSpy`, `ApiSpy`) should inherit from this
    base to implement specific interfaces while leveraging the call recording
    and verification infrastructure provided here.

    Note: While this base class includes verification methods, the dedicated
    `Verifier` class (`crudclient.testing.verification.Verifier`) offers a more
    decoupled approach for complex verification scenarios, potentially involving
    multiple spies.
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
        exception: Optional[Exception] = None,
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

    def _format_args_string(self, *args: Any, **kwargs: Any) -> str:
        """
        Format arguments as a string.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Formatted string representation of the arguments
        """
        ...

    def verify_called(self, method_name: str) -> None:
        """
        Verify that a method was called.

        Args:
            method_name: Name of the method

        Raises:
            SpyError: If the method was not called
        """
        ...

    def verify_not_called(self, method_name: str) -> None:
        """
        Verify that a method was not called.

        Args:
            method_name: Name of the method

        Raises:
            SpyError: If the method was called
        """
        ...

    def verify_called_with(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Verify that a method was called with specific arguments.

        Args:
            method_name: Name of the method
            *args: Expected positional arguments
            **kwargs: Expected keyword arguments

        Raises:
            SpyError: If the method was not called with the expected arguments
        """
        ...

    def verify_call_count(self, method_name: str, count: int) -> None:
        """
        Verify that a method was called a specific number of times.

        Args:
            method_name: Name of the method
            count: Expected number of calls

        Raises:
            SpyError: If the method was not called the expected number of times
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
    # Deprecated methods for backward compatibility
    def assert_called(self, method_name: str) -> None:
        """
        Assert that a method was called (deprecated, use verify_called instead).

        Args:
            method_name: Name of the method

        Raises:
            AssertionError: If the method was not called
        """
        ...

    def assert_not_called(self, method_name: str) -> None:
        """
        Assert that a method was not called (deprecated, use verify_not_called instead).

        Args:
            method_name: Name of the method

        Raises:
            AssertionError: If the method was called
        """
        ...

    def assert_called_with(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Assert that a method was called with specific arguments (deprecated, use verify_called_with instead).

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
        Assert that a method was called a specific number of times (deprecated, use verify_call_count instead).

        Args:
            method_name: Name of the method
            count: Expected number of calls

        Raises:
            AssertionError: If the method was not called the expected number of times
        """
        ...

from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Protocol

if TYPE_CHECKING:
    from .enhanced import CallRecord  # Avoid circular import


class SpyProtocol(Protocol):
    """
    Defines the protocol required by SpyAssertionsMixin.
    """
    _calls: List['CallRecord']
    _method_calls: Dict[str, List['CallRecord']]

    def was_called(self, method_name: str) -> bool: ...
    def was_called_with(self, method_name: str, *args: Any, **kwargs: Any) -> bool: ...
    def get_call_count(self, method_name: Optional[str] = None) -> int: ...
    def get_calls(self, method_name: Optional[str] = None) -> List['CallRecord']: ...


class SpyAssertionsMixin:
    """
    A mixin class providing assertion methods for spy objects.

    This mixin enhances classes that conform to the SpyProtocol with various
    assertion methods to verify interactions recorded by the spy.
    """

    def assert_called(self: SpyProtocol, method_name: str) -> None:
        """
        Asserts that the specified method was called at least once.

        Args:
            method_name: The name of the method to check.

        Raises:
            AssertionError: If the method was not called.
        """
        ...

    def assert_not_called(self: SpyProtocol, method_name: str) -> None:
        """
        Asserts that the specified method was never called.

        Args:
            method_name: The name of the method to check.

        Raises:
            AssertionError: If the method was called.
        """
        ...

    def assert_called_with(
        self: SpyProtocol,
        method_name: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Asserts that the specified method was called at least once with the exact
        arguments provided.

        Args:
            method_name: The name of the method to check.
            *args: The expected positional arguments.
            **kwargs: The expected keyword arguments.

        Raises:
            AssertionError: If the method was not called with the specified arguments.
        """
        ...

    def assert_called_once(self: SpyProtocol, method_name: str) -> None:
        """
        Asserts that the specified method was called exactly once.

        Args:
            method_name: The name of the method to check.

        Raises:
            AssertionError: If the method was called zero times or more than once.
        """
        ...

    def assert_called_times(self: SpyProtocol, method_name: str, count: int) -> None:
        """
        Asserts that the specified method was called exactly `count` times.

        Args:
            method_name: The name of the method to check.
            count: The expected number of calls.

        Raises:
            AssertionError: If the method was called a different number of times.
        """
        ...

    def assert_called_with_params_matching(
        self: SpyProtocol,
        method_name: str,
        param_matcher: Callable[[Dict[str, Any]], bool]
    ) -> None:
        """
        Asserts that the specified method was called at least once with parameters
        that satisfy the provided matcher function.

        The matcher function receives a dictionary containing both positional (keyed
        as 'arg0', 'arg1', etc.) and keyword arguments for each call.

        Args:
            method_name: The name of the method to check.
            param_matcher: A callable that takes a dictionary of parameters and
                           returns True if they match the criteria.

        Raises:
            AssertionError: If the method was not called or if no call satisfied
                          the `param_matcher`.
        """
        ...

    def assert_call_order(self: SpyProtocol, *method_names: str) -> None:
        """
        Asserts that the specified methods were called in the exact order given,
        considering the first call to each method.

        Args:
            *method_names: A sequence of method names representing the expected
                           call order.

        Raises:
            AssertionError: If any method was not called or if the first calls
                          occurred in a different order.
        """
        ...

    def assert_no_errors(self: SpyProtocol) -> None:
        """
        Asserts that no exceptions were recorded during any of the spied calls.

        Raises:
            AssertionError: If any call recorded an exception.
        """
        ...

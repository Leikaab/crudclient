"""
Verifier Pattern Implementation for Test Assertions on Spies/Mocks.

This module implements the **Verifier pattern** via the static methods on the
`Verifier` class. It provides a dedicated, consistent interface for making
assertions about interactions with test doubles (mocks, spies) used within the
`crudclient` testing framework or potentially standard `unittest.mock` objects.

**Benefits:**
- **Decoupling:** Separates assertion logic from the test double's implementation.
- **Readability:** Offers a clear, fluent API for common verification tasks.
- **Consistency:** Provides a uniform way to verify interactions across different
  types of spies (e.g., `ClientSpy`, `ApiSpy`, `AuthSpy`).

**Usage:**
The `Verifier` methods typically expect a `target` object that records its method
calls, often in an attribute like `method_calls` or `call_args_list` (compatible
with `unittest.mock.Mock` and the `SpyTarget` protocol).

Example:
    >>> from unittest.mock import Mock
    >>> mock_service = Mock()
    >>> mock_service.do_something("arg1", key="value")
    >>> # In a test:
    >>> Verifier.verify_called_once_with(mock_service, "do_something", "arg1", key="value")
    True
    >>> try:
    ...     Verifier.verify_not_called(mock_service, "do_something")
    ... except VerificationError as e:
    ...     print("Verification failed as expected") # doctest: +SKIP
    Verification failed as expected
"""

from typing import Any, Union

from typing_extensions import TypeAlias

from .exceptions import VerificationError
from .types import SpyTarget

class Verifier:
    """
    Provides static methods for verifying interactions with test doubles (Spies/Mocks).

    Implements the **Verifier pattern**, offering a decoupled and consistent way to
    assert how methods on a `target` object were called during a test. It inspects
    the call records (e.g., `method_calls`, `call_args_list`) assumed to exist on
    the `target` object.

    **Note on Return Values:** While methods return `True` on success, the primary
    indication of success is the *absence* of a `VerificationError`. The primary
    indication of failure is a raised `VerificationError`. Rely on catching or
    *not* catching `VerificationError` in tests, rather than the boolean return.
    """

    @staticmethod
    def verify_called_with(target: Union[SpyTarget, object], method_name: str, *args: Any, **kwargs: Any) -> bool:
        """
        Verify the **last call** to the method was made with the specified arguments.

        Checks only the arguments of the most recent call recorded for `method_name`.
        Use `verify_any_call` to check if *any* call matches the arguments.

        Args:
            target: The spy or mock object whose calls are being verified.
            method_name: The name of the method expected to have been called.
            *args: The exact positional arguments expected in the last call.
            **kwargs: The exact keyword arguments expected in the last call.

        Returns:
            True if the last call matches the arguments.

        Raises:
            VerificationError: If the method was never called, or if the last call
                               did not match the provided arguments.

        Example:
            >>> spy = Mock()
            >>> spy.send("msg1")
            >>> spy.send("msg2", priority=1)
            >>> Verifier.verify_called_with(spy, "send", "msg2", priority=1)
            True
            >>> # This would fail: Verifier.verify_called_with(spy, "send", "msg1")
        """
        ...

    @staticmethod
    def verify_called_once_with(target: Union[SpyTarget, object], method_name: str, *args: Any, **kwargs: Any) -> bool:
        """
        Verify the method was called **exactly once**, and with the specified arguments.

        Checks both the total call count (must be 1) and the arguments of that single call.

        Args:
            target: The spy or mock object.
            method_name: The name of the method.
            *args: The exact positional arguments expected in the single call.
            **kwargs: The exact keyword arguments expected in the single call.

        Returns:
            True if the method was called exactly once with the specified arguments.

        Raises:
            VerificationError: If the method was not called exactly once, or if the
                               arguments of the single call do not match.

        Example:
            >>> spy = Mock()
            >>> spy.process("data")
            >>> Verifier.verify_called_once_with(spy, "process", "data")
            True
            >>> # This would fail: spy.process("other_data"); Verifier.verify_called_once_with(spy, "process", "data")
            >>> # This would also fail: Verifier.verify_called_once_with(spy, "process", "wrong_data")
        """
        ...

    @staticmethod
    def verify_not_called(target: Union[SpyTarget, object], method_name: str) -> bool:
        """
        Verify the specified method was **never called**.

        Args:
            target: The spy or mock object.
            method_name: The name of the method that should not have been called.

        Returns:
            True if the method was never called.

        Raises:
            VerificationError: If the method was called one or more times.

        Example:
            >>> spy = Mock()
            >>> spy.setup()
            >>> Verifier.verify_not_called(spy, "execute")
            True
            >>> # This would fail: spy.execute(); Verifier.verify_not_called(spy, "execute")
        """
        ...

    @staticmethod
    def verify_call_count(target: Union[SpyTarget, object], method_name: str, count: int) -> bool:
        """
        Verify the method was called exactly `count` times, regardless of arguments.

        Args:
            target: The spy or mock object.
            method_name: The name of the method whose calls are being counted.
            count: The exact expected number of calls.

        Returns:
            True if the method was called exactly `count` times.

        Raises:
            VerificationError: If the actual call count does not match `count`.

        Example:
            >>> spy = Mock()
            >>> spy.ping()
            >>> spy.ping()
            >>> Verifier.verify_call_count(spy, "ping", 2)
            True
            >>> Verifier.verify_call_count(spy, "other_method", 0)
            True
            >>> # This would fail: Verifier.verify_call_count(spy, "ping", 1)
        """
        ...

    @staticmethod
    def verify_any_call(target: Union[SpyTarget, object], method_name: str, *args: Any, **kwargs: Any) -> bool:
        """
        Verify the method was called **at least once** with the specified arguments.

        Checks the entire call history for `method_name` to see if *any* recorded
        call matches the provided `args` and `kwargs`.

        Args:
            target: The spy or mock object.
            method_name: The name of the method.
            *args: The exact positional arguments expected in at least one call.
            **kwargs: The exact keyword arguments expected in at least one call.

        Returns:
            True if at least one call matches the arguments.

        Raises:
            VerificationError: If the method was never called, or if no call
                               matches the provided arguments.

        Example:
            >>> spy = Mock()
            >>> spy.log("info", "Starting")
            >>> spy.log("error", "Failed")
            >>> spy.log("info", "Finished")
            >>> Verifier.verify_any_call(spy, "log", "error", "Failed") # Matches the second call
            True
            >>> Verifier.verify_any_call(spy, "log", "info", "Starting") # Matches the first call
            True
            >>> # This would fail: Verifier.verify_any_call(spy, "log", "debug", "Message")
        """
        ...

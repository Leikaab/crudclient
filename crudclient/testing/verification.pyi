"""
Verifier Pattern Implementation for Test Assertions.

This module implements the **Verifier pattern**, providing a dedicated interface
(`Verifier` class) for making assertions about interactions with test doubles
(mocks, spies) used within the `crudclient` testing framework.

It centralizes the logic for checking method calls, call counts, and arguments,
decoupling the verification step from the test doubles themselves. This promotes
cleaner and more readable test code by offering a fluent API for common
verification tasks across different types of spies (e.g., `ClientSpy`,
`AuthSpy`).
"""

from typing import Any, Union

from typing_extensions import TypeAlias

from .exceptions import VerificationError
from .types import SpyTarget


class Verifier:
    """
    Implements the **Verifier pattern** for asserting interactions with test doubles.

    This class provides static methods that act as the primary interface for
    verifying how test doubles (specifically objects conforming to the `SpyTarget`
    protocol or similar mock objects) were used during a test. It allows checking
    if methods were called, how many times, and with what arguments.

    Using a dedicated Verifier class separates the assertion logic from the
    mock/spy object's primary responsibilities (simulating behavior, recording calls),
    leading to a clearer separation of concerns in tests.
    """

    @staticmethod
    def verify_called_with(target: Union[SpyTarget, object], method_name: str, *args: Any, **kwargs: Any) -> bool:
        """
        Verify that the given method was called with the given arguments.

        Args:
            target: The object that was called.
            method_name: The name of the method that was called.
            *args: The positional arguments that should have been passed.
            **kwargs: The keyword arguments that should have been passed.

        Returns:
            True if the method was called with the given arguments, False otherwise.

        Raises:
            VerificationError: If the verification fails.
        """
        ...

    @staticmethod
    def verify_called_once_with(target: Union[SpyTarget, object], method_name: str, *args: Any, **kwargs: Any) -> bool:
        """
        Verify that the given method was called exactly once with the given arguments.

        Args:
            target: The object that was called.
            method_name: The name of the method that was called.
            *args: The positional arguments that should have been passed.
            **kwargs: The keyword arguments that should have been passed.

        Returns:
            True if the method was called exactly once with the given arguments, False otherwise.

        Raises:
            VerificationError: If the verification fails.
        """
        ...

    @staticmethod
    def verify_not_called(target: Union[SpyTarget, object], method_name: str) -> bool:
        """
        Verify that the given method was not called.

        Args:
            target: The object that was called.
            method_name: The name of the method that was called.

        Returns:
            True if the method was not called, False otherwise.

        Raises:
            VerificationError: If the verification fails.
        """
        ...

    @staticmethod
    def verify_call_count(target: Union[SpyTarget, object], method_name: str, count: int) -> bool:
        """
        Verify that the given method was called exactly count times.

        Args:
            target: The object that was called.
            method_name: The name of the method that was called.
            count: The expected number of calls.

        Returns:
            True if the method was called exactly count times, False otherwise.

        Raises:
            VerificationError: If the verification fails.
        """
        ...

    @staticmethod
    def verify_any_call(target: Union[SpyTarget, object], method_name: str, *args: Any, **kwargs: Any) -> bool:
        """
        Verify that the given method was called at least once with the given arguments.

        Args:
            target: The object that was called.
            method_name: The name of the method that was called.
            *args: The positional arguments that should have been passed.
            **kwargs: The keyword arguments that should have been passed.

        Returns:
            True if the method was called at least once with the given arguments, False otherwise.

        Raises:
            VerificationError: If the verification fails.
        """
        ...

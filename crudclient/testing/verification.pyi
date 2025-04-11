"""
Verification utilities for the crudclient testing framework.

This module provides high-level verification functions and classes that might
coordinate verification across different spies (client, auth, crud).
"""

from typing import Any, Union

from typing_extensions import TypeAlias

from .exceptions import VerificationError
from .types import SpyTarget


class Verifier:
    """
    High-level verification utilities for the testing framework.

    This class provides methods to verify interactions with mock objects
    across different components of the testing framework.
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

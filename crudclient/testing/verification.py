"""
Verification utilities for the crudclient testing framework.

This module provides high-level verification functions and classes that might
coordinate verification across different spies (client, auth, crud).
"""

from typing import Any, Dict, List, Optional, Pattern, Union
import re

from .exceptions import VerificationError
from .types import CallRecord, SpyTarget


class Verifier:
    """
    High-level verification utilities for the testing framework.

    This class provides methods to verify interactions with mock objects
    across different components of the testing framework.
    """

    @staticmethod
    def verify_called_with(
        target: SpyTarget,
        method_name: str,
        *args: Any,
        **kwargs: Any
    ) -> bool:
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
        if not hasattr(target, 'calls'):
            raise VerificationError(f"Target object {target} does not have 'calls' attribute")

        for call in target.calls:
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

                return True

        args_str = ", ".join(str(arg) for arg in args)
        kwargs_str = ", ".join(f"{key}={value}" for key, value in kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        raise VerificationError(
            f"Method {method_name} was not called with arguments ({all_args})"
        )

    @staticmethod
    def verify_called_once_with(
        target: SpyTarget,
        method_name: str,
        *args: Any,
        **kwargs: Any
    ) -> bool:
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
        if not hasattr(target, 'calls'):
            raise VerificationError(f"Target object {target} does not have 'calls' attribute")

        matching_calls = []

        for call in target.calls:
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

                matching_calls.append(call)

        if len(matching_calls) == 1:
            return True

        args_str = ", ".join(str(arg) for arg in args)
        kwargs_str = ", ".join(f"{key}={value}" for key, value in kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        if len(matching_calls) == 0:
            raise VerificationError(
                f"Method {method_name} was not called with arguments ({all_args})"
            )
        else:
            raise VerificationError(
                f"Method {method_name} was called {len(matching_calls)} times with arguments ({all_args}), "
                f"expected exactly once"
            )

    @staticmethod
    def verify_not_called(
        target: SpyTarget,
        method_name: str
    ) -> bool:
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
        if not hasattr(target, 'calls'):
            raise VerificationError(f"Target object {target} does not have 'calls' attribute")

        for call in target.calls:
            if call.method_name == method_name:
                raise VerificationError(f"Method {method_name} was called")

        return True

    @staticmethod
    def verify_call_count(
        target: SpyTarget,
        method_name: str,
        count: int
    ) -> bool:
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
        if not hasattr(target, 'calls'):
            raise VerificationError(f"Target object {target} does not have 'calls' attribute")

        actual_count = sum(1 for call in target.calls if call.method_name == method_name)

        if actual_count != count:
            raise VerificationError(
                f"Method {method_name} was called {actual_count} times, "
                f"expected {count} times"
            )

        return True

    @staticmethod
    def verify_any_call(
        target: SpyTarget,
        method_name: str,
        *args: Any,
        **kwargs: Any
    ) -> bool:
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
        if not hasattr(target, 'calls'):
            raise VerificationError(f"Target object {target} does not have 'calls' attribute")

        for call in target.calls:
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

                return True

        args_str = ", ".join(str(arg) for arg in args)
        kwargs_str = ", ".join(f"{key}={value}" for key, value in kwargs.items())
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        raise VerificationError(
            f"Method {method_name} was not called with arguments ({all_args})"
        )

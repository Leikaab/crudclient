"""
Enhanced spy components for detailed interaction recording and verification.

This module provides advanced spy classes and utilities that build upon the basic
spy functionality, offering features like timestamping, duration tracking, stack
trace capture, and more sophisticated assertion capabilities through mixins.
"""

import inspect
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

from .method_call import MethodCall
from .spy_assertions import SpyAssertionsMixin

class CallRecord(MethodCall):
    """
    Represents a single recorded method call with enhanced details.

    Inherits basic call information (method name, args, kwargs, result, exception)
    from MethodCall and adds timestamp, duration, stack trace, and caller info.
    """

    timestamp: float
    duration: Optional[float]
    result: Any  # Overrides return_value from MethodCall
    stack_trace: List[str]
    caller_info: Optional[Dict[str, Any]]

    def __init__(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        timestamp: float,
        duration: Optional[float] = None,
        result: Any = None,
        exception: Optional[Exception] = None,
    ) -> None:
        """
        Initializes an enhanced record of a method call.

        Args:
            method_name: The name of the method that was called.
            args: Positional arguments passed to the method.
            kwargs: Keyword arguments passed to the method.
            timestamp: The time the call was recorded (via time.time()).
            duration: The execution duration of the original method call in seconds.
            result: The value returned by the method call.
            exception: The exception raised by the method call, if any.
        """
        ...

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the call record."""
        ...

class EnhancedSpyBase(SpyAssertionsMixin):
    """
    Base class for enhanced spies, providing call recording and retrieval logic.

    Includes methods for recording calls, retrieving call records, checking call counts,
    and basic call verification. Assertion methods are provided via SpyAssertionsMixin.
    """

    _calls: List[CallRecord]  # Keep for type checking mixin, though technically private
    _method_calls: Dict[str, List[CallRecord]]  # Keep for type checking mixin

    def __init__(self) -> None:
        """Initializes the spy with empty call lists."""
        ...
    # _record_call is intentionally omitted as it's protected

    def get_calls(self, method_name: Optional[str] = None) -> List[CallRecord]:
        """
        Retrieves recorded calls.

        Args:
            method_name: If provided, returns only calls to this specific method.
                         Otherwise, returns all recorded calls in order.

        Returns:
            A list of CallRecord objects.
        """
        ...

    def get_call_count(self, method_name: Optional[str] = None) -> int:
        """
        Gets the number of times a method (or any method) was called.

        Args:
            method_name: If provided, returns the call count for this specific method.
                         Otherwise, returns the total number of recorded calls.

        Returns:
            The number of calls.
        """
        ...

    def was_called(self, method_name: str) -> bool:
        """
        Checks if the specified method was called at least once.

        Args:
            method_name: The name of the method to check.

        Returns:
            True if the method was called, False otherwise.
        """
        ...

    def was_called_with(self, method_name: str, *args: Any, **kwargs: Any) -> bool:
        """
        Checks if the specified method was called at least once with the exact
        arguments provided.

        Args:
            method_name: The name of the method to check.
            *args: The expected positional arguments.
            **kwargs: The expected keyword arguments.

        Returns:
            True if a matching call was found, False otherwise.
        """
        ...
    # Assertion methods like assert_called, assert_called_with, etc.,
    # are inherited from SpyAssertionsMixin and defined in its stub.

    def reset(self) -> None:
        """Clears all recorded calls."""
        ...

class MethodSpy:
    """
    Wraps a single method to spy on its calls, delegating to an EnhancedSpyBase.
    """

    original_method: Callable
    spy: EnhancedSpyBase
    method_name: str
    record_only: bool

    def __init__(self, original_method: Callable, spy: EnhancedSpyBase, method_name: str, record_only: bool = False) -> None:
        """
        Initializes a spy for a specific method.

        Args:
            original_method: The original method to wrap and potentially call.
            spy: The EnhancedSpyBase instance to record calls to.
            method_name: The name of the method being spied on.
            record_only: If True, the original method is not called, only the
                         interaction is recorded. Defaults to False.
        """
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Handles calls to the spied method, records them, and optionally calls
        the original method.
        """
        ...

class ClassSpy(EnhancedSpyBase):
    """
    Spies on methods of a target object instance.

    Creates MethodSpy wrappers for specified (or all public) methods of the
    target object. Delegates attribute access for non-spied attributes to the
    target object.
    """

    target_object: Any
    record_only: bool

    def __init__(self, target_object: Any, methods: Optional[List[str]] = None, record_only: bool = False) -> None:
        """
        Initializes a spy for an object instance.

        Args:
            target_object: The object instance whose methods will be spied on.
            methods: An optional list of method names to spy on. If None, all
                     public methods (not starting with '_') are spied on.
            record_only: If True, the original methods are not called, only the
                         interactions are recorded. Defaults to False.
        """
        ...

    def __getattr__(self, name: str) -> Any:
        """
        Delegates attribute access to the target object if the attribute is not
        a spied method.
        """
        ...

class FunctionSpy(EnhancedSpyBase):
    """
    Spies on calls to a standalone function.
    """

    target_function: Callable
    record_only: bool
    method_name: str  # Stores the function name

    def __init__(self, target_function: Callable, record_only: bool = False) -> None:
        """
        Initializes a spy for a standalone function.

        Args:
            target_function: The function to spy on.
            record_only: If True, the original function is not called, only the
                         interaction is recorded. Defaults to False.
        """
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Handles calls to the spied function, records them, and optionally calls
        the original function.
        """
        ...

class EnhancedSpyFactory:
    """
    Provides static methods to conveniently create different types of enhanced spies.
    """

    @staticmethod
    def create_class_spy(target_object: Any, methods: Optional[List[str]] = None, record_only: bool = False) -> ClassSpy:
        """
        Factory method to create a ClassSpy.

        Args:
            target_object: The object instance to spy on.
            methods: Optional list of method names to spy on. Defaults to all public methods.
            record_only: If True, only record calls without executing original methods.

        Returns:
            A configured ClassSpy instance.
        """
        ...

    @staticmethod
    def create_function_spy(target_function: Callable, record_only: bool = False) -> FunctionSpy:
        """
        Factory method to create a FunctionSpy.

        Args:
            target_function: The function to spy on.
            record_only: If True, only record calls without executing the original function.

        Returns:
            A configured FunctionSpy instance.
        """
        ...

    @staticmethod
    def patch_method(target_object: Any, method_name: str, record_only: bool = False) -> FunctionSpy:
        """
        Patches a method on an object with a FunctionSpy.

        Replaces the specified method on the target object with a spy that records
        calls and optionally calls the original method.

        Args:
            target_object: The object instance whose method will be patched.
            method_name: The name of the method to patch.
            record_only: If True, only record calls without executing the original method.

        Returns:
            The FunctionSpy instance used for patching.
        """
        ...

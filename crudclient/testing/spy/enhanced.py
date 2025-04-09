"""
Enhanced spy implementations for verification-focused testing.

This module provides sophisticated spy implementations that record detailed information
about method calls, including call order, parameters, timing, and more. These enhanced
spy implementations extend the basic spy functionality with additional features for
more comprehensive testing and verification.

The enhanced spy components can be used to:
- Record detailed information about method calls
- Verify call sequences and timing
- Create spies for classes and functions
- Perform sophisticated verification of interactions
"""

import inspect
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union

from .method_call import MethodCall


class CallRecord(MethodCall):
    """
    Records detailed information about a method call with enhanced metadata.

    This class extends the basic MethodCall with additional information such as
    timestamps, duration, stack traces, and caller information, enabling more
    sophisticated verification in tests.

    Attributes:
        method_name: Name of the called method
        args: Positional arguments
        kwargs: Keyword arguments
        timestamp: Time when the call was made
        duration: Duration of the call in seconds
        result: Return value of the call
        exception: Exception raised by the call, if any
        stack_trace: Stack trace at the time of the call
        caller_info: Information about the caller
    """

    def __init__(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        timestamp: float,
        duration: Optional[float] = None,
        result: Any = None,
        exception: Optional[Exception] = None
    ):
        """
        Initialize a call record with enhanced metadata.

        Args:
            method_name: Name of the called method
            args: Positional arguments
            kwargs: Keyword arguments
            timestamp: Time when the call was made
            duration: Duration of the call in seconds
            result: Return value of the call
            exception: Exception raised by the call, if any
        """
        # Initialize the base MethodCall with the common attributes
        super().__init__(method_name, args, kwargs, result, exception)

        # Add enhanced attributes
        self.timestamp = timestamp
        self.duration = duration

        # Rename return_value to result for consistency with the enhanced spy implementation
        self.result = self.return_value
        delattr(self, 'return_value')

        # Capture stack trace and caller info
        stack = inspect.stack()
        self.stack_trace = [
            f"{frame.filename}:{frame.lineno} in {frame.function}"
            for frame in stack[2:]  # Skip this method and the spy method
        ]

        # Get caller info (the first frame that's not in this file)
        self.caller_info = None
        for frame in stack[2:]:
            if not frame.filename.endswith('enhanced.py'):
                self.caller_info = {
                    'filename': frame.filename,
                    'lineno': frame.lineno,
                    'function': frame.function,
                    'code_context': frame.code_context[0].strip() if frame.code_context else None
                }
                break

    def __repr__(self) -> str:
        """Return string representation of the call record with enhanced information."""
        args_str = ', '.join([repr(arg) for arg in self.args])
        kwargs_str = ', '.join([f"{k}={repr(v)}" for k, v in self.kwargs.items()])
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))

        timestamp_str = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S.%f')

        if self.exception:
            result_str = f"raised {type(self.exception).__name__}: {self.exception}"
        else:
            result_str = f"returned {repr(self.result)}"

        duration_str = f" (took {self.duration:.6f}s)" if self.duration is not None else ""

        return f"{self.method_name}({all_args}) {result_str}{duration_str} at {timestamp_str}"


class EnhancedSpyBase:
    """
    Base class for enhanced spy implementations.

    This class provides comprehensive functionality for recording and verifying method calls,
    including detailed call records, sophisticated verification methods, and support for
    call sequences and timing.
    """

    def __init__(self):
        """Initialize the enhanced spy base."""
        self._calls: List[CallRecord] = []
        self._method_calls: Dict[str, List[CallRecord]] = {}

    def _record_call(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        result: Any = None,
        exception: Optional[Exception] = None,
        duration: Optional[float] = None
    ) -> None:
        """
        Record a method call with enhanced metadata.

        Args:
            method_name: Name of the called method
            args: Positional arguments
            kwargs: Keyword arguments
            result: Return value of the call
            exception: Exception raised by the call, if any
            duration: Duration of the call in seconds
        """
        timestamp = time.time()

        record = CallRecord(
            method_name=method_name,
            args=args,
            kwargs=kwargs,
            timestamp=timestamp,
            duration=duration,
            result=result,
            exception=exception
        )

        self._calls.append(record)

        if method_name not in self._method_calls:
            self._method_calls[method_name] = []

        self._method_calls[method_name].append(record)

    def get_calls(self, method_name: Optional[str] = None) -> List[CallRecord]:
        """
        Get all recorded calls, optionally filtered by method name.

        Args:
            method_name: Optional method name to filter by

        Returns:
            List of call records
        """
        if method_name is None:
            return self._calls

        return self._method_calls.get(method_name, [])

    def get_call_count(self, method_name: Optional[str] = None) -> int:
        """
        Get the number of recorded calls, optionally filtered by method name.

        Args:
            method_name: Optional method name to filter by

        Returns:
            Number of calls
        """
        return len(self.get_calls(method_name))

    def was_called(self, method_name: str) -> bool:
        """
        Check if a method was called.

        Args:
            method_name: Method name

        Returns:
            True if the method was called, False otherwise
        """
        return method_name in self._method_calls and len(self._method_calls[method_name]) > 0

    def was_called_with(
        self,
        method_name: str,
        *args: Any,
        **kwargs: Any
    ) -> bool:
        """
        Check if a method was called with specific arguments.

        Args:
            method_name: Method name
            *args: Expected positional arguments
            **kwargs: Expected keyword arguments

        Returns:
            True if the method was called with the specified arguments, False otherwise
        """
        if not self.was_called(method_name):
            return False

        for call in self._method_calls[method_name]:
            # Check positional arguments
            if len(call.args) != len(args):
                continue

            args_match = all(a == b for a, b in zip(call.args, args))
            if not args_match:
                continue

            # Check keyword arguments
            kwargs_match = True
            for key, value in kwargs.items():
                if key not in call.kwargs or call.kwargs[key] != value:
                    kwargs_match = False
                    break

            if kwargs_match:
                return True

        return False

    def assert_called(self, method_name: str) -> None:
        """
        Assert that a method was called.

        Args:
            method_name: Method name

        Raises:
            AssertionError: If the method was not called
        """
        assert self.was_called(method_name), f"Method {method_name} was not called"

    def assert_not_called(self, method_name: str) -> None:
        """
        Assert that a method was not called.

        Args:
            method_name: Method name

        Raises:
            AssertionError: If the method was called
        """
        assert not self.was_called(method_name), f"Method {method_name} was called"

    def assert_called_with(
        self,
        method_name: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Assert that a method was called with specific arguments.

        Args:
            method_name: Method name
            *args: Expected positional arguments
            **kwargs: Expected keyword arguments

        Raises:
            AssertionError: If the method was not called with the specified arguments
        """
        assert self.was_called_with(method_name, *args, **kwargs), (
            f"Method {method_name} was not called with args={args}, kwargs={kwargs}"
        )

    def assert_called_once(self, method_name: str) -> None:
        """
        Assert that a method was called exactly once.

        Args:
            method_name: Method name

        Raises:
            AssertionError: If the method was not called exactly once
        """
        call_count = self.get_call_count(method_name)
        assert call_count == 1, f"Method {method_name} was called {call_count} times, expected 1"

    def assert_called_times(self, method_name: str, count: int) -> None:
        """
        Assert that a method was called a specific number of times.

        Args:
            method_name: Method name
            count: Expected number of calls

        Raises:
            AssertionError: If the method was not called the specified number of times
        """
        call_count = self.get_call_count(method_name)
        assert call_count == count, f"Method {method_name} was called {call_count} times, expected {count}"

    def assert_called_with_params_matching(
        self,
        method_name: str,
        param_matcher: Callable[[Dict[str, Any]], bool]
    ) -> None:
        """
        Assert that a method was called with parameters matching a predicate.

        This method allows for more sophisticated verification of method calls by
        providing a custom matcher function that can check for complex conditions.

        Args:
            method_name: Method name
            param_matcher: Function that takes a dict of all parameters and returns True if they match

        Raises:
            AssertionError: If the method was not called with matching parameters
        """
        if not self.was_called(method_name):
            raise AssertionError(f"Method {method_name} was not called")

        for call in self._method_calls[method_name]:
            # Combine args and kwargs into a single dict
            params = {}

            # Add positional args with their index as key
            for i, arg in enumerate(call.args):
                params[f"arg{i}"] = arg

            # Add keyword args
            params.update(call.kwargs)

            if param_matcher(params):
                return

        raise AssertionError(f"Method {method_name} was not called with matching parameters")

    def assert_call_order(self, *method_names: str) -> None:
        """
        Assert that methods were called in a specific order.

        This method verifies that the specified methods were called in the exact
        order provided, which is useful for testing workflows and sequences.

        Args:
            *method_names: Method names in expected order

        Raises:
            AssertionError: If the methods were not called in the specified order
        """
        # Check that all methods were called
        for method_name in method_names:
            if not self.was_called(method_name):
                raise AssertionError(f"Method {method_name} was not called")

        # Check the order
        last_index = -1
        for method_name in method_names:
            # Find the first call to this method
            for i, call in enumerate(self._calls):
                if call.method_name == method_name:
                    if i <= last_index:
                        raise AssertionError(
                            f"Method {method_name} was called out of order"
                        )
                    last_index = i
                    break

    def assert_no_errors(self) -> None:
        """
        Assert that no methods raised exceptions.

        This method verifies that none of the recorded method calls resulted in
        exceptions, which is useful for ensuring that the code under test executed
        without errors.

        Raises:
            AssertionError: If any method raised an exception
        """
        for call in self._calls:
            if call.exception is not None:
                raise AssertionError(
                    f"Method {call.method_name} raised an exception: {call.exception}"
                )

    def reset(self) -> None:
        """Reset the spy, clearing all recorded calls."""
        self._calls = []
        self._method_calls = {}


class MethodSpy:
    """
    Spy for a single method.

    This class wraps a method and records calls to it, providing detailed
    information about each call for later verification.
    """

    def __init__(
        self,
        original_method: Callable,
        spy: EnhancedSpyBase,
        method_name: str,
        record_only: bool = False
    ):
        """
        Initialize the method spy.

        Args:
            original_method: Original method to spy on
            spy: Spy instance to record calls
            method_name: Name of the method
            record_only: Whether to only record calls without executing the original method
        """
        self.original_method = original_method
        self.spy = spy
        self.method_name = method_name
        self.record_only = record_only

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Call the method and record the call.

        This method intercepts calls to the original method, records detailed
        information about the call, and optionally executes the original method.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of the original method

        Raises:
            Exception: Any exception raised by the original method
        """
        start_time = time.time()
        result = None
        exception = None

        try:
            if not self.record_only:
                result = self.original_method(*args, **kwargs)
            return result
        except Exception as e:
            exception = e
            raise
        finally:
            duration = time.time() - start_time
            self.spy._record_call(
                method_name=self.method_name,
                args=args,
                kwargs=kwargs,
                result=result,
                exception=exception,
                duration=duration
            )


class ClassSpy(EnhancedSpyBase):
    """
    Spy for a class.

    This class wraps an object and records calls to its methods, providing
    detailed information about each call for later verification.
    """

    def __init__(
        self,
        target_object: Any,
        methods: Optional[List[str]] = None,
        record_only: bool = False
    ):
        """
        Initialize the class spy.

        Args:
            target_object: Object to spy on
            methods: Optional list of method names to spy on (default: all public methods)
            record_only: Whether to only record calls without executing the original methods
        """
        super().__init__()
        self.target_object = target_object
        self.record_only = record_only

        # If no methods are specified, spy on all public methods
        if methods is None:
            methods = [
                name for name in dir(target_object)
                if callable(getattr(target_object, name)) and not name.startswith('_')
            ]

        # Wrap each method with a spy
        for method_name in methods:
            original_method = getattr(target_object, method_name)
            if callable(original_method):
                spy_method = MethodSpy(
                    original_method=original_method,
                    spy=self,
                    method_name=method_name,
                    record_only=record_only
                )
                setattr(self, method_name, spy_method)

    def __getattr__(self, name: str) -> Any:
        """
        Get an attribute from the target object.

        This method delegates attribute access to the target object for
        attributes that are not spied methods.

        Args:
            name: Attribute name

        Returns:
            Attribute value

        Raises:
            AttributeError: If the attribute does not exist
        """
        # If the attribute is not a spied method, delegate to the target object
        return getattr(self.target_object, name)


class FunctionSpy(EnhancedSpyBase):
    """
    Spy for a function.

    This class wraps a function and records calls to it, providing detailed
    information about each call for later verification.
    """

    def __init__(
        self,
        target_function: Callable,
        record_only: bool = False
    ):
        """
        Initialize the function spy.

        Args:
            target_function: Function to spy on
            record_only: Whether to only record calls without executing the original function
        """
        super().__init__()
        self.target_function = target_function
        self.record_only = record_only

        # Get the function name
        self.method_name = target_function.__name__

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """
        Call the function and record the call.

        This method intercepts calls to the original function, records detailed
        information about the call, and optionally executes the original function.

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Result of the original function

        Raises:
            Exception: Any exception raised by the original function
        """
        start_time = time.time()
        result = None
        exception = None

        try:
            if not self.record_only:
                result = self.target_function(*args, **kwargs)
            return result
        except Exception as e:
            exception = e
            raise
        finally:
            duration = time.time() - start_time
            self._record_call(
                method_name=self.method_name,
                args=args,
                kwargs=kwargs,
                result=result,
                exception=exception,
                duration=duration
            )


class EnhancedSpyFactory:
    """
    Factory for creating enhanced spy implementations.

    This class provides static methods for creating various types of spies,
    making it easy to instrument code for testing and verification.
    """

    @staticmethod
    def create_class_spy(
        target_object: Any,
        methods: Optional[List[str]] = None,
        record_only: bool = False
    ) -> ClassSpy:
        """
        Create a spy for a class.

        Args:
            target_object: Object to spy on
            methods: Optional list of method names to spy on (default: all public methods)
            record_only: Whether to only record calls without executing the original methods

        Returns:
            Class spy
        """
        return ClassSpy(target_object, methods, record_only)

    @staticmethod
    def create_function_spy(
        target_function: Callable,
        record_only: bool = False
    ) -> FunctionSpy:
        """
        Create a spy for a function.

        Args:
            target_function: Function to spy on
            record_only: Whether to only record calls without executing the original function

        Returns:
            Function spy
        """
        return FunctionSpy(target_function, record_only)

    @staticmethod
    def patch_method(
        target_object: Any,
        method_name: str,
        record_only: bool = False
    ) -> FunctionSpy:
        """
        Patch a method with a spy.

        This method replaces a method on an object with a spy, allowing for
        detailed recording and verification of calls to that method.

        Args:
            target_object: Object whose method to patch
            method_name: Name of the method to patch
            record_only: Whether to only record calls without executing the original method

        Returns:
            Function spy
        """
        original_method = getattr(target_object, method_name)
        spy = FunctionSpy(original_method, record_only)
        setattr(target_object, method_name, spy)
        return spy


# Helper functions for common verification patterns

def verify_call_sequence(spy: EnhancedSpyBase, *method_names: str) -> None:
    """
    Verify that methods were called in a specific sequence.

    Args:
        spy: Spy instance
        *method_names: Method names in expected order

    Raises:
        AssertionError: If the methods were not called in the specified order
    """
    spy.assert_call_order(*method_names)


def verify_no_unexpected_calls(
    spy: EnhancedSpyBase,
    expected_methods: List[str]
) -> None:
    """
    Verify that no unexpected methods were called.

    This function checks that only the specified methods were called on the spy,
    which is useful for ensuring that the code under test only interacts with
    the expected parts of the API.

    Args:
        spy: Spy instance
        expected_methods: List of expected method names

    Raises:
        AssertionError: If any unexpected methods were called
    """
    for call in spy.get_calls():
        if call.method_name not in expected_methods:
            raise AssertionError(f"Unexpected method call: {call.method_name}")


def verify_call_timing(
    spy: EnhancedSpyBase,
    method_name: str,
    max_duration: float
) -> None:
    """
    Verify that a method was called and completed within a specific time.

    This function checks that a method was called and that its execution time
    did not exceed the specified maximum duration, which is useful for
    performance testing.

    Args:
        spy: Spy instance
        method_name: Method name
        max_duration: Maximum allowed duration in seconds

    Raises:
        AssertionError: If the method was not called or took too long
    """
    spy.assert_called(method_name)

    for call in spy.get_calls(method_name):
        if call.duration is not None and call.duration > max_duration:
            raise AssertionError(
                f"Method {method_name} took {call.duration:.6f}s, "
                f"which is longer than the maximum allowed {max_duration:.6f}s"
            )


def verify_call_arguments(
    spy: EnhancedSpyBase,
    method_name: str,
    expected_args: Dict[str, Any]
) -> None:
    """
    Verify that a method was called with specific arguments.

    This function checks that a method was called with the specified arguments,
    which is useful for ensuring that the code under test interacts with the
    API correctly.

    Args:
        spy: Spy instance
        method_name: Method name
        expected_args: Dictionary of expected argument names and values

    Raises:
        AssertionError: If the method was not called with the expected arguments
    """
    spy.assert_called(method_name)

    for call in spy.get_calls(method_name):
        # Check if all expected args are present with the correct values
        all_args_match = True

        for arg_name, arg_value in expected_args.items():
            if arg_name in call.kwargs:
                if call.kwargs[arg_name] != arg_value:
                    all_args_match = False
                    break
            else:
                # Check if it's a positional arg
                try:
                    arg_index = int(arg_name.replace('arg', ''))
                    if arg_index < len(call.args) and call.args[arg_index] != arg_value:
                        all_args_match = False
                        break
                except (ValueError, IndexError):
                    all_args_match = False
                    break

        if all_args_match:
            return

    raise AssertionError(
        f"Method {method_name} was not called with the expected arguments: {expected_args}"
    )

"""
Method call record for spy implementations.

This module provides a class for recording method calls, which can be used
for verification in tests.
"""

from typing import Any, Dict, Optional, Tuple


class MethodCall:
    """
    Record of a method call for verification.

    This class stores information about a method call, including the method name,
    arguments, and return value.
    """

    def __init__(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        return_value: Any = None,
        exception: Optional[Exception] = None
    ):
        """
        Initialize a method call record.

        Args:
            method_name: Name of the method called
            args: Positional arguments
            kwargs: Keyword arguments
            return_value: Return value (if any)
            exception: Exception raised (if any)
        """
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs
        self.return_value = return_value
        self.exception = exception

    def __repr__(self) -> str:
        """String representation of the method call."""
        args_str = ", ".join([repr(arg) for arg in self.args])
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in self.kwargs.items()])
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        if self.exception:
            result = f" -> raised {self.exception.__class__.__name__}({self.exception})"
        else:
            result = f" -> returned {repr(self.return_value)}" if self.return_value is not None else ""

        return f"{self.method_name}({all_args}){result}"

"""
Data structure for representing a recorded method call.

This module defines the `MethodCall` class, used by spy objects to store
information about interactions for later verification.
"""

from typing import Any, Dict, Optional, Tuple

class MethodCall:
    """
    Record of a method call for verification.

    This class stores information about a method call, including the method name,
    arguments, and return value.
    """

    method_name: str
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    return_value: Any
    exception: Optional[Exception]

    def __init__(
        self, method_name: str, args: Tuple[Any, ...], kwargs: Dict[str, Any], return_value: Any = None, exception: Optional[Exception] = None
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
        ...

    def __repr__(self) -> str:
        """String representation of the method call."""
        ...

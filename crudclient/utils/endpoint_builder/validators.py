"""
Validation functions for endpoint path segments.

This module provides pure validation functions that can be used
independently to validate path segments before building endpoints.
"""

from typing import Optional, Union

# Type alias for path arguments
PathArgs = Optional[Union[str, int]]


def validate_path_segments(*args: PathArgs) -> None:
    """
    Validate that all path segments are of acceptable types and values.

    Parameters
    ----------
    *args : PathArgs
        Variable number of path segments (e.g., resource IDs, actions).

    Raises
    ------
    TypeError
        If any arg is not None, str, or int.
    ValueError
        If any path segment is None, empty, or contains dangerous characters.

    Examples
    --------
    >>> validate_path_segments("users", 123, "edit")  # Valid
    >>> validate_path_segments("users", None, "edit")  # Raises ValueError
    >>> validate_path_segments("users", [], "edit")  # Raises TypeError
    """
    for arg in args:
        if arg is None:
            raise ValueError("Path segment cannot be None")

        if not isinstance(arg, (str, int)):
            raise TypeError(f"Path segment must be string or integer, got {type(arg).__name__}")

        if isinstance(arg, str):
            if not arg.strip():
                raise ValueError("Path segment cannot be empty")

            # Check for dangerous path traversal patterns
            if ".." in arg or arg.startswith("/") or arg.endswith("/"):
                raise ValueError("Path segment contains potentially dangerous characters")

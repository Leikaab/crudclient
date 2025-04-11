from datetime import datetime
from typing import Any, Callable, List, Optional, Union

def required_field(value: Any) -> Optional[str]:
    """
    Validates that a field is present and not empty.

    Args:
        value: The value of the field to validate.

    Returns:
        An error message string if validation fails, None otherwise.
    """
    ...

def min_length(min_len: int) -> Callable[[Any], Optional[str]]:
    """
    Creates a validator that checks if a string field meets a minimum length.

    Args:
        min_len: The minimum required length.

    Returns:
        A validator function.
    """
    ...

def max_length(max_len: int) -> Callable[[Any], Optional[str]]:
    """
    Creates a validator that checks if a string field does not exceed a maximum length.

    Args:
        max_len: The maximum allowed length.

    Returns:
        A validator function.
    """
    ...

def pattern_match(pattern: str, error_msg: str = "Field has invalid format") -> Callable[[Any], Optional[str]]:
    """
    Creates a validator that checks if a string field matches a regex pattern.

    Args:
        pattern: The regex pattern to match against.
        error_msg: The error message to return on failure.

    Returns:
        A validator function.
    """
    ...

def min_value(min_val: Union[int, float]) -> Callable[[Any], Optional[str]]:
    """
    Creates a validator that checks if a numeric field meets a minimum value.

    Args:
        min_val: The minimum allowed value.

    Returns:
        A validator function.
    """
    ...

def max_value(max_val: Union[int, float]) -> Callable[[Any], Optional[str]]:
    """
    Creates a validator that checks if a numeric field does not exceed a maximum value.

    Args:
        max_val: The maximum allowed value.

    Returns:
        A validator function.
    """
    ...

def one_of(allowed_values: List[Any], error_msg: str = "Field has invalid value") -> Callable[[Any], Optional[str]]:
    """
    Creates a validator that checks if a field's value is one of the allowed values.

    Args:
        allowed_values: A list of allowed values.
        error_msg: The error message to return on failure.

    Returns:
        A validator function.
    """
    ...

def is_email() -> Callable[[Any], Optional[str]]:
    """
    Creates a validator that checks if a string field is a valid email address.

    Returns:
        A validator function.
    """
    ...

def is_url() -> Callable[[Any], Optional[str]]:
    """
    Creates a validator that checks if a string field is a valid URL.

    Returns:
        A validator function.
    """
    ...

def is_date(format_str: str = "%Y-%m-%d") -> Callable[[Any], Optional[str]]:
    """
    Creates a validator that checks if a string field is a valid date in the specified format.

    Args:
        format_str: The expected date format string (e.g., "%Y-%m-%d").

    Returns:
        A validator function.
    """
    ...

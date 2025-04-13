import re
from datetime import datetime
from typing import Any, Callable, List, Optional, Union

# Common validator functions


def required_field(value: Any) -> Optional[str]:
    if value is None:
        return "Field is required"
    if isinstance(value, str) and not value.strip():
        return "Field cannot be empty"
    return None


def min_length(min_len: int) -> Callable[[Any], Optional[str]]:
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return "Field must be a string"
        if len(value) < min_len:
            return f"Field must be at least {min_len} characters long"
        return None

    return validator


def max_length(max_len: int) -> Callable[[Any], Optional[str]]:
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return "Field must be a string"
        if len(value) > max_len:
            return f"Field cannot be longer than {max_len} characters"
        return None

    return validator


def pattern_match(pattern: str, error_msg: str = "Field has invalid format") -> Callable[[Any], Optional[str]]:
    regex = re.compile(pattern)

    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return "Field must be a string"
        if not regex.match(value):
            return error_msg
        return None

    return validator


def min_value(min_val: Union[int, float]) -> Callable[[Any], Optional[str]]:
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, (int, float)):
            return "Field must be a number"
        if value < min_val:
            return f"Field must be at least {min_val}"
        return None

    return validator


def max_value(max_val: Union[int, float]) -> Callable[[Any], Optional[str]]:
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, (int, float)):
            return "Field must be a number"
        if value > max_val:
            return f"Field cannot be greater than {max_val}"
        return None

    return validator


def one_of(allowed_values: List[Any], error_msg: str = "Field has invalid value") -> Callable[[Any], Optional[str]]:
    def validator(value: Any) -> Optional[str]:
        if value not in allowed_values:
            return error_msg
        return None

    return validator


def is_email() -> Callable[[Any], Optional[str]]:
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return pattern_match(email_pattern, "Field must be a valid email address")


def is_url() -> Callable[[Any], Optional[str]]:
    url_pattern = r"^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w%!$&'()*+,;=:]+)*(?:\?[-\w%!$&'()*+,;=:/?]+)?(?:#[-\w%!$&'()*+,;=:/?]+)?$"
    return pattern_match(url_pattern, "Field must be a valid URL")


def is_date(format_str: str = "%Y-%m-%d") -> Callable[[Any], Optional[str]]:
    def validator(value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return "Field must be a string"
        try:
            datetime.strptime(value, format_str)
            return None
        except ValueError:
            return f"Field must be a valid date in the format {format_str}"

    return validator

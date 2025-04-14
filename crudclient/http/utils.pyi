from typing import Any, Dict, Mapping, Set

def redact_sensitive_headers(headers: Mapping[str, str]) -> Dict[str, str]:
    """
    Creates a copy of headers with sensitive values redacted.

    Args:
        headers: A mapping (like a dictionary or CaseInsensitiveDict) of headers.

    Returns:
        A new dictionary with sensitive header values replaced by "[REDACTED]".
    """
    ...

# Note: The default value _SENSITIVE_BODY_KEYS_LOWER is defined in the .py file

def redact_json_body(data: Any, sensitive_keys: Set[str] = ...) -> Any:
    """
    Recursively redact sensitive information from a JSON-like structure (dicts and lists).

    Creates a deep copy to avoid modifying the original data.

    Handles:
    - General key-based redaction (case-insensitive) using `sensitive_keys`.
      Keys are matched case-insensitively using a default set of common sensitive keys
      if `sensitive_keys` is not provided (the default is taken from the .py file).
    - A specific pattern: Dictionaries containing both a "name" key (value "api_key", case-insensitive)
      and a "value" key will have the "value" field redacted. This check takes precedence
      for the "value" field if the pattern matches.

    Args:
        data: The data structure (dict, list, or other type) to redact.
        sensitive_keys: A set of lower-case strings representing keys to redact.
                        Defaults to `_SENSITIVE_BODY_KEYS_LOWER` from the implementation file.

    Returns:
        A new data structure with sensitive values replaced by "[REDACTED]".
    """
    ...

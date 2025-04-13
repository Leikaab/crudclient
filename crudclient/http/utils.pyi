from typing import Dict, Mapping


def redact_sensitive_headers(headers: Mapping[str, str]) -> Dict[str, str]:
    """
    Creates a copy of headers with sensitive values redacted.

    Args:
        headers: A mapping (like a dictionary or CaseInsensitiveDict) of headers.

    Returns:
        A new dictionary with sensitive header values replaced by "[REDACTED]".
    """
    ...

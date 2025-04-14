import logging
from typing import Any, Dict, Mapping, Set

# Set up logging
logger = logging.getLogger(__name__)

# --- Header Redaction ---
_SENSITIVE_HEADERS_LOWER = {
    "authorization",
    "cookie",
    "set-cookie",
    "proxy-authorization",
}
_SENSITIVE_HEADER_PREFIXES_LOWER = (
    "x-api-key",
    "x-auth-token",
    # Add other common sensitive prefixes here if needed
)
_REDACTED_VALUE = "[REDACTED]"


def redact_sensitive_headers(headers: Mapping[str, str]) -> Dict[str, str]:
    redacted_headers: Dict[str, str] = {}
    if not headers:
        return redacted_headers

    for name, value in headers.items():

        lower_name = name.lower()
        is_sensitive = lower_name in _SENSITIVE_HEADERS_LOWER or lower_name.startswith(_SENSITIVE_HEADER_PREFIXES_LOWER)
        # Ensure value is treated as a string for logging consistency
        redacted_headers[name] = _REDACTED_VALUE if is_sensitive else str(value)
    return redacted_headers


# --- End Header Redaction ---


# --- Body Redaction ---
_SENSITIVE_BODY_KEYS_LOWER: Set[str] = {
    "password",
    "token",
    "secret",
    "apikey",
    "api_key",  # Added
    "access_token",
    "refresh_token",
    "client_secret",
    "authorization",
    "cookie",
    "sessionid",
    "session_token",  # Added
    "secret_code",  # Added
    "password_hash",  # Added based on test failure
}


def redact_json_body(data: Any, sensitive_keys: Set[str] = _SENSITIVE_BODY_KEYS_LOWER) -> Any:
    if isinstance(data, dict):
        redacted_data = {}
        # Check for special pattern first to potentially override value redaction later
        name_key = None
        value_key = None
        api_key_name_present = False
        for k, v in data.items():
            # Ensure key is string before lowercasing and comparison
            if isinstance(k, str):
                key_lower = k.lower()
                if key_lower == "name":
                    name_key = k
                    # Check if the value associated with 'name' is 'api_key' (case-insensitive)
                    if isinstance(v, str) and v.lower() == "api_key":
                        api_key_name_present = True
                elif key_lower == "value":
                    value_key = k
            # Handle non-string keys gracefully if necessary, though less common in JSON context
            # else: pass or handle appropriately

        is_special_api_key_pattern = name_key and value_key and api_key_name_present

        for key, value in data.items():
            key_str = str(key)  # Ensure key is string for comparison

            # Condition 1: Key is generally sensitive (case-insensitive check)
            if key_str.lower() in sensitive_keys:
                redacted_data[key] = _REDACTED_VALUE
            # Condition 2: Special API key pattern applies AND current key is the 'value' key
            elif is_special_api_key_pattern and key == value_key:
                redacted_data[key] = _REDACTED_VALUE
            # Condition 3: Neither key redaction condition met, recurse into the value
            else:
                redacted_data[key] = redact_json_body(value, sensitive_keys)  # Pass sensitive_keys down

        return redacted_data
    elif isinstance(data, list):
        # Create a copy and recurse into list items, passing sensitive_keys down
        return [redact_json_body(item, sensitive_keys) for item in data]
    else:
        # Return non-dict/list types as is (no copy needed for immutables)
        return data


# --- End Body Redaction ---

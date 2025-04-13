import logging
from typing import Dict, Mapping

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
        is_sensitive = (
            lower_name in _SENSITIVE_HEADERS_LOWER
            or lower_name.startswith(_SENSITIVE_HEADER_PREFIXES_LOWER)
        )
        # Ensure value is treated as a string for logging consistency
        redacted_headers[name] = _REDACTED_VALUE if is_sensitive else str(value)
    return redacted_headers
# --- End Header Redaction ---

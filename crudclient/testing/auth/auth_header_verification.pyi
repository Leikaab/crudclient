"""
Specific utilities for verifying authentication header formats in tests.

This module provides the `AuthHeaderVerification` class containing static methods
focused solely on checking the structural correctness and basic format of common
authentication headers like Basic, Bearer, and API Key.

These methods are typically used internally by higher-level verification helpers
(like `AuthVerificationHelpers`) or can be used directly for fine-grained header checks.
They raise `VerificationError` upon failure.
"""

from typing import Any, Dict, Optional

from ..exceptions import VerificationError  # Import VerificationError
from .auth_extraction_utils import AuthExtractionUtils

class AuthHeaderVerification:
    """
    Provides static methods focused on verifying authentication header formats.

    Contains specific checks for Basic, Bearer, and API Key header structures.
    Methods raise `VerificationError` if the format is invalid.
    """

    @staticmethod
    def verify_basic_auth_header(header_value: str) -> bool:
        """
        Verify the format of a Basic Authentication header value.

        Checks if the value starts with "Basic " followed by a Base64 encoded string.
        Does *not* decode or validate the credentials themselves.

        Args:
            header_value: The full value of the Authorization header (e.g., "Basic dXNlcjpwYXNz").

        Returns:
            True if the format is valid.

        Raises:
            VerificationError: If the format is invalid (e.g., missing "Basic ", not Base64).

        Example:
            >>> AuthHeaderVerification.verify_basic_auth_header("Basic dXNlcjpwYXNz")
            True
            >>> try:
            ...     AuthHeaderVerification.verify_basic_auth_header("Bearer token")
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        ...

    @staticmethod
    def verify_bearer_auth_header(header_value: str) -> bool:
        """
        Verify the format of a Bearer Authentication header value.

        Checks if the value starts with "Bearer " followed by a non-empty token string.
        Does *not* validate the token content itself.

        Args:
            header_value: The full value of the Authorization header (e.g., "Bearer mytoken123").

        Returns:
            True if the format is valid.

        Raises:
            VerificationError: If the format is invalid (e.g., missing "Bearer ", empty token).

        Example:
            >>> AuthHeaderVerification.verify_bearer_auth_header("Bearer abcdef12345")
            True
            >>> try:
            ...     AuthHeaderVerification.verify_bearer_auth_header("Basic dXNlcjpwYXNz")
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        ...

    @staticmethod
    def verify_api_key_header(header_value: str, expected_key: Optional[str] = None) -> bool:
        """
        Verify an API Key header value, optionally matching against an expected key.

        Checks if the `header_value` is a non-empty string. If `expected_key` is
        provided, it also checks for an exact match. Assumes the `header_value` is
        the key itself, without any scheme prefix.

        Args:
            header_value: The value of the header containing the API key (e.g., "mysecretkey").
            expected_key: Optional. If provided, the `header_value` must match this exactly.

        Returns:
            True if the verification passes.

        Raises:
            VerificationError: If `header_value` is empty, or if `expected_key` is provided
                               and does not match `header_value`.

        Example:
            >>> AuthHeaderVerification.verify_api_key_header("secret1", expected_key="secret1")
            True
            >>> AuthHeaderVerification.verify_api_key_header("anykey") # Format check only (non-empty)
            True
            >>> try:
            ...     AuthHeaderVerification.verify_api_key_header("secret1", expected_key="secret2")
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        ...

    @staticmethod
    def verify_auth_header_format(headers: Dict[str, str], auth_type: str, header_name: str = "Authorization") -> None:
        """
        Verify a specific authentication header exists and has the correct basic format.

        Looks for `header_name` in the `headers` dictionary and checks if its value
        starts with the expected scheme (`auth_type` + " ") or, if `auth_type` is
        "ApiKey", checks that the value is simply non-empty.

        Args:
            headers: Dictionary of headers (case-insensitive keys recommended).
            auth_type: The expected scheme ("Basic", "Bearer", or "ApiKey").
            header_name: The name of the header to check (default: "Authorization").

        Raises:
            VerificationError: If the header is missing, or if its value does not conform
                               to the expected format for the given `auth_type`.

        Example:
            >>> headers = {"Authorization": "Bearer mytoken", "Content-Type": "application/json"}
            >>> AuthHeaderVerification.verify_auth_header_format(headers, "Bearer")
            >>> AuthHeaderVerification.verify_auth_header_format({"X-API-Key": "key123"}, "ApiKey", header_name="X-API-Key")
            >>> try:
            ...     AuthHeaderVerification.verify_auth_header_format(headers, "Basic")
            ... except VerificationError:
            ...     print("Failed as expected") # doctest: +SKIP
            Failed as expected
        """
        ...

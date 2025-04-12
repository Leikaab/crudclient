"""
Authentication error verification utilities for testing.

This module provides helper methods for verifying authentication error responses
and rate limit headers.
"""

from typing import Any, Dict, List, Optional

from ..exceptions import VerificationError  # Import VerificationError


class AuthErrorVerification:
    """
    Helper methods for verifying authentication error responses.

    This class provides static methods for verifying authentication error responses
    and rate limit headers.
    """

    @staticmethod
    def verify_auth_error_response(
        response: Dict[str, Any], expected_status: int = 401, expected_error: Optional[str] = None, expected_error_description: Optional[str] = None
    ) -> None:
        """
        Verify that an authentication error response is correct.

        Args:
            response: The response to verify
            expected_status: The expected HTTP status code
            expected_error: The expected error code
            expected_error_description: The expected error description

        Raises:
            VerificationError: If the response does not match the expected values
        """
        ...

    @staticmethod
    def verify_rate_limit_headers(
        headers: Dict[str, str], expected_limit: Optional[int] = None, expected_remaining: Optional[int] = None, expected_reset: Optional[int] = None
    ) -> None:
        """
        Verify that rate limit headers are correct.

        Args:
            headers: The headers to verify
            expected_limit: The expected rate limit
            expected_remaining: The expected remaining requests
            expected_reset: The expected reset time

        Raises:
            VerificationError: If the headers do not match the expected values
        """
        ...

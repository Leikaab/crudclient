"""
Authentication error verification utilities for testing.

This module provides helper methods for verifying authentication error responses
and rate limit headers.
"""

from typing import Any, Dict, Optional


class AuthErrorVerification:
    """
    Helper methods for verifying authentication error responses.

    This class provides static methods for verifying authentication error responses
    and rate limit headers.
    """

    @staticmethod
    def assert_auth_error_response(
        response: Dict[str, Any],
        expected_status: int = 401,
        expected_error: Optional[str] = None,
        expected_error_description: Optional[str] = None
    ) -> None:
        """
        Assert that an authentication error response is correct.

        Args:
            response: The response to verify
            expected_status: The expected HTTP status code
            expected_error: The expected error code
            expected_error_description: The expected error description

        Raises:
            AssertionError: If the response does not match the expected values
        """
        # Check status code
        if "status_code" in response:
            if response["status_code"] != expected_status:
                raise AssertionError(f"Expected status code {expected_status}, got {response['status_code']}")

        # Check error code
        if expected_error and "error" in response:
            if response["error"] != expected_error:
                raise AssertionError(f"Expected error code '{expected_error}', got '{response['error']}'")

        # Check error description
        if expected_error_description and "error_description" in response:
            if response["error_description"] != expected_error_description:
                raise AssertionError(f"Expected error description '{expected_error_description}', got '{response['error_description']}'")

    @staticmethod
    def assert_rate_limit_headers(
        headers: Dict[str, str],
        expected_limit: Optional[int] = None,
        expected_remaining: Optional[int] = None,
        expected_reset: Optional[int] = None
    ) -> None:
        """
        Assert that rate limit headers are correct.

        Args:
            headers: The headers to verify
            expected_limit: The expected rate limit
            expected_remaining: The expected remaining requests
            expected_reset: The expected reset time

        Raises:
            AssertionError: If the headers do not match the expected values
        """
        # Check for standard rate limit headers
        rate_limit_headers = {
            "X-RateLimit-Limit": expected_limit,
            "X-RateLimit-Remaining": expected_remaining,
            "X-RateLimit-Reset": expected_reset
        }

        for header, expected_value in rate_limit_headers.items():
            if expected_value is not None:
                if header not in headers:
                    raise AssertionError(f"Missing rate limit header: {header}")

                try:
                    actual_value = int(headers[header])
                    if actual_value != expected_value:
                        raise AssertionError(f"Expected {header} to be {expected_value}, got {actual_value}")
                except ValueError:
                    raise AssertionError(f"Rate limit header {header} is not an integer: {headers[header]}")

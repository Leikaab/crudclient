"""
Authentication verification helpers for testing.

This module provides helper methods for verifying authentication behavior,
including header validation, error handling, and token refresh verification.
"""

from typing import Any, Dict, List, Optional, Tuple

from .auth_error_verification import AuthErrorVerification
from .auth_extraction_utils import AuthExtractionUtils
from .auth_header_verification import AuthHeaderVerification
from .auth_token_verification import AuthTokenVerification

class AuthVerificationHelpers:
    """
    Helper methods for verifying authentication behavior with enhanced capabilities.

    This class provides static methods for verifying various aspects of authentication,
    including header validation, token validation, and error response validation.
    """

    # Header verification methods
    @staticmethod
    def verify_basic_auth_header(header_value: str) -> bool:
        """
        Verify that a Basic Auth header is correctly formatted.

        Args:
            header_value: The value of the Authorization header

        Returns:
            True if the header is a valid Basic Auth header, False otherwise
        """
        ...

    @staticmethod
    def verify_bearer_auth_header(header_value: str) -> bool:
        """
        Verify that a Bearer Auth header is correctly formatted.

        Args:
            header_value: The value of the Authorization header

        Returns:
            True if the header is a valid Bearer Auth header, False otherwise
        """
        ...

    @staticmethod
    def verify_api_key_header(header_value: str, expected_key: Optional[str] = None) -> bool:
        """
        Verify that an API Key header is correctly formatted and matches the expected key.

        Args:
            header_value: The value of the API Key header
            expected_key: The expected API key value (if None, only format is checked)

        Returns:
            True if the header is a valid API Key header, False otherwise
        """
        ...

    @staticmethod
    def assert_auth_header_format(headers: Dict[str, str], auth_type: str, header_name: str = "Authorization") -> None:
        """
        Assert that an authentication header has the correct format.

        Args:
            headers: The headers dictionary
            auth_type: The authentication type ("Basic", "Bearer", or "ApiKey")
            header_name: The name of the header (default: "Authorization")

        Raises:
            AssertionError: If the header is missing or has an invalid format
        """
        ...
    # Token verification methods
    @staticmethod
    def verify_oauth_token(
        token: str,
        required_scopes: Optional[List[str]] = None,
        check_expiration: bool = True,
        expected_client_id: Optional[str] = None,
        expected_user: Optional[str] = None,
    ) -> bool:
        """
        Verify that an OAuth token is valid and has the required scopes.

        Args:
            token: The OAuth token to verify
            required_scopes: List of required scopes
            check_expiration: Whether to check if the token is expired
            expected_client_id: The expected client ID
            expected_user: The expected user

        Returns:
            True if the token is valid, False otherwise
        """
        ...

    @staticmethod
    def verify_token_refresh(old_token: str, new_token: str) -> bool:
        """
        Verify that a token refresh operation was successful.

        Args:
            old_token: The old token
            new_token: The new token

        Returns:
            True if the refresh was successful, False otherwise
        """
        ...

    @staticmethod
    def verify_token_expiration(token: str, jwt: bool = True) -> bool:
        """
        Verify if a token is expired.

        Args:
            token: The token to check
            jwt: Whether the token is a JWT

        Returns:
            True if the token is expired, False otherwise
        """
        ...

    @staticmethod
    def assert_token_usage(
        token: str, required_scopes: Optional[List[str]] = None, expected_client_id: Optional[str] = None, expected_user: Optional[str] = None
    ) -> None:
        """
        Assert that a token is being used correctly.

        Args:
            token: The token to verify
            required_scopes: List of required scopes
            expected_client_id: The expected client ID
            expected_user: The expected user

        Raises:
            AssertionError: If the token is not being used correctly
        """
        ...

    @staticmethod
    def assert_refresh_behavior(old_token: str, new_token: str, expected_client_id: Optional[str] = None) -> None:
        """
        Assert that token refresh behavior is correct.

        Args:
            old_token: The old token
            new_token: The new token
            expected_client_id: The expected client ID

        Raises:
            AssertionError: If the refresh behavior is incorrect
        """
        ...

    @staticmethod
    def assert_token_has_scopes(token: str, required_scopes: List[str]) -> None:
        """
        Assert that a token has the required scopes.

        Args:
            token: The token to verify
            required_scopes: List of required scopes

        Raises:
            AssertionError: If the token does not have the required scopes
        """
        ...
    # Extraction utilities
    @staticmethod
    def extract_basic_auth_credentials(header_value: str) -> Tuple[str, str]:
        """
        Extract username and password from a Basic Auth header.

        Args:
            header_value: The value of the Authorization header

        Returns:
            A tuple of (username, password)

        Raises:
            ValueError: If the header is not a valid Basic Auth header
        """
        ...

    @staticmethod
    def extract_bearer_token(header_value: str) -> str:
        """
        Extract token from a Bearer Auth header.

        Args:
            header_value: The value of the Authorization header

        Returns:
            The Bearer token

        Raises:
            ValueError: If the header is not a valid Bearer Auth header
        """
        ...

    @staticmethod
    def extract_jwt_payload(token: str) -> Dict[str, Any]:
        """
        Extract and decode the payload from a JWT token.

        Args:
            token: The JWT token

        Returns:
            The decoded JWT payload as a dictionary

        Raises:
            ValueError: If the token is not a valid JWT
        """
        ...
    # Error verification methods
    @staticmethod
    def assert_auth_error_response(
        response: Dict[str, Any], expected_status: int = 401, expected_error: Optional[str] = None, expected_error_description: Optional[str] = None
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
        ...

    @staticmethod
    def assert_rate_limit_headers(
        headers: Dict[str, str], expected_limit: Optional[int] = None, expected_remaining: Optional[int] = None, expected_reset: Optional[int] = None
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
        ...

# For backward compatibility
__all__ = ["AuthVerificationHelpers", "AuthExtractionUtils", "AuthHeaderVerification", "AuthTokenVerification", "AuthErrorVerification"]

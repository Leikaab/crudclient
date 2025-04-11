"""
Base authentication mock class for testing.

This module provides the base class for authentication mocks with chainable configuration.
It serves as the foundation for all specialized authentication mock classes in the
crudclient testing framework.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from ..response_builder import ResponseBuilder

class AuthMockBase:
    """
    Base class for authentication mocks with chainable configuration.

    This class provides common functionality for all authentication mock implementations,
    including failure simulation, token expiration, refresh token handling, and
    multi-factor authentication scenarios.

    All specialized authentication mocks inherit from this base class to ensure
    consistent behavior and interface.
    """

    should_fail: bool
    failure_type: str
    failure_status_code: int
    failure_message: str
    token_expired: bool
    token_expiry_time: Optional[datetime]
    refresh_token: Optional[str]
    refresh_token_expired: bool
    refresh_attempts: int
    max_refresh_attempts: int
    mfa_required: bool
    mfa_verified: bool
    request_count: int
    fail_after_requests: Optional[int]
    custom_headers: Dict[str, str]
    custom_params: Dict[str, str]

    def __init__(self) -> None:
        """Initialize the base authentication mock with default settings."""
        ...

    def with_failure(
        self,
        failure_type: str = "invalid_token",
        status_code: int = 401,
        message: str = "Authentication failed"
    ) -> 'AuthMockBase':
        """
        Configure the mock to simulate authentication failure.

        Args:
            failure_type: Type of authentication failure (e.g., "invalid_token", "expired_token")
            status_code: HTTP status code to return for the failure
            message: Error message to include in the response

        Returns:
            Self for method chaining
        """
        ...

    def with_success(self) -> 'AuthMockBase':
        """
        Configure the mock to simulate authentication success.

        Returns:
            Self for method chaining
        """
        ...

    def with_token_expiration(
        self,
        expires_in_seconds: int = 3600
    ) -> 'AuthMockBase':
        """
        Configure the mock to simulate token expiration.

        Args:
            expires_in_seconds: Number of seconds until the token expires

        Returns:
            Self for method chaining
        """
        ...

    def with_expired_token(self) -> 'AuthMockBase':
        """
        Configure the mock to simulate an already expired token.

        Returns:
            Self for method chaining
        """
        ...

    def with_refresh_token(
        self,
        refresh_token: str = "refresh_token",
        max_refresh_attempts: int = 3
    ) -> 'AuthMockBase':
        """
        Configure the mock with a refresh token.

        Args:
            refresh_token: The refresh token value
            max_refresh_attempts: Maximum number of times the token can be refreshed

        Returns:
            Self for method chaining
        """
        ...

    def with_expired_refresh_token(self) -> 'AuthMockBase':
        """
        Configure the mock with an expired refresh token.

        Returns:
            Self for method chaining
        """
        ...

    def with_mfa_required(self, verified: bool = False) -> 'AuthMockBase':
        """
        Configure the mock to require multi-factor authentication.

        Args:
            verified: Whether MFA has been verified

        Returns:
            Self for method chaining
        """
        ...

    def fail_after(self, request_count: int) -> 'AuthMockBase':
        """
        Configure the mock to fail after a specific number of requests.

        Args:
            request_count: Number of successful requests before failing

        Returns:
            Self for method chaining
        """
        ...

    def with_custom_header(self, name: str, value: str) -> 'AuthMockBase':
        """
        Add a custom header to the auth strategy.

        Args:
            name: Header name
            value: Header value

        Returns:
            Self for method chaining
        """
        ...

    def with_custom_param(self, name: str, value: str) -> 'AuthMockBase':
        """
        Add a custom parameter to the auth strategy.

        Args:
            name: Parameter name
            value: Parameter value

        Returns:
            Self for method chaining
        """
        ...

    def is_token_expired(self) -> bool:
        """
        Check if the token is expired.

        Returns:
            True if the token is expired, False otherwise
        """
        ...

    def can_refresh_token(self) -> bool:
        """
        Check if the token can be refreshed.

        Returns:
            True if the token can be refreshed, False otherwise
        """
        ...

    def refresh(self) -> bool:
        """
        Attempt to refresh the token.

        Returns:
            True if the token was refreshed successfully, False otherwise
        """
        ...

    def should_fail_auth(self) -> bool:
        """
        Determine if authentication should fail.

        Returns:
            True if authentication should fail, False otherwise
        """
        ...

    def get_auth_error_response(self) -> Any:
        """
        Get the appropriate authentication error response.

        Returns:
            A mock response object with appropriate error details
        """
        ...

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the authentication header has the correct format.

        Args:
            header_value: The value of the authentication header

        Returns:
            True if the header is valid, False otherwise
        """
        ...

    def verify_token_usage(self, token: str) -> bool:
        """
        Verify that the token is being used correctly.

        Args:
            token: The token to verify

        Returns:
            True if the token is being used correctly, False otherwise
        """
        ...

    def verify_refresh_behavior(self, old_token: str, new_token: str) -> bool:
        """
        Verify that token refresh behavior is correct.

        Args:
            old_token: The token before refresh
            new_token: The token after refresh

        Returns:
            True if the refresh behavior is correct, False otherwise
        """
        ...

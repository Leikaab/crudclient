"""
Base authentication mock class for testing.

This module provides the base class for authentication mocks with chainable configuration.
It serves as the foundation for all specialized authentication mock classes in the
crudclient testing framework.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional

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

    def __init__(self):
        """Initialize the base authentication mock with default settings."""
        self.should_fail = False
        self.failure_type = "invalid_token"
        self.failure_status_code = 401
        self.failure_message = "Authentication failed"
        self.token_expired = False
        self.token_expiry_time = None
        self.refresh_token = None
        self.refresh_token_expired = False
        self.refresh_attempts = 0
        self.max_refresh_attempts = 3
        self.mfa_required = False
        self.mfa_verified = False
        self.request_count = 0
        self.fail_after_requests = None
        self.custom_headers = {}
        self.custom_params = {}

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
        self.should_fail = True
        self.failure_type = failure_type
        self.failure_status_code = status_code
        self.failure_message = message
        return self

    def with_success(self) -> 'AuthMockBase':
        """
        Configure the mock to simulate authentication success.

        Returns:
            Self for method chaining
        """
        self.should_fail = False
        return self

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
        self.token_expired = False
        self.token_expiry_time = datetime.now() + timedelta(seconds=expires_in_seconds)
        return self

    def with_expired_token(self) -> 'AuthMockBase':
        """
        Configure the mock to simulate an already expired token.

        Returns:
            Self for method chaining
        """
        self.token_expired = True
        self.token_expiry_time = datetime.now() - timedelta(seconds=60)
        return self

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
        self.refresh_token = refresh_token
        self.refresh_token_expired = False
        self.refresh_attempts = 0
        self.max_refresh_attempts = max_refresh_attempts
        return self

    def with_expired_refresh_token(self) -> 'AuthMockBase':
        """
        Configure the mock with an expired refresh token.

        Returns:
            Self for method chaining
        """
        self.refresh_token = "expired_refresh_token"
        self.refresh_token_expired = True
        return self

    def with_mfa_required(self, verified: bool = False) -> 'AuthMockBase':
        """
        Configure the mock to require multi-factor authentication.

        Args:
            verified: Whether MFA has been verified

        Returns:
            Self for method chaining
        """
        self.mfa_required = True
        self.mfa_verified = verified
        return self

    def fail_after(self, request_count: int) -> 'AuthMockBase':
        """
        Configure the mock to fail after a specific number of requests.

        Args:
            request_count: Number of successful requests before failing

        Returns:
            Self for method chaining
        """
        self.fail_after_requests = request_count
        return self

    def with_custom_header(self, name: str, value: str) -> 'AuthMockBase':
        """
        Add a custom header to the auth strategy.

        Args:
            name: Header name
            value: Header value

        Returns:
            Self for method chaining
        """
        self.custom_headers[name] = value
        return self

    def with_custom_param(self, name: str, value: str) -> 'AuthMockBase':
        """
        Add a custom parameter to the auth strategy.

        Args:
            name: Parameter name
            value: Parameter value

        Returns:
            Self for method chaining
        """
        self.custom_params[name] = value
        return self

    def is_token_expired(self) -> bool:
        """
        Check if the token is expired.

        Returns:
            True if the token is expired, False otherwise
        """
        if self.token_expired:
            return True
        if self.token_expiry_time and datetime.now() > self.token_expiry_time:
            self.token_expired = True
            return True
        return False

    def can_refresh_token(self) -> bool:
        """
        Check if the token can be refreshed.

        Returns:
            True if the token can be refreshed, False otherwise
        """
        if not self.refresh_token:
            return False
        if self.refresh_token_expired:
            return False
        if self.refresh_attempts >= self.max_refresh_attempts:
            return False
        return True

    def refresh(self) -> bool:
        """
        Attempt to refresh the token.

        Returns:
            True if the token was refreshed successfully, False otherwise
        """
        if not self.can_refresh_token():
            return False

        self.refresh_attempts += 1
        self.token_expired = False
        self.token_expiry_time = datetime.now() + timedelta(seconds=3600)
        return True

    def should_fail_auth(self) -> bool:
        """
        Determine if authentication should fail.

        Returns:
            True if authentication should fail, False otherwise
        """
        self.request_count += 1

        if self.should_fail:
            return True

        if self.fail_after_requests and self.request_count > self.fail_after_requests:
            return True

        if self.is_token_expired() and not self.can_refresh_token():
            return True

        if self.mfa_required and not self.mfa_verified:
            return True

        return False

    def get_auth_error_response(self):
        """
        Get the appropriate authentication error response.

        Returns:
            A mock response object with appropriate error details
        """
        if self.is_token_expired():
            return ResponseBuilder.create_auth_error(
                error_type="expired_token",
                status_code=401
            )

        if self.mfa_required and not self.mfa_verified:
            return ResponseBuilder.create_auth_error(
                error_type="mfa_required",
                status_code=401
            )

        return ResponseBuilder.create_auth_error(
            error_type=self.failure_type,
            status_code=self.failure_status_code
        )

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the authentication header has the correct format.

        Args:
            header_value: The value of the authentication header

        Returns:
            True if the header is valid, False otherwise
        """
        return True  # Base implementation always passes

    def verify_token_usage(self, token: str) -> bool:
        """
        Verify that the token is being used correctly.

        Args:
            token: The token to verify

        Returns:
            True if the token is being used correctly, False otherwise
        """
        return True  # Base implementation always passes

    def verify_refresh_behavior(self, old_token: str, new_token: str) -> bool:
        """
        Verify that token refresh behavior is correct.

        Args:
            old_token: The token before refresh
            new_token: The token after refresh

        Returns:
            True if the refresh behavior is correct, False otherwise
        """
        return old_token != new_token  # Basic check that tokens are different

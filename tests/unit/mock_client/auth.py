"""
Authentication mocking utilities for testing.

This module provides specialized mock factories and utilities for testing
authentication strategies, including Basic, Bearer, and Custom auth.
"""

import base64
import re
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from crudclient.auth.base import AuthStrategy
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import ApiKeyAuth, CustomAuth

from .response import MockResponse
from .response_builder import ResponseBuilder


class AuthMockBase:
    """Base class for authentication mocks with chainable configuration."""

    def __init__(self):
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
        """Configure the mock to simulate authentication failure."""
        self.should_fail = True
        self.failure_type = failure_type
        self.failure_status_code = status_code
        self.failure_message = message
        return self

    def with_success(self) -> 'AuthMockBase':
        """Configure the mock to simulate authentication success."""
        self.should_fail = False
        return self

    def with_token_expiration(
        self,
        expires_in_seconds: int = 3600
    ) -> 'AuthMockBase':
        """Configure the mock to simulate token expiration."""
        self.token_expired = False
        self.token_expiry_time = datetime.now() + timedelta(seconds=expires_in_seconds)
        return self

    def with_expired_token(self) -> 'AuthMockBase':
        """Configure the mock to simulate an already expired token."""
        self.token_expired = True
        self.token_expiry_time = datetime.now() - timedelta(seconds=60)
        return self

    def with_refresh_token(
        self,
        refresh_token: str = "refresh_token",
        max_refresh_attempts: int = 3
    ) -> 'AuthMockBase':
        """Configure the mock with a refresh token."""
        self.refresh_token = refresh_token
        self.refresh_token_expired = False
        self.refresh_attempts = 0
        self.max_refresh_attempts = max_refresh_attempts
        return self

    def with_expired_refresh_token(self) -> 'AuthMockBase':
        """Configure the mock with an expired refresh token."""
        self.refresh_token = "expired_refresh_token"
        self.refresh_token_expired = True
        return self

    def with_mfa_required(self, verified: bool = False) -> 'AuthMockBase':
        """Configure the mock to require multi-factor authentication."""
        self.mfa_required = True
        self.mfa_verified = verified
        return self

    def fail_after(self, request_count: int) -> 'AuthMockBase':
        """Configure the mock to fail after a specific number of requests."""
        self.fail_after_requests = request_count
        return self

    def with_custom_header(self, name: str, value: str) -> 'AuthMockBase':
        """Add a custom header to the auth strategy."""
        self.custom_headers[name] = value
        return self

    def with_custom_param(self, name: str, value: str) -> 'AuthMockBase':
        """Add a custom parameter to the auth strategy."""
        self.custom_params[name] = value
        return self

    def is_token_expired(self) -> bool:
        """Check if the token is expired."""
        if self.token_expired:
            return True
        if self.token_expiry_time and datetime.now() > self.token_expiry_time:
            self.token_expired = True
            return True
        return False

    def can_refresh_token(self) -> bool:
        """Check if the token can be refreshed."""
        if not self.refresh_token:
            return False
        if self.refresh_token_expired:
            return False
        if self.refresh_attempts >= self.max_refresh_attempts:
            return False
        return True

    def refresh(self) -> bool:
        """Attempt to refresh the token."""
        if not self.can_refresh_token():
            return False

        self.refresh_attempts += 1
        self.token_expired = False
        self.token_expiry_time = datetime.now() + timedelta(seconds=3600)
        return True

    def should_fail_auth(self) -> bool:
        """Determine if authentication should fail."""
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

    def get_auth_error_response(self) -> MockResponse:
        """Get the appropriate authentication error response."""
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
        """Verify that the authentication header has the correct format."""
        return True  # Base implementation always passes

    def verify_token_usage(self, token: str) -> bool:
        """Verify that the token is being used correctly."""
        return True  # Base implementation always passes

    def verify_refresh_behavior(self, old_token: str, new_token: str) -> bool:
        """Verify that token refresh behavior is correct."""
        return old_token != new_token  # Basic check that tokens are different


class BasicAuthMock(AuthMockBase):
    """Mock for Basic Authentication strategy."""

    def __init__(self, username: str = "user", password: str = "pass"):
        super().__init__()
        self.username = username
        self.password = password
        self.auth_strategy = BasicAuth(username=username, password=password)

    def with_credentials(self, username: str, password: str) -> 'BasicAuthMock':
        """Set the credentials for the Basic Auth mock."""
        self.username = username
        self.password = password
        self.auth_strategy = BasicAuth(username=username, password=password)
        return self

    def verify_auth_header(self, header_value: str) -> bool:
        """Verify that the Basic Auth header has the correct format."""
        if not header_value.startswith("Basic "):
            return False

        try:
            encoded_part = header_value[6:]  # Skip "Basic "
            decoded = base64.b64decode(encoded_part).decode('utf-8')
            return ":" in decoded
        except Exception:
            return False

    def get_auth_strategy(self) -> AuthStrategy:
        """Get the configured auth strategy."""
        return self.auth_strategy


class BearerAuthMock(AuthMockBase):
    """Mock for Bearer Authentication strategy."""

    def __init__(self, token: str = "valid_token"):
        super().__init__()
        self.token = token
        self.auth_strategy = BearerAuth(token=token)
        self.issued_tokens = [token]

    def with_token(self, token: str) -> 'BearerAuthMock':
        """Set the token for the Bearer Auth mock."""
        self.token = token
        self.auth_strategy = BearerAuth(token=token)
        self.issued_tokens = [token]
        return self

    def refresh(self) -> bool:
        """Refresh the token and update the auth strategy."""
        if not super().refresh():
            return False

        new_token = f"{self.token}_refreshed_{self.refresh_attempts}"
        self.token = new_token
        self.auth_strategy = BearerAuth(token=new_token)
        self.issued_tokens.append(new_token)
        return True

    def verify_auth_header(self, header_value: str) -> bool:
        """Verify that the Bearer Auth header has the correct format."""
        return header_value.startswith("Bearer ")

    def verify_token_usage(self, token: str) -> bool:
        """Verify that the token is one that was issued by this mock."""
        return token in self.issued_tokens

    def get_auth_strategy(self) -> AuthStrategy:
        """Get the configured auth strategy."""
        return self.auth_strategy


class ApiKeyAuthMock(AuthMockBase):
    """Mock for API Key Authentication strategy."""

    def __init__(
        self,
        api_key: str = "valid_api_key",
        header_name: Optional[str] = "X-API-Key",
        param_name: Optional[str] = None
    ):
        super().__init__()
        self.api_key = api_key
        self.header_name = header_name
        self.param_name = param_name

        if header_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, header_name=header_name)
        elif param_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, param_name=param_name)
        else:
            raise ValueError("Either header_name or param_name must be provided")

    def with_api_key(self, api_key: str) -> 'ApiKeyAuthMock':
        """Set the API key for the API Key Auth mock."""
        self.api_key = api_key

        if self.header_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, header_name=self.header_name)
        elif self.param_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, param_name=self.param_name)

        return self

    def as_header(self, header_name: str = "X-API-Key") -> 'ApiKeyAuthMock':
        """Configure the API Key Auth to use a header."""
        self.header_name = header_name
        self.param_name = None
        self.auth_strategy = ApiKeyAuth(api_key=self.api_key, header_name=header_name)
        return self

    def as_param(self, param_name: str = "api_key") -> 'ApiKeyAuthMock':
        """Configure the API Key Auth to use a query parameter."""
        self.header_name = None
        self.param_name = param_name
        self.auth_strategy = ApiKeyAuth(api_key=self.api_key, param_name=param_name)
        return self

    def verify_auth_header(self, header_value: str) -> bool:
        """Verify that the API Key header has the correct format."""
        if not self.header_name:
            return False  # Not using header auth

        # For API Key, we just check it's not empty
        return bool(header_value)

    def verify_token_usage(self, token: str) -> bool:
        """Verify that the API key is being used correctly."""
        return token == self.api_key

    def get_auth_strategy(self) -> AuthStrategy:
        """Get the configured auth strategy."""
        return self.auth_strategy


class CustomAuthMock(AuthMockBase):
    """Mock for Custom Authentication strategy."""

    def __init__(
        self,
        header_callback: Optional[Callable[[], Dict[str, str]]] = None,
        param_callback: Optional[Callable[[], Dict[str, str]]] = None
    ):
        super().__init__()

        # Default callbacks if none provided
        if header_callback is None and param_callback is None:
            def header_callback(): return {"X-Custom-Auth": "custom_value"}

        self.header_callback = header_callback
        self.param_callback = param_callback
        self.auth_strategy = CustomAuth(
            header_callback=header_callback if header_callback else lambda: {},
            param_callback=param_callback
        )

    def with_header_callback(self, callback: Callable[[], Dict[str, str]]) -> 'CustomAuthMock':
        """Set the header callback for the Custom Auth mock."""
        self.header_callback = callback
        self.auth_strategy = CustomAuth(
            header_callback=callback,
            param_callback=self.param_callback
        )
        return self

    def with_param_callback(self, callback: Callable[[], Dict[str, str]]) -> 'CustomAuthMock':
        """Set the parameter callback for the Custom Auth mock."""
        self.param_callback = callback
        self.auth_strategy = CustomAuth(
            header_callback=self.header_callback if self.header_callback else lambda: {},
            param_callback=callback
        )
        return self

    def with_failing_callback(self, error_message: str = "Callback failed") -> 'CustomAuthMock':
        """Configure the mock with a callback that fails."""
        def failing_callback():
            raise ValueError(error_message)

        self.header_callback = failing_callback
        self.auth_strategy = CustomAuth(
            header_callback=failing_callback,
            param_callback=self.param_callback
        )
        return self

    def verify_auth_header(self, headers: Dict[str, str]) -> bool:
        """Verify that the custom auth headers are present."""
        if not self.header_callback:
            return True  # Not using header auth

        try:
            expected_headers = self.header_callback()
            for key, value in expected_headers.items():
                if key not in headers or headers[key] != value:
                    return False
            return True
        except Exception:
            return False

    def get_auth_strategy(self) -> AuthStrategy:
        """Get the configured auth strategy."""
        return self.auth_strategy


# Verification helpers for auth testing
class AuthVerificationHelpers:
    """Helper methods for verifying authentication behavior."""

    @staticmethod
    def verify_basic_auth_header(header_value: str) -> bool:
        """Verify that a Basic Auth header is correctly formatted."""
        if not header_value.startswith("Basic "):
            return False

        try:
            encoded_part = header_value[6:]  # Skip "Basic "
            decoded = base64.b64decode(encoded_part).decode('utf-8')
            return ":" in decoded
        except Exception:
            return False

    @staticmethod
    def verify_bearer_auth_header(header_value: str) -> bool:
        """Verify that a Bearer Auth header is correctly formatted."""
        return header_value.startswith("Bearer ")

    @staticmethod
    def verify_api_key_header(header_value: str, expected_key: Optional[str] = None) -> bool:
        """Verify that an API Key header is correctly formatted."""
        if not header_value:
            return False

        if expected_key:
            return header_value == expected_key

        return True

    @staticmethod
    def verify_token_refresh(old_token: str, new_token: str) -> bool:
        """Verify that token refresh behavior is correct."""
        return old_token != new_token

    @staticmethod
    def extract_basic_auth_credentials(header_value: str) -> Tuple[str, str]:
        """Extract username and password from a Basic Auth header."""
        if not header_value.startswith("Basic "):
            raise ValueError("Not a Basic Auth header")

        encoded_part = header_value[6:]  # Skip "Basic "
        decoded = base64.b64decode(encoded_part).decode('utf-8')

        if ":" not in decoded:
            raise ValueError("Invalid Basic Auth format")

        username, password = decoded.split(":", 1)
        return username, password

    @staticmethod
    def extract_bearer_token(header_value: str) -> str:
        """Extract the token from a Bearer Auth header."""
        if not header_value.startswith("Bearer "):
            raise ValueError("Not a Bearer Auth header")

        return header_value[7:]  # Skip "Bearer "

    @staticmethod
    def assert_auth_header_format(
        headers: Dict[str, str],
        auth_type: str,
        header_name: str = "Authorization"
    ) -> None:
        """Assert that an authentication header has the correct format."""
        if header_name not in headers:
            raise AssertionError(f"Authentication header '{header_name}' not found")

        header_value = headers[header_name]

        if auth_type.lower() == "basic":
            if not AuthVerificationHelpers.verify_basic_auth_header(header_value):
                raise AssertionError(f"Invalid Basic Auth header format: {header_value}")

        elif auth_type.lower() == "bearer":
            if not AuthVerificationHelpers.verify_bearer_auth_header(header_value):
                raise AssertionError(f"Invalid Bearer Auth header format: {header_value}")

        elif auth_type.lower() == "apikey":
            if not header_value:
                raise AssertionError(f"Empty API Key header: {header_value}")

    @staticmethod
    def assert_token_usage(
        headers: Dict[str, str],
        expected_token: str,
        auth_type: str = "bearer",
        header_name: str = "Authorization"
    ) -> None:
        """Assert that a token is being used correctly."""
        if header_name not in headers:
            raise AssertionError(f"Authentication header '{header_name}' not found")

        header_value = headers[header_name]

        if auth_type.lower() == "bearer":
            token = AuthVerificationHelpers.extract_bearer_token(header_value)
            if token != expected_token:
                raise AssertionError(f"Expected token '{expected_token}', got '{token}'")

        elif auth_type.lower() == "apikey":
            if header_value != expected_token:
                raise AssertionError(f"Expected API key '{expected_token}', got '{header_value}'")

    @staticmethod
    def assert_refresh_behavior(
        old_headers: Dict[str, str],
        new_headers: Dict[str, str],
        auth_type: str = "bearer",
        header_name: str = "Authorization"
    ) -> None:
        """Assert that token refresh behavior is correct."""
        if header_name not in old_headers:
            raise AssertionError(f"Old authentication header '{header_name}' not found")

        if header_name not in new_headers:
            raise AssertionError(f"New authentication header '{header_name}' not found")

        old_value = old_headers[header_name]
        new_value = new_headers[header_name]

        if auth_type.lower() == "bearer":
            old_token = AuthVerificationHelpers.extract_bearer_token(old_value)
            new_token = AuthVerificationHelpers.extract_bearer_token(new_value)

            if old_token == new_token:
                raise AssertionError("Token was not refreshed")


# Factory functions for creating auth mocks
def create_basic_auth_mock(
    username: str = "user",
    password: str = "pass"
) -> BasicAuthMock:
    """Create a Basic Authentication mock."""
    return BasicAuthMock(username=username, password=password)


def create_bearer_auth_mock(
    token: str = "valid_token"
) -> BearerAuthMock:
    """Create a Bearer Authentication mock."""
    return BearerAuthMock(token=token)


def create_api_key_auth_mock(
    api_key: str = "valid_api_key",
    header_name: Optional[str] = "X-API-Key",
    param_name: Optional[str] = None
) -> ApiKeyAuthMock:
    """Create an API Key Authentication mock."""
    return ApiKeyAuthMock(api_key=api_key, header_name=header_name, param_name=param_name)


def create_custom_auth_mock(
    header_callback: Optional[Callable[[], Dict[str, str]]] = None,
    param_callback: Optional[Callable[[], Dict[str, str]]] = None
) -> CustomAuthMock:
    """Create a Custom Authentication mock."""
    return CustomAuthMock(header_callback=header_callback, param_callback=param_callback)

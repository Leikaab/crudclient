"""
API Key authentication mock for testing.

This module provides a mock for API Key Authentication strategy with support
for key validation, rate limiting, and usage tracking.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Pattern, Set, Tuple, TypeVar

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import ApiKeyAuth

from ..response_builder.response import MockResponse
from .api_key_rate_limiter import ApiKeyRateLimiter
from .api_key_usage_tracker import ApiKeyUsageTracker
from .api_key_validator import ApiKeyValidator
from .base import AuthMockBase

T = TypeVar("T", bound="ApiKeyAuthMock")

class ApiKeyAuthMock(AuthMockBase):
    """
    Mock for API Key Authentication strategy with enhanced validation and rate limiting.

    This class provides a configurable mock implementation of the API Key Authentication
    strategy, with support for key validation, rate limiting, and usage tracking.
    """

    api_key: str
    header_name: Optional[str]
    param_name: Optional[str]
    validator: ApiKeyValidator
    rate_limiter: ApiKeyRateLimiter
    usage_tracker: ApiKeyUsageTracker
    auth_strategy: ApiKeyAuth

    def __init__(self, api_key: str = "valid_api_key", header_name: Optional[str] = "X-API-Key", param_name: Optional[str] = None) -> None:
        """
        Initialize an API Key Authentication mock.

        Args:
            api_key: The default API key
            header_name: Name of the header for API key (None if using param)
            param_name: Name of the query parameter for API key (None if using header)
        """
        ...

    def with_api_key(self, api_key: str) -> ApiKeyAuthMock:
        """
        Set the API key for the API Key Auth mock.

        Args:
            api_key: The API key to use

        Returns:
            Self for method chaining
        """
        ...

    def with_additional_valid_key(self, api_key: str) -> ApiKeyAuthMock:
        """
        Add an additional valid API key.

        Args:
            api_key: An additional valid API key

        Returns:
            Self for method chaining
        """
        ...

    def with_key_metadata(
        self,
        api_key: Optional[str] = None,
        owner: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        tier: Optional[str] = None,
        expires_in_seconds: Optional[int] = None,
    ) -> ApiKeyAuthMock:
        """
        Set metadata for a specific API key or the current key.

        Args:
            api_key: The API key to set metadata for (defaults to the current key)
            owner: Owner of the API key
            permissions: List of permissions associated with the key
            tier: Service tier associated with the key
            expires_in_seconds: Number of seconds until the key expires

        Returns:
            Self for method chaining
        """
        ...

    def with_key_format_validation(self, pattern: str) -> ApiKeyAuthMock:
        """
        Set a regex pattern that valid API keys must match.

        Args:
            pattern: Regular expression pattern for API key validation

        Returns:
            Self for method chaining
        """
        ...

    def revoke_key(self, api_key: Optional[str] = None) -> ApiKeyAuthMock:
        """
        Revoke a specific API key or the current key.

        Args:
            api_key: The API key to revoke (defaults to the current key)

        Returns:
            Self for method chaining
        """
        ...

    def with_rate_limiting(self, requests_per_period: int = 100, period_seconds: int = 3600) -> ApiKeyAuthMock:
        """
        Enable rate limiting for API keys.

        Args:
            requests_per_period: Number of requests allowed per period
            period_seconds: Period length in seconds

        Returns:
            Self for method chaining
        """
        ...

    def with_usage_tracking(self) -> ApiKeyAuthMock:
        """
        Enable usage tracking for API keys.

        Returns:
            Self for method chaining
        """
        ...

    def as_header(self, header_name: str = "X-API-Key") -> ApiKeyAuthMock:
        """
        Configure the API Key Auth to use a header.

        Args:
            header_name: Name of the header for the API key

        Returns:
            Self for method chaining
        """
        ...

    def as_param(self, param_name: str = "api_key") -> ApiKeyAuthMock:
        """
        Configure the API Key Auth to use a query parameter.

        Args:
            param_name: Name of the query parameter for the API key

        Returns:
            Self for method chaining
        """
        ...

    def track_request(self, api_key: str, endpoint: Optional[str] = None) -> bool:
        """
        Track a request for rate limiting and usage tracking purposes.

        Args:
            api_key: The API key used for the request
            endpoint: The endpoint being accessed (for usage tracking)

        Returns:
            True if the request is within rate limits, False otherwise
        """
        ...

    def validate_key(self, api_key: str) -> bool:
        """
        Validate an API key against all configured rules.

        Args:
            api_key: The API key to validate

        Returns:
            True if the key is valid, False otherwise
        """
        ...

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the API Key header has the correct format and key is valid.

        Args:
            header_value: The value of the API key header

        Returns:
            True if the header is valid, False otherwise
        """
        ...

    def verify_token_usage(self, token: str) -> bool:
        """
        Verify that the API key is being used correctly.

        Args:
            token: The API key to verify

        Returns:
            True if the key is being used correctly, False otherwise
        """
        ...

    def get_usage_stats(self) -> Dict:
        """
        Get usage statistics for API keys and endpoints.

        Returns:
            Dictionary with usage statistics
        """
        ...

    def get_rate_limit_status(self, api_key: Optional[str] = None) -> Dict:
        """
        Get rate limit status for a specific API key or the current key.

        Args:
            api_key: The API key to get status for (defaults to the current key)

        Returns:
            Dictionary with rate limit status
        """
        ...

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured ApiKeyAuth strategy
        """
        ...

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers for the current API key.

        Returns:
            A tuple of (header_name, api_key) or None if using param auth
        """
        ...

    def handle_auth_error(self, response: MockResponse) -> bool:
        """
        Handle authentication errors (API keys don't have a refresh mechanism).

        Args:
            response: The error response that triggered the auth error

        Returns:
            Always False for API keys as they don't have a refresh mechanism
        """
        ...

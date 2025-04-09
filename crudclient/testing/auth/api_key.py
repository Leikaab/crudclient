"""
API Key authentication mock for testing.

This module provides a mock for API Key Authentication strategy with support
for key validation, rate limiting, and usage tracking.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import ApiKeyAuth

from .base import AuthMockBase


class ApiKeyAuthMock(AuthMockBase):
    """
    Mock for API Key Authentication strategy with enhanced validation and rate limiting.

    This class provides a configurable mock implementation of the API Key Authentication
    strategy, with support for key validation, rate limiting, and usage tracking.
    """

    def __init__(
        self,
        api_key: str = "valid_api_key",
        header_name: Optional[str] = "X-API-Key",
        param_name: Optional[str] = None
    ):
        """
        Initialize an API Key Authentication mock.

        Args:
            api_key: The default API key
            header_name: Name of the header for API key (None if using param)
            param_name: Name of the query parameter for API key (None if using header)
        """
        super().__init__()
        self.api_key = api_key
        self.header_name = header_name
        self.param_name = param_name

        # Key validation
        self.valid_keys: Set[str] = {api_key}
        self.key_format_pattern = None
        self.key_metadata: Dict[str, Dict] = {
            api_key: {
                "issued_at": datetime.now(),
                "expires_at": None,
                "owner": "default_user",
                "permissions": ["read", "write"],
                "tier": "standard"
            }
        }
        self.revoked_keys: Set[str] = set()

        # Rate limiting
        self.rate_limit_enabled = False
        self.rate_limit_requests = 100
        self.rate_limit_period = 3600  # seconds (1 hour)
        self.request_history: Dict[str, List[datetime]] = {api_key: []}

        # Usage tracking
        self.usage_tracking_enabled = False
        self.usage_by_endpoint: Dict[str, int] = {}
        self.usage_by_key: Dict[str, int] = {api_key: 0}

        # Initialize auth strategy
        if header_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, header_name=header_name)
        elif param_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, param_name=param_name)
        else:
            raise ValueError("Either header_name or param_name must be provided")

    def with_api_key(self, api_key: str) -> 'ApiKeyAuthMock':
        """
        Set the API key for the API Key Auth mock.

        Args:
            api_key: The API key to use

        Returns:
            Self for method chaining
        """
        self.api_key = api_key
        self.valid_keys.add(api_key)

        # Initialize key metadata if not exists
        if api_key not in self.key_metadata:
            self.key_metadata[api_key] = {
                "issued_at": datetime.now(),
                "expires_at": None,
                "owner": "default_user",
                "permissions": ["read", "write"],
                "tier": "standard"
            }

        # Initialize request history if not exists
        if api_key not in self.request_history:
            self.request_history[api_key] = []

        # Initialize usage tracking if not exists
        if api_key not in self.usage_by_key:
            self.usage_by_key[api_key] = 0

        # Update auth strategy
        if self.header_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, header_name=self.header_name)
        elif self.param_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, param_name=self.param_name)

        return self

    def with_additional_valid_key(self, api_key: str) -> 'ApiKeyAuthMock':
        """
        Add an additional valid API key.

        Args:
            api_key: An additional valid API key

        Returns:
            Self for method chaining
        """
        self.valid_keys.add(api_key)

        # Initialize key metadata if not exists
        if api_key not in self.key_metadata:
            self.key_metadata[api_key] = {
                "issued_at": datetime.now(),
                "expires_at": None,
                "owner": "default_user",
                "permissions": ["read", "write"],
                "tier": "standard"
            }

        # Initialize request history if not exists
        if api_key not in self.request_history:
            self.request_history[api_key] = []

        # Initialize usage tracking if not exists
        if api_key not in self.usage_by_key:
            self.usage_by_key[api_key] = 0

        return self

    def with_key_metadata(
        self,
        api_key: Optional[str] = None,
        owner: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        tier: Optional[str] = None,
        expires_in_seconds: Optional[int] = None
    ) -> 'ApiKeyAuthMock':
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
        target_key = api_key or self.api_key

        if target_key not in self.key_metadata:
            self.key_metadata[target_key] = {
                "issued_at": datetime.now(),
                "expires_at": None,
                "owner": "default_user",
                "permissions": ["read", "write"],
                "tier": "standard"
            }

        metadata = self.key_metadata[target_key]

        if owner:
            metadata["owner"] = owner
        if permissions:
            metadata["permissions"] = permissions
        if tier:
            metadata["tier"] = tier
        if expires_in_seconds is not None:
            metadata["expires_at"] = datetime.now() + timedelta(seconds=expires_in_seconds)

        return self

    def with_key_format_validation(self, pattern: str) -> 'ApiKeyAuthMock':
        """
        Set a regex pattern that valid API keys must match.

        Args:
            pattern: Regular expression pattern for API key validation

        Returns:
            Self for method chaining
        """
        import re
        self.key_format_pattern = re.compile(pattern)
        return self

    def revoke_key(self, api_key: Optional[str] = None) -> 'ApiKeyAuthMock':
        """
        Revoke a specific API key or the current key.

        Args:
            api_key: The API key to revoke (defaults to the current key)

        Returns:
            Self for method chaining
        """
        target_key = api_key or self.api_key
        if target_key in self.valid_keys:
            self.revoked_keys.add(target_key)
        return self

    def with_rate_limiting(
        self,
        requests_per_period: int = 100,
        period_seconds: int = 3600
    ) -> 'ApiKeyAuthMock':
        """
        Enable rate limiting for API keys.

        Args:
            requests_per_period: Number of requests allowed per period
            period_seconds: Period length in seconds

        Returns:
            Self for method chaining
        """
        self.rate_limit_enabled = True
        self.rate_limit_requests = requests_per_period
        self.rate_limit_period = period_seconds
        return self

    def with_usage_tracking(self) -> 'ApiKeyAuthMock':
        """
        Enable usage tracking for API keys.

        Returns:
            Self for method chaining
        """
        self.usage_tracking_enabled = True
        return self

    def as_header(self, header_name: str = "X-API-Key") -> 'ApiKeyAuthMock':
        """
        Configure the API Key Auth to use a header.

        Args:
            header_name: Name of the header for the API key

        Returns:
            Self for method chaining
        """
        self.header_name = header_name
        self.param_name = None
        self.auth_strategy = ApiKeyAuth(api_key=self.api_key, header_name=header_name)
        return self

    def as_param(self, param_name: str = "api_key") -> 'ApiKeyAuthMock':
        """
        Configure the API Key Auth to use a query parameter.

        Args:
            param_name: Name of the query parameter for the API key

        Returns:
            Self for method chaining
        """
        self.header_name = None
        self.param_name = param_name
        self.auth_strategy = ApiKeyAuth(api_key=self.api_key, param_name=param_name)
        return self

    def track_request(self, api_key: str, endpoint: Optional[str] = None) -> bool:
        """
        Track a request for rate limiting and usage tracking purposes.

        Args:
            api_key: The API key used for the request
            endpoint: The endpoint being accessed (for usage tracking)

        Returns:
            True if the request is within rate limits, False otherwise
        """
        # Record request time for rate limiting
        now = datetime.now()
        if api_key not in self.request_history:
            self.request_history[api_key] = []
        self.request_history[api_key].append(now)

        # Track usage if enabled
        if self.usage_tracking_enabled:
            if api_key not in self.usage_by_key:
                self.usage_by_key[api_key] = 0
            self.usage_by_key[api_key] += 1

            if endpoint:
                if endpoint not in self.usage_by_endpoint:
                    self.usage_by_endpoint[endpoint] = 0
                self.usage_by_endpoint[endpoint] += 1

        # Check rate limit if enabled
        if self.rate_limit_enabled:
            # Clean up old requests outside the current period
            period_start = now - timedelta(seconds=self.rate_limit_period)
            self.request_history[api_key] = [
                t for t in self.request_history[api_key] if t >= period_start
            ]

            # Check if rate limit exceeded
            return len(self.request_history[api_key]) <= self.rate_limit_requests

        return True  # No rate limiting or limit not exceeded

    def validate_key(self, api_key: str) -> bool:
        """
        Validate an API key against all configured rules.

        Args:
            api_key: The API key to validate

        Returns:
            True if the key is valid, False otherwise
        """
        # Check if key is valid
        if api_key not in self.valid_keys:
            return False

        # Check if key has been revoked
        if api_key in self.revoked_keys:
            return False

        # Check key format if pattern is set
        if self.key_format_pattern and not self.key_format_pattern.match(api_key):
            return False

        # Check key expiration
        if api_key in self.key_metadata:
            expires_at = self.key_metadata[api_key].get("expires_at")
            if expires_at and datetime.now() > expires_at:
                return False

        # Check rate limit
        if self.rate_limit_enabled:
            if not self.track_request(api_key):
                return False
        elif self.usage_tracking_enabled:
            # Just track the request without rate limiting
            self.track_request(api_key)

        return True

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the API Key header has the correct format and key is valid.

        Args:
            header_value: The value of the API key header

        Returns:
            True if the header is valid, False otherwise
        """
        if not self.header_name:
            return False  # Not using header auth

        # For API Key, we check it's not empty and it's valid
        return bool(header_value) and self.validate_key(header_value)

    def verify_token_usage(self, token: str) -> bool:
        """
        Verify that the API key is being used correctly.

        Args:
            token: The API key to verify

        Returns:
            True if the key is being used correctly, False otherwise
        """
        return self.validate_key(token)

    def get_usage_stats(self) -> Dict:
        """
        Get usage statistics for API keys and endpoints.

        Returns:
            Dictionary with usage statistics
        """
        return {
            "by_key": self.usage_by_key,
            "by_endpoint": self.usage_by_endpoint,
            "total_requests": sum(self.usage_by_key.values())
        }

    def get_rate_limit_status(self, api_key: Optional[str] = None) -> Dict:
        """
        Get rate limit status for a specific API key or the current key.

        Args:
            api_key: The API key to get status for (defaults to the current key)

        Returns:
            Dictionary with rate limit status
        """
        target_key = api_key or self.api_key

        if not self.rate_limit_enabled:
            return {"enabled": False}

        if target_key not in self.request_history:
            return {
                "enabled": True,
                "limit": self.rate_limit_requests,
                "remaining": self.rate_limit_requests,
                "reset": datetime.now() + timedelta(seconds=self.rate_limit_period)
            }

        # Clean up old requests
        now = datetime.now()
        period_start = now - timedelta(seconds=self.rate_limit_period)
        self.request_history[target_key] = [
            t for t in self.request_history[target_key] if t >= period_start
        ]

        # Calculate remaining requests
        used = len(self.request_history[target_key])
        remaining = max(0, self.rate_limit_requests - used)

        # Calculate reset time (when the oldest request will expire)
        if used > 0:
            oldest = min(self.request_history[target_key])
            reset = oldest + timedelta(seconds=self.rate_limit_period)
        else:
            reset = now + timedelta(seconds=self.rate_limit_period)

        return {
            "enabled": True,
            "limit": self.rate_limit_requests,
            "remaining": remaining,
            "reset": reset,
            "used": used
        }

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured ApiKeyAuth strategy
        """
        return self.auth_strategy

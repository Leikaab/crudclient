import re
from datetime import datetime, timedelta
from typing import (  # Added Tuple, TYPE_CHECKING
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Tuple,
)

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import ApiKeyAuth

from .api_key_rate_limiter import ApiKeyRateLimiter
from .api_key_usage_tracker import ApiKeyUsageTracker
from .api_key_validator import ApiKeyValidator
from .base import AuthMockBase

if TYPE_CHECKING:  # Added TYPE_CHECKING block
    from ..response_builder import MockResponse


class ApiKeyAuthMock(AuthMockBase):
    def __init__(self, api_key: str = "valid_api_key", header_name: Optional[str] = "X-API-Key", param_name: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.header_name = header_name
        self.param_name = param_name

        # Initialize components
        self.validator = ApiKeyValidator()
        self.rate_limiter = ApiKeyRateLimiter()
        self.usage_tracker = ApiKeyUsageTracker()

        # Add initial key
        self.validator.add_valid_key(api_key)
        self.validator.set_key_metadata(api_key=api_key, owner="default_user", permissions=["read", "write"], tier="standard")
        self.rate_limiter.initialize_key(api_key)
        self.usage_tracker.initialize_key(api_key)

        # Initialize auth strategy
        if header_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, header_name=header_name)
        elif param_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, param_name=param_name)
        else:
            raise ValueError("Either header_name or param_name must be provided")

    def with_api_key(self, api_key: str) -> "ApiKeyAuthMock":
        self.api_key = api_key
        self.validator.add_valid_key(api_key)
        self.validator.set_key_metadata(api_key=api_key, owner="default_user", permissions=["read", "write"], tier="standard")
        self.rate_limiter.initialize_key(api_key)
        self.usage_tracker.initialize_key(api_key)

        # Update auth strategy
        if self.header_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, header_name=self.header_name)
        elif self.param_name:
            self.auth_strategy = ApiKeyAuth(api_key=api_key, param_name=self.param_name)

        return self

    def with_additional_valid_key(self, api_key: str) -> "ApiKeyAuthMock":
        self.validator.add_valid_key(api_key)
        self.validator.set_key_metadata(api_key=api_key, owner="default_user", permissions=["read", "write"], tier="standard")
        self.rate_limiter.initialize_key(api_key)
        self.usage_tracker.initialize_key(api_key)
        return self

    def with_key_metadata(
        self,
        api_key: Optional[str] = None,
        owner: Optional[str] = None,
        permissions: Optional[List[str]] = None,
        tier: Optional[str] = None,
        expires_in_seconds: Optional[int] = None,
    ) -> "ApiKeyAuthMock":
        target_key = api_key or self.api_key
        expires_at = None
        if expires_in_seconds is not None:
            expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)

        self.validator.set_key_metadata(api_key=target_key, owner=owner, permissions=permissions, tier=tier, expires_at=expires_at)
        return self

    def with_key_format_validation(self, pattern: str) -> "ApiKeyAuthMock":
        self.validator.set_key_format_pattern(re.compile(pattern))
        return self

    def revoke_key(self, api_key: Optional[str] = None) -> "ApiKeyAuthMock":
        target_key = api_key or self.api_key
        self.validator.revoke_key(target_key)
        return self

    def with_rate_limiting(self, requests_per_period: int = 100, period_seconds: int = 3600) -> "ApiKeyAuthMock":
        self.rate_limiter.enable_rate_limiting(requests_per_period=requests_per_period, period_seconds=period_seconds)
        return self

    def with_usage_tracking(self) -> "ApiKeyAuthMock":
        self.usage_tracker.enable_usage_tracking()
        return self

    def as_header(self, header_name: str = "X-API-Key") -> "ApiKeyAuthMock":
        self.header_name = header_name
        self.param_name = None
        self.auth_strategy = ApiKeyAuth(api_key=self.api_key, header_name=header_name)
        return self

    def as_param(self, param_name: str = "api_key") -> "ApiKeyAuthMock":
        self.header_name = None
        self.param_name = param_name
        self.auth_strategy = ApiKeyAuth(api_key=self.api_key, param_name=param_name)
        return self

    def track_request(self, api_key: str, endpoint: Optional[str] = None) -> bool:
        # Track usage
        self.usage_tracker.track_request(api_key, endpoint)

        # Check rate limit
        return self.rate_limiter.track_request(api_key)

    def validate_key(self, api_key: str) -> bool:
        # Validate the key
        if not self.validator.validate_key(api_key):
            return False

        # Check rate limit if enabled
        if self.rate_limiter.rate_limit_enabled:
            if not self.track_request(api_key):
                return False
        elif self.usage_tracker.usage_tracking_enabled:
            # Just track the request without rate limiting
            self.usage_tracker.track_request(api_key)

        return True

    def verify_auth_header(self, header_value: str) -> bool:
        if not self.header_name:
            return False  # Not using header auth

        # For API Key, we check it's not empty and it's valid
        return bool(header_value) and self.validate_key(header_value)

    def verify_token_usage(self, token: str) -> bool:
        return self.validate_key(token)

    def get_usage_stats(self) -> Dict:
        return self.usage_tracker.get_usage_stats()

    def get_rate_limit_status(self, api_key: Optional[str] = None) -> Dict:
        target_key = api_key or self.api_key
        return self.rate_limiter.get_rate_limit_status(target_key)

    def get_auth_strategy(self) -> AuthStrategy:
        return self.auth_strategy

    # --- Added Abstract Method Implementations ---

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        if self.header_name and self.api_key:
            return (self.header_name, self.api_key)
        # If using param_name, no standard header tuple is returned here.
        return None

    def handle_auth_error(self, response: "MockResponse") -> bool:
        # API keys generally don't have a refresh mechanism
        return False

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from ..response_builder import MockResponse


class AuthMockBase(ABC):
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

    def with_failure(self, failure_type: str = "invalid_token", status_code: int = 401, message: str = "Authentication failed") -> "AuthMockBase":
        self.should_fail = True
        self.failure_type = failure_type
        self.failure_status_code = status_code
        self.failure_message = message
        return self

    def with_success(self) -> "AuthMockBase":
        self.should_fail = False
        return self

    def with_token_expiration(self, expires_in_seconds: int = 3600) -> "AuthMockBase":
        self.token_expired = False
        self.token_expiry_time = datetime.now() + timedelta(seconds=expires_in_seconds)
        return self

    def with_expired_token(self) -> "AuthMockBase":
        self.token_expired = True
        self.token_expiry_time = datetime.now() - timedelta(seconds=60)
        return self

    def with_refresh_token(self, refresh_token: str = "refresh_token", max_refresh_attempts: int = 3) -> "AuthMockBase":
        self.refresh_token = refresh_token
        self.refresh_token_expired = False
        self.refresh_attempts = 0
        self.max_refresh_attempts = max_refresh_attempts
        return self

    def with_expired_refresh_token(self) -> "AuthMockBase":
        self.refresh_token = "expired_refresh_token"
        self.refresh_token_expired = True
        return self

    def with_mfa_required(self, verified: bool = False) -> "AuthMockBase":
        self.mfa_required = True
        self.mfa_verified = verified
        return self

    def fail_after(self, request_count: int) -> "AuthMockBase":
        self.fail_after_requests = request_count
        return self

    def with_custom_header(self, name: str, value: str) -> "AuthMockBase":
        self.custom_headers[name] = value
        return self

    def with_custom_param(self, name: str, value: str) -> "AuthMockBase":
        self.custom_params[name] = value
        return self

    def is_token_expired(self) -> bool:
        if self.token_expired:
            return True
        if self.token_expiry_time and datetime.now() > self.token_expiry_time:
            self.token_expired = True
            return True
        return False

    def can_refresh_token(self) -> bool:
        if not self.refresh_token:
            return False
        if self.refresh_token_expired:
            return False
        if self.refresh_attempts >= self.max_refresh_attempts:
            return False
        return True

    def refresh(self) -> bool:
        if not self.can_refresh_token():
            return False

        self.refresh_attempts += 1
        self.token_expired = False
        self.token_expiry_time = datetime.now() + timedelta(seconds=3600)
        return True

    def should_fail_auth(self) -> bool:
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
        error_type = self.failure_type
        status_code = self.failure_status_code

        if self.is_token_expired():
            error_type = "expired_token"
            status_code = 401
        elif self.mfa_required and not self.mfa_verified:
            error_type = "mfa_required"
            status_code = 401

        from ..response_builder import ResponseBuilder

        return ResponseBuilder.create_auth_error(error_type=error_type, status_code=status_code)

    @abstractmethod
    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        pass

    @abstractmethod
    def handle_auth_error(self, response: "MockResponse") -> bool:
        pass

    def verify_auth_header(self, header_value: str) -> bool:
        return True

    def verify_token_usage(self, token: str) -> bool:
        return True

    def verify_refresh_behavior(self, old_token: str, new_token: str) -> bool:
        return old_token != new_token

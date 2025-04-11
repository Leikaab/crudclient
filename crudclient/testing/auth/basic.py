import base64
import re
from typing import TYPE_CHECKING, Optional, Tuple  # Added Tuple, TYPE_CHECKING

from crudclient.auth.base import AuthStrategy
from crudclient.auth.basic import BasicAuth

from .base import AuthMockBase

if TYPE_CHECKING:  # Added TYPE_CHECKING block
    from ..response_builder import MockResponse


class BasicAuthMock(AuthMockBase):

    def __init__(self, username: str = "user", password: str = "pass"):
        super().__init__()
        self.username = username
        self.password = password
        self.auth_strategy = BasicAuth(username=username, password=password)
        self.valid_credentials = [(username, password)]
        self.username_pattern = None
        self.password_pattern = None
        self.password_min_length = None
        self.password_complexity = False
        self.case_sensitive = True
        self.max_attempts = None
        self.current_attempts = 0

    def with_credentials(self, username: str, password: str) -> "BasicAuthMock":
        self.username = username
        self.password = password
        self.auth_strategy = BasicAuth(username=username, password=password)
        self.valid_credentials = [(username, password)]
        return self

    def with_additional_valid_credentials(self, username: str, password: str) -> "BasicAuthMock":
        self.valid_credentials.append((username, password))
        return self

    def with_username_pattern(self, pattern: str) -> "BasicAuthMock":
        self.username_pattern = re.compile(pattern)
        return self

    def with_password_requirements(self, min_length: Optional[int] = None, complexity: bool = False) -> "BasicAuthMock":
        self.password_min_length = min_length
        self.password_complexity = complexity
        return self

    def with_case_insensitive_username(self) -> "BasicAuthMock":
        self.case_sensitive = False
        return self

    def with_max_attempts(self, max_attempts: int) -> "BasicAuthMock":
        self.max_attempts = max_attempts
        self.current_attempts = 0
        return self

    def verify_auth_header(self, header_value: str) -> bool:
        if not header_value.startswith("Basic "):
            return False

        try:
            encoded_part = header_value[6:]  # Skip "Basic "
            decoded = base64.b64decode(encoded_part).decode("utf-8")
            if ":" not in decoded:
                return False

            username, password = decoded.split(":", 1)
            return self.validate_credentials(username, password)
        except Exception:
            return False

    def validate_credentials(self, username: str, password: str) -> bool:
        # Track authentication attempts if max_attempts is set
        if self.max_attempts is not None:
            self.current_attempts += 1
            if self.current_attempts > self.max_attempts:
                return False

        # Check username pattern if configured
        if self.username_pattern and not self.username_pattern.match(username):
            return False

        # Check password requirements if configured
        if self.password_min_length is not None and len(password) < self.password_min_length:
            return False

        # Check password complexity if required
        if self.password_complexity:
            # Simple complexity check: must contain at least one uppercase, one lowercase,
            # one digit, and one special character
            if not (
                re.search(r"[A-Z]", password)
                and re.search(r"[a-z]", password)
                and re.search(r"[0-9]", password)
                and re.search(r"[^A-Za-z0-9]", password)
            ):
                return False

        # Check against valid credentials
        for valid_username, valid_password in self.valid_credentials:
            if self.case_sensitive:
                username_match = username == valid_username
            else:
                username_match = username.lower() == valid_username.lower()

            if username_match and password == valid_password:
                self.current_attempts = 0  # Reset on success
                return True

        return False

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        if not self.username or self.password is None:
            # Should ideally not happen due to __init__ defaults
            return None
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        return ("Authorization", f"Basic {encoded_credentials}")

    def handle_auth_error(self, response: "MockResponse") -> bool:
        # Basic auth typically fails outright, no refresh mechanism
        return False

    def get_auth_strategy(self) -> AuthStrategy:
        return self.auth_strategy

    def reset_attempts(self) -> "BasicAuthMock":
        self.current_attempts = 0
        return self

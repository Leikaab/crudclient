"""
Basic authentication mock for testing.

This module provides a mock for Basic Authentication strategy with support
for username/password validation and various authentication scenarios.
"""

import base64
import re
from typing import Optional

from crudclient.auth.base import AuthStrategy
from crudclient.auth.basic import BasicAuth

from .base import AuthMockBase


class BasicAuthMock(AuthMockBase):
    """
    Mock for Basic Authentication strategy with enhanced validation capabilities.

    This class provides a configurable mock implementation of the Basic Authentication
    strategy, with support for username/password validation, pattern matching,
    case sensitivity options, and attempt limiting.
    """

    def __init__(self, username: str = "user", password: str = "pass"):
        """
        Initialize a Basic Authentication mock.

        Args:
            username: The default username
            password: The default password
        """
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

    def with_credentials(self, username: str, password: str) -> 'BasicAuthMock':
        """
        Set the credentials for the Basic Auth mock.

        Args:
            username: The username to use
            password: The password to use

        Returns:
            Self for method chaining
        """
        self.username = username
        self.password = password
        self.auth_strategy = BasicAuth(username=username, password=password)
        self.valid_credentials = [(username, password)]
        return self

    def with_additional_valid_credentials(self, username: str, password: str) -> 'BasicAuthMock':
        """
        Add additional valid credentials for the Basic Auth mock.

        This allows the mock to accept multiple sets of valid credentials.

        Args:
            username: An additional valid username
            password: The corresponding password

        Returns:
            Self for method chaining
        """
        self.valid_credentials.append((username, password))
        return self

    def with_username_pattern(self, pattern: str) -> 'BasicAuthMock':
        """
        Set a regex pattern that valid usernames must match.

        Args:
            pattern: Regular expression pattern for username validation

        Returns:
            Self for method chaining
        """
        self.username_pattern = re.compile(pattern)
        return self

    def with_password_requirements(
        self,
        min_length: Optional[int] = None,
        complexity: bool = False
    ) -> 'BasicAuthMock':
        """
        Set password requirements for validation.

        Args:
            min_length: Minimum password length (None for no minimum)
            complexity: Whether to enforce password complexity rules

        Returns:
            Self for method chaining
        """
        self.password_min_length = min_length
        self.password_complexity = complexity
        return self

    def with_case_insensitive_username(self) -> 'BasicAuthMock':
        """
        Configure the mock to validate usernames in a case-insensitive manner.

        Returns:
            Self for method chaining
        """
        self.case_sensitive = False
        return self

    def with_max_attempts(self, max_attempts: int) -> 'BasicAuthMock':
        """
        Set the maximum number of authentication attempts before failing.

        Args:
            max_attempts: Maximum number of allowed authentication attempts

        Returns:
            Self for method chaining
        """
        self.max_attempts = max_attempts
        self.current_attempts = 0
        return self

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the Basic Auth header has the correct format and credentials.

        Args:
            header_value: The value of the Authorization header

        Returns:
            True if the header is valid, False otherwise
        """
        if not header_value.startswith("Basic "):
            return False

        try:
            encoded_part = header_value[6:]  # Skip "Basic "
            decoded = base64.b64decode(encoded_part).decode('utf-8')
            if ":" not in decoded:
                return False

            username, password = decoded.split(":", 1)
            return self.validate_credentials(username, password)
        except Exception:
            return False

    def validate_credentials(self, username: str, password: str) -> bool:
        """
        Validate the provided username and password against configured rules.

        Args:
            username: The username to validate
            password: The password to validate

        Returns:
            True if the credentials are valid, False otherwise
        """
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
            if not (re.search(r'[A-Z]', password)
                    and re.search(r'[a-z]', password)
                    and re.search(r'[0-9]', password)
                    and re.search(r'[^A-Za-z0-9]', password)):
                return False

        # Check against valid credentials
        for valid_username, valid_password in self.valid_credentials:
            if self.case_sensitive:
                username_match = (username == valid_username)
            else:
                username_match = (username.lower() == valid_username.lower())

            if username_match and password == valid_password:
                return True

        return False

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured BasicAuth strategy
        """
        return self.auth_strategy

    def reset_attempts(self) -> 'BasicAuthMock':
        """
        Reset the authentication attempt counter.

        Returns:
            Self for method chaining
        """
        self.current_attempts = 0
        return self

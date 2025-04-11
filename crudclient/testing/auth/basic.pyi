"""
Basic authentication mock for testing.

This module provides a mock implementation of Basic authentication
for testing API clients with username/password authentication.
"""

import base64
import re
from typing import TYPE_CHECKING, List, Optional, Pattern, Tuple

from crudclient.auth.base import AuthStrategy
from crudclient.auth.basic import BasicAuth

from .base import AuthMockBase

if TYPE_CHECKING:
    from ..response_builder import MockResponse

class BasicAuthMock(AuthMockBase):
    """
    Mock implementation of Basic authentication.

    This class provides a configurable mock for Basic authentication,
    supporting username/password validation, pattern matching, and
    various authentication scenarios.
    """

    username: str
    password: str
    auth_strategy: BasicAuth
    valid_credentials: List[Tuple[str, str]]
    username_pattern: Optional[Pattern]
    password_pattern: Optional[Pattern]
    password_min_length: Optional[int]
    password_complexity: bool
    case_sensitive: bool
    max_attempts: Optional[int]
    current_attempts: int

    def __init__(self, username: str = "user", password: str = "pass"):
        """
        Initialize a BasicAuthMock instance.

        Args:
            username: Initial username
            password: Initial password
        """
        ...

    def with_credentials(self, username: str, password: str) -> "BasicAuthMock":
        """
        Configure the mock with specific credentials.

        Args:
            username: Username
            password: Password

        Returns:
            Self for method chaining
        """
        ...

    def with_additional_valid_credentials(self, username: str, password: str) -> "BasicAuthMock":
        """
        Add additional valid credentials.

        Args:
            username: Additional valid username
            password: Additional valid password

        Returns:
            Self for method chaining
        """
        ...

    def with_username_pattern(self, pattern: str) -> "BasicAuthMock":
        """
        Configure the mock with username pattern validation.

        Args:
            pattern: Regular expression pattern for valid usernames

        Returns:
            Self for method chaining
        """
        ...

    def with_password_requirements(self, min_length: Optional[int] = None, complexity: bool = False) -> "BasicAuthMock":
        """
        Configure the mock with password requirements.

        Args:
            min_length: Minimum password length
            complexity: Whether to enforce password complexity rules

        Returns:
            Self for method chaining
        """
        ...

    def with_case_insensitive_username(self) -> "BasicAuthMock":
        """
        Configure the mock to use case-insensitive username matching.

        Returns:
            Self for method chaining
        """
        ...

    def with_max_attempts(self, max_attempts: int) -> "BasicAuthMock":
        """
        Configure the mock with a maximum number of authentication attempts.

        Args:
            max_attempts: Maximum number of authentication attempts

        Returns:
            Self for method chaining
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

    def validate_credentials(self, username: str, password: str) -> bool:
        """
        Validate a set of credentials.

        Args:
            username: Username to validate
            password: Password to validate

        Returns:
            True if the credentials are valid, False otherwise
        """
        ...

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers.

        Returns:
            Tuple of (header_name, header_value) or None if no credentials are available
        """
        ...

    def handle_auth_error(self, response: "MockResponse") -> bool:
        """
        Handle an authentication error.

        Args:
            response: Mock response with authentication error

        Returns:
            True if the error was handled successfully, False otherwise
        """
        ...

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the underlying authentication strategy.

        Returns:
            BasicAuth instance
        """
        ...

    def reset_attempts(self) -> "BasicAuthMock":
        """
        Reset the authentication attempt counter.

        Returns:
            Self for method chaining
        """
        ...

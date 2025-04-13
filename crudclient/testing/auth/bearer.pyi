"""
Bearer authentication mock for testing.

This module provides a mock implementation of Bearer authentication
for testing API clients with token-based authentication.
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Type

if TYPE_CHECKING:
    from ..response_builder import MockResponse

from crudclient.auth.base import AuthStrategy
from crudclient.auth.bearer import BearerAuth

from .base import AuthMockBase

class BearerAuthMock(AuthMockBase):
    """
    Mock implementation of Bearer authentication.

    This class provides a configurable mock for Bearer token authentication,
    supporting token validation, expiration, refresh, and various other
    authentication scenarios.
    """

    token: str
    auth_strategy: BearerAuth
    issued_tokens: List[str]
    revoked_tokens: Set[str]
    token_metadata: Dict[str, Dict]
    valid_token_prefixes: Set[str]
    token_format_pattern: Optional[Type]
    required_scopes: List[str]
    jwt_validation: bool
    token_type: str

    def __init__(self, token: str = "valid_token"):
        """
        Initialize a BearerAuthMock instance.

        Args:
            token: Initial bearer token value
        """
        ...

    def with_token(self, token: str) -> "BearerAuthMock":
        """
        Configure the mock with a specific token.

        Args:
            token: Bearer token value

        Returns:
            Self for method chaining
        """
        ...

    def with_token_metadata(
        self, user_id: Optional[str] = None, client_id: Optional[str] = None, scopes: Optional[List[str]] = None
    ) -> "BearerAuthMock":
        """
        Configure the mock with token metadata.

        Args:
            user_id: User ID associated with the token
            client_id: Client ID associated with the token
            scopes: Permission scopes associated with the token

        Returns:
            Self for method chaining
        """
        ...

    def with_token_expiration(self, expires_in_seconds: int = 3600, token: Optional[str] = None) -> "BearerAuthMock":
        """
        Configure the mock with token expiration.

        Args:
            expires_in_seconds: Number of seconds until the token expires
            token: Specific token to configure expiration for (defaults to current token)

        Returns:
            Self for method chaining
        """
        ...

    def with_token_format_validation(self, pattern: str) -> "BearerAuthMock":
        """
        Configure the mock with token format validation.

        Args:
            pattern: Regular expression pattern for valid token format

        Returns:
            Self for method chaining
        """
        ...

    def with_valid_token_prefix(self, prefix: str) -> "BearerAuthMock":
        """
        Configure the mock with a valid token prefix.

        Args:
            prefix: Valid token prefix

        Returns:
            Self for method chaining
        """
        ...

    def with_required_scopes(self, scopes: List[str]) -> "BearerAuthMock":
        """
        Configure the mock with required permission scopes.

        Args:
            scopes: List of required permission scopes

        Returns:
            Self for method chaining
        """
        ...

    def with_jwt_validation(self) -> "BearerAuthMock":
        """
        Configure the mock to validate tokens as JWTs.

        Returns:
            Self for method chaining
        """
        ...

    def with_token_type(self, token_type: str) -> "BearerAuthMock":
        """
        Configure the mock with a specific token type.

        Args:
            token_type: Token type (e.g., "access_token", "id_token", "refresh_token")

        Returns:
            Self for method chaining
        """
        ...

    def revoke_token(self, token: str) -> "BearerAuthMock":
        """
        Revoke a specific token.

        Args:
            token: Token to revoke

        Returns:
            Self for method chaining
        """
        ...

    def refresh(self) -> bool:
        """
        Attempt to refresh the token.

        Returns:
            True if the token was refreshed successfully, False otherwise
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

    def validate_token(self, token: str) -> bool:
        """
        Validate a token.

        Args:
            token: Token to validate

        Returns:
            True if the token is valid, False otherwise
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

    def get_token_metadata(self, token: str) -> Optional[Dict]:
        """
        Get metadata for a specific token.

        Args:
            token: Token to get metadata for

        Returns:
            Token metadata or None if the token is not found
        """
        ...

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers.

        Returns:
            Tuple of (header_name, header_value) or None if no token is available
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
            BearerAuth instance
        """
        ...

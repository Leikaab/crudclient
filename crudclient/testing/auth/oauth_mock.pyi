"""
OAuth authentication mock for testing.

This module provides a mock for OAuth Authentication strategy with support
for different grant types, scopes, and advanced authentication scenarios.
"""

from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import CustomAuth

from ..response_builder.response import MockResponse
from .base import AuthMockBase
from .oauth_grant_handler import OAuthGrantHandler
from .oauth_scope_validator import OAuthScopeValidator
from .oauth_token_manager import OAuthTokenManager

class OAuthMock(AuthMockBase):
    """
    Mock for OAuth Authentication with support for different grant types and scopes.

    This class provides a configurable mock implementation of OAuth Authentication,
    supporting various grant types, token management, and scope validation.
    """

    client_id: str
    client_secret: str
    token_url: str
    authorize_url: Optional[str]
    redirect_uri: Optional[str]
    scope: Optional[str]
    token_manager: OAuthTokenManager
    scope_validator: OAuthScopeValidator
    grant_handler: OAuthGrantHandler
    auth_strategy: CustomAuth

    def __init__(
        self,
        client_id: str = "client_id",
        client_secret: str = "client_secret",
        token_url: str = "https://example.com/oauth/token",
        authorize_url: Optional[str] = "https://example.com/oauth/authorize",
        redirect_uri: Optional[str] = "https://app.example.com/callback",
        scope: Optional[str] = "read write",
    ) -> None:
        """
        Initialize an OAuth Authentication mock.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            token_url: URL for token endpoint
            authorize_url: URL for authorization endpoint
            redirect_uri: Redirect URI for authorization code flow
            scope: Space-separated list of scopes
        """
        ...

    def with_client_credentials(self, client_id: str, client_secret: str) -> "OAuthMock":
        """
        Set the client credentials for the OAuth mock.

        Args:
            client_id: The client ID
            client_secret: The client secret

        Returns:
            Self for method chaining
        """
        ...

    def with_token_url(self, token_url: str) -> "OAuthMock":
        """
        Set the token URL for the OAuth mock.

        Args:
            token_url: The token URL

        Returns:
            Self for method chaining
        """
        ...

    def with_authorize_url(self, authorize_url: str) -> "OAuthMock":
        """
        Set the authorize URL for the OAuth mock.

        Args:
            authorize_url: The authorize URL

        Returns:
            Self for method chaining
        """
        ...

    def with_redirect_uri(self, redirect_uri: str) -> "OAuthMock":
        """
        Set the redirect URI for the OAuth mock.

        Args:
            redirect_uri: The redirect URI

        Returns:
            Self for method chaining
        """
        ...

    def with_scope(self, scope: str) -> "OAuthMock":
        """
        Set the scope for the OAuth mock.

        Args:
            scope: The scope

        Returns:
            Self for method chaining
        """
        ...

    def with_grant_type(self, grant_type: str) -> "OAuthMock":
        """
        Set the grant type for the OAuth mock.

        Args:
            grant_type: The grant type

        Returns:
            Self for method chaining
        """
        ...

    def with_access_token(self, access_token: str) -> "OAuthMock":
        """
        Set the access token for the OAuth mock.

        Args:
            access_token: The access token

        Returns:
            Self for method chaining
        """
        ...

    def with_refresh_token(self, refresh_token: str = ..., max_refresh_attempts: int = ...) -> "OAuthMock":
        """
        Set the refresh token for the OAuth mock.

        Args:
            refresh_token: The refresh token

        Returns:
            Self for method chaining
        """
        ...

    def with_token_expiration(self, expires_in_seconds: int = ...) -> "OAuthMock":
        """
        Set the token expiration for the OAuth mock.

        Args:
            expires_in_seconds: The number of seconds until the token expires

        Returns:
            Self for method chaining
        """
        ...

    def with_expired_token(self) -> "OAuthMock":
        """
        Set the token to be expired.

        Returns:
            Self for method chaining
        """
        ...

    def with_required_scopes(self, scopes: List[str]) -> "OAuthMock":
        """
        Set the required scopes for the OAuth mock.

        Args:
            scopes: The required scopes

        Returns:
            Self for method chaining
        """
        ...

    def with_available_scopes(self, scopes: List[str]) -> "OAuthMock":
        """
        Set the available scopes for the OAuth mock.

        Args:
            scopes: The available scopes

        Returns:
            Self for method chaining
        """
        ...

    def with_user(self, username: str, password: str, scopes: List[str]) -> "OAuthMock":
        """
        Add a user for password grant type.

        Args:
            username: The username
            password: The password
            scopes: The scopes for the user

        Returns:
            Self for method chaining
        """
        ...

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the Bearer Auth header has the correct format and token is valid.

        Args:
            header_value: The value of the Authorization header

        Returns:
            True if the header is valid, False otherwise
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

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured CustomAuth strategy
        """
        ...

    def is_token_expired(self) -> bool:
        """
        Check if the current access token is expired using the token manager.

        Returns:
            True if the token is expired, False otherwise
        """
        ...

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        """
        Get the authentication headers for the current token.

        Returns:
            A tuple of (header_name, header_value) or None if no valid token
        """
        ...

    def handle_auth_error(self, response: "MockResponse") -> bool:
        """
        Attempt to refresh the token if it's expired and refreshable.

        Args:
            response: The error response that triggered the auth error

        Returns:
            True if the error was handled and the request should be retried, False otherwise
        """
        ...

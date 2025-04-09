from datetime import datetime, timedelta
from typing import List, Optional

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import CustomAuth

from .base import AuthMockBase
from .oauth_grant_handler import OAuthGrantHandler
from .oauth_scope_validator import OAuthScopeValidator
from .oauth_token_manager import OAuthTokenManager


class OAuthMock(AuthMockBase):
    def __init__(
        self,
        client_id: str = "client_id",
        client_secret: str = "client_secret",
        token_url: str = "https://example.com/oauth/token",
        authorize_url: Optional[str] = "https://example.com/oauth/authorize",
        redirect_uri: Optional[str] = "https://app.example.com/callback",
        scope: Optional[str] = "read write"
    ):
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.authorize_url = authorize_url
        self.redirect_uri = redirect_uri
        self.scope = scope

        # Initialize components
        self.token_manager = OAuthTokenManager()
        self.scope_validator = OAuthScopeValidator()
        self.grant_handler = OAuthGrantHandler(self.token_manager, self.scope_validator)

        # Initialize with a default token
        self.token_manager.initialize_default_token(client_id, scope)

        # Create auth strategy
        self.auth_strategy = CustomAuth(
            header_callback=lambda: {"Authorization": f"Bearer {self.token_manager.current_access_token}"}
        )

    def with_client_credentials(self, client_id: str, client_secret: str) -> 'OAuthMock':
        """
        Set the client credentials for the OAuth mock.

        Args:
            client_id: The client ID
            client_secret: The client secret

        Returns:
            Self for method chaining
        """
        self.client_id = client_id
        self.client_secret = client_secret
        return self

    def with_token_url(self, token_url: str) -> 'OAuthMock':
        """
        Set the token URL for the OAuth mock.

        Args:
            token_url: The token URL

        Returns:
            Self for method chaining
        """
        self.token_url = token_url
        return self

    def with_authorize_url(self, authorize_url: str) -> 'OAuthMock':
        """
        Set the authorize URL for the OAuth mock.

        Args:
            authorize_url: The authorize URL

        Returns:
            Self for method chaining
        """
        self.authorize_url = authorize_url
        return self

    def with_redirect_uri(self, redirect_uri: str) -> 'OAuthMock':
        """
        Set the redirect URI for the OAuth mock.

        Args:
            redirect_uri: The redirect URI

        Returns:
            Self for method chaining
        """
        self.redirect_uri = redirect_uri
        return self

    def with_scope(self, scope: str) -> 'OAuthMock':
        """
        Set the scope for the OAuth mock.

        Args:
            scope: The scope

        Returns:
            Self for method chaining
        """
        self.scope = scope
        return self

    def with_grant_type(self, grant_type: str) -> 'OAuthMock':
        """
        Set the grant type for the OAuth mock.

        Args:
            grant_type: The grant type

        Returns:
            Self for method chaining
        """
        self.grant_handler.set_default_grant_type(grant_type)
        return self

    def with_access_token(self, access_token: str) -> 'OAuthMock':
        """
        Set the access token for the OAuth mock.

        Args:
            access_token: The access token

        Returns:
            Self for method chaining
        """
        # Create a new token with the specified value
        now = datetime.now()
        self.token_manager.access_tokens[access_token] = {
            "client_id": self.client_id,
            "scope": self.scope,
            "expires_at": now + timedelta(hours=1),
            "token_type": "Bearer",
            "grant_type": self.grant_handler.grant_type
        }

        # Update the current token
        self.token_manager.current_access_token = access_token

        # Update the auth strategy
        self.auth_strategy = CustomAuth(
            header_callback=lambda: {"Authorization": f"Bearer {access_token}"}
        )

        return self

    def with_refresh_token(self, refresh_token: str) -> 'OAuthMock':
        """
        Set the refresh token for the OAuth mock.

        Args:
            refresh_token: The refresh token

        Returns:
            Self for method chaining
        """
        # Link the refresh token to the current access token
        self.token_manager.refresh_tokens[refresh_token] = self.token_manager.current_access_token
        self.token_manager.current_refresh_token = refresh_token

        return self

    def with_token_expiration(self, expires_in_seconds: int) -> 'OAuthMock':
        """
        Set the token expiration for the OAuth mock.

        Args:
            expires_in_seconds: The number of seconds until the token expires

        Returns:
            Self for method chaining
        """
        # Update the expiration time for the current token
        token_data = self.token_manager.access_tokens[self.token_manager.current_access_token]
        token_data["expires_at"] = datetime.now() + timedelta(seconds=expires_in_seconds)

        return self

    def with_expired_token(self) -> 'OAuthMock':
        """
        Set the token to be expired.

        Returns:
            Self for method chaining
        """
        # Set the token to expire in the past
        return self.with_token_expiration(-3600)

    def with_required_scopes(self, scopes: List[str]) -> 'OAuthMock':
        """
        Set the required scopes for the OAuth mock.

        Args:
            scopes: The required scopes

        Returns:
            Self for method chaining
        """
        self.scope_validator.set_required_scopes(scopes)
        return self

    def with_available_scopes(self, scopes: List[str]) -> 'OAuthMock':
        """
        Set the available scopes for the OAuth mock.

        Args:
            scopes: The available scopes

        Returns:
            Self for method chaining
        """
        self.scope_validator.set_available_scopes(scopes)
        return self

    def with_user(self, username: str, password: str, scopes: List[str]) -> 'OAuthMock':
        """
        Add a user for password grant type.

        Args:
            username: The username
            password: The password
            scopes: The scopes for the user

        Returns:
            Self for method chaining
        """
        self.token_manager.add_user(username, password, scopes)
        return self

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the Bearer Auth header has the correct format and token is valid.

        Args:
            header_value: The value of the Authorization header

        Returns:
            True if the header is valid, False otherwise
        """
        # Check if it's a Bearer token
        if not header_value.startswith("Bearer "):
            return False

        # Extract the token
        token = header_value[7:]

        # Validate the token
        return self.token_manager.validate_token(token)

    def verify_token_usage(self, token: str) -> bool:
        """
        Verify that the token is being used correctly.

        Args:
            token: The token to verify

        Returns:
            True if the token is being used correctly, False otherwise
        """
        return self.token_manager.validate_token(token)

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured CustomAuth strategy
        """
        return self.auth_strategy

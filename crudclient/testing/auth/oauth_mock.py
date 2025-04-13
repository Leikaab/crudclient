from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List, Optional, Tuple  # Added Tuple, TYPE_CHECKING

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import CustomAuth

from .base import AuthMockBase
from .oauth_grant_handler import OAuthGrantHandler
from .oauth_scope_validator import OAuthScopeValidator
from .oauth_token_manager import OAuthTokenManager

if TYPE_CHECKING:  # Added TYPE_CHECKING block
    from ..response_builder import MockResponse


class OAuthMock(AuthMockBase):
    def __init__(
        self,
        client_id: str = "client_id",
        client_secret: str = "client_secret",
        token_url: str = "https://example.com/oauth/token",
        authorize_url: Optional[str] = "https://example.com/oauth/authorize",
        redirect_uri: Optional[str] = "https://app.example.com/callback",
        scope: Optional[str] = "read write",
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
        self.auth_strategy = CustomAuth(header_callback=lambda: {"Authorization": f"Bearer {self.token_manager.current_access_token}"})

    def with_client_credentials(self, client_id: str, client_secret: str) -> "OAuthMock":
        self.client_id = client_id
        self.client_secret = client_secret
        return self

    def with_token_url(self, token_url: str) -> "OAuthMock":
        self.token_url = token_url
        return self

    def with_authorize_url(self, authorize_url: str) -> "OAuthMock":
        self.authorize_url = authorize_url
        return self

    def with_redirect_uri(self, redirect_uri: str) -> "OAuthMock":
        self.redirect_uri = redirect_uri
        return self

    def with_scope(self, scope: str) -> "OAuthMock":
        self.scope = scope
        return self

    def with_grant_type(self, grant_type: str) -> "OAuthMock":
        self.grant_handler.set_default_grant_type(grant_type)
        return self

    def with_access_token(self, access_token: str) -> "OAuthMock":
        # Create a new token with the specified value
        now = datetime.now()
        self.token_manager.access_tokens[access_token] = {
            "client_id": self.client_id,
            "scope": self.scope,
            "expires_at": now + timedelta(hours=1),
            "token_type": "Bearer",
            "grant_type": self.grant_handler.grant_type,
        }

        # Update the current token
        self.token_manager.current_access_token = access_token

        # Update the auth strategy
        self.auth_strategy = CustomAuth(header_callback=lambda: {"Authorization": f"Bearer {access_token}"})

        return self

    def with_refresh_token(self, refresh_token: str) -> "OAuthMock":
        # Link the refresh token to the current access token
        self.token_manager.refresh_tokens[refresh_token] = self.token_manager.current_access_token
        self.token_manager.current_refresh_token = refresh_token
        # Also update the base class state for consistency
        super().with_refresh_token(refresh_token)
        return self

    def with_token_expiration(self, expires_in_seconds: int) -> "OAuthMock":
        # Update the expiration time for the current token
        token_data = self.token_manager.access_tokens[self.token_manager.current_access_token]
        token_data["expires_at"] = datetime.now() + timedelta(seconds=expires_in_seconds)

        return self

    def with_expired_token(self) -> "OAuthMock":
        # Set the token to expire in the past
        return self.with_token_expiration(-3600)

    def with_required_scopes(self, scopes: List[str]) -> "OAuthMock":
        self.scope_validator.set_required_scopes(scopes)
        return self

    def with_available_scopes(self, scopes: List[str]) -> "OAuthMock":
        self.scope_validator.set_available_scopes(scopes)
        return self

    def with_user(self, username: str, password: str, scopes: List[str]) -> "OAuthMock":
        self.token_manager.add_user(username, password, scopes)
        return self

    def verify_auth_header(self, header_value: str) -> bool:
        # Check if it's a Bearer token
        if not header_value.startswith("Bearer "):
            return False

        # Extract the token
        token = header_value[7:]

        # Validate the token
        return self.token_manager.validate_token(token)

    def verify_token_usage(self, token: str) -> bool:
        return self.token_manager.validate_token(token)

    def get_auth_strategy(self) -> AuthStrategy:
        return self.auth_strategy

    # --- Method Overrides & Implementations ---

    def is_token_expired(self) -> bool:
        token = self.token_manager.current_access_token
        if not token or token not in self.token_manager.access_tokens:
            return True  # No valid current token or token unknown
        token_data = self.token_manager.access_tokens[token]
        # Check if 'expires_at' exists and is in the past
        expires_at = token_data.get("expires_at")
        return expires_at is not None and expires_at < datetime.now()

    def get_auth_headers(self) -> Optional[Tuple[str, str]]:
        token = self.token_manager.current_access_token
        # Use the overridden is_token_expired to check status
        if not token or self.is_token_expired():
            return None
        return ("Authorization", f"Bearer {token}")

    def handle_auth_error(self, response: "MockResponse") -> bool:
        # Use the overridden is_token_expired and base can_refresh_token
        if self.is_token_expired() and self.can_refresh_token():
            # Attempt to refresh via the token manager
            new_token_info = self.token_manager.refresh_token(self.token_manager.current_refresh_token)

            if new_token_info and "access_token" in new_token_info:
                # Update base class state for consistency
                self.refresh_attempts += 1  # Track attempt via base
                # Update the auth_strategy with the new token from token_manager
                self.auth_strategy = CustomAuth(header_callback=lambda: {"Authorization": f"Bearer {self.token_manager.current_access_token}"})
                return True  # Refresh succeeded
            else:
                # Refresh failed via token manager
                return False

        # If not an expiration error or refresh is not possible/failed
        return False

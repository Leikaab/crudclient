from datetime import datetime
from typing import Any, Dict, Optional, Set

from .oauth_scope_validator import OAuthScopeValidator
from .oauth_token_manager import OAuthTokenManager


class OAuthGrantHandler:
    def __init__(self, token_manager: OAuthTokenManager, scope_validator: OAuthScopeValidator):
        self.token_manager = token_manager
        self.scope_validator = scope_validator

        self.grant_type = "authorization_code"  # Default grant type
        self.supported_grant_types: Set[str] = {"authorization_code", "client_credentials", "password", "refresh_token", "implicit"}

    def set_supported_grant_types(self, grant_types: Set[str]) -> None:
        self.supported_grant_types = grant_types

    def set_default_grant_type(self, grant_type: str) -> None:
        if grant_type not in self.supported_grant_types:
            raise ValueError(f"Grant type {grant_type} is not supported")
        self.grant_type = grant_type

    def handle_token_request(
        self,
        grant_type: str,
        client_id: str,
        client_secret: str,
        scope: Optional[str] = None,
        code: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Validate grant type
        if grant_type not in self.supported_grant_types:
            return {"error": "unsupported_grant_type", "error_description": f"Grant type {grant_type} is not supported"}

        # Validate scopes
        if scope and not self.scope_validator.validate_scopes(scope):
            return {"error": "invalid_scope", "error_description": "The requested scope is invalid"}

        # Handle different grant types
        if grant_type == "authorization_code":
            return self._handle_authorization_code_grant(client_id, client_secret, code, redirect_uri, scope)
        elif grant_type == "client_credentials":
            return self._handle_client_credentials_grant(client_id, client_secret, scope)
        elif grant_type == "password":
            return self._handle_password_grant(client_id, client_secret, username, password, scope)
        elif grant_type == "refresh_token":
            return self._handle_refresh_token_grant(client_id, client_secret, refresh_token, scope)
        else:  # implicit grant is handled differently
            return {"error": "invalid_request", "error_description": "Grant type not properly implemented"}

    def _handle_authorization_code_grant(
        self, client_id: str, client_secret: str, code: Optional[str], redirect_uri: Optional[str], scope: Optional[str]
    ) -> Dict[str, Any]:
        if not code or not redirect_uri:
            return {"error": "invalid_request", "error_description": "Code and redirect_uri are required"}

        # Validate the authorization code
        if code not in self.token_manager.authorization_codes:
            return {"error": "invalid_grant", "error_description": "Invalid authorization code"}

        code_data = self.token_manager.authorization_codes[code]

        # Check if the code is expired
        if code_data["expires_at"] < datetime.now():
            return {"error": "invalid_grant", "error_description": "Authorization code expired"}

        # Check if the client_id matches
        if code_data["client_id"] != client_id:
            return {"error": "invalid_grant", "error_description": "Authorization code was not issued to this client"}

        # Check if the redirect_uri matches
        if code_data["redirect_uri"] != redirect_uri:
            return {"error": "invalid_grant", "error_description": "Redirect URI does not match the one used in the authorization request"}

        # Create a new token
        return self.token_manager.create_token(client_id=client_id, scope=scope or code_data["scope"], grant_type="authorization_code")

    def _handle_client_credentials_grant(self, client_id: str, client_secret: str, scope: Optional[str]) -> Dict[str, Any]:
        # Create a new token
        return self.token_manager.create_token(client_id=client_id, scope=scope, grant_type="client_credentials")

    def _handle_password_grant(
        self, client_id: str, client_secret: str, username: Optional[str], password: Optional[str], scope: Optional[str]
    ) -> Dict[str, Any]:
        if not username or not password:
            return {"error": "invalid_request", "error_description": "Username and password are required"}

        # Validate the username and password
        if not self.token_manager.validate_user(username, password):
            return {"error": "invalid_grant", "error_description": "Invalid username or password"}

        # Create a new token
        return self.token_manager.create_token(client_id=client_id, scope=scope, grant_type="password", user=username)

    def _handle_refresh_token_grant(self, client_id: str, client_secret: str, refresh_token: Optional[str], scope: Optional[str]) -> Dict[str, Any]:
        if not refresh_token:
            return {"error": "invalid_request", "error_description": "Refresh token is required"}

        # Refresh the token
        new_token = self.token_manager.refresh_token(refresh_token)
        if not new_token:
            return {"error": "invalid_grant", "error_description": "Invalid refresh token"}

        return new_token

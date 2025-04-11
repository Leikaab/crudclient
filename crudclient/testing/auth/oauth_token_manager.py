from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class OAuthTokenManager:
    def __init__(self):
        # Token management
        self.access_tokens: Dict[str, Dict] = {}
        self.refresh_tokens: Dict[str, str] = {}  # refresh_token -> access_token
        self.authorization_codes: Dict[str, Dict] = {}
        self.current_access_token = "access_token"
        self.current_refresh_token = "refresh_token"

        # User management for password grant
        self.users: Dict[str, Dict] = {"user": {"password": "pass", "scopes": ["read", "write"]}}

    def initialize_default_token(self, client_id: str, scope: Optional[str]) -> None:
        now = datetime.now()
        self.access_tokens[self.current_access_token] = {
            "client_id": client_id,
            "scope": scope,
            "expires_at": now + timedelta(hours=1),
            "token_type": "Bearer",
            "grant_type": "client_credentials",
        }

        self.refresh_tokens[self.current_refresh_token] = self.current_access_token

    def create_token(
        self,
        client_id: str,
        scope: Optional[str] = None,
        expires_in: int = 3600,
        token_type: str = "Bearer",
        grant_type: str = "client_credentials",
        user: Optional[str] = None,
    ) -> Dict[str, Any]:
        now = datetime.now()
        access_token = f"access_token_{now.timestamp()}"
        refresh_token = f"refresh_token_{now.timestamp()}"

        self.access_tokens[access_token] = {
            "client_id": client_id,
            "scope": scope,
            "expires_at": now + timedelta(seconds=expires_in),
            "token_type": token_type,
            "grant_type": grant_type,
            "user": user,
        }

        self.refresh_tokens[refresh_token] = access_token
        self.current_access_token = access_token
        self.current_refresh_token = refresh_token

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "token_type": token_type,
            "scope": scope or "",
        }

    def create_authorization_code(self, client_id: str, redirect_uri: str, scope: Optional[str] = None, state: Optional[str] = None) -> str:
        now = datetime.now()
        code = f"auth_code_{now.timestamp()}"

        self.authorization_codes[code] = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": scope,
            "state": state,
            "expires_at": now + timedelta(minutes=10),
        }

        return code

    def validate_token(self, token: str) -> bool:
        if token not in self.access_tokens:
            return False

        token_data = self.access_tokens[token]
        if token_data["expires_at"] < datetime.now():
            return False

        return True

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        if refresh_token not in self.refresh_tokens:
            return None

        old_access_token = self.refresh_tokens[refresh_token]
        if old_access_token not in self.access_tokens:
            return None

        old_token_data = self.access_tokens[old_access_token]

        # Create a new token with the same properties
        return self.create_token(
            client_id=old_token_data["client_id"],
            scope=old_token_data["scope"],
            token_type=old_token_data["token_type"],
            grant_type="refresh_token",
            user=old_token_data.get("user"),
        )

    def revoke_token(self, token: str) -> bool:
        if token not in self.access_tokens:
            return False

        # Find and remove the refresh token
        refresh_token = None
        for rt, at in self.refresh_tokens.items():
            if at == token:
                refresh_token = rt
                break

        if refresh_token:
            del self.refresh_tokens[refresh_token]

        # Remove the access token
        del self.access_tokens[token]

        # Update current token if it was revoked
        if self.current_access_token == token:
            if self.access_tokens:
                self.current_access_token = next(iter(self.access_tokens))
            else:
                self.current_access_token = ""

        return True

    def add_user(self, username: str, password: str, scopes: List[str]) -> None:
        self.users[username] = {"password": password, "scopes": scopes}

    def validate_user(self, username: str, password: str) -> bool:
        if username not in self.users:
            return False

        return self.users[username]["password"] == password

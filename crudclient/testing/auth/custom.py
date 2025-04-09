"""
Custom authentication mock for testing.

This module provides a mock for Custom Authentication strategy with support
for OAuth grant types, scopes, and advanced authentication scenarios.
"""

from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Set, Tuple, Union

from crudclient.auth.base import AuthStrategy
from crudclient.auth.custom import CustomAuth

from .base import AuthMockBase


class OAuthMock(AuthMockBase):
    """
    Mock for OAuth Authentication with support for different grant types and scopes.

    This class provides a configurable mock implementation of OAuth Authentication,
    supporting various grant types, token management, and scope validation.
    """

    def __init__(
        self,
        client_id: str = "client_id",
        client_secret: str = "client_secret",
        token_url: str = "https://example.com/oauth/token",
        authorize_url: Optional[str] = "https://example.com/oauth/authorize",
        redirect_uri: Optional[str] = "https://app.example.com/callback",
        scope: Optional[str] = "read write"
    ):
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
        super().__init__()
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.authorize_url = authorize_url
        self.redirect_uri = redirect_uri
        self.scope = scope

        # OAuth configuration
        self.grant_type = "authorization_code"  # Default grant type
        self.supported_grant_types = {
            "authorization_code", "client_credentials",
            "password", "refresh_token", "implicit"
        }
        self.available_scopes = {"read", "write", "admin", "user", "profile", "email"}
        self.required_scopes: Set[str] = set()

        # Token management
        self.access_tokens: Dict[str, Dict] = {}
        self.refresh_tokens: Dict[str, str] = {}  # refresh_token -> access_token
        self.authorization_codes: Dict[str, Dict] = {}
        self.current_access_token = "access_token"
        self.current_refresh_token = "refresh_token"

        # User management for password grant
        self.users: Dict[str, Dict] = {
            "user": {
                "password": "pass",
                "scopes": ["read", "write"]
            }
        }

        # Initialize with a default token
        self._initialize_default_token()

        # Create auth strategy
        self.auth_strategy = CustomAuth(
            header_callback=lambda: {"Authorization": f"Bearer {self.current_access_token}"}
        )

    def _initialize_default_token(self) -> None:
        """Initialize default tokens."""
        now = datetime.now()
        self.access_tokens[self.current_access_token] = {
            "client_id": self.client_id,
            "scope": self.scope,
            "expires_at": now + timedelta(hours=1),
            "issued_at": now,
            "user_id": "default_user",
            "grant_type": self.grant_type
        }
        self.refresh_tokens[self.current_refresh_token] = self.current_access_token

    def with_client_credentials(
        self,
        client_id: str,
        client_secret: str
    ) -> 'OAuthMock':
        """
        Set the client credentials.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret

        Returns:
            Self for method chaining
        """
        self.client_id = client_id
        self.client_secret = client_secret
        return self

    def with_grant_type(self, grant_type: str) -> 'OAuthMock':
        """
        Set the OAuth grant type.

        Args:
            grant_type: OAuth grant type (authorization_code, client_credentials, etc.)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If the grant type is not supported
        """
        if grant_type not in self.supported_grant_types:
            raise ValueError(f"Unsupported grant type: {grant_type}")
        self.grant_type = grant_type
        return self

    def with_scope(self, scope: str) -> 'OAuthMock':
        """
        Set the OAuth scope.

        Args:
            scope: Space-separated list of scopes

        Returns:
            Self for method chaining
        """
        self.scope = scope
        return self

    def with_required_scopes(self, scopes: List[str]) -> 'OAuthMock':
        """
        Set required scopes for validation.

        Args:
            scopes: List of scopes that tokens must have

        Returns:
            Self for method chaining
        """
        self.required_scopes = set(scopes)
        return self

    def with_available_scopes(self, scopes: List[str]) -> 'OAuthMock':
        """
        Set available scopes for the OAuth service.

        Args:
            scopes: List of scopes that the service supports

        Returns:
            Self for method chaining
        """
        self.available_scopes = set(scopes)
        return self

    def with_user(
        self,
        username: str,
        password: str,
        scopes: Optional[List[str]] = None
    ) -> 'OAuthMock':
        """
        Add a user for password grant type.

        Args:
            username: Username for password grant
            password: Password for password grant
            scopes: List of scopes associated with the user

        Returns:
            Self for method chaining
        """
        self.users[username] = {
            "password": password,
            "scopes": scopes or ["read", "write"]
        }
        return self

    def with_access_token(
        self,
        token: str,
        expires_in_seconds: int = 3600,
        scope: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> 'OAuthMock':
        """
        Set a custom access token.

        Args:
            token: The access token
            expires_in_seconds: Number of seconds until the token expires
            scope: Space-separated list of scopes associated with the token
            user_id: User ID associated with the token

        Returns:
            Self for method chaining
        """
        now = datetime.now()
        self.current_access_token = token
        self.access_tokens[token] = {
            "client_id": self.client_id,
            "scope": scope or self.scope,
            "expires_at": now + timedelta(seconds=expires_in_seconds),
            "issued_at": now,
            "user_id": user_id or "default_user",
            "grant_type": self.grant_type
        }

        # Update auth strategy
        self.auth_strategy = CustomAuth(
            header_callback=lambda: {"Authorization": f"Bearer {self.current_access_token}"}
        )
        return self

    def with_refresh_token(self, refresh_token: str, access_token: Optional[str] = None) -> 'OAuthMock':
        """
        Set a custom refresh token.

        Args:
            refresh_token: The refresh token
            access_token: The access token associated with the refresh token

        Returns:
            Self for method chaining
        """
        self.current_refresh_token = refresh_token
        self.refresh_tokens[refresh_token] = access_token or self.current_access_token
        return self

    def with_authorization_code(
        self,
        code: str,
        redirect_uri: Optional[str] = None,
        scope: Optional[str] = None,
        expires_in_seconds: int = 600  # 10 minutes
    ) -> 'OAuthMock':
        """
        Set a custom authorization code.

        Args:
            code: The authorization code
            redirect_uri: The redirect URI associated with the code
            scope: Space-separated list of scopes associated with the code
            expires_in_seconds: Number of seconds until the code expires

        Returns:
            Self for method chaining
        """
        now = datetime.now()
        self.authorization_codes[code] = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri or self.redirect_uri,
            "scope": scope or self.scope,
            "expires_at": now + timedelta(seconds=expires_in_seconds),
            "issued_at": now
        }
        return self

    def refresh(self) -> bool:
        """
        Refresh the access token using the refresh token.

        Returns:
            True if the token was refreshed successfully, False otherwise
        """
        if not super().refresh():
            return False

        if self.current_refresh_token not in self.refresh_tokens:
            return False

        # Generate new tokens
        old_access_token = self.current_access_token
        new_access_token = f"{old_access_token}_refreshed_{self.refresh_attempts}"
        new_refresh_token = f"{self.current_refresh_token}_refreshed_{self.refresh_attempts}"

        # Copy metadata from old token
        if old_access_token in self.access_tokens:
            token_data = self.access_tokens[old_access_token].copy()
            token_data["issued_at"] = datetime.now()
            token_data["expires_at"] = datetime.now() + timedelta(hours=1)
            self.access_tokens[new_access_token] = token_data

        # Update tokens
        self.current_access_token = new_access_token
        self.current_refresh_token = new_refresh_token
        self.refresh_tokens[new_refresh_token] = new_access_token

        # Update auth strategy
        self.auth_strategy = CustomAuth(
            header_callback=lambda: {"Authorization": f"Bearer {self.current_access_token}"}
        )
        return True

    def validate_token(self, token: str) -> bool:
        """
        Validate an access token.

        Args:
            token: The access token to validate

        Returns:
            True if the token is valid, False otherwise
        """
        if token not in self.access_tokens:
            return False

        token_data = self.access_tokens[token]

        # Check expiration
        if datetime.now() > token_data["expires_at"]:
            return False

        # Check scopes if required
        if self.required_scopes:
            token_scopes = set(token_data["scope"].split())
            if not self.required_scopes.issubset(token_scopes):
                return False

        return True

    def validate_authorization_code(self, code: str, redirect_uri: Optional[str] = None) -> bool:
        """
        Validate an authorization code.

        Args:
            code: The authorization code to validate
            redirect_uri: The redirect URI to validate against

        Returns:
            True if the code is valid, False otherwise
        """
        if code not in self.authorization_codes:
            return False

        code_data = self.authorization_codes[code]

        # Check expiration
        if datetime.now() > code_data["expires_at"]:
            return False

        # Check redirect URI if provided
        if redirect_uri and redirect_uri != code_data["redirect_uri"]:
            return False

        return True

    def validate_client_credentials(self, client_id: str, client_secret: str) -> bool:
        """
        Validate client credentials.

        Args:
            client_id: The client ID to validate
            client_secret: The client secret to validate

        Returns:
            True if the credentials are valid, False otherwise
        """
        return client_id == self.client_id and client_secret == self.client_secret

    def validate_user_credentials(self, username: str, password: str) -> bool:
        """
        Validate user credentials for password grant.

        Args:
            username: The username to validate
            password: The password to validate

        Returns:
            True if the credentials are valid, False otherwise
        """
        return (username in self.users
                and self.users[username]["password"] == password)

    def get_token_response(
        self,
        grant_type: Optional[str] = None,
        code: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        refresh_token: Optional[str] = None,
        scope: Optional[str] = None
    ) -> Dict:
        """
        Generate a token response based on the grant type and parameters.

        Args:
            grant_type: OAuth grant type
            code: Authorization code (for authorization_code grant)
            redirect_uri: Redirect URI (for authorization_code grant)
            client_id: Client ID
            client_secret: Client secret
            username: Username (for password grant)
            password: Password (for password grant)
            refresh_token: Refresh token (for refresh_token grant)
            scope: Requested scope

        Returns:
            Token response dictionary
        """
        current_grant = grant_type or self.grant_type

        # Validate grant type
        if current_grant not in self.supported_grant_types:
            return {
                "error": "unsupported_grant_type",
                "error_description": f"The grant type '{current_grant}' is not supported"
            }

        # Authorization Code Grant
        if current_grant == "authorization_code":
            if not code:
                return {"error": "invalid_request", "error_description": "Missing code parameter"}

            if not self.validate_authorization_code(code, redirect_uri):
                return {"error": "invalid_grant", "error_description": "Invalid authorization code"}

            code_data = self.authorization_codes[code]
            token_scope = code_data["scope"]

        # Client Credentials Grant
        elif current_grant == "client_credentials":
            if not client_id or not client_secret:
                return {"error": "invalid_request", "error_description": "Missing client credentials"}

            if not self.validate_client_credentials(client_id, client_secret):
                return {"error": "invalid_client", "error_description": "Invalid client credentials"}

            token_scope = scope or self.scope

        # Password Grant
        elif current_grant == "password":
            if not username or not password:
                return {"error": "invalid_request", "error_description": "Missing username or password"}

            if not self.validate_user_credentials(username, password):
                return {"error": "invalid_grant", "error_description": "Invalid user credentials"}

            token_scope = scope or " ".join(self.users[username]["scopes"])

        # Refresh Token Grant
        elif current_grant == "refresh_token":
            if not refresh_token:
                return {"error": "invalid_request", "error_description": "Missing refresh token"}

            if refresh_token not in self.refresh_tokens:
                return {"error": "invalid_grant", "error_description": "Invalid refresh token"}

            access_token = self.refresh_tokens[refresh_token]
            if access_token in self.access_tokens:
                token_scope = self.access_tokens[access_token]["scope"]
            else:
                token_scope = self.scope

        # Implicit Grant (typically handled in the authorize endpoint)
        elif current_grant == "implicit":
            token_scope = scope or self.scope

        else:
            return {"error": "unsupported_grant_type", "error_description": "Unsupported grant type"}

        # Validate scopes
        if token_scope:
            requested_scopes = set(token_scope.split())
            if not requested_scopes.issubset(self.available_scopes):
                invalid_scopes = requested_scopes - self.available_scopes
                return {
                    "error": "invalid_scope",
                    "error_description": f"The requested scope is invalid: {', '.join(invalid_scopes)}"
                }
        else:
            token_scope = ""

        # Generate tokens
        now = datetime.now()
        expires_in = 3600  # 1 hour

        access_token = f"access_token_{now.timestamp()}"
        refresh_token = f"refresh_token_{now.timestamp()}"

        # Store token data
        self.access_tokens[access_token] = {
            "client_id": client_id or self.client_id,
            "scope": token_scope,
            "expires_at": now + timedelta(seconds=expires_in),
            "issued_at": now,
            "user_id": username or "default_user",
            "grant_type": current_grant
        }

        self.refresh_tokens[refresh_token] = access_token

        # Update current tokens
        self.current_access_token = access_token
        self.current_refresh_token = refresh_token

        # Update auth strategy
        self.auth_strategy = CustomAuth(
            header_callback=lambda: {"Authorization": f"Bearer {self.current_access_token}"}
        )

        # Return token response
        response = {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": expires_in,
            "scope": token_scope
        }

        # Add refresh token for supported grant types
        if current_grant in ["authorization_code", "password"]:
            response["refresh_token"] = refresh_token

        return response

    def verify_auth_header(self, header_value: str) -> bool:
        """
        Verify that the Bearer Auth header has the correct format and token is valid.

        Args:
            header_value: The value of the Authorization header

        Returns:
            True if the header is valid, False otherwise
        """
        if not header_value.startswith("Bearer "):
            return False

        token = header_value[7:]  # Skip "Bearer "
        return self.validate_token(token)

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured CustomAuth strategy
        """
        return self.auth_strategy


class CustomAuthMock(AuthMockBase):
    """
    Mock for Custom Authentication strategy with enhanced capabilities.

    This class provides a configurable mock implementation of the Custom Authentication
    strategy, with support for header and parameter callbacks, validation, and error simulation.
    """

    def __init__(
        self,
        header_callback: Optional[Callable[[], Dict[str, str]]] = None,
        param_callback: Optional[Callable[[], Dict[str, str]]] = None
    ):
        """
        Initialize a Custom Authentication mock.

        Args:
            header_callback: Callback function that returns authentication headers
            param_callback: Callback function that returns authentication parameters
        """
        super().__init__()

        # Default callbacks if none provided
        def default_header_callback(): return {"X-Custom-Auth": "custom_value"}
        if header_callback is None and param_callback is None:
            header_callback = default_header_callback

        self.header_callback = header_callback
        self.param_callback = param_callback
        self.auth_strategy = CustomAuth(
            header_callback=header_callback if header_callback else lambda: {},
            param_callback=param_callback
        )

        # Additional properties for enhanced functionality
        self.expected_headers: Dict[str, str] = {}
        self.expected_params: Dict[str, str] = {}
        self.required_headers: List[str] = []
        self.required_params: List[str] = []
        self.header_validators: Dict[str, Callable[[str], bool]] = {}
        self.param_validators: Dict[str, Callable[[str], bool]] = {}

    def with_header_callback(self, callback: Callable[[], Dict[str, str]]) -> 'CustomAuthMock':
        """
        Set the header callback for the Custom Auth mock.

        Args:
            callback: Callback function that returns authentication headers

        Returns:
            Self for method chaining
        """
        self.header_callback = callback
        self.auth_strategy = CustomAuth(
            header_callback=callback,
            param_callback=self.param_callback
        )
        return self

    def with_param_callback(self, callback: Callable[[], Dict[str, str]]) -> 'CustomAuthMock':
        """
        Set the parameter callback for the Custom Auth mock.

        Args:
            callback: Callback function that returns authentication parameters

        Returns:
            Self for method chaining
        """
        self.param_callback = callback
        self.auth_strategy = CustomAuth(
            header_callback=self.header_callback if self.header_callback else lambda: {},
            param_callback=callback
        )
        return self

    def with_expected_header(self, name: str, value: str) -> 'CustomAuthMock':
        """
        Add an expected header for validation.

        Args:
            name: Header name
            value: Expected header value

        Returns:
            Self for method chaining
        """
        self.expected_headers[name] = value
        return self

    def with_expected_param(self, name: str, value: str) -> 'CustomAuthMock':
        """
        Add an expected parameter for validation.

        Args:
            name: Parameter name
            value: Expected parameter value

        Returns:
            Self for method chaining
        """
        self.expected_params[name] = value
        return self

    def with_required_headers(self, header_names: List[str]) -> 'CustomAuthMock':
        """
        Set required headers for validation.

        Args:
            header_names: List of required header names

        Returns:
            Self for method chaining
        """
        self.required_headers = header_names
        return self

    def with_required_params(self, param_names: List[str]) -> 'CustomAuthMock':
        """
        Set required parameters for validation.

        Args:
            param_names: List of required parameter names

        Returns:
            Self for method chaining
        """
        self.required_params = param_names
        return self

    def with_header_validator(
        self,
        header_name: str,
        validator: Callable[[str], bool]
    ) -> 'CustomAuthMock':
        """
        Add a custom validator function for a header.

        Args:
            header_name: Header name to validate
            validator: Function that takes a header value and returns True if valid

        Returns:
            Self for method chaining
        """
        self.header_validators[header_name] = validator
        return self

    def with_param_validator(
        self,
        param_name: str,
        validator: Callable[[str], bool]
    ) -> 'CustomAuthMock':
        """
        Add a custom validator function for a parameter.

        Args:
            param_name: Parameter name to validate
            validator: Function that takes a parameter value and returns True if valid

        Returns:
            Self for method chaining
        """
        self.param_validators[param_name] = validator
        return self

    def with_failing_callback(self, error_message: str = "Callback failed") -> 'CustomAuthMock':
        """
        Configure the mock with a callback that fails.

        Args:
            error_message: Error message to include in the exception

        Returns:
            Self for method chaining
        """
        def failing_callback():
            raise ValueError(error_message)

        self.header_callback = failing_callback

        # Create a custom auth strategy that will raise the error immediately
        class FailingCustomAuth(CustomAuth):
            def prepare_request_headers(self):
                # This will raise the ValueError when called
                return self.header_callback()

            def get_auth_headers(self):
                # Make sure the error is raised when getting auth headers
                return self.prepare_request_headers()

        # Store the error message to be raised later
        self.error_message = error_message

        self.auth_strategy = FailingCustomAuth(
            header_callback=failing_callback,
            param_callback=self.param_callback
        )
        return self

    def verify_auth_header(self, headers: Dict[str, str]) -> bool:
        """
        Verify that the custom auth headers are present and valid.

        Args:
            headers: Dictionary of headers to validate

        Returns:
            True if the headers are valid, False otherwise
        """
        # Check if using header auth
        if not self.header_callback and not self.expected_headers and not self.required_headers:
            return True  # Not using header auth

        try:
            # Check headers from callback
            if self.header_callback:
                expected_headers = self.header_callback()
                for key, value in expected_headers.items():
                    if key not in headers or headers[key] != value:
                        return False

            # Check explicitly expected headers
            for key, value in self.expected_headers.items():
                if key not in headers or headers[key] != value:
                    return False

            # Check required headers
            for key in self.required_headers:
                if key not in headers:
                    return False

            # Apply custom validators
            for key, validator in self.header_validators.items():
                if key in headers and not validator(headers[key]):
                    return False

            return True
        except Exception:
            return False

    def verify_auth_params(self, params: Dict[str, str]) -> bool:
        """
        Verify that the custom auth parameters are present and valid.

        Args:
            params: Dictionary of parameters to validate

        Returns:
            True if the parameters are valid, False otherwise
        """
        # Check if using param auth
        if not self.param_callback and not self.expected_params and not self.required_params:
            return True  # Not using param auth

        try:
            # Check params from callback
            if self.param_callback:
                expected_params = self.param_callback()
                for key, value in expected_params.items():
                    if key not in params or params[key] != value:
                        return False

            # Check explicitly expected params
            for key, value in self.expected_params.items():
                if key not in params or params[key] != value:
                    return False

            # Check required params
            for key in self.required_params:
                if key not in params:
                    return False

            # Apply custom validators
            for key, validator in self.param_validators.items():
                if key in params and not validator(params[key]):
                    return False

            return True
        except Exception:
            return False

    def get_auth_strategy(self) -> AuthStrategy:
        """
        Get the configured auth strategy.

        Returns:
            The configured CustomAuth strategy

        Raises:
            ValueError: If a failing callback was configured
        """
        # If we have a failing callback, raise the error immediately
        if hasattr(self, 'error_message') and self.header_callback:
            try:
                # This will raise the ValueError
                self.header_callback()
            except ValueError as e:
                # Re-raise the error
                raise ValueError(str(e))
        return self.auth_strategy

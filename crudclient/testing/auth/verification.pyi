"""
Authentication Verification Helpers and Extraction Utilities for Testing.

This module provides the `AuthVerificationHelpers` class, which aggregates static
methods for common authentication-related tasks in tests:
- Verifying the format and content of authentication headers (Basic, Bearer, API Key).
- Verifying properties of tokens (OAuth, JWT), such as scopes and expiration.
- Verifying authentication error responses and rate limit headers.
- Extracting credentials or payloads from headers and tokens.

These helpers often delegate to more specialized classes (`AuthHeaderVerification`,
`AuthTokenVerification`, etc.) but provide a convenient single point of access.

**Note:** Verification methods typically raise `VerificationError` on failure, while
extraction methods may raise `ValueError` for invalid input formats.
"""

from typing import Any, Dict, List, Optional, Tuple

from ..exceptions import VerificationError  # Import VerificationError
from .auth_error_verification import AuthErrorVerification
from .auth_extraction_utils import AuthExtractionUtils
from .auth_header_verification import AuthHeaderVerification
from .auth_token_verification import AuthTokenVerification

class AuthVerificationHelpers:
    """
    Aggregates static helper methods for verifying authentication behavior in tests.

    Provides a unified interface for common checks related to auth headers, tokens,
    error responses, and credential extraction. Methods typically raise exceptions
    (`VerificationError`, `ValueError`) upon failure or invalid input.
    """

    # Header verification methods
    @staticmethod
    def verify_basic_auth_header(header_value: str) -> bool:
        """
        Verify the format of a Basic Authentication header value.

        Checks if the value starts with "Basic " followed by a Base64 encoded string.
        Does *not* decode or validate the credentials themselves.

        Args:
            header_value: The full value of the Authorization header (e.g., "Basic dXNlcjpwYXNz").

        Returns:
            True if the format is valid.

        Raises:
            VerificationError: If the format is invalid (e.g., missing "Basic ", not Base64).

        Example:
            >>> AuthVerificationHelpers.verify_basic_auth_header("Basic dXNlcjpwYXNz")
            True
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_basic_auth_header("Bearer token")
        """
        ...

    @staticmethod
    def verify_bearer_auth_header(header_value: str) -> bool:
        """
        Verify the format of a Bearer Authentication header value.

        Checks if the value starts with "Bearer " followed by a non-empty token string.
        Does *not* validate the token content itself.

        Args:
            header_value: The full value of the Authorization header (e.g., "Bearer mytoken123").

        Returns:
            True if the format is valid.

        Raises:
            VerificationError: If the format is invalid (e.g., missing "Bearer ", empty token).

        Example:
            >>> AuthVerificationHelpers.verify_bearer_auth_header("Bearer abcdef12345")
            True
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_bearer_auth_header("Basic dXNlcjpwYXNz")
        """
        ...

    @staticmethod
    def verify_api_key_header(header_value: str, expected_key: Optional[str] = None) -> bool:
        """
        Verify an API Key header value, optionally matching against an expected key.

        Checks if the `header_value` is a non-empty string. If `expected_key` is
        provided, it also checks for an exact match.

        Args:
            header_value: The value of the header containing the API key (e.g., "mysecretkey").
                          This is the raw value, not including any scheme like "ApiKey ".
            expected_key: Optional. If provided, the `header_value` must match this exactly.

        Returns:
            True if the verification passes.

        Raises:
            VerificationError: If `header_value` is empty, or if `expected_key` is provided
                               and does not match `header_value`.

        Example:
            >>> AuthVerificationHelpers.verify_api_key_header("secret1", expected_key="secret1")
            True
            >>> AuthVerificationHelpers.verify_api_key_header("anykey") # Format check only
            True
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_api_key_header("secret1", expected_key="secret2")
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_api_key_header("")
        """
        ...

    @staticmethod
    def verify_auth_header_format(headers: Dict[str, str], auth_type: str, header_name: str = "Authorization") -> None:
        """
        Verify a specific authentication header exists and has the correct basic format.

        Looks for `header_name` in the `headers` dictionary and checks if its value
        starts with the expected scheme (`auth_type` + " ") or, if `auth_type` is
        "ApiKey", checks that the value is simply non-empty.

        Args:
            headers: Dictionary of headers (case-insensitive keys recommended).
            auth_type: The expected scheme ("Basic", "Bearer", or "ApiKey").
            header_name: The name of the header to check (default: "Authorization").

        Raises:
            VerificationError: If the header is missing, or if its value does not conform
                               to the expected format for the given `auth_type`.

        Example:
            >>> headers = {"Authorization": "Bearer mytoken", "Content-Type": "application/json"}
            >>> AuthVerificationHelpers.verify_auth_header_format(headers, "Bearer")
            >>> AuthVerificationHelpers.verify_auth_header_format({"X-API-Key": "key123"}, "ApiKey", header_name="X-API-Key")
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_auth_header_format(headers, "Basic")
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_auth_header_format({}, "Bearer")
        """
        ...
    # Token verification methods

    @staticmethod
    def verify_oauth_token(
        token: str,
        required_scopes: Optional[List[str]] = None,
        check_expiration: bool = True,
        expected_client_id: Optional[str] = None,
        expected_user: Optional[str] = None,
    ) -> bool:
        """
        Verify properties of an OAuth token (likely JWT), such as scopes and expiration.

        Assumes the token is a JWT unless underlying implementation handles others.
        Decodes the token payload to check claims. Does *not* typically verify
        the signature (depends on underlying implementation).

        Args:
            token: The OAuth token string (usually a JWT).
            required_scopes: Optional list of scope strings that must all be present
                             in the token's 'scope' or 'scp' claim.
            check_expiration: If True (default), checks if the token's 'exp' claim is in the past.
            expected_client_id: Optional string to match against the token's 'cid' or 'client_id' claim.
            expected_user: Optional string to match against the token's 'sub' or 'user_id' claim.

        Returns:
            True if all specified checks pass.

        Raises:
            VerificationError: If the token is invalid (e.g., cannot be decoded), expired
                              (if `check_expiration` is True), missing required scopes,
                              or does not match expected client/user IDs.

        Example:
            >>> # Assume valid_jwt contains {"exp": future_time, "scope": "read write", "cid": "app1"}
            >>> AuthVerificationHelpers.verify_oauth_token(valid_jwt, required_scopes=["read"], expected_client_id="app1")
            True
            >>> # Assume expired_jwt contains {"exp": past_time, "scope": "read"}
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_oauth_token(expired_jwt)
            >>> # Assume missing_scope_jwt contains {"exp": future_time, "scope": "read"}
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_oauth_token(missing_scope_jwt, required_scopes=["write"])
        """
        ...

    @staticmethod
    def verify_token_refresh(old_token: str, new_token: str) -> bool:
        """
        Verify basic indicators of a successful token refresh.

        Checks that the `new_token` is different from the `old_token` and that
        `new_token` is not empty. May perform additional checks depending on the
        underlying implementation (e.g., basic JWT structure).

        Args:
            old_token: The original token string.
            new_token: The token string received after a refresh attempt.

        Returns:
            True if `new_token` is non-empty and different from `old_token`.

        Raises:
            VerificationError: If `new_token` is empty or identical to `old_token`.

        Example:
            >>> AuthVerificationHelpers.verify_token_refresh("token1", "token2")
            True
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_token_refresh("token1", "token1")
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_token_refresh("token1", "")
        """
        ...

    @staticmethod
    def verify_token_expiration(token: str, jwt: bool = True) -> bool:
        """
        Verify if a token (assumed JWT by default) is expired based on its 'exp' claim.

        Args:
            token: The token string.
            jwt: If True (default), assumes JWT and decodes to find 'exp' claim.
                 If False, behavior depends on underlying implementation (may be no-op or error).

        Returns:
            True if the token is considered expired (e.g., 'exp' claim is in the past).
            False if the token is not expired or expiration cannot be determined.

        Raises:
            VerificationError: If `jwt` is True and the token cannot be decoded or lacks an 'exp' claim.

        Example:
            >>> # Assume expired_jwt has 'exp' in the past
            >>> AuthVerificationHelpers.verify_token_expiration(expired_jwt)
            True
            >>> # Assume valid_jwt has 'exp' in the future
            >>> AuthVerificationHelpers.verify_token_expiration(valid_jwt)
            False
        """
        ...

    @staticmethod
    def verify_token_usage(
        token: str, required_scopes: Optional[List[str]] = None, expected_client_id: Optional[str] = None, expected_user: Optional[str] = None
    ) -> None:
        """
        Verify token properties like scopes, client ID, and user ID (similar to verify_oauth_token).

        This is often an alias or wrapper around `verify_oauth_token` focusing on
        the authorization aspects (scopes, identity) rather than just validity.
        Assumes JWT structure to decode claims.

        Args:
            token: The token string (usually JWT).
            required_scopes: Optional list of scope strings that must be present.
            expected_client_id: Optional expected client ID ('cid', 'client_id').
            expected_user: Optional expected user ('sub', 'user_id').

        Raises:
            VerificationError: If the token is invalid, missing scopes, or doesn't match
                               expected client/user.

        Example:
            >>> # Assume token_jwt has {"scope": "read admin", "cid": "app1", "sub": "user123"}
            >>> AuthVerificationHelpers.verify_token_usage(token_jwt, required_scopes=["admin"], expected_client_id="app1")
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_token_usage(token_jwt, required_scopes=["write"])
        """
        ...

    @staticmethod
    def verify_refresh_behavior(old_token: str, new_token: str, expected_client_id: Optional[str] = None) -> None:
        """
        Verify aspects of token refresh behavior, potentially checking claims consistency.

        Extends `verify_token_refresh` by potentially decoding both tokens (if JWTs)
        and comparing claims like client ID or user ID to ensure they remain consistent
        after refresh, if supported by the underlying implementation.

        Args:
            old_token: The original token string.
            new_token: The new token string received after refresh.
            expected_client_id: Optional client ID to verify in the `new_token` (and potentially `old_token`).

        Raises:
            VerificationError: If basic refresh checks fail (see `verify_token_refresh`)
                               or if claims consistency checks fail (e.g., client ID changes).

        Example:
            >>> # Assume old_jwt has {"cid": "app1"} and new_jwt has {"cid": "app1"}
            >>> AuthVerificationHelpers.verify_refresh_behavior(old_jwt, new_jwt, expected_client_id="app1")
            >>> # Assume bad_new_jwt has {"cid": "app2"}
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_refresh_behavior(old_jwt, bad_new_jwt, expected_client_id="app1")
        """
        ...

    @staticmethod
    def verify_token_has_scopes(token: str, required_scopes: List[str]) -> None:
        """
        Verify a token (assumed JWT) contains all specified scopes in its 'scope'/'scp' claim.

        Args:
            token: The token string (usually JWT).
            required_scopes: List of scope strings that must all be present.

        Raises:
            VerificationError: If the token is invalid, lacks a scope claim, or is missing
                               one or more of the `required_scopes`.

        Example:
            >>> # Assume token_jwt has {"scope": "read write data:sync"}
            >>> AuthVerificationHelpers.verify_token_has_scopes(token_jwt, ["read", "write"])
            >>> AuthVerificationHelpers.verify_token_has_scopes(token_jwt, ["data:sync"])
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_token_has_scopes(token_jwt, ["admin"])
        """
        ...
    # Extraction utilities

    @staticmethod
    def extract_basic_auth_credentials(header_value: str) -> Tuple[str, str]:
        """
        Extract and decode username/password from a Basic Auth header value.

        Args:
            header_value: The full Authorization header value (e.g., "Basic dXNlcjpwYXNz").

        Returns:
            A tuple containing the decoded (username, password).

        Raises:
            ValueError: If the header value is not a valid Basic Auth format (e.g.,
                        missing "Basic ", invalid Base64, decoded string not "user:pass").

        Example:
            >>> AuthVerificationHelpers.extract_basic_auth_credentials("Basic dXNlcjE6cGFzc3dvcmQ=")
            ('user1', 'password')
            >>> # Raises ValueError: AuthVerificationHelpers.extract_basic_auth_credentials("Bearer token")
        """
        ...

    @staticmethod
    def extract_bearer_token(header_value: str) -> str:
        """
        Extract the token part from a Bearer Authentication header value.

        Args:
            header_value: The full Authorization header value (e.g., "Bearer mytoken123").

        Returns:
            The extracted token string (e.g., "mytoken123").

        Raises:
            ValueError: If the header value is not a valid Bearer Auth format (e.g.,
                        missing "Bearer ", empty token part).

        Example:
            >>> AuthVerificationHelpers.extract_bearer_token("Bearer abc-123")
            'abc-123'
            >>> # Raises ValueError: AuthVerificationHelpers.extract_bearer_token("Basic dXNlcjpwYXNz")
        """
        ...

    @staticmethod
    def extract_jwt_payload(token: str) -> Dict[str, Any]:
        """
        Decode and return the payload (claims) section of a JWT token.

        Performs Base64 decoding of the payload part. Does *not* verify the signature.

        Args:
            token: The JWT token string.

        Returns:
            A dictionary representing the decoded JSON payload (claims).

        Raises:
            ValueError: If the token is not a structurally valid JWT or the payload
                        is not valid JSON or Base64.

        Example:
            >>> # Assume jwt_string is "header.eyJzdWIiOiIxMjMifQ.signature"
            >>> payload = AuthVerificationHelpers.extract_jwt_payload(jwt_string)
            >>> print(payload['sub'])
            '123'
            >>> # Raises ValueError for invalid token format
        """
        ...
    # Error verification methods

    @staticmethod
    def verify_auth_error_response(
        response: Dict[str, Any], expected_status: int = 401, expected_error: Optional[str] = None, expected_error_description: Optional[str] = None
    ) -> None:
        """
        Verify the structure and content of an authentication error response body.

        Checks if the `response` dictionary contains expected keys (like 'status',
        'error', 'error_description') and if their values match the provided expected
        values.

        Args:
            response: The dictionary representing the parsed JSON error response body.
            expected_status: The expected HTTP status code (often checked separately,
                             but can be verified if present in the response body). Defaults to 401.
            expected_error: Optional expected value for the 'error' field (e.g., "invalid_token").
            expected_error_description: Optional expected value for the 'error_description' field.

        Raises:
            VerificationError: If the response structure is incorrect or if provided
                               expected values do not match the actual values in the response.

        Example:
            >>> error_resp = {"status": 401, "error": "invalid_request", "error_description": "Missing credentials"}
            >>> AuthVerificationHelpers.verify_auth_error_response(error_resp, expected_status=401, expected_error="invalid_request")
            >>> # Raises VerificationError if e.g. expected_error="invalid_token"
        """
        ...

    @staticmethod
    def verify_rate_limit_headers(
        headers: Dict[str, str], expected_limit: Optional[int] = None, expected_remaining: Optional[int] = None, expected_reset: Optional[int] = None
    ) -> None:
        """
        Verify the presence and optionally the values of standard rate limit headers.

        Checks for headers like 'X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset'.
        If expected values are provided, compares them against the header values (after
        converting header values to integers).

        Args:
            headers: Dictionary of response headers (case-insensitive keys recommended).
            expected_limit: Optional integer value for 'X-RateLimit-Limit'.
            expected_remaining: Optional integer value for 'X-RateLimit-Remaining'.
            expected_reset: Optional integer value for 'X-RateLimit-Reset' (timestamp).

        Raises:
            VerificationError: If a header is expected but missing, cannot be parsed as an
                               integer, or does not match the provided expected value.

        Example:
            >>> rate_limit_headers = {"X-RateLimit-Limit": "100", "X-RateLimit-Remaining": "99"}
            >>> AuthVerificationHelpers.verify_rate_limit_headers(rate_limit_headers, expected_limit=100)
            >>> AuthVerificationHelpers.verify_rate_limit_headers(rate_limit_headers, expected_remaining=99)
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_rate_limit_headers(rate_limit_headers, expected_limit=50)
            >>> # Raises VerificationError: AuthVerificationHelpers.verify_rate_limit_headers({}, expected_limit=100)
        """
        ...

# For backward compatibility
__all__ = ["AuthVerificationHelpers", "AuthExtractionUtils", "AuthHeaderVerification", "AuthTokenVerification", "AuthErrorVerification"]

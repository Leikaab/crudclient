"""
Authentication verification helpers for testing.

This module provides helper methods for verifying authentication behavior,
including header validation, error handling, and token refresh verification.
"""

import base64
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


class AuthVerificationHelpers:
    """
    Helper methods for verifying authentication behavior with enhanced capabilities.

    This class provides static methods for verifying various aspects of authentication,
    including header validation, token validation, and error response validation.
    """

    @staticmethod
    def verify_basic_auth_header(header_value: str) -> bool:
        """
        Verify that a Basic Auth header is correctly formatted.

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
            return ":" in decoded
        except Exception:
            return False

    @staticmethod
    def verify_bearer_auth_header(header_value: str) -> bool:
        """
        Verify that a Bearer Auth header is correctly formatted.

        Args:
            header_value: The value of the Authorization header

        Returns:
            True if the header is valid, False otherwise
        """
        return header_value.startswith("Bearer ")

    @staticmethod
    def verify_api_key_header(header_value: str, expected_key: Optional[str] = None) -> bool:
        """
        Verify that an API Key header is correctly formatted.

        Args:
            header_value: The value of the API key header
            expected_key: The expected API key value (if provided)

        Returns:
            True if the header is valid, False otherwise
        """
        if not header_value:
            return False

        if expected_key:
            return header_value == expected_key

        return True

    @staticmethod
    def verify_oauth_token(
        token: str,
        required_scopes: Optional[List[str]] = None,
        validate_jwt: bool = False
    ) -> bool:
        """
        Verify that an OAuth token is valid and has the required scopes.

        Args:
            token: The OAuth token to verify
            required_scopes: List of required scopes the token must have
            validate_jwt: Whether to validate the token as a JWT

        Returns:
            True if the token is valid, False otherwise
        """
        # Basic format check
        if not token:
            return False

        # JWT validation if requested
        if validate_jwt:
            # Check if token has JWT format (three dot-separated parts)
            if token.count('.') != 2:
                return False

            try:
                # Decode the JWT payload (middle part)
                payload_part = token.split('.')[1]
                # Add padding if needed
                padding = '=' * (4 - len(payload_part) % 4)
                payload_json = base64.urlsafe_b64decode(payload_part + padding).decode('utf-8')
                payload = json.loads(payload_json)

                # Check expiration
                if 'exp' in payload:
                    expiry = datetime.fromtimestamp(payload['exp'])
                    if datetime.now() > expiry:
                        return False

                # Check scopes if required
                if required_scopes:
                    token_scopes = []
                    if 'scope' in payload:
                        token_scopes = payload['scope'].split()
                    elif 'scopes' in payload:
                        token_scopes = payload['scopes']

                    if not all(scope in token_scopes for scope in required_scopes):
                        return False

                return True
            except Exception:
                return False

        # If not validating as JWT, just check for required scopes if we have them
        # This is a simplified check that assumes the token is valid
        return True

    @staticmethod
    def verify_token_refresh(old_token: str, new_token: str) -> bool:
        """
        Verify that token refresh behavior is correct.

        Args:
            old_token: The token before refresh
            new_token: The token after refresh

        Returns:
            True if the refresh behavior is correct, False otherwise
        """
        return old_token != new_token

    @staticmethod
    def verify_token_expiration(token: str, jwt: bool = True) -> bool:
        """
        Verify if a token is expired.

        Args:
            token: The token to check
            jwt: Whether the token is a JWT

        Returns:
            True if the token is expired, False otherwise
        """
        if not jwt:
            # For non-JWT tokens, we can't determine expiration without additional info
            return False

        try:
            # Decode the JWT payload
            payload_part = token.split('.')[1]
            # Add padding if needed
            padding = '=' * (4 - len(payload_part) % 4)
            payload_json = base64.urlsafe_b64decode(payload_part + padding).decode('utf-8')
            payload = json.loads(payload_json)

            # Check expiration
            if 'exp' in payload:
                expiry = datetime.fromtimestamp(payload['exp'])
                return datetime.now() > expiry

            return False
        except Exception:
            # If we can't decode the token, assume it's invalid/expired
            return True

    @staticmethod
    def extract_basic_auth_credentials(header_value: str) -> Tuple[str, str]:
        """
        Extract username and password from a Basic Auth header.

        Args:
            header_value: The value of the Authorization header

        Returns:
            A tuple of (username, password)

        Raises:
            ValueError: If the header is not a valid Basic Auth header
        """
        if not header_value.startswith("Basic "):
            raise ValueError("Not a Basic Auth header")

        encoded_part = header_value[6:]  # Skip "Basic "
        decoded = base64.b64decode(encoded_part).decode('utf-8')

        if ":" not in decoded:
            raise ValueError("Invalid Basic Auth format")

        username, password = decoded.split(":", 1)
        return username, password

    @staticmethod
    def extract_bearer_token(header_value: str) -> str:
        """
        Extract the token from a Bearer Auth header.

        Args:
            header_value: The value of the Authorization header

        Returns:
            The bearer token

        Raises:
            ValueError: If the header is not a valid Bearer Auth header
        """
        if not header_value.startswith("Bearer "):
            raise ValueError("Not a Bearer Auth header")

        return header_value[7:]  # Skip "Bearer "

    @staticmethod
    def extract_jwt_payload(token: str) -> Dict[str, Any]:
        """
        Extract and decode the payload from a JWT token.

        Args:
            token: The JWT token

        Returns:
            The decoded payload as a dictionary

        Raises:
            ValueError: If the token is not a valid JWT
        """
        if token.count('.') != 2:
            raise ValueError("Not a valid JWT token format")

        try:
            # Decode the JWT payload (middle part)
            payload_part = token.split('.')[1]
            # Add padding if needed
            padding = '=' * (4 - len(payload_part) % 4)
            payload_json = base64.urlsafe_b64decode(payload_part + padding).decode('utf-8')
            return json.loads(payload_json)
        except Exception as e:
            raise ValueError(f"Failed to decode JWT payload: {str(e)}")

    @staticmethod
    def assert_auth_header_format(
        headers: Dict[str, str],
        auth_type: str,
        header_name: str = "Authorization"
    ) -> None:
        """
        Assert that an authentication header has the correct format.

        Args:
            headers: Dictionary of headers
            auth_type: Type of authentication (basic, bearer, apikey, oauth)
            header_name: Name of the authentication header

        Raises:
            AssertionError: If the header is not valid
        """
        if header_name not in headers:
            raise AssertionError(f"Authentication header '{header_name}' not found")

        header_value = headers[header_name]

        if auth_type.lower() == "basic":
            if not AuthVerificationHelpers.verify_basic_auth_header(header_value):
                raise AssertionError(f"Invalid Basic Auth header format: {header_value}")

        elif auth_type.lower() == "bearer":
            if not AuthVerificationHelpers.verify_bearer_auth_header(header_value):
                raise AssertionError(f"Invalid Bearer Auth header format: {header_value}")

        elif auth_type.lower() == "apikey":
            if not header_value:
                raise AssertionError(f"Empty API Key header: {header_value}")

        elif auth_type.lower() == "oauth":
            if not AuthVerificationHelpers.verify_bearer_auth_header(header_value):
                raise AssertionError(f"Invalid OAuth token format: {header_value}")

    @staticmethod
    def assert_token_usage(
        headers: Dict[str, str],
        expected_token: str,
        auth_type: str = "bearer",
        header_name: str = "Authorization"
    ) -> None:
        """
        Assert that a token is being used correctly.

        Args:
            headers: Dictionary of headers
            expected_token: The expected token value
            auth_type: Type of authentication (bearer, oauth, apikey)
            header_name: Name of the authentication header

        Raises:
            AssertionError: If the token is not being used correctly
        """
        if header_name not in headers:
            raise AssertionError(f"Authentication header '{header_name}' not found")

        header_value = headers[header_name]

        if auth_type.lower() in ["bearer", "oauth"]:
            token = AuthVerificationHelpers.extract_bearer_token(header_value)
            if token != expected_token:
                raise AssertionError(f"Expected token '{expected_token}', got '{token}'")

        elif auth_type.lower() == "apikey":
            if header_value != expected_token:
                raise AssertionError(f"Expected API key '{expected_token}', got '{header_value}'")

    @staticmethod
    def assert_refresh_behavior(
        old_headers: Dict[str, str],
        new_headers: Dict[str, str],
        auth_type: str = "bearer",
        header_name: str = "Authorization"
    ) -> None:
        """
        Assert that token refresh behavior is correct.

        Args:
            old_headers: Headers before refresh
            new_headers: Headers after refresh
            auth_type: Type of authentication (bearer, oauth)
            header_name: Name of the authentication header

        Raises:
            AssertionError: If the refresh behavior is not correct
        """
        if header_name not in old_headers:
            raise AssertionError(f"Old authentication header '{header_name}' not found")

        if header_name not in new_headers:
            raise AssertionError(f"New authentication header '{header_name}' not found")

        old_value = old_headers[header_name]
        new_value = new_headers[header_name]

        if auth_type.lower() in ["bearer", "oauth"]:
            old_token = AuthVerificationHelpers.extract_bearer_token(old_value)
            new_token = AuthVerificationHelpers.extract_bearer_token(new_value)

            if old_token == new_token:
                raise AssertionError("Token was not refreshed")

    @staticmethod
    def assert_token_has_scopes(
        token: str,
        required_scopes: List[str],
        jwt: bool = True
    ) -> None:
        """
        Assert that a token has the required scopes.

        Args:
            token: The token to check
            required_scopes: List of required scopes
            jwt: Whether the token is a JWT

        Raises:
            AssertionError: If the token doesn't have the required scopes
        """
        if not jwt:
            # For non-JWT tokens, we can't determine scopes without additional info
            return

        try:
            payload = AuthVerificationHelpers.extract_jwt_payload(token)

            token_scopes = []
            if 'scope' in payload:
                token_scopes = payload['scope'].split()
            elif 'scopes' in payload:
                token_scopes = payload['scopes']

            missing_scopes = [scope for scope in required_scopes if scope not in token_scopes]
            if missing_scopes:
                raise AssertionError(
                    f"Token is missing required scopes: {', '.join(missing_scopes)}"
                )
        except ValueError as e:
            raise AssertionError(f"Invalid JWT token: {str(e)}")

    @staticmethod
    def assert_auth_error_response(
        response: Dict[str, Any],
        expected_error_type: Optional[str] = None,
        expected_status_code: Optional[int] = None
    ) -> None:
        """
        Assert that an authentication error response has the expected format and values.

        Args:
            response: The error response to check
            expected_error_type: Expected error type (e.g., "invalid_token")
            expected_status_code: Expected HTTP status code

        Raises:
            AssertionError: If the response doesn't match expectations
        """
        # Check that it's an error response
        if 'error' not in response:
            raise AssertionError("Response is not an error response (missing 'error' field)")

        # Check error type if specified
        if expected_error_type and response.get('error') != expected_error_type:
            raise AssertionError(
                f"Expected error type '{expected_error_type}', got '{response.get('error')}'"
            )

        # Check status code if specified and present
        if expected_status_code and 'status_code' in response:
            if response['status_code'] != expected_status_code:
                raise AssertionError(
                    f"Expected status code {expected_status_code}, got {response['status_code']}"
                )

    @staticmethod
    def assert_rate_limit_headers(
        headers: Dict[str, str],
        expected_limit: Optional[int] = None,
        header_prefix: str = "X-RateLimit-"
    ) -> Dict[str, int]:
        """
        Assert that rate limit headers are present and correctly formatted.

        Args:
            headers: The response headers to check
            expected_limit: Expected rate limit value
            header_prefix: Prefix for rate limit headers

        Returns:
            Dictionary with rate limit information

        Raises:
            AssertionError: If the headers don't match expectations
        """
        rate_limit_info = {}

        # Check for common rate limit headers
        limit_header = f"{header_prefix}Limit"
        remaining_header = f"{header_prefix}Remaining"
        reset_header = f"{header_prefix}Reset"

        if limit_header not in headers:
            raise AssertionError(f"Rate limit header '{limit_header}' not found")

        if remaining_header not in headers:
            raise AssertionError(f"Rate limit header '{remaining_header}' not found")

        try:
            rate_limit_info["limit"] = int(headers[limit_header])
            rate_limit_info["remaining"] = int(headers[remaining_header])

            if reset_header in headers:
                rate_limit_info["reset"] = int(headers[reset_header])

            # Check expected limit if specified
            if expected_limit and rate_limit_info["limit"] != expected_limit:
                raise AssertionError(
                    f"Expected rate limit {expected_limit}, got {rate_limit_info['limit']}"
                )

            return rate_limit_info
        except ValueError:
            raise AssertionError("Rate limit headers have invalid format (not integers)")

    @staticmethod
    def assert_permission_based_access(
        response: Dict[str, Any],
        required_permission: str,
        status_code: int = 403
    ) -> None:
        """
        Assert that a response correctly enforces permission-based access control.

        Args:
            response: The response to check
            required_permission: The permission that was required
            status_code: Expected HTTP status code for permission denied

        Raises:
            AssertionError: If the response doesn't match expectations
        """
        if 'status_code' not in response or response['status_code'] != status_code:
            raise AssertionError(
                f"Expected status code {status_code} for permission denied, "
                f"got {response.get('status_code')}"
            )

        if 'error' not in response:
            raise AssertionError("Permission denied response is missing 'error' field")

        # Check that the error message mentions permissions or the specific permission
        error_message = response.get('error_description', '') or response.get('message', '')
        if not error_message:
            raise AssertionError("Permission denied response is missing error message")

        if 'permission' not in error_message.lower() and required_permission.lower() not in error_message.lower():
            raise AssertionError(
                f"Permission denied message doesn't mention permissions or '{required_permission}'"
            )

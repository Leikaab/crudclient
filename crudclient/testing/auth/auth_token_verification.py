from datetime import datetime
from typing import List, Optional

from ..exceptions import VerificationError  # Import VerificationError
from .auth_extraction_utils import AuthExtractionUtils


class AuthTokenVerification:
    @staticmethod
    def verify_oauth_token(
        token: str,
        required_scopes: Optional[List[str]] = None,
        check_expiration: bool = True,
        expected_client_id: Optional[str] = None,
        expected_user: Optional[str] = None,
    ) -> bool:
        try:
            # Try to decode as JWT
            payload = AuthExtractionUtils.extract_jwt_payload(token)

            # Check expiration
            if check_expiration and "exp" in payload:
                exp_timestamp = payload["exp"]
                if datetime.now().timestamp() > exp_timestamp:
                    return False

            # Check client ID
            if expected_client_id and "client_id" in payload:
                if payload["client_id"] != expected_client_id:
                    return False

            # Check user
            if expected_user and "sub" in payload:
                if payload["sub"] != expected_user:
                    return False

            # Check scopes
            if required_scopes and "scope" in payload:
                token_scopes = payload["scope"].split()
                for scope in required_scopes:
                    if scope not in token_scopes:
                        return False

            return True
        except ValueError:
            # Not a JWT token, could be an opaque token
            # In a real implementation, you would validate against the token introspection endpoint
            return True

    @staticmethod
    def verify_token_refresh(old_token: str, new_token: str) -> bool:
        # Check that the tokens are different
        if old_token == new_token:
            return False

        try:
            # Try to decode as JWT
            old_payload = AuthExtractionUtils.extract_jwt_payload(old_token)
            new_payload = AuthExtractionUtils.extract_jwt_payload(new_token)

            # Check that the new token has a later expiration
            if "exp" in old_payload and "exp" in new_payload:
                if new_payload["exp"] <= old_payload["exp"]:
                    return False

            # Check that the client ID and user are the same
            for key in ["client_id", "sub"]:
                if key in old_payload and key in new_payload:
                    if old_payload[key] != new_payload[key]:
                        return False

            return True
        except ValueError:
            # Not JWT tokens, could be opaque tokens
            # In a real implementation, you would validate against the token introspection endpoint
            return True

    @staticmethod
    def verify_token_expiration(token: str, jwt: bool = True) -> bool:
        if not jwt:
            # For non-JWT tokens, we can't determine expiration without introspection
            return False

        try:
            payload = AuthExtractionUtils.extract_jwt_payload(token)

            if "exp" in payload:
                exp_timestamp = payload["exp"]
                return datetime.now().timestamp() > exp_timestamp

            return False  # No expiration claim
        except ValueError:
            return False  # Not a valid JWT

    @staticmethod
    def verify_token_usage(
        token: str, required_scopes: Optional[List[str]] = None, expected_client_id: Optional[str] = None, expected_user: Optional[str] = None
    ) -> None:
        if not token:
            raise VerificationError("Token is empty")

        try:
            # Try to decode as JWT
            payload = AuthExtractionUtils.extract_jwt_payload(token)

            # Check expiration
            if "exp" in payload:
                exp_timestamp = payload["exp"]
                if datetime.now().timestamp() > exp_timestamp:
                    raise VerificationError("Token is expired")

            # Check client ID
            if expected_client_id and "client_id" in payload:
                if payload["client_id"] != expected_client_id:
                    raise VerificationError(f"Token client ID mismatch: expected {expected_client_id}, got {payload['client_id']}")

            # Check user
            if expected_user and "sub" in payload:
                if payload["sub"] != expected_user:
                    raise VerificationError(f"Token user mismatch: expected {expected_user}, got {payload['sub']}")

            # Check scopes
            if required_scopes and "scope" in payload:
                token_scopes = payload["scope"].split()
                for scope in required_scopes:
                    if scope not in token_scopes:
                        raise VerificationError(f"Token missing required scope: {scope}")
        except ValueError:
            # Not a JWT token, could be an opaque token
            # In a real implementation, you would validate against the token introspection endpoint
            pass

    @staticmethod
    def verify_refresh_behavior(old_token: str, new_token: str, expected_client_id: Optional[str] = None) -> None:
        # Check that the tokens are different
        if old_token == new_token:
            raise VerificationError("New token is the same as the old token")

        try:
            # Try to decode as JWT
            old_payload = AuthExtractionUtils.extract_jwt_payload(old_token)
            new_payload = AuthExtractionUtils.extract_jwt_payload(new_token)

            # Check that the new token has a later expiration
            if "exp" in old_payload and "exp" in new_payload:
                if new_payload["exp"] <= old_payload["exp"]:
                    raise VerificationError("New token does not have a later expiration")

            # Check that the client ID is the same
            if "client_id" in old_payload and "client_id" in new_payload:
                if old_payload["client_id"] != new_payload["client_id"]:
                    raise VerificationError("Client ID changed during refresh")

                if expected_client_id and new_payload["client_id"] != expected_client_id:
                    raise VerificationError(f"Token client ID mismatch: expected {expected_client_id}, got {new_payload['client_id']}")

            # Check that the user is the same
            if "sub" in old_payload and "sub" in new_payload:
                if old_payload["sub"] != new_payload["sub"]:
                    raise VerificationError("User changed during refresh")
        except ValueError:
            # Not JWT tokens, could be opaque tokens
            # In a real implementation, you would validate against the token introspection endpoint
            pass

    @staticmethod
    def verify_token_has_scopes(token: str, required_scopes: List[str]) -> None:
        try:
            # Try to decode as JWT
            payload = AuthExtractionUtils.extract_jwt_payload(token)

            # Check scopes
            if "scope" in payload:
                token_scopes = payload["scope"].split()
                for scope in required_scopes:
                    if scope not in token_scopes:
                        raise VerificationError(f"Token missing required scope: {scope}")
            else:
                raise VerificationError("Token does not contain scope claim")
        except ValueError as e:
            # Not a JWT token, could be an opaque token
            # In a real implementation, you would validate against the token introspection endpoint
            raise VerificationError(f"Could not extract scopes from token: {str(e)}")

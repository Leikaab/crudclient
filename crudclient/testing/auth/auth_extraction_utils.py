import base64
import json
from typing import Any, Dict, Tuple


class AuthExtractionUtils:

    @staticmethod
    def extract_basic_auth_credentials(header_value: str) -> Tuple[str, str]:
        if not header_value.startswith("Basic "):
            raise ValueError("Not a Basic Auth header")

        try:
            # Extract the base64-encoded credentials
            encoded_credentials = header_value[6:]  # Skip "Basic "
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")

            # Split into username and password
            if ":" not in decoded_credentials:
                raise ValueError("Invalid Basic Auth format")

            username, password = decoded_credentials.split(":", 1)
            return username, password
        except Exception as e:
            raise ValueError(f"Invalid Basic Auth header: {str(e)}")

    @staticmethod
    def extract_bearer_token(header_value: str) -> str:
        if not header_value.startswith("Bearer "):
            raise ValueError("Not a Bearer Auth header")

        # Extract the token
        token = header_value[7:]  # Skip "Bearer "
        if not token:
            raise ValueError("Empty Bearer token")

        return token

    @staticmethod
    def extract_jwt_payload(token: str) -> Dict[str, Any]:
        if not isinstance(token, str):
            raise TypeError(f"Expected token to be a string, but got {type(token).__name__}")

        # Split the token into parts
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Not a valid JWT token")

        try:
            # Decode the payload (second part)
            payload_base64 = parts[1]

            # Add padding if needed
            padding = len(payload_base64) % 4
            if padding:
                payload_base64 += "=" * (4 - padding)

            # Decode and parse as JSON
            payload_json = base64.b64decode(payload_base64).decode("utf-8")
            return json.loads(payload_json)
        except Exception as e:
            raise ValueError(f"Invalid JWT payload: {str(e)}")

from typing import Dict, Optional

from ..exceptions import VerificationError  # Import VerificationError
from .auth_extraction_utils import AuthExtractionUtils


class AuthHeaderVerification:
    @staticmethod
    def verify_basic_auth_header(header_value: str) -> bool:
        if not header_value.startswith("Basic "):
            return False

        try:
            AuthExtractionUtils.extract_basic_auth_credentials(header_value)
            return True
        except ValueError:
            return False

    @staticmethod
    def verify_bearer_auth_header(header_value: str) -> bool:
        if not header_value.startswith("Bearer "):
            return False

        # Check if there's a token after "Bearer "
        token = header_value[7:]
        return bool(token.strip())

    @staticmethod
    def verify_api_key_header(header_value: str, expected_key: Optional[str] = None) -> bool:

        # Check if the header is empty
        if not header_value:
            return False

        # If an expected key is provided, check if it matches
        if expected_key is not None:
            return header_value == expected_key

        return True

    @staticmethod
    def verify_auth_header_format(headers: Dict[str, str], auth_type: str, header_name: str = "Authorization") -> None:
        # Check if the header exists
        if header_name not in headers:
            raise VerificationError(f"Missing {header_name} header")

        header_value = headers[header_name]

        # Verify the header based on the auth type (case-insensitive)
        auth_type_lower = auth_type.lower()
        if auth_type_lower == "basic":
            if not AuthHeaderVerification.verify_basic_auth_header(header_value):
                raise VerificationError(f"Invalid Basic Auth header: {header_value}")
        elif auth_type_lower == "bearer":
            if not AuthHeaderVerification.verify_bearer_auth_header(header_value):
                raise VerificationError(f"Invalid Bearer Auth header: {header_value}")
        elif auth_type_lower == "apikey":
            # Assuming header_name might vary for ApiKey, but verification logic handles it
            if not AuthHeaderVerification.verify_api_key_header(header_value):
                raise VerificationError(f"Invalid API Key header in {header_name}: {header_value}")
        else:
            raise VerificationError(f"Unsupported auth type: {auth_type}")

from typing import Any, Dict, Optional

from ..exceptions import VerificationError  # Import VerificationError


class AuthErrorVerification:

    @staticmethod
    def verify_auth_error_response(
        response: Dict[str, Any], expected_status: int = 401, expected_error: Optional[str] = None, expected_error_description: Optional[str] = None
    ) -> None:
        # Check status code
        if "status_code" in response:
            if response["status_code"] != expected_status:
                raise VerificationError(f"Expected status code {expected_status}, got {response['status_code']}")

        # Check error code
        if expected_error and "error" in response:
            if response["error"] != expected_error:
                raise VerificationError(f"Expected error code '{expected_error}', got '{response['error']}'")

        # Check error description
        if expected_error_description and "error_description" in response:
            if response["error_description"] != expected_error_description:
                raise VerificationError(f"Expected error description '{expected_error_description}', got '{response['error_description']}'")

    @staticmethod
    def verify_rate_limit_headers(
        headers: Dict[str, str], expected_limit: Optional[int] = None, expected_remaining: Optional[int] = None, expected_reset: Optional[int] = None
    ) -> None:
        # Check for standard rate limit headers
        rate_limit_headers = {"X-RateLimit-Limit": expected_limit, "X-RateLimit-Remaining": expected_remaining, "X-RateLimit-Reset": expected_reset}

        for header, expected_value in rate_limit_headers.items():
            if expected_value is not None:
                if header not in headers:
                    raise VerificationError(f"Missing rate limit header: {header}")

                try:
                    actual_value = int(headers[header])
                    if actual_value != expected_value:
                        raise VerificationError(f"Expected {header} to be {expected_value}, got {actual_value}")
                except ValueError:
                    raise VerificationError(f"Rate limit header {header} is not an integer: {headers[header]}")

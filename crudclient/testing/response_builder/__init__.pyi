# crudclient/testing/response_builder/__init__.pyi
from typing import Dict, Optional, Union

from .response import MockResponse

class ResponseBuilder:
    """
    Utility class for creating common API error responses.

    Provides static methods to generate standardized mock responses for common
    API error scenarios like validation errors, rate limiting, and authentication failures.
    """

    @staticmethod
    def create_validation_error(
        fields: Optional[Dict[str, str]] = None, status_code: int = 422, error_code: str = "VALIDATION_ERROR", message: str = "Validation failed"
    ) -> MockResponse:
        """
        Create a mock response for a validation error.

        Generates a standardized validation error response with field-specific error messages,
        following common REST API error patterns.

        Args:
            fields: Dictionary mapping field names to error messages
            status_code: HTTP status code for the response (typically 422 Unprocessable Entity)
            error_code: Error code identifier
            message: General error message

        Returns:
            A MockResponse instance with validation error details

        Examples:
            ```python
            # Create a validation error for email and password fields
            response = ResponseBuilder.create_validation_error({
                "email": "Invalid email format",
                "password": "Password must be at least 8 characters"
            })

            # Create a custom validation error
            response = ResponseBuilder.create_validation_error(
                fields={"name": "Name is required"},
                status_code=400,
                error_code="INVALID_REQUEST",
                message="Request validation failed"
            )
            ```
        """
        ...

    @staticmethod
    def create_rate_limit_error(limit: int = 100, remaining: int = 0, reset_seconds: int = 60, status_code: int = 429) -> MockResponse:
        """
        Create a mock response for a rate limit exceeded error.

        Generates a standardized rate limit error response with appropriate headers
        indicating limits, remaining requests, and reset time.

        Args:
            limit: Maximum number of requests allowed in the time window
            remaining: Number of requests remaining in the current time window
            reset_seconds: Seconds until the rate limit resets
            status_code: HTTP status code (typically 429 Too Many Requests)

        Returns:
            A MockResponse instance with rate limit error details and headers

        Examples:
            ```python
            # Create a standard rate limit error
            response = ResponseBuilder.create_rate_limit_error()

            # Create a custom rate limit error
            response = ResponseBuilder.create_rate_limit_error(
                limit=1000,
                remaining=0,
                reset_seconds=300
            )
            ```
        """
        ...

    @staticmethod
    def create_auth_error(error_type: str = "invalid_token", status_code: int = 401) -> MockResponse:
        """
        Create a mock response for an authentication error.

        Generates a standardized authentication error response. The response includes:
        - A `WWW-Authenticate` header with the format:
          `Bearer realm="api", error="{error_type}", error_description="{message}"`
        - A JSON body with the structure:
          `{"errors": [{"message": message, "code": error_type.upper(), "request_id": uuid}]}`

        Args:
            error_type: Type of authentication error. Supported values:
                        "invalid_token", "invalid_credentials", "missing_credentials",
                        "insufficient_scope", "mfa_required"
            status_code: HTTP status code (typically 401 Unauthorized)

        Returns:
            A MockResponse instance with authentication error details and headers

        Examples:
            ```python
            # Create an invalid token error
            response = ResponseBuilder.create_auth_error()

            # Create a missing credentials error
            response = ResponseBuilder.create_auth_error(
                error_type="missing_credentials"
            )

            # Create a custom auth error with 403 Forbidden status
            response = ResponseBuilder.create_auth_error(
                error_type="insufficient_scope",
                status_code=403
            )
            ```
        """
        ...

__all__ = [
    "MockResponse",
    "ResponseBuilder",
]

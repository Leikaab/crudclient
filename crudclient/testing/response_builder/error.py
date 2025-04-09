"""
Error response builder utilities for mock client.

This module provides utilities for building error API responses with consistent
formats and appropriate HTTP status codes. It supports common error types such as
validation errors, rate limit errors, and authentication errors.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .basic import BasicResponseBuilder
from .response import MockResponse


class ErrorResponseBuilder:
    """
    Builder for creating error API responses.

    This class provides methods to generate standardized error responses for various
    error scenarios. It creates responses with appropriate status codes, error messages,
    and additional context such as request IDs and timestamps. The responses follow
    common API error format conventions.
    """

    @staticmethod
    def create_error_response(
        status_code: int = 400,
        message: str = "Bad Request",
        error_code: str = "BAD_REQUEST",
        details: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        """
        Create a generic error response.

        This method creates a standardized error response with configurable details.
        It follows common API error format conventions and includes a unique request ID
        for error tracking.

        Args:
            status_code: HTTP status code for the response
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details or context
            request_id: Unique identifier for the request (generated if not provided)
            headers: HTTP headers to include in the response

        Returns:
            A MockResponse instance configured as an error response
        """
        error: Dict[str, Any] = {
            "message": message,
            "code": error_code,
        }

        if details:
            error["details"] = details  # type: ignore

        if request_id:
            error["request_id"] = request_id
        else:
            error["request_id"] = str(uuid.uuid4())

        errors = [error]

        response_headers = {
            "Content-Type": "application/json",
        }

        # Add common error headers
        if status_code == 429:
            retry_after = random.randint(30, 120)
            response_headers["Retry-After"] = str(retry_after)
            response_headers["X-RateLimit-Reset"] = str(int((datetime.now() + timedelta(seconds=retry_after)).timestamp()))

        # Merge with custom headers if provided
        if headers:
            response_headers.update(headers)

        return BasicResponseBuilder.create_response(
            status_code=status_code,
            errors=errors,
            headers=response_headers
        )

    @staticmethod
    def create_validation_error(
        fields: Dict[str, str],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
    ) -> MockResponse:
        """
        Create a validation error response with field-specific errors.

        This method creates a response for validation errors, with detailed information
        about which fields failed validation and why. This is particularly useful for
        form submissions and API requests with invalid data.

        Args:
            fields: Dictionary mapping field names to error messages
            status_code: HTTP status code for the response
            error_code: Error code for the validation error
            message: Overall error message

        Returns:
            A MockResponse instance configured with validation errors
        """
        details = []
        for field, error_msg in fields.items():
            details.append({
                "field": field,
                "message": error_msg,
                "code": "INVALID_FIELD"
            })

        return ErrorResponseBuilder.create_error_response(
            status_code=status_code,
            message=message,
            error_code=error_code,
            details=details
        )

    @staticmethod
    def create_rate_limit_error(
        limit: int = 100,
        remaining: int = 0,
        reset_seconds: int = 60,
    ) -> MockResponse:
        """
        Create a rate limit error response.

        This method creates a response for rate limiting errors, including information
        about the rate limit, remaining requests, and when the limit will reset.
        It includes appropriate headers according to common rate limiting conventions.

        Args:
            limit: Maximum number of requests allowed in the time window
            remaining: Number of requests remaining in the current time window
            reset_seconds: Seconds until the rate limit resets

        Returns:
            A MockResponse instance configured as a rate limit error
        """
        reset_time = int((datetime.now() + timedelta(seconds=reset_seconds)).timestamp())

        headers = {
            "Content-Type": "application/json",
            "Retry-After": str(reset_seconds),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time)
        }

        return ErrorResponseBuilder.create_error_response(
            status_code=429,
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            details=[{
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time
            }],
            request_id=str(uuid.uuid4()),
            headers=headers
        )

    @staticmethod
    def create_auth_error(
        error_type: str = "invalid_token",
        status_code: int = 401,
    ) -> MockResponse:
        """
        Create an authentication error response.

        This method creates a response for authentication errors, with appropriate
        status codes and WWW-Authenticate headers according to OAuth 2.0 and HTTP
        authentication specifications.

        Args:
            error_type: Type of authentication error (e.g., invalid_token, expired_token)
            status_code: HTTP status code for the response (typically 401 or 403)

        Returns:
            A MockResponse instance configured as an authentication error
        """
        error_messages = {
            "invalid_token": "The access token is invalid",
            "expired_token": "The access token has expired",
            "insufficient_scope": "The access token does not have the required scope",
            "invalid_client": "Client authentication failed",
            "invalid_grant": "The provided authorization grant is invalid",
            "unauthorized_client": "The client is not authorized to use this grant type"
        }

        message = error_messages.get(error_type, "Authentication failed")

        headers = {
            "Content-Type": "application/json",
            "WWW-Authenticate": f'Bearer realm="api", error="{error_type}", error_description="{message}"'
        }

        return ErrorResponseBuilder.create_error_response(
            status_code=status_code,
            message=message,
            error_code=error_type.upper(),
            headers=headers
        )

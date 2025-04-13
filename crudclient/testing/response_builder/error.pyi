"""
Error response builder utilities for mock client.

This module provides utilities for creating various types of error responses
commonly encountered in API interactions, such as validation errors,
rate limit errors, and authentication errors.
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .basic import BasicResponseBuilder
from .response import MockResponse

class ErrorResponseBuilder:
    """
    Builder for creating standardized API error responses.

    This class provides static methods for generating various types of error responses
    that follow common API error patterns, including validation errors, rate limiting
    errors, and authentication errors.
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
        Create a standardized error response.

        Generates an error response with a consistent structure including message,
        error code, optional details, and a request ID for tracking.

        Args:
            status_code: HTTP status code for the error response
            message: Human-readable error message
            error_code: Machine-readable error code identifier
            details: Additional error details, typically for field-level errors
            request_id: Unique identifier for the request (generated if not provided)
            headers: HTTP headers to include in the response

        Returns:
            A MockResponse instance representing an error response
        """
        ...

    @staticmethod
    def create_validation_error(
        fields: Dict[str, str],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
    ) -> MockResponse:
        """
        Create a validation error response with field-specific error messages.

        Generates a structured validation error response that includes specific
        error messages for each invalid field.

        Args:
            fields: Dictionary mapping field names to error messages
            status_code: HTTP status code (defaults to 422 Unprocessable Entity)
            error_code: Machine-readable error code identifier
            message: Human-readable error message

        Returns:
            A MockResponse instance representing a validation error
        """
        ...

    @staticmethod
    def create_rate_limit_error(
        limit: int = 100,
        remaining: int = 0,
        reset_seconds: int = 60,
    ) -> MockResponse:
        """
        Create a rate limit exceeded error response.

        Generates a rate limiting error response with appropriate headers
        indicating limits, remaining requests, and reset time.

        Args:
            limit: Maximum number of requests allowed in the time window
            remaining: Number of requests remaining in the current window
            reset_seconds: Seconds until the rate limit resets

        Returns:
            A MockResponse instance representing a rate limit error with
            appropriate rate limiting headers
        """
        ...

    @staticmethod
    def create_auth_error(
        error_type: str = "invalid_token",
        status_code: int = 401,
    ) -> MockResponse:
        """
        Create an authentication error response.

        Generates an authentication error response with appropriate WWW-Authenticate
        headers based on the specified error type.

        Args:
            error_type: Type of authentication error (e.g., "invalid_token",
                       "expired_token", "insufficient_scope")
            status_code: HTTP status code (defaults to 401 Unauthorized)

        Returns:
            A MockResponse instance representing an authentication error with
            appropriate WWW-Authenticate headers
        """
        ...

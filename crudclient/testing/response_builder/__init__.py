"""
Response builder module for creating mock responses.

This module provides utilities for building mock responses for testing purposes.
"""

from .response import MockResponse
from .patterns import ResponsePattern
from .api_patterns import APIPatternBuilder
from .basic import BasicResponseBuilder
from .data_generation import DataGenerationBuilder
from .entity_relationships import EntityRelationshipBuilder
from .error import ErrorResponseBuilder
from .pagination import PaginationResponseBuilder
from .validation import ValidationErrorBuilder, BusinessLogicConstraintBuilder
from .validation import (
    required_field, min_length, max_length, pattern_match,
    min_value, max_value, one_of, is_email, is_url, is_date
)


class ResponseBuilder:
    """
    Utility class for building mock responses.

    This class provides static methods for creating common types of mock responses
    such as validation errors, rate limit errors, and authentication errors.
    """

    @staticmethod
    def create_validation_error(
        fields=None,
        status_code=422,
        error_code="VALIDATION_ERROR",
        message="Validation failed"
    ):
        """
        Create a validation error response.

        Args:
            fields: Dictionary of field names to error messages
            status_code: HTTP status code to return
            error_code: Error code to include in the response
            message: Error message to include in the response

        Returns:
            A MockResponse configured as a validation error
        """
        if fields is None:
            fields = {"field": "Invalid value"}

        data = {
            "error": {
                "code": error_code,
                "message": message,
                "fields": fields
            }
        }

        return MockResponse(
            status_code=status_code,
            json_data=data,
            headers={"Content-Type": "application/json"}
        )

    @staticmethod
    def create_rate_limit_error(
        limit=100,
        remaining=0,
        reset_seconds=60,
        status_code=429
    ):
        """
        Create a rate limit error response.

        Args:
            limit: Rate limit maximum requests
            remaining: Remaining requests allowed
            reset_seconds: Seconds until rate limit resets
            status_code: HTTP status code to return

        Returns:
            A MockResponse configured as a rate limit error
        """
        data = {
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded. Please try again later."
            }
        }

        headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_seconds)
        }

        return MockResponse(
            status_code=status_code,
            json_data=data,
            headers=headers
        )

    @staticmethod
    def create_auth_error(
        error_type="invalid_token",
        status_code=401
    ):
        """
        Create an authentication error response.

        Args:
            error_type: Type of authentication error
            status_code: HTTP status code to return

        Returns:
            A MockResponse configured as an authentication error
        """
        error_messages = {
            "invalid_token": "The access token is invalid or has expired",
            "invalid_credentials": "Invalid username or password",
            "missing_credentials": "Authentication credentials were not provided",
            "insufficient_scope": "The access token does not have the required scope",
            "mfa_required": "Multi-factor authentication is required"
        }

        message = error_messages.get(
            error_type,
            "Authentication failed"
        )

        data = {
            "error": {
                "code": error_type.upper(),
                "message": message
            }
        }

        headers = {
            "Content-Type": "application/json",
            "WWW-Authenticate": f'Bearer error="{error_type}", error_description="{message}"'
        }

        return MockResponse(
            status_code=status_code,
            json_data=data,
            headers=headers
        )

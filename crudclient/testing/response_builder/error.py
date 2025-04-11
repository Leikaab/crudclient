import random
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .basic import BasicResponseBuilder
from .response import MockResponse


class ErrorResponseBuilder:

    @staticmethod
    def create_error_response(
        status_code: int = 400,
        message: str = "Bad Request",
        error_code: str = "BAD_REQUEST",
        details: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
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

        return BasicResponseBuilder.create_response(status_code=status_code, errors=errors, headers=response_headers)

    @staticmethod
    def create_validation_error(
        fields: Dict[str, str],
        status_code: int = 422,
        error_code: str = "VALIDATION_ERROR",
        message: str = "Validation failed",
    ) -> MockResponse:
        details = []
        for field, error_msg in fields.items():
            details.append({"field": field, "message": error_msg, "code": "INVALID_FIELD"})

        return ErrorResponseBuilder.create_error_response(status_code=status_code, message=message, error_code=error_code, details=details)

    @staticmethod
    def create_rate_limit_error(
        limit: int = 100,
        remaining: int = 0,
        reset_seconds: int = 60,
    ) -> MockResponse:
        reset_time = int((datetime.now() + timedelta(seconds=reset_seconds)).timestamp())

        headers = {
            "Content-Type": "application/json",
            "Retry-After": str(reset_seconds),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time),
        }

        return ErrorResponseBuilder.create_error_response(
            status_code=429,
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            details=[{"limit": limit, "remaining": remaining, "reset": reset_time}],
            request_id=str(uuid.uuid4()),
            headers=headers,
        )

    @staticmethod
    def create_auth_error(
        error_type: str = "invalid_token",
        status_code: int = 401,
    ) -> MockResponse:
        error_messages = {
            "invalid_token": "The access token is invalid",
            "expired_token": "The access token has expired",
            "insufficient_scope": "The access token does not have the required scope",
            "invalid_client": "Client authentication failed",
            "invalid_grant": "The provided authorization grant is invalid",
            "unauthorized_client": "The client is not authorized to use this grant type",
        }

        message = error_messages.get(error_type, "Authentication failed")

        headers = {"Content-Type": "application/json", "WWW-Authenticate": f'Bearer realm="api", error="{error_type}", error_description="{message}"'}

        return ErrorResponseBuilder.create_error_response(status_code=status_code, message=message, error_code=error_type.upper(), headers=headers)

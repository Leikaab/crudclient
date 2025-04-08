"""
Response builder for mock client.

This module provides utilities for building complex API responses.
"""

from typing import Any, Dict, List, Optional, Union, Callable
import json
import random
import string
import uuid
from datetime import datetime, timedelta

from .response import MockResponse


class ResponseBuilder:
    """Builder for creating complex API responses."""

    @staticmethod
    def create_response(
        status_code: int = 200,
        data: Any = None,
        metadata: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> MockResponse:
        """
        Create a mock response with structured data.

        Args:
            status_code: HTTP status code
            data: Response data
            metadata: Response metadata
            links: HATEOAS links
            errors: Error details
            headers: HTTP headers

        Returns:
            MockResponse instance
        """
        response_body: Dict[str, Any] = {}

        if data is not None:
            response_body["data"] = data

        if metadata is not None:
            response_body["metadata"] = metadata

        if links is not None:
            response_body["links"] = links

        if errors is not None:
            response_body["errors"] = errors

        return MockResponse(
            status_code=status_code,
            json_data=response_body,
            headers=headers or {"Content-Type": "application/json"}
        )

    @staticmethod
    def create_paginated_response(
        items: List[Any],
        page: int = 1,
        per_page: int = 10,
        total_items: Optional[int] = None,
        total_pages: Optional[int] = None,
        base_url: str = "/api/items",
        include_links: bool = True,
    ) -> MockResponse:
        """
        Create a paginated response.

        Args:
            items: List of items for the current page
            page: Current page number
            per_page: Items per page
            total_items: Total number of items
            total_pages: Total number of pages
            base_url: Base URL for pagination links
            include_links: Whether to include HATEOAS links

        Returns:
            MockResponse instance with pagination
        """
        # Calculate totals if not provided
        _total_items = total_items if total_items is not None else len(items)
        _total_pages = total_pages if total_pages is not None else max(1, (_total_items + per_page - 1) // per_page)

        # Get items for the current page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, _total_items)

        # If we have actual items, paginate them
        page_items = []
        if items and start_idx < len(items):
            page_items = items[start_idx:min(end_idx, len(items))]

        # Create metadata
        metadata = {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": _total_items,
                "total_pages": _total_pages,
            }
        }

        # Create links
        links = None
        if include_links:
            links = {
                "self": f"{base_url}?page={page}&per_page={per_page}",
                "first": f"{base_url}?page=1&per_page={per_page}",
                "last": f"{base_url}?page={_total_pages}&per_page={per_page}",
            }

            if page > 1:
                links["prev"] = f"{base_url}?page={page - 1}&per_page={per_page}"

            if page < _total_pages:
                links["next"] = f"{base_url}?page={page + 1}&per_page={per_page}"

        return ResponseBuilder.create_response(
            status_code=200,
            data=page_items,
            metadata=metadata,
            links=links
        )

    @staticmethod
    def create_error_response(
        status_code: int = 400,
        message: str = "Bad Request",
        error_code: str = "BAD_REQUEST",
        details: Optional[List[Dict[str, Any]]] = None,
        request_id: Optional[str] = None,
    ) -> MockResponse:
        """
        Create an error response.

        Args:
            status_code: HTTP status code
            message: Error message
            error_code: Error code
            details: Detailed error information
            request_id: Request ID for tracking

        Returns:
            MockResponse instance with error details
        """
        error = {
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

        headers = {
            "Content-Type": "application/json",
        }

        # Add common error headers
        if status_code == 429:
            retry_after = random.randint(30, 120)
            headers["Retry-After"] = str(retry_after)
            headers["X-RateLimit-Reset"] = str(int((datetime.now() + timedelta(seconds=retry_after)).timestamp()))

        return ResponseBuilder.create_response(
            status_code=status_code,
            errors=errors,
            headers=headers
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

        Args:
            fields: Dict mapping field names to error messages
            status_code: HTTP status code
            error_code: Error code
            message: Error message

        Returns:
            MockResponse instance with validation errors
        """
        details = []
        for field, error_msg in fields.items():
            details.append({
                "field": field,
                "message": error_msg,
                "code": "INVALID_FIELD"
            })

        return ResponseBuilder.create_error_response(
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

        Args:
            limit: Rate limit
            remaining: Remaining requests
            reset_seconds: Seconds until rate limit resets

        Returns:
            MockResponse instance with rate limit error
        """
        reset_time = int((datetime.now() + timedelta(seconds=reset_seconds)).timestamp())

        headers = {
            "Content-Type": "application/json",
            "Retry-After": str(reset_seconds),
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(reset_time)
        }

        return ResponseBuilder.create_error_response(
            status_code=429,
            message="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            details=[{
                "limit": limit,
                "remaining": remaining,
                "reset": reset_time
            }],
            request_id=str(uuid.uuid4())
        )

    @staticmethod
    def create_auth_error(
        error_type: str = "invalid_token",
        status_code: int = 401,
    ) -> MockResponse:
        """
        Create an authentication error response.

        Args:
            error_type: Type of auth error (invalid_token, expired_token, etc.)
            status_code: HTTP status code

        Returns:
            MockResponse instance with auth error
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

        return ResponseBuilder.create_error_response(
            status_code=status_code,
            message=message,
            error_code=error_type.upper(),
            headers=headers  # type: ignore
        )

    @staticmethod
    def create_graphql_response(
        data: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
        extensions: Optional[Dict[str, Any]] = None,
    ) -> MockResponse:
        """
        Create a GraphQL response.

        Args:
            data: GraphQL data response
            errors: GraphQL errors
            extensions: GraphQL extensions

        Returns:
            MockResponse instance with GraphQL format
        """
        response_body: Dict[str, Any] = {}

        if data is not None:
            response_body["data"] = data

        if errors is not None:
            response_body["errors"] = errors

        if extensions is not None:
            response_body["extensions"] = extensions

        return MockResponse(
            status_code=200 if not errors else 400,
            json_data=response_body,
            headers={"Content-Type": "application/json"}
        )

    @staticmethod
    def create_nested_response(
        structure: Dict[str, Any],
        status_code: int = 200,
    ) -> MockResponse:
        """
        Create a response with a nested structure.

        Args:
            structure: Nested structure for the response
            status_code: HTTP status code

        Returns:
            MockResponse instance with nested structure
        """
        return MockResponse(
            status_code=status_code,
            json_data=structure,
            headers={"Content-Type": "application/json"}
        )

    @staticmethod
    def create_random_data(
        schema: Dict[str, Any],
        count: int = 1
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Create random data based on a schema.

        Args:
            schema: Schema defining the structure and types
            count: Number of items to generate

        Returns:
            Random data matching the schema
        """
        def generate_item(schema_def):
            result = {}
            for key, value_type in schema_def.items():
                if isinstance(value_type, dict):
                    # Nested object
                    result[key] = generate_item(value_type)
                elif isinstance(value_type, list) and len(value_type) > 0:
                    # Array of items
                    if isinstance(value_type[0], dict):
                        # Array of objects
                        array_count = random.randint(1, 5)
                        result[key] = [generate_item(value_type[0]) for _ in range(array_count)]
                    else:
                        # Array of primitives
                        array_count = random.randint(1, 5)
                        result[key] = [_generate_primitive(value_type[0]) for _ in range(array_count)]
                else:
                    # Primitive type
                    result[key] = _generate_primitive(value_type)
            return result

        def _generate_primitive(type_hint):
            if type_hint == 'string' or type_hint == str:
                return ''.join(random.choices(string.ascii_letters, k=random.randint(5, 10)))
            elif type_hint == 'email':
                return f"{''.join(random.choices(string.ascii_lowercase, k=8))}@example.com"
            elif type_hint == 'name':
                first_names = ['John', 'Jane', 'Alice', 'Bob', 'Charlie', 'Diana', 'Edward', 'Fiona']
                last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Miller', 'Davis']
                return f"{random.choice(first_names)} {random.choice(last_names)}"
            elif type_hint == 'int' or type_hint == int:
                return random.randint(1, 1000)
            elif type_hint == 'float' or type_hint == float:
                return round(random.uniform(1.0, 1000.0), 2)
            elif type_hint == 'bool' or type_hint == bool:
                return random.choice([True, False])
            elif type_hint == 'date':
                days = random.randint(0, 365 * 2)
                date = datetime.now() - timedelta(days=days)
                return date.strftime('%Y-%m-%d')
            elif type_hint == 'datetime':
                days = random.randint(0, 365 * 2)
                hours = random.randint(0, 23)
                minutes = random.randint(0, 59)
                seconds = random.randint(0, 59)
                dt = datetime.now() - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
                return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
            elif type_hint == 'uuid':
                return str(uuid.uuid4())
            elif type_hint == 'url':
                return f"https://example.com/{''.join(random.choices(string.ascii_lowercase, k=8))}"
            elif type_hint == 'ip':
                return f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            else:
                return str(type_hint)  # Default to string representation

        if count == 1:
            return generate_item(schema)
        else:
            return [generate_item(schema) for _ in range(count)]

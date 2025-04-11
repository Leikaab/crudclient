"""
Mock implementation for create (POST) operations in CRUD testing.

This module provides a mock implementation for testing create operations,
with support for validation constraints, unique constraints, and auto-incrementing IDs.
"""

import copy
import json
from typing import Any, Callable, Dict, List, Optional, Set, Union

from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock
from .exceptions import ValidationFailedError
from .request_record import RequestRecord

class CreateMock(BaseCrudMock):
    """
    Mock implementation for create (POST) operations.

    This class provides a configurable mock for testing create operations,
    with support for validation constraints, unique constraints, and
    auto-incrementing IDs. It allows for detailed control over the behavior
    of create operations during testing.
    """

    def __init__(self) -> None:
        """
        Initialize a new CreateMock instance.

        Sets up the default response, constraints, and tracking for created resources.
        """
        self.default_response: MockResponse
        self._unique_constraints: Dict[str, Set[Any]]
        self._validation_constraints: Dict[str, tuple[Callable[[Any], bool], str]]
        self._stored_resources: List[Dict[str, Any]]
        self._auto_increment_id: int
        ...

    def with_unique_constraint(self, field_name: str, error_message: Optional[str] = None) -> "CreateMock":
        """
        Configure a unique constraint for a field.

        This method sets up validation to ensure that values for the specified
        field are unique across all resources created through this mock.

        Args:
            field_name: The name of the field that must have unique values
            error_message: Custom error message for constraint violations

        Returns:
            Self for method chaining
        """
        ...

    def with_validation_constraint(self, field_name: str, validator: Callable[[Any], bool], error_message: str) -> "CreateMock":
        """
        Configure a validation constraint for a field.

        This method sets up custom validation for a field using the provided
        validator function.

        Args:
            field_name: The name of the field to validate
            validator: Function that takes the field value and returns True if valid
            error_message: Error message to use when validation fails

        Returns:
            Self for method chaining
        """
        ...

    def with_auto_increment_id(self, id_field: str = "id") -> "CreateMock":
        """
        Configure auto-incrementing IDs for created resources.

        This method sets up the mock to automatically assign incrementing ID values
        to created resources if they don't already have an ID.

        Args:
            id_field: The name of the ID field (default: "id")

        Returns:
            Self for method chaining
        """
        ...

    def post(self, url: str, **kwargs: Any) -> Any:
        """
        Handle a POST request to create a resource.

        This method processes the request, applies any configured constraints,
        records the request, and returns an appropriate response.

        Args:
            url: The URL for the request
            **kwargs: Request parameters (params, data, json, headers)

        Returns:
            The response data (typically a dict with the created resource)

        Raises:
            ValidationFailedError: If the request data fails validation
        """
        ...

    def with_success_response(self, url_pattern: str, response_data: Dict[str, Any], status_code: int = 201, **kwargs: Any) -> "CreateMock":
        """
        Configure a successful response for a specific URL pattern.

        This method sets up the mock to return a specific response when
        a POST request matching the URL pattern is received.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            response_data: Data to include in the response
            status_code: HTTP status code for the response (default: 201)
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def _add_request_preprocessor(self, processor: Callable[..., Optional[MockResponse]]) -> None:
        """
        Add a preprocessor function for handling requests.

        This internal method adds a function that will be called before
        the normal request processing, allowing for custom handling.

        Args:
            processor: Function that takes request parameters and returns
                      a MockResponse or None
        """
        ...

    def with_validation_failure(
        self, url_pattern: str, validation_errors: Dict[str, List[str]], status_code: int = 422, **kwargs: Any
    ) -> "CreateMock":
        """
        Configure a validation failure response for a specific URL pattern.

        This method sets up the mock to return a validation error response
        when a POST request matching the URL pattern is received.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            validation_errors: Dictionary mapping field names to lists of error messages
            status_code: HTTP status code for the response (default: 422)
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

"""
Base Mock Object for CRUD Operations using Builder Configuration.

This module provides `BaseCrudMock`, the foundation for mocking specific CRUD
operations (like Create, Read, Update, Delete) within the `crudclient` testing
framework. It implements the **Mock Object pattern** for simulating CRUD endpoint
behavior and uses a **Builder pattern** variant (`with_...` methods) for flexible
configuration.
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional, Type, Union

from requests import PreparedRequest  # Added

from crudclient.exceptions import DataValidationError  # Replaced ValidationError
from crudclient.testing.response_builder.response import MockResponse

class BaseCrudMock:
    """
    Base **Mock Object** for simulating CRUD endpoint interactions.

    This class serves as the base for specific CRUD operation mocks (e.g.,
    `CreateMock`, `ReadMock`). It combines several patterns:

    1.  **Mock Object:** Simulates the behavior of a CRUD endpoint by matching
        incoming requests against configured patterns and returning predefined
        responses or errors.
    2.  **Builder Pattern:** Uses a fluent interface with chainable `with_...`
        methods (`with_response`, `with_validation_error`, etc.) to configure
        the mock's response patterns and behavior step-by-step.
    3.  **Spy Pattern:** Records incoming requests in `request_history` for later
        verification using the provided `assert_...` methods.

    Subclasses typically inherit from this base and implement specific CRUD
    method interfaces (e.g., `create`, `list`, `retrieve`), delegating the core
    request matching, response generation, and recording to this base class.
    """

    def __init__(self) -> None:
        """
        Initialize the base CRUD mock.

        Sets up the response patterns, request history, and default response.
        """
        ...

    def with_response(
        self,
        url_pattern: str,
        response: Union[MockResponse, Dict[str, Any], List[Dict[str, Any]], str, Callable[..., Optional[MockResponse]]],
        **kwargs: Any,
    ) -> "BaseCrudMock":
        """
        Add a response pattern to the mock.

        This method configures the mock to return a specific response when a request
        matching the given URL pattern and other criteria is received.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            response: Response to return (MockResponse, dict, list, string, or callable)
            **kwargs: Additional criteria for matching requests (params, data, json, headers)
                      and configuration options (max_calls, status_code, error)

        Returns:
            Self for method chaining
        """
        ...

    def with_default_response(self, response: Union[MockResponse, Dict[str, Any], List[Dict[str, Any]], str]) -> "BaseCrudMock":
        """
        Set the default response for unmatched requests.

        Args:
            response: Response to return when no pattern matches

        Returns:
            Self for method chaining
        """
        ...

    def with_parent_id_handling(self, enabled: bool = True) -> "BaseCrudMock":
        """
        Enable or disable parent_id handling.

        When enabled, the mock will process parent_id parameters to build
        URLs in the format 'parents/{parent_id}/{resource_path}'.

        Args:
            enabled: Whether to enable parent_id handling

        Returns:
            Self for method chaining
        """
        ...

    def with_validation_error(self, url_pattern: str, model_class: Type, invalid_data: Dict[str, Any], **kwargs: Any) -> "BaseCrudMock":
        """
        Configure a validation error response.

        This method configures the mock to return a validation error response
        when a request matching the given URL pattern is received.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            model_class: Pydantic model class to use for validation
            invalid_data: Invalid data that will fail validation
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def _find_matching_pattern(self, method: str, url: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        Find a matching response pattern.

        This method searches through the configured response patterns to find
        one that matches the given request.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Request parameters (params, data, json, headers)

        Returns:
            Matching pattern dict or None if no match found
        """
        ...

    def _process_parent_id(self, url: str, parent_id: Optional[str]) -> str:
        """
        Process parent_id to build the correct URL.

        Args:
            url: Original URL
            parent_id: Parent resource ID

        Returns:
            URL with parent_id incorporated
        """
        ...

    def _filter_requests(self, url_pattern: Optional[str] = None, method: Optional[str] = None) -> List[PreparedRequest]:
        """
        Filter the request history based on URL pattern and method.

        Args:
            url_pattern: Optional URL pattern to filter requests.
            method: Optional HTTP method to filter requests.

        Returns:
            A list of matching request objects.
        """
        ...

    def _ensure_mock_response(self, response: Union[MockResponse, Dict[str, Any], List[Dict[str, Any]], str]) -> MockResponse:
        """
        Ensure the response is a MockResponse object.

        Converts dict, list, or string inputs into a MockResponse.

        Args:
            response: The input response (MockResponse, dict, list, or str).

        Returns:
            A MockResponse object.
        """
        ...

    def assert_request_count(self, count: int, url_pattern: Optional[str] = None) -> None:
        """
        Assert that a specific number of matching requests were made.

        Args:
            count: Expected number of requests
            url_pattern: Optional URL pattern to filter requests

        Raises:
            AssertionError: If the actual count doesn't match the expected count
        """
        ...

    def assert_request_sequence(self, sequence: List[Dict[str, Any]], strict: bool = False) -> None:
        """
        Assert that requests were made in a specific sequence.

        Args:
            sequence: List of request matchers, each containing criteria like 'url_pattern'
            strict: If True, the number of requests must match exactly

        Raises:
            AssertionError: If the sequence doesn't match
        """
        ...

    def assert_request_payload(self, payload: Dict[str, Any], url_pattern: Optional[str] = None, match_all: bool = False) -> None:
        """
        Assert that requests were made with specific payload.

        Args:
            payload: Expected payload (key-value pairs)
            url_pattern: Optional URL pattern to filter requests
            match_all: If True, all matching requests must have the payload

        Raises:
            AssertionError: If no matching request has the expected payload
        """
        ...

    def assert_operation_parameters(self, url_pattern: str, expected_params: Dict[str, Any], method: Optional[str] = None) -> None:
        """
        Assert that operations were called with specific parameters.

        Args:
            url_pattern: URL pattern to match
            expected_params: Expected parameters (can be in params, data, or json)
            method: HTTP method to filter by (e.g., 'GET', 'POST')

        Raises:
            AssertionError: If no matching requests or parameters don't match
        """
        ...

    def assert_response_handling(
        self, url_pattern: str, expected_status: int, expected_data: Optional[Dict[str, Any]] = None, method: Optional[str] = None
    ) -> None:
        """
        Assert that responses were handled correctly.

        Args:
            url_pattern: URL pattern to match
            expected_status: Expected HTTP status code
            expected_data: Expected response data (optional)
            method: HTTP method to filter by (e.g., 'GET', 'POST')

        Raises:
            AssertionError: If no matching requests or responses don't match
        """
        ...

    def assert_error_handling(
        self, url_pattern: str, expected_error_type: Type[Exception], expected_status: Optional[int] = None, method: Optional[str] = None
    ) -> None:
        """
        Assert that errors were handled correctly.

        Args:
            url_pattern: URL pattern to match
            expected_error_type: Expected exception type
            expected_status: Expected HTTP status code (optional)
            method: HTTP method to filter by (e.g., 'GET', 'POST')

        Raises:
            AssertionError: If no matching requests or errors don't match
        """
        ...

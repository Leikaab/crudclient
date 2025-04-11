"""
Mock HTTP client implementation.

This module provides a mock implementation of the crudclient.http.Client class
that can be used in tests to simulate HTTP requests and responses without making
actual network calls.
"""

import re  # Added
from typing import (  # Added List, Pattern, Union
    Any,
    Dict,
    List,
    Optional,
    Pattern,
    Tuple,
    Union,
)
from urllib.parse import urljoin

import requests
from requests import Response

from ..exceptions import RequestNotConfiguredError
from ..types import (
    Headers,
    HttpMethod,
    QueryParams,
    RequestBody,
    ResponseBody,
    StatusCode,
)

class MockHTTPClient:
    """
    Mock implementation of the crudclient.http.Client class.

    This class simulates HTTP requests and responses without making actual network calls.
    It allows configuring expected requests and their responses for testing purposes,
    including exact path matches and regex pattern matching. It also supports
    simulating basic network conditions like latency.
    """

    base_url: str
    _configured_responses: Dict[Tuple[HttpMethod, str], Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]]
    _configured_patterns: List[Tuple[HttpMethod, Pattern, Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]]]  # Added
    _latency_ms: float  # Added

    def __init__(self, base_url: str = "https://api.example.com") -> None:
        """
        Initialize a new MockHTTPClient.

        Args:
            base_url: The base URL for the mock client.
        """
        ...

    def reset(self) -> None:
        """Reset the mock HTTP client to its initial state, clearing all configurations."""
        ...

    def configure_response(
        self,
        method: HttpMethod,
        path: str,
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None:
        """
        Configure a response for a specific request with an exact path match.

        This configuration takes precedence over patterns defined with
        `with_response_pattern`.

        Args:
            method: The HTTP method of the request (e.g., 'GET', 'POST').
            path: The exact path of the request (e.g., '/users/1').
            status_code: The HTTP status code to return (default: 200).
            data: The data to return in the response body (default: None).
            headers: The headers to return in the response (default: None).
            error: An exception to raise instead of returning a response (default: None).
        """
        ...

    def with_response_pattern(
        self,
        method: HttpMethod,
        path_pattern: Union[str, Pattern],
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None:
        """
        Configure a response for requests matching a path pattern (regex).

        Patterns are checked in reverse order of addition (LIFO). The first
        matching pattern for the given method and path will be used. Exact
        matches configured with `configure_response` take precedence.

        Args:
            method: The HTTP method of the request (e.g., 'GET', 'POST').
            path_pattern: A regex string or compiled pattern to match against the request path.
            status_code: The HTTP status code to return (default: 200).
            data: The data to return in the response body (default: None).
            headers: The headers to return in the response (default: None).
            error: An exception to raise instead of returning a response (default: None).
        """
        ...

    def with_network_condition(
        self,
        latency_ms: float = 0.0,
        # Future: packet_loss_rate: float = 0.0
    ) -> None:
        """
        Configure simulated network conditions for all subsequent requests.

        Currently supports simulating latency.

        Args:
            latency_ms: The delay in milliseconds to add before processing each request (default: 0.0).

        Raises:
            ValueError: If latency_ms is negative.
        """
        ...

    def _get_configured_response(self, method: HttpMethod, path: str) -> Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]:
        """
        Find a configured response, checking exact matches first, then patterns (LIFO).

        Args:
            method: The HTTP method of the request.
            path: The path of the request.

        Returns:
            A tuple of (status_code, response_body, headers, error).

        Raises:
            RequestNotConfiguredError: If no response is configured for the request
                                       (neither exact match nor pattern match).
        """
        ...

    def request(
        self,
        method: HttpMethod,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any,
    ) -> Response:
        """
        Make a mock HTTP request, applying configured responses and network conditions.

        Args:
            method: The HTTP method of the request.
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments (ignored by mock, but captured).

        Returns:
            A Response object with the configured response.

        Raises:
            RequestNotConfiguredError: If no response is configured for the request.
            Exception: If an error is configured for the request.
            ValueError: If network conditions are invalid (e.g., negative latency).
        """
        ...
    # Convenience methods for common HTTP methods

    def get(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Response:
        """
        Make a mock GET request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with the configured response.
        """
        ...

    def post(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Response:
        """
        Make a mock POST request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with the configured response.
        """
        ...

    def put(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Response:
        """
        Make a mock PUT request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with the configured response.
        """
        ...

    def delete(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Response:
        """
        Make a mock DELETE request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with the configured response.
        """
        ...

    def patch(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Response:
        """
        Make a mock PATCH request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            A Response object with the configured response.
        """
        ...

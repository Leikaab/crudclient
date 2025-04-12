"""
Mock Client implementation for testing.

This module provides a mock implementation of the crudclient.Client class
that can be used in tests to simulate client behavior without making
actual network calls.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Union

from crudclient.auth.base import AuthStrategy
from crudclient.config import ClientConfig

from ..response_builder.response import MockResponse
from ..types import (
    Headers,
    HttpMethod,
    QueryParams,
    RequestBody,
    ResponseBody,
    StatusCode,
)


class MockClient:
    """
    Mock implementation of the crudclient.Client class.

    This class simulates client behavior without making actual network calls.
    It allows configuring expected requests and their responses for testing purposes.

    Features:
    - Configurable response patterns
    - Request history tracking
    - Authentication strategy support
    - Verification helpers
    """

    http_client: Any
    base_url: str
    enable_spy: bool
    config: ClientConfig
    _auth_strategy: Optional[AuthStrategy]
    request_history: List[Dict[str, Any]]

    def __init__(
        self,
        http_client: Any,
        base_url: Optional[str] = None,
        config: Optional[ClientConfig] = None,
        enable_spy: bool = False,
        **kwargs: Any
    ) -> None:
        """
        Initialize a new MockClient.

        Args:
            http_client: The HTTP client to use for making requests.
            base_url: The base URL for the mock client. If not provided, it will be derived from http_client.
            config: Optional configuration for the client. If not provided, a default one will be created.
            enable_spy: Whether to enable spying on the mock client.
            **kwargs: Additional keyword arguments.
        """
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
        Configure a response for a specific request.

        Args:
            method: The HTTP method of the request.
            path: The path of the request.
            status_code: The status code to return.
            data: The data to return in the response body.
            headers: The headers to return in the response.
            error: An exception to raise instead of returning a response.
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

        Delegates to the underlying HTTP client's pattern configuration.
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
        Configure simulated network conditions for the mock client.

        Delegates to the underlying HTTP client's network condition configuration.
        Currently supports simulating latency.

        Args:
            latency_ms: The delay in milliseconds to add before processing each request (default: 0.0).

        Raises:
            ValueError: If latency_ms is negative (raised by underlying HTTP client).
        """
        ...

    def with_rate_limiter(self, limit: int, window_seconds: int) -> None:
        """
        Configure rate limiting for the mock client.

        Args:
            limit: The maximum number of requests allowed in the rate window.
            window_seconds: The time window for rate limiting in seconds.
        """
        ...

    def verify_request_sequence(self, expected_sequence: List[Dict[str, Any]]) -> None:
        """
        Assert that requests were made in the expected sequence.

        Args:
            expected_sequence: The expected sequence of requests.

        Raises:
            AssertionError: If the requests were not made in the expected sequence.
        """
        ...

    def verify_request_params(self, expected_params: Dict[str, str], method: Optional[HttpMethod] = None, path_pattern: Optional[str] = None) -> None:
        """
        Assert that a request was made with the expected parameters.

        Args:
            expected_params: The expected query parameters.
            method: Optional HTTP method to filter by.
            path_pattern: Optional path pattern to filter by.

        Raises:
            AssertionError: If no matching request was made with the expected parameters.
        """
        ...

    def create_paginated_response(self, items: List[Any], per_page: int, base_url: str, page: int = 1) -> MockResponse:
        """
        Create a paginated response helper.

        Args:
            items: The items to paginate.
            per_page: The number of items per page.
            base_url: The base URL for pagination links.
            page: The current page number (default: 1).

        Returns:
            A MockResponse object with paginated data.
        """
        ...

    def set_auth_strategy(self, auth_strategy: AuthStrategy) -> None:
        """
        Set the authentication strategy for the mock client.

        Args:
            auth_strategy: The authentication strategy to use.
        """
        ...

    def get_auth_strategy(self) -> Optional[AuthStrategy]:
        """
        Get the current authentication strategy.

        Returns:
            The current authentication strategy, or None if not set.
        """
        ...

    def _prepare_request_args(
        self,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
    ) -> Dict[str, Any]:
        """
        Applies auth strategy headers/params and merges with explicit ones.

        Internal helper to consolidate request arguments before recording
        and sending the request.

        Args:
            headers: Explicitly provided headers for the request.
            params: Explicitly provided query parameters for the request.

        Returns:
            A dictionary containing the final 'headers' and 'params' after
            applying the authentication strategy.
        """
        ...

    def _record_request(
        self,
        method: HttpMethod,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any,
    ) -> None:
        """
        Record a request in the request history.

        Args:
            method: The HTTP method of the request.
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.
        """
        ...
    # HTTP method implementations

    def get(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Any:
        """
        Make a mock GET request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response from the mock HTTP client.
        """
        ...

    def post(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Any:
        """
        Make a mock POST request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response from the mock HTTP client.
        """
        ...

    def put(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Any:
        """
        Make a mock PUT request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response from the mock HTTP client.
        """
        ...

    def delete(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Any:
        """
        Make a mock DELETE request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response from the mock HTTP client.
        """
        ...

    def patch(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Any:
        """
        Make a mock PATCH request.

        Args:
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments.

        Returns:
            The response from the mock HTTP client.
        """
        ...
    # Verification methods

    def get_request_count(self, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> int:
        """
        Get the number of requests matching the given criteria.

        Args:
            method: Optional HTTP method to filter by.
            path_pattern: Optional path pattern to filter by.

        Returns:
            The number of matching requests.
        """
        ...

    def verify_request_count(self, count: int, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> None:
        """
        Assert that a specific number of matching requests were made.

        Args:
            count: The expected number of requests.
            method: Optional HTTP method to filter by.
            path_pattern: Optional path pattern to filter by.

        Raises:
            AssertionError: If the number of matching requests does not match the expected count.
        """
        ...

    def verify_request_made(self, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> None:
        """
        Assert that at least one matching request was made.

        Args:
            method: Optional HTTP method to filter by.
            path_pattern: Optional path pattern to filter by.

        Raises:
            AssertionError: If no matching requests were made.
        """
        ...

    def verify_request_not_made(self, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> None:
        """
        Assert that no matching requests were made.

        Args:
            method: Optional HTTP method to filter by.
            path_pattern: Optional path pattern to filter by.

        Raises:
            AssertionError: If any matching requests were made.
        """
        ...

    def _filter_requests(self, method: Optional[HttpMethod] = None, path_pattern: Optional[Union[str, Pattern]] = None) -> List[Dict[str, Any]]:
        """
        Filter request history by method and path pattern.

        Args:
            method: Optional HTTP method to filter by.
            path_pattern: Optional path pattern to filter by.

        Returns:
            A list of matching requests.
        """
        ...

    def reset(self) -> None:
        """Reset the mock client to its initial state."""
        ...

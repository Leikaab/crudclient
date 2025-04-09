"""
Mock Client implementation for testing.

This module provides a mock implementation of the crudclient.Client class
that can be used in tests to simulate client behavior without making
actual network calls.
"""

import re
from typing import Any, Dict, List, Optional, Pattern, Union, Callable

from crudclient.auth.base import AuthStrategy
from crudclient.config import ClientConfig

from ..types import Headers, HttpMethod, QueryParams, RequestBody, ResponseBody, StatusCode


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
        base_url: str = "https://api.example.com",
        enable_spy: bool = False,
        **kwargs: Any
    ) -> None:
        """
        Initialize a new MockClient.

        Args:
            http_client: The HTTP client to use for making requests.
            base_url: The base URL for the mock client.
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
        error: Optional[Exception] = None
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
        url_pattern: str,
        response: Any = None,
        status_code: StatusCode = 200,
        headers: Optional[Headers] = None,
        params: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Configure a response pattern for the mock client.

        Args:
            method: The HTTP method to match.
            url_pattern: The URL pattern to match.
            response: The response data to return.
            status_code: The status code to return.
            headers: The headers to return.
            params: The query parameters to match.
        """
        ...

    def with_network_condition(
        self,
        latency_ms: int = 0,
        packet_loss_percentage: float = 0,
        error_rate_percentage: float = 0
    ) -> None:
        """
        Configure network conditions for the mock client.

        Args:
            latency_ms: The simulated network latency in milliseconds.
            packet_loss_percentage: The percentage of requests that will be dropped.
            error_rate_percentage: The percentage of requests that will raise errors.
        """
        ...

    def with_rate_limiter(
        self,
        limit: int,
        window_seconds: int
    ) -> None:
        """
        Configure rate limiting for the mock client.

        Args:
            limit: The maximum number of requests allowed in the rate window.
            window_seconds: The time window for rate limiting in seconds.
        """
        ...

    def assert_request_sequence(
        self,
        expected_sequence: List[Dict[str, Any]]
    ) -> None:
        """
        Assert that requests were made in the expected sequence.

        Args:
            expected_sequence: The expected sequence of requests.

        Raises:
            AssertionError: If the requests were not made in the expected sequence.
        """
        ...

    def assert_request_params(
        self,
        expected_params: Dict[str, str],
        method: Optional[HttpMethod] = None,
        url_pattern: Optional[str] = None
    ) -> None:
        """
        Assert that a request was made with the expected parameters.

        Args:
            expected_params: The expected query parameters.
            method: Optional HTTP method to filter by.
            url_pattern: Optional URL pattern to filter by.

        Raises:
            AssertionError: If no matching request was made with the expected parameters.
        """
        ...

    def create_paginated_response(
        self,
        items: List[Any],
        page_size: int,
        base_url: str
    ) -> Any:
        """
        Create a paginated response helper.

        Args:
            items: The items to paginate.
            page_size: The number of items per page.
            base_url: The base URL for pagination links.

        Returns:
            A paginator object that can be used to get paginated responses.
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

    def _record_request(
        self,
        method: HttpMethod,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
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

    def get(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        **kwargs: Any
    ) -> Any:
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
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
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
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
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

    def delete(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        **kwargs: Any
    ) -> Any:
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
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
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

    def get_request_count(
        self,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> int:
        """
        Get the number of requests matching the given criteria.

        Args:
            method: Optional HTTP method to filter by.
            path_pattern: Optional path pattern to filter by.

        Returns:
            The number of matching requests.
        """
        ...

    def assert_request_count(
        self,
        count: int,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> None:
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

    def assert_request_made(
        self,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> None:
        """
        Assert that at least one matching request was made.

        Args:
            method: Optional HTTP method to filter by.
            path_pattern: Optional path pattern to filter by.

        Raises:
            AssertionError: If no matching requests were made.
        """
        ...

    def assert_request_not_made(
        self,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> None:
        """
        Assert that no matching requests were made.

        Args:
            method: Optional HTTP method to filter by.
            path_pattern: Optional path pattern to filter by.

        Raises:
            AssertionError: If any matching requests were made.
        """
        ...

    def _filter_requests(
        self,
        method: Optional[HttpMethod] = None,
        path_pattern: Optional[Union[str, Pattern]] = None
    ) -> List[Dict[str, Any]]:
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

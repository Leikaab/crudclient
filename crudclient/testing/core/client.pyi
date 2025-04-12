"""
Mock Object Pattern Implementation for `crudclient.Client`.

This module provides `MockClient`, an implementation of the **Mock Object pattern**
for the `crudclient.client.Client` interface. It allows tests to simulate client
behavior, configure specific responses or errors for defined request patterns,
and verify interactions without making actual network calls.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Union

from crudclient.auth.base import AuthStrategy
from crudclient.config import ClientConfig
from crudclient.testing.spy.enhanced import EnhancedSpyBase

from ..response_builder.response import MockResponse
from ..types import (
    Headers,
    HttpMethod,
    QueryParams,
    RequestBody,
    ResponseBody,
    StatusCode,
)

class MockClient(EnhancedSpyBase):
    """
    Implements the **Mock Object pattern** for `crudclient.Client`.

    This test double replaces the real `Client` in tests. It allows setting up
    predefined responses or errors for specific HTTP requests based on method and
    path (using `configure_response` or `with_response_pattern`). This enables
    testing components that depend on the client in isolation.

    As a Mock Object, its primary roles are:
    1.  **Simulation:** Mimics the `Client` interface (`get`, `post`, etc.).
    2.  **Expectation Setting:** Allows configuration of responses/errors for
        specific request patterns.
    3.  **Interaction Verification:** By inheriting from `EnhancedSpyBase`, it also
        acts as a **Spy**, recording calls made to it. Tests can verify these
        interactions using the inherited verification methods or the dedicated
        `Verifier` class.

    This differs from a simple Stub (which only provides canned responses) or a
    pure Spy (which only records calls) by combining configurable behavior with
    verification capabilities.
    """

    http_client: Any
    base_url: str
    enable_spy: bool
    config: ClientConfig
    _auth_strategy: Optional[AuthStrategy]

    def __init__(
        self, http_client: Any, base_url: Optional[str] = None, config: Optional[ClientConfig] = None, enable_spy: bool = False, **kwargs: Any
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

        Delegates to the underlying HTTP client's rate limiting configuration.
        This simulates scenarios where an API enforces usage limits.

        Args:
            limit: The maximum number of requests allowed within the specified window.
            window_seconds: The duration of the time window for rate limiting, in seconds.

        Raises:
            ValueError: If limit or window_seconds are non-positive (raised by underlying HTTP client).
            NotImplementedError: If the underlying HTTP client does not support rate limiting.
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
    # HTTP method implementations

    def _execute_http_method(
        self,
        method_name: str,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Internal helper to execute HTTP methods, apply auth, record calls, and handle timing.

        This method centralizes the logic for handling requests made via `get`, `post`, etc.
        It prepares arguments, records the call if spying is enabled, executes the
        request via the underlying mock HTTP client, and returns the result.

        Args:
            method_name: The name of the HTTP method (e.g., 'GET', 'POST').
            path: The request path.
            headers: Optional request headers.
            params: Optional query parameters.
            data: Optional request body data.
            **kwargs: Additional keyword arguments passed to the underlying HTTP client.

        Returns:
            The response object returned by the underlying mock HTTP client.

        Raises:
            Any exceptions raised by the underlying mock HTTP client or the auth strategy.
        """
        ...

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

    def reset(self) -> None:
        """
        Resets the mock client to its initial state.

        This clears all configured responses (both exact and pattern-based),
        resets any simulated network conditions or rate limiters configured on
        the underlying HTTP client, and clears the recorded call history
        inherited from `EnhancedSpyBase`.
        """
        ...

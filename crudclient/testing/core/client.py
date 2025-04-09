"""
Mock Client implementation for testing.

This module provides a mock implementation of the crudclient.Client class
that can be used in tests to simulate client behavior without making
actual network calls.
"""

from typing import Any, Callable, Dict, List, Optional, Pattern, Union
import re
from urllib.parse import urljoin

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.auth.base import AuthStrategy

from ..exceptions import MockConfigurationError, RequestNotConfiguredError
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
        self.http_client = http_client
        self.base_url = base_url
        self.enable_spy = enable_spy

        # Create a config object
        self.config = ClientConfig(hostname=base_url)

        # Authentication strategy
        self._auth_strategy: Optional[AuthStrategy] = None

        # Request history
        self.request_history: List[Dict[str, Any]] = []

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
        self.http_client.configure_response(
            method=method,
            path=path,
            status_code=status_code,
            data=data,
            headers=headers,
            error=error
        )

    def set_auth_strategy(self, auth_strategy: AuthStrategy) -> None:
        """
        Set the authentication strategy for the mock client.

        Args:
            auth_strategy: The authentication strategy to use.
        """
        self._auth_strategy = auth_strategy
        self.config.auth_strategy = auth_strategy

    def get_auth_strategy(self) -> Optional[AuthStrategy]:
        """
        Get the current authentication strategy.

        Returns:
            The current authentication strategy, or None if not set.
        """
        return self._auth_strategy

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
        self.request_history.append({
            'method': method,
            'path': path,
            'headers': headers or {},
            'params': params or {},
            'data': data,
            'kwargs': kwargs
        })

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
        self._record_request('GET', path, headers, params, **kwargs)
        return self.http_client.get(path, headers=headers, params=params, **kwargs)

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
        self._record_request('POST', path, headers, params, data, **kwargs)
        return self.http_client.post(path, headers=headers, params=params, data=data, **kwargs)

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
        self._record_request('PUT', path, headers, params, data, **kwargs)
        return self.http_client.put(path, headers=headers, params=params, data=data, **kwargs)

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
        self._record_request('DELETE', path, headers, params, **kwargs)
        return self.http_client.delete(path, headers=headers, params=params, **kwargs)

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
        self._record_request('PATCH', path, headers, params, data, **kwargs)
        return self.http_client.patch(path, headers=headers, params=params, data=data, **kwargs)

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
        return len(self._filter_requests(method, path_pattern))

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
        actual_count = self.get_request_count(method, path_pattern)
        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. "
            f"Filters: method={method}, path_pattern={path_pattern}"
        )

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
        actual_count = self.get_request_count(method, path_pattern)
        assert actual_count > 0, (
            f"Expected at least one matching request, but found none. "
            f"Filters: method={method}, path_pattern={path_pattern}"
        )

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
        actual_count = self.get_request_count(method, path_pattern)
        assert actual_count == 0, (
            f"Expected no matching requests, but found {actual_count}. "
            f"Filters: method={method}, path_pattern={path_pattern}"
        )

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
        result = self.request_history

        if method:
            method = method.upper()
            result = [r for r in result if r['method'].upper() == method]

        if path_pattern:
            if isinstance(path_pattern, str):
                pattern = re.compile(path_pattern)
            else:
                pattern = path_pattern
            result = [r for r in result if pattern.search(r['path'])]

        return result

    def reset(self) -> None:
        """Reset the mock client to its initial state."""
        self.request_history = []
        # Reset the HTTP client if it has a reset method
        if hasattr(self.http_client, 'reset'):
            self.http_client.reset()

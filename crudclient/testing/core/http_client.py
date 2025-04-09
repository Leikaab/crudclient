"""
Mock HTTP client implementation.

This module provides a mock implementation of the crudclient.http.Client class
that can be used in tests to simulate HTTP requests and responses without making
actual network calls.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

from crudclient.http.client import HttpClient
import requests
from requests import Response

from ..exceptions import RequestNotConfiguredError
from ..types import Headers, HttpMethod, QueryParams, RequestBody, ResponseBody, StatusCode


class MockHTTPClient:
    """
    Mock implementation of the crudclient.http.Client class.

    This class simulates HTTP requests and responses without making actual network calls.
    It allows configuring expected requests and their responses for testing purposes.
    """

    def __init__(self, base_url: str = "https://api.example.com") -> None:
        """
        Initialize a new MockHTTPClient.

        Args:
            base_url: The base URL for the mock client.
        """
        self.base_url = base_url
        self._configured_responses: Dict[Tuple[HttpMethod, str], Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]] = {}

    def reset(self) -> None:
        """Reset the mock HTTP client to its initial state."""
        self._configured_responses = {}

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
        # Normalize the method to uppercase
        method = method.upper()

        # Normalize the path to remove leading slash if present
        path = path.lstrip('/')

        # Store the configured response
        self._configured_responses[(method, path)] = (
            status_code,
            data or {},
            headers or {},
            error
        )

    def _get_configured_response(
        self,
        method: HttpMethod,
        path: str
    ) -> Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]:
        """
        Get the configured response for a specific request.

        Args:
            method: The HTTP method of the request.
            path: The path of the request.

        Returns:
            A tuple of (status_code, response_body, headers, error).

        Raises:
            RequestNotConfiguredError: If no response is configured for the request.
        """
        # Normalize the method to uppercase
        method = method.upper()

        # Normalize the path to remove leading slash if present
        path = path.lstrip('/')

        # Get the configured response
        key = (method, path)
        if key not in self._configured_responses:
            raise RequestNotConfiguredError(method, path)

        return self._configured_responses[key]

    def request(
        self,
        method: HttpMethod,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
    ) -> Response:
        """
        Make a mock HTTP request.

        Args:
            method: The HTTP method of the request.
            path: The path of the request.
            headers: Optional headers for the request.
            params: Optional query parameters for the request.
            data: Optional body for the request.
            **kwargs: Additional keyword arguments (ignored).

        Returns:
            A Response object with the configured response.

        Raises:
            RequestNotConfiguredError: If no response is configured for the request.
            Exception: If an error is configured for the request.
        """
        # Get the configured response
        status_code, response_body, response_headers, error = self._get_configured_response(
            method=method,
            path=path
        )

        # If an error is configured, raise it
        if error is not None:
            raise error

        # Create a Response object with the configured response
        url = urljoin(self.base_url, path)
        response = requests.Response()
        response.status_code = status_code
        response.headers.update(response_headers or {})
        response._content = (response_body.encode('utf-8') if isinstance(response_body, str)
                             else (response_body if response_body is not None else b''))
        response.url = url

        return response

    # Convenience methods for common HTTP methods

    def get(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        **kwargs: Any
    ) -> Response:
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
        return self.request(
            method="GET",
            path=path,
            headers=headers,
            params=params,
            **kwargs
        )

    def post(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
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
        return self.request(
            method="POST",
            path=path,
            headers=headers,
            params=params,
            data=data,
            **kwargs
        )

    def put(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
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
        return self.request(
            method="PUT",
            path=path,
            headers=headers,
            params=params,
            data=data,
            **kwargs
        )

    def delete(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        **kwargs: Any
    ) -> Response:
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
        return self.request(
            method="DELETE",
            path=path,
            headers=headers,
            params=params,
            **kwargs
        )

    def patch(
        self,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any
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
        return self.request(
            method="PATCH",
            path=path,
            headers=headers,
            params=params,
            data=data,
            **kwargs
        )

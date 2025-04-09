"""
Mock HTTP client implementation.

This module provides a mock implementation of the crudclient.http.Client class
that can be used in tests to simulate HTTP requests and responses without making
actual network calls.
"""

from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin

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

    base_url: str
    _configured_responses: Dict[Tuple[HttpMethod, str], Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]]

    def __init__(self, base_url: str = "https://api.example.com") -> None:
        """
        Initialize a new MockHTTPClient.

        Args:
            base_url: The base URL for the mock client.
        """
        ...

    def reset(self) -> None:
        """Reset the mock HTTP client to its initial state."""
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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

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
        ...

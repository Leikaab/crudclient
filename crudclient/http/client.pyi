"""
Module `client.py`
=================

This module defines the HttpClient class, which is responsible for making HTTP requests.
It provides a clean interface for making requests while delegating specialized concerns
to other components.

Class `HttpClient`
-----------------

The `HttpClient` class provides a centralized way to make HTTP requests for API clients.
It delegates session management, request preparation, response handling, error handling,
and retry logic to specialized components.

To use the HttpClient:
    1. Create a ClientConfig object with the necessary configuration.
    2. Initialize an HttpClient instance with the config and optional components.
    3. Use the HttpClient to make HTTP requests.

Example:
    config = ClientConfig(base_url="https://api.example.com")
    client = HttpClient(config)
    response = client.get("users")
    # Use the response data

Classes:
    - HttpClient: Main class for making HTTP requests.
"""

from typing import Any, Dict, Literal, Optional, Union, overload

import requests

from ..config import ClientConfig
from ..types import RawResponseSimple
from .errors import ErrorHandler
from .request import RequestFormatter
from .response import ResponseHandler
from .retry import RetryHandler
from .session import SessionManager

class HttpClient:
    """
    Makes HTTP requests and delegates specialized concerns to other components.

    This class is responsible for making HTTP requests while delegating session management,
    request preparation, response handling, error handling, and retry logic to specialized
    components.

    Attributes:
        config (ClientConfig): Configuration object for the client.
        session_manager (SessionManager): Manages the HTTP session.
        request_formatter (RequestFormatter): Formats request data.
        response_handler (ResponseHandler): Processes HTTP responses.
        error_handler (ErrorHandler): Handles error responses.
        retry_handler (RetryHandler): Manages retry policies.
    """

    config: ClientConfig
    session_manager: SessionManager
    request_formatter: RequestFormatter
    response_handler: ResponseHandler
    error_handler: ErrorHandler
    retry_handler: RetryHandler

    def __init__(
        self,
        config: ClientConfig,
        session_manager: Optional[SessionManager] = None,
        request_formatter: Optional[RequestFormatter] = None,
        response_handler: Optional[ResponseHandler] = None,
        error_handler: Optional[ErrorHandler] = None,
        retry_handler: Optional[RetryHandler] = None,
    ) -> None:
        """
        Initialize the HttpClient with a configuration and optional components.

        Args:
            config (ClientConfig): Configuration for the client.
            session_manager (Optional[SessionManager]): Session manager component.
                If not provided, a new one will be created.
            request_formatter (Optional[RequestFormatter]): Request formatter component.
                If not provided, a new one will be created.
            response_handler (Optional[ResponseHandler]): Response handler component.
                If not provided, a new one will be created.
            error_handler (Optional[ErrorHandler]): Error handler component.
                If not provided, a new one will be created.
            retry_handler (Optional[RetryHandler]): Retry handler component.
                If not provided, a new one will be created.

        Raises:
            TypeError: If the provided config is not a ClientConfig object.
        """
        ...

    @overload
    def _request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        handle_response: Literal[True] = True,
        **kwargs: Any
    ) -> RawResponseSimple: ...

    @overload
    def _request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        handle_response: Literal[False] = False,
        **kwargs: Any
    ) -> requests.Response: ...

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> RawResponseSimple:
        """
        Make a GET request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to request.
            params (Optional[Dict[str, Any]]): Query parameters to include in the request.
                Defaults to None.

        Returns:
            RawResponseSimple: The processed response data.

        Raises:
            TypeError: If the parameters are of incorrect types.
        """
        ...

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Make a POST request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to request.
            data (Optional[Dict[str, Any]]): Form data to include in the request.
                Defaults to None.
            json (Optional[Any]): JSON data to include in the request.
                Defaults to None.
            files (Optional[Dict[str, Any]]): Files to include in the request.
                Defaults to None.

        Returns:
            RawResponseSimple: The processed response data.

        Raises:
            TypeError: If the parameters are of incorrect types.
        """
        ...

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Make a PUT request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to request.
            data (Optional[Dict[str, Any]]): Form data to include in the request.
                Defaults to None.
            json (Optional[Any]): JSON data to include in the request.
                Defaults to None.
            files (Optional[Dict[str, Any]]): Files to include in the request.
                Defaults to None.

        Returns:
            RawResponseSimple: The processed response data.

        Raises:
            TypeError: If the parameters are of incorrect types.
        """
        ...

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        """
        Make a DELETE request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to request.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            RawResponseSimple: The processed response data.

        Raises:
            TypeError: If the parameters are of incorrect types.
        """
        ...

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Make a PATCH request to the specified endpoint.

        Args:
            endpoint (str): The API endpoint to request.
            data (Optional[Dict[str, Any]]): Form data to include in the request.
                Defaults to None.
            json (Optional[Any]): JSON data to include in the request.
                Defaults to None.
            files (Optional[Dict[str, Any]]): Files to include in the request.
                Defaults to None.

        Returns:
            RawResponseSimple: The processed response data.

        Raises:
            TypeError: If the parameters are of incorrect types.
        """
        ...

    def _prepare_data(
        self,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Prepare request data based on the provided parameters.

        This method delegates to the request_formatter to prepare the request data
        and set the appropriate content-type headers.

        Args:
            data (Optional[Dict[str, Any]]): Form data to include in the request.
            json (Optional[Any]): JSON data to include in the request.
            files (Optional[Dict[str, Any]]): Files to include in the request.

        Returns:
            Dict[str, Any]: A dictionary containing the prepared request data and headers.

        Raises:
            TypeError: If the parameters are of incorrect types.
        """
        ...

    def request_raw(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs: Any
    ) -> requests.Response:
        """
        Make a raw HTTP request and return the Response object without processing.

        This method is useful when you need access to the raw response object
        for custom processing.

        Args:
            method (str): The HTTP method to use (GET, POST, PUT, DELETE, PATCH).
            endpoint (Optional[str]): The API endpoint to request. Either endpoint or url must be provided.
            url (Optional[str]): The full URL to request. Either endpoint or url must be provided.
            **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            requests.Response: The raw Response object.

        Raises:
            ValueError: If neither endpoint nor url is provided.
            TypeError: If the parameters are of incorrect types.
        """
        ...

    def close(self) -> None:
        """
        Close the HTTP session and clean up resources.

        This method should be called when the client is no longer needed
        to ensure proper cleanup of resources.
        """
        ...

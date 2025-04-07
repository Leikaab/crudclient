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

import logging
from typing import Any, Dict, Optional

import requests

from ..config import ClientConfig
from ..types import RawResponseSimple
from .errors import ErrorHandler
from .request import RequestFormatter
from .response import ResponseHandler
from .retry import RetryHandler
from .session import SessionManager

# Set up logging
logger = logging.getLogger(__name__)


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

    def __init__(
        self,
        config: ClientConfig,
        session_manager: Optional[SessionManager] = None,
        request_formatter: Optional[RequestFormatter] = None,
        response_handler: Optional[ResponseHandler] = None,
        error_handler: Optional[ErrorHandler] = None,
        retry_handler: Optional[RetryHandler] = None,
    ) -> None:
        if not isinstance(config, ClientConfig):
            raise TypeError("config must be a ClientConfig object")

        self.config = config
        self.session_manager = session_manager or SessionManager(config)
        self.request_formatter = request_formatter or RequestFormatter()
        self.response_handler = response_handler or ResponseHandler()
        self.error_handler = error_handler or ErrorHandler()
        self.retry_handler = retry_handler or RetryHandler()

    def _request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        handle_response: bool = True,
        **kwargs: Any
    ) -> Any:
        # Runtime type checks for critical parameters
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if endpoint is not None and not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string or None, got {type(endpoint).__name__}")

        if url is not None and not isinstance(url, str):
            raise TypeError(f"url must be a string or None, got {type(url).__name__}")

        if not isinstance(handle_response, bool):
            raise TypeError(f"handle_response must be a boolean, got {type(handle_response).__name__}")
        if url is None:
            if endpoint is None:
                raise ValueError("Either 'endpoint' or 'url' must be provided.")
            # Construct the URL from the base URL and endpoint
            url = f"{self.config.base_url}/{endpoint.lstrip('/')}"

        logger.debug(f"Making {method} request to {url} with params: {kwargs}")

        # Define a function to make the request
        def make_request() -> requests.Response:
            return self.session_manager.session.request(
                method, url, timeout=self.session_manager.timeout, **kwargs
            )

        # Execute the request with retry logic
        try:
            response = self.retry_handler.execute_with_retry(
                make_request,
                self.session_manager.session,
                self.session_manager.refresh_auth
            )
        except requests.HTTPError as e:
            # Handle error responses
            self.error_handler.handle_error_response(e.response)
            # If handle_error_response doesn't raise an exception, return the response
            return e.response if not handle_response else self.response_handler.handle_response(e.response)

        # Check if we need to retry after a 403 Forbidden
        if response.status_code == 403:
            response = self.retry_handler.maybe_retry_after_403(
                method, url, kwargs, response, self.session_manager.session, self.session_manager.refresh_auth
            )

        if not handle_response:
            return response

        # Process the response
        try:
            return self.response_handler.handle_response(response)
        except requests.HTTPError:
            # Handle error responses
            self.error_handler.handle_error_response(response)
            # If handle_error_response doesn't raise an exception, return the response
            return response

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> RawResponseSimple:
        # Runtime type checks
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if params is not None and not isinstance(params, dict):
            raise TypeError(f"params must be a dictionary or None, got {type(params).__name__}")
        return self._request("GET", endpoint=endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        # Runtime type checks
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        prepared_data = self._prepare_data(data, json, files)
        return self._request("POST", endpoint=endpoint, **prepared_data)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        # Runtime type checks
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PUT", endpoint=endpoint, **prepared_data)

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        # Runtime type check
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")
        return self._request("DELETE", endpoint=endpoint, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        # Runtime type checks
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PATCH", endpoint=endpoint, **prepared_data)

    def _prepare_data(
        self,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Runtime type checks
        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        prepared_data, headers = self.request_formatter.prepare_data(data, json, files)

        # If headers were returned, update the session headers
        if headers:
            self.session_manager.update_headers(headers)

        return prepared_data

    def request_raw(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs: Any
    ) -> requests.Response:
        # Runtime type checks
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if endpoint is not None and not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string or None, got {type(endpoint).__name__}")

        if url is not None and not isinstance(url, str):
            raise TypeError(f"url must be a string or None, got {type(url).__name__}")
        return self._request(method, endpoint, url, handle_response=False, **kwargs)

    def close(self) -> None:
        self.session_manager.close()
        logger.debug("HttpClient closed.")

from typing import Any, Dict, Literal, Optional, Tuple, Union, overload

import requests

from .config import ClientConfig
from .exceptions import ConfigurationError
from .http.client import HttpClient
from .types import RawResponseSimple

# filepath: /workspace/crudclient/client.pyi
"""
Stub file for `client.py`
=========================

This file provides type hints and method signatures for the `client.py` module.
It is used to provide better type checking and autocompletion support.
"""

class Client:
    """
    Client class for making API requests.

    This class delegates HTTP operations to the HttpClient class, which handles
    request preparation, authentication, response handling, and error handling.

    Attributes:
        config (ClientConfig): Configuration object for the client.
        http_client (HttpClient): The HTTP client used for making requests.
        base_url (str): The base URL for the API.
    """

    config: ClientConfig
    http_client: HttpClient
    base_url: str

    def __init__(self, config: Union[ClientConfig, Dict[str, Any]]) -> None:
        """
        Initialize the Client.

        Logging behavior (e.g., request/response body logging) can be controlled
        via the `logging` section of the configuration. By default, logging is
        disabled using a `NullHandler`. See `docs/logging.md` for details.

        Args:
            config (Union[ClientConfig, Dict[str, Any]]): Configuration for the client.
                Can be a ClientConfig object or a dictionary containing parameters
                like `base_url`, `auth`, `timeout`, and logging settings
                (`log_request_body`, `log_response_body`).

        Raises:
            ConfigurationError: If the provided config is invalid (wrong type, missing fields, invalid values).
        """
        ...

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
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

    @overload
    def _request(
        self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: Literal[True] = True, **kwargs: Any
    ) -> RawResponseSimple: ...
    @overload
    def _request(
        self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: Literal[False] = False, **kwargs: Any
    ) -> requests.Response: ...
    @property
    def session(self) -> requests.Session:
        """
        Get the HTTP session.

        This property is provided for backward compatibility with existing tests.
        It returns the session from the HTTP client's session manager.

        Returns:
            requests.Session: The HTTP session.
        """
        ...

    def _setup_auth(self) -> None:
        """
        Set up authentication for the session.

        This method is provided for backward compatibility with existing tests.
        It delegates to the HttpClient's session_manager.
        """
        ...

    def _prepare_data(
        self, data: Optional[Dict[str, Any]] = None, json: Optional[Any] = None, files: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, str], Dict[str, Any]]:
        """
        Prepare request data based on the provided parameters.

        This method is provided for backward compatibility with existing tests.
        It returns headers and request kwargs instead of modifying session state directly.

        Args:
            data (Optional[Dict[str, Any]]): Form data to include in the request.
            json (Optional[Any]): JSON data to include in the request.
            files (Optional[Dict[str, Any]]): Files to include in the request.

        Returns:
            Tuple[Dict[str, str], Dict[str, Any]]: A tuple containing:
                - Headers dictionary with the appropriate content-type.
                - A dictionary containing the prepared request data.
        """
        ...

    def _maybe_retry_after_403(self, method: str, url: str, kwargs: Dict[str, Any], response: requests.Response) -> requests.Response:
        """
        Retry a request after receiving a 403 Forbidden response.

        This method is provided for backward compatibility with existing tests.
        It delegates to the HttpClient's retry_handler.

        Args:
            method (str): The HTTP method for the request.
            url (str): The URL for the request.
            kwargs (dict): Additional keyword arguments for the request.
            response (requests.Response): The response from the original request.

        Returns:
            requests.Response: The response from the retry or the original response if no retry.
        """
        ...

    def _handle_response(self, response: requests.Response) -> RawResponseSimple:
        """
        Handle the response from the API based on the content type.

        This method is provided for backward compatibility with existing tests.
        It delegates to the HttpClient's response_handler.

        Args:
            response (requests.Response): The response object from the API.

        Returns:
            RawResponseSimple: The parsed response content.
        """
        ...

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.

        This method is provided for backward compatibility with existing tests.
        It delegates to the HttpClient's error_handler.

        Args:
            response (requests.Response): The response object from the API.

        Raises:
            AuthenticationError: If the status code is 401 (Unauthorized).
            NotFoundError: If the status code is 404 (Not Found).
            CrudClientError: For other error status codes.
        """
        ...

    def close(self) -> None:
        """
        Close the HTTP client and clean up resources.

        This method should be called when the client is no longer needed
        to ensure proper cleanup of resources.
        """
        ...

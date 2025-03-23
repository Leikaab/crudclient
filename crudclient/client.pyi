from typing import Any, Dict, Optional, Union

import requests

from .config import ClientConfig
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

    This class manages the HTTP session, handles authentication, and provides
    methods for different types of HTTP requests (GET, POST, PUT, DELETE, PATCH).

    Attributes:
        config (ClientConfig): Configuration object for the client.
        session (requests.Session): The HTTP session used for making requests.
        base_url (str): The base URL for the API.
        timeout (float): The timeout for requests in seconds.

    Methods:
        _setup_auth: Sets up authentication for the requests session.
        _setup_retries_and_timeouts: Sets up retries and timeouts for the requests session.
        _set_content_type_header: Sets the 'Content-Type' header for the request.
        _prepare_data: Prepares the data for the request based on the content type.
        _handle_response: Handles the response from the API based on the content type.
        _handle_error_response: Handles error responses from the API.
        _request: Makes a request to the API using the requests session.
        get: Makes a GET request to the API.
        post: Makes a POST request to the API.
        put: Makes a PUT request to the API.
        delete: Makes a DELETE request to the API.
        patch: Makes a PATCH request to the API.
        close: Closes the HTTP session.
    """

    config: ClientConfig
    session: requests.Session
    base_url: str
    timeout: float

    def __init__(self, config: Union[ClientConfig, Dict[str, Any]]) -> None:
        """
        Initialize the Client.

        Args:
            config (Union[ClientConfig, Dict[str, Any]]): Configuration for the client.
                Can be a ClientConfig object or a dictionary of configuration parameters.

        Raises:
            TypeError: If the provided config is neither a ClientConfig object nor a dict.
        """
        ...

    def _setup_auth(self) -> None:
        """
        This function sets up authentication for the requests session. It retrieves the authentication information from the config and updates the session headers or auth attribute accordingly.
        Parameters:
        - None
        Returns:
        - None

        """
        ...

    def _setup_retries_and_timeouts(self) -> None:
        """
        This function sets up the retries and timeouts for the requests session. It retrieves the number of retries and timeout duration from the config. If the number of retries is not specified in the config, it defaults to 3. If the timeout duration is not specified in the config, it defaults to 5.
        The function creates an HTTPAdapter with the specified number of retries and mounts it to both 'http://' and 'https://' URLs in the session. It also sets the timeout duration for the session.
        Parameters:
        - None
        Returns:
        - None

        """
        ...

    def _set_content_type_header(self, content_type: str) -> None:
        """
        This function sets the 'Content-Type' header for the request session. It updates the 'Content-Type' header in the session headers with the specified content type.
        Parameters:
        - content_type (str): The content type to set in the 'Content-Type' header.
        Returns:
        - None

        """
        ...

    def _prepare_data(self, data: Optional[Dict[str, Any]] = ..., json: Optional[Any] = ..., files: Optional[Dict[str, Any]] = ...) -> Dict[str, Any]:
        """
        This function prepares the data for the request based on the content type. It checks if the data is JSON, files, or form data, and sets the appropriate 'Content-Type' header for the request session.
        Parameters:
        - data (Optional[Dict[str, Any]]): The data to send in the request body.
        - json (Optional[Any]): The JSON data to send in the request body.
        - files (Optional[Dict[str, Any]]): The files to send in the request body.
        Returns:
        - Dict[str, Any]: A dictionary containing the data, json, or files to send in the request body.

        """
        ...

    def _maybe_retry_after_403(self, method: str, url: str, kwargs: dict, response: requests.Response) -> requests.Response: ...
    def _handle_response(self, response: requests.Response) -> RawResponseSimple:
        """
        This function handles the response from the API based on the content type. It checks the 'Content-Type' header in the response and parses the response content accordingly.
        Parameters:
        - response (requests.Response): The response object from the API.
        Returns:
        - RawResponseSimple: The parsed response content.

        """
        ...

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        This function handles error responses from the API. It parses the response content and raises an appropriate exception with the error message.
        Parameters:
        - response (requests.Response): The response object from the API.
        Raises:
        - requests.RequestException: If the request fails with an error response.
        - requests.HTTPError: If an HTTP error occurs.
        Returns:
        - None

        """
        ...

    def _request(self, method: str, endpoint: Optional[str] = ..., url: Optional[str] = ..., **kwargs: Any) -> Any:
        """
        This function makes a request to the API using the requests session. It constructs the URL for the request based on the endpoint or URL provided. It logs the request details and returns the parsed response from the API.
        Parameters:
        - method (str): The HTTP method for the request (GET, POST, PUT, DELETE, PATCH).
        - endpoint (Optional[str]): The endpoint for the request.
        - url (Optional[str]): The full URL for the request (alternative to endpoint).
        - kwargs: Additional keyword arguments for the request.
        Raises:
        - ValueError: If neither 'endpoint' nor 'url' is provided
        - requests.RequestException: If the request fails with an error response.
        - requests.HTTPError: If an HTTP error occurs.
        Returns:
        - Any: The parsed response content from the API.
        """
        ...

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = ...) -> RawResponseSimple:
        """
        Make a GET request to the API.
        Parameters:
        - endpoint (str): The endpoint for the request.
        - params (Optional[Dict[str, Any]]): The query parameters for the request.
        Raises:
        - ValueError: If 'endpoint' is not provided.
        - requests.RequestException: If the request fails with an error response.
        - requests.HTTPError: If an HTTP error occurs.
        Returns:
        - RawResponseSimple: The parsed response content from the API.
        """
        ...

    def post(
        self, endpoint: str, data: Optional[Dict[str, Any]] = ..., json: Optional[Any] = ..., files: Optional[Dict[str, Any]] = ...
    ) -> RawResponseSimple:
        """
        Make a POST request to the API.
        Parameters:
        - endpoint (str): The endpoint for the request.
        - data (Optional[Dict[str, Any]]): The form data to send in the request body.
        - json (Optional[Any]): The JSON data to send in the request body.
        - files (Optional[Dict[str, Any]]): The files to send in the request body.
        Raises:
        - ValueError: If neither 'data' nor 'json' is provided.
        - requests.RequestException: If the request fails with an error response.
        - requests.HTTPError: If an HTTP error occurs.
        Returns:
        - RawResponseSimple: The parsed response content from the API.
        """
        ...

    def put(
        self, endpoint: str, data: Optional[Dict[str, Any]] = ..., json: Optional[Any] = ..., files: Optional[Dict[str, Any]] = ...
    ) -> RawResponseSimple:
        """
        Make a PUT request to the API.
        Parameters:
        - endpoint (str): The endpoint for the request.
        - data (Optional[Dict[str, Any]]): The form data to send in the request body.
        - json (Optional[Any]): The JSON data to send in the request body.
        - files (Optional[Dict[str, Any]]): The files to send in the request body.
        Raises:
        - ValueError: If neither 'data' nor 'json' is provided.
        - requests.RequestException: If the request fails with an error response.
        - requests.HTTPError: If an HTTP error occurs.
        Returns:
        - RawResponseSimple: The parsed response content from the API.
        """
        ...

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        """
        Make a DELETE request to the API.
        Parameters:
        - endpoint (str): The endpoint for the request.
        Raises:
        - ValueError: If 'endpoint' is not provided.
        - requests.RequestException: If the request fails with an error response.
        - requests.HTTPError: If an HTTP error occurs.
        Returns:
        - RawResponseSimple: The parsed response content from the API.
        """
        ...

    def patch(
        self, endpoint: str, data: Optional[Dict[str, Any]] = ..., json: Optional[Any] = ..., files: Optional[Dict[str, Any]] = ...
    ) -> RawResponseSimple:
        """
        Make a PATCH request to the API.
        Parameters:
        - endpoint (str): The endpoint for the request.
        - data (Optional[Dict[str, Any]]): The form data to send in the request body.
        - json (Optional[Any]): The JSON data to send in the request body.
        - files (Optional[Dict[str, Any]]): The files to send in the request body.
        Raises:
        - ValueError: If neither 'data' nor 'json' is provided.
        - requests.RequestException: If the request fails with an error response.
        - requests.HTTPError: If an HTTP error occurs.
        Returns:
        - RawResponseSimple: The parsed response content from the API.
        """
        ...

    def close(self) -> None:
        """
        Close the HTTP session.
        Parameters:
        - None
        Returns:
        - None
        """
        ...

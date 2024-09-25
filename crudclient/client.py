"""
Module `client.py`
==================

This module defines the Client class, which is responsible for managing HTTP requests to the API.
The Client class handles authentication, request preparation, and response handling.

Class `Client`
--------------

The `Client` class provides a flexible way to interact with various API endpoints.
It includes methods for different HTTP methods (GET, POST, PUT, DELETE, PATCH) and handles
request preparation, authentication, and response parsing.

To use the Client:
    1. Create a ClientConfig object with the necessary configuration.
    2. Initialize a Client instance with the config.
    3. Use the Client methods to make API requests.

Example:
    config = ClientConfig(hostname="https://api.example.com", api_key="your_api_key")
    client = Client(config)
    response = client.get("users")

Classes:
    - Client: Main class for making API requests.

Exceptions:
    - RequestException: Raised when a request fails.
    - HTTPError: Raised when an HTTP error occurs.
"""

import logging
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter

from .config import ClientConfig
from .runtime_type_checkers import assert_type
from .types import RawResponseSimple

# Set up logging
logger = logging.getLogger(__name__)


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

    def __init__(self, config: ClientConfig | Dict[str, Any]) -> None:
        """
        Initialize the Client.

        Args:
            config (Union[ClientConfig, Dict[str, Any]]): Configuration for the client.
                Can be a ClientConfig object or a dictionary of configuration parameters.

        Raises:
            TypeError: If the provided config is neither a ClientConfig object nor a dict.
        """

        # Validate and set up the config
        assert_type("config", config, (ClientConfig, dict), logger)
        if isinstance(config, dict):
            config = ClientConfig(**config)

        assert isinstance(config, ClientConfig)  # for mypy
        self.config: ClientConfig = config

        # Set up the requests session
        self.session = requests.Session()

        # Set up authentication
        self._setup_auth()

        # Set up default headers, if any
        if self.config.headers:
            self.session.headers.update(self.config.headers)

        # Set base URL for the API
        self.base_url = self.config.base_url

        # Set up retries and timeouts
        self._setup_retries_and_timeouts()

    # Temporary function to do auth setup
    def _setup_auth(self) -> None:
        """
        This function sets up authentication for the requests session. It retrieves the authentication information from the config and updates the session headers or auth attribute accordingly.
        Parameters:
        - None
        Returns:
        - None

        """
        auth = self.config.auth()
        if auth is not None:
            if isinstance(auth, dict):
                self.session.headers.update(auth)
            elif isinstance(auth, tuple) and len(auth) == 2:
                self.session.auth = auth
            elif callable(auth):
                auth(self.session)

    def _setup_retries_and_timeouts(self) -> None:
        """
        This function sets up the retries and timeouts for the requests session. It retrieves the number of retries and timeout duration from the config. If the number of retries is not specified in the config, it defaults to 3. If the timeout duration is not specified in the config, it defaults to 5.
        The function creates an HTTPAdapter with the specified number of retries and mounts it to both 'http://' and 'https://' URLs in the session. It also sets the timeout duration for the session.
        Parameters:
        - None
        Returns:
        - None

        """
        retries = self.config.retries or 3
        timeout = self.config.timeout or 5

        adapter = HTTPAdapter(max_retries=retries)

        # Mount the adapter to both 'http://' and 'https://' URLs in the session
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set the timeout duration for the session
        self.timeout = timeout

    def _set_content_type_header(self, content_type: str) -> None:
        """
        This function sets the 'Content-Type' header for the request session. It updates the 'Content-Type' header in the session headers with the specified content type.
        Parameters:
        - content_type (str): The content type to set in the 'Content-Type' header.
        Returns:
        - None

        """
        self.session.headers["Content-Type"] = content_type

    def _prepare_data(
        self, data: Optional[Dict[str, Any]] = None, json: Optional[Any] = None, files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        This function prepares the data for the request based on the content type. It checks if the data is JSON, files, or form data, and sets the appropriate 'Content-Type' header for the request session.
        Parameters:
        - data (Optional[Dict[str, Any]]): The data to send in the request body.
        - json (Optional[Any]): The JSON data to send in the request body.
        - files (Optional[Dict[str, Any]]): The files to send in the request body.
        Returns:
        - Dict[str, Any]: A dictionary containing the data, json, or files to send in the request body.

        """
        if json is not None:
            self._set_content_type_header("application/json")
            return {"json": json}
        elif files is not None:
            self._set_content_type_header("multipart/form-data")
            return {"files": files, "data": data}
        elif data is not None:
            self._set_content_type_header("application/x-www-form-urlencoded")
            return {"data": data}
        return {}

    def _handle_response(self, response: requests.Response) -> RawResponseSimple:
        """
        This function handles the response from the API based on the content type. It checks the 'Content-Type' header in the response and parses the response content accordingly.
        Parameters:
        - response (requests.Response): The response object from the API.
        Returns:
        - RawResponseSimple: The parsed response content.

        """
        if not response.ok:
            self._handle_error_response(response)

        content_type = response.headers.get("Content-Type", "")

        if "application/json" in content_type:
            return response.json()
        elif "application/octet-stream" in content_type or "multipart/form-data" in content_type:
            return response.content
        else:
            return response.text

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

        try:
            error_data = response.json()
        except ValueError:
            logger.warning("Failed to parse JSON response.")
            error_data = response.text

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.error(f"HTTP error occurred: {response.status_code}, {error_data}")
            raise e

        raise requests.RequestException(f"Request failed with status code {response.status_code}, {error_data}")

    def _request(self, method: str, endpoint: str | None = None, url: str | None = None, **kwargs) -> Any:
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

        if url is None:
            if endpoint is None:
                raise ValueError("Either 'endpoint' or 'url' must be provided.")
            url = f"{self.config.base_url}/{endpoint.lstrip('/')}"

        logger.debug(f"Making {method} request to {url} with params: {kwargs}")
        response: requests.Response = self.session.request(method, url, **kwargs)
        return self._handle_response(response)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
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

        return self._request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
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

        prepared_data = self._prepare_data(data, json, files)
        return self._request("POST", endpoint, **prepared_data)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
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
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PUT", endpoint, **prepared_data)

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
        return self._request("DELETE", endpoint, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
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
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PATCH", endpoint, **prepared_data)

    def close(self) -> None:
        """
        Close the HTTP session.
        Parameters:
        - None
        Returns:
        - None
        """
        self.session.close()
        logger.debug("Session closed.")

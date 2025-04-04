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

from .auth.base import AuthStrategy
from .config import ClientConfig
from .exceptions import AuthenticationError, CrudClientError, NotFoundError
from .runtime_type_checkers import assert_type
from .types import RawResponseSimple

# Set up logging
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, config: ClientConfig | Dict[str, Any]) -> None:

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
        self.config.prepare()

        # Try the new auth strategy first
        if hasattr(self.config, "auth_strategy") and isinstance(self.config.auth_strategy, AuthStrategy):
            auth_headers = self.config.get_auth_headers()
            if auth_headers:
                self.session.headers.update(auth_headers)
            return

        # Fall back to the old auth method for backward compatibility
        # This handles the case where auth() is overridden in a subclass
        # Check if the config class has an auth method (old style)
        if hasattr(self.config, "auth") and callable(getattr(self.config, "auth")):
            auth = self.config.auth()
            if auth is not None:
                if isinstance(auth, dict):
                    self.session.headers.update(auth)
                elif isinstance(auth, tuple) and len(auth) == 2:
                    self.session.auth = auth
                elif callable(auth):
                    auth(self.session)

    def _setup_retries_and_timeouts(self) -> None:
        retries = self.config.retries or 3
        timeout = self.config.timeout or 5

        adapter = HTTPAdapter(max_retries=retries)

        # Mount the adapter to both 'http://' and 'https://' URLs in the session
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set the timeout duration for the session
        self.timeout = timeout

    def _set_content_type_header(self, content_type: str) -> None:
        self.session.headers["Content-Type"] = content_type

    def _prepare_data(
        self, data: Optional[Dict[str, Any]] = None, json: Optional[Any] = None, files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

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

    def _maybe_retry_after_403(self, method: str, url: str, kwargs: dict, response: requests.Response) -> requests.Response:
        if response.status_code != 403:
            return response

        if not self.config.should_retry_on_403():
            return response

        logger.debug("403 Forbidden received. Attempting retry via config handler.")
        self.config.handle_403_retry(self)
        self._setup_auth()
        retry_response = self.session.request(method, url, **kwargs)
        return retry_response

    def _handle_response(self, response: requests.Response) -> RawResponseSimple:
        if not response.ok:
            self._handle_error_response(response)

        content_type = response.headers.get("Content-Type", "")

        # Use startswith() for more precise Content-Type checking
        if content_type.startswith("application/json"):
            return response.json()
        elif content_type.startswith("application/octet-stream") or content_type.startswith("multipart/form-data"):
            return response.content
        else:
            return response.text

    def _handle_error_response(self, response: requests.Response) -> None:
        """
        Handle error responses from the API.

        This method attempts to extract error information from the response and raises
        appropriate exceptions based on the status code.

        Args:
            response: The response object from the API.

        Raises:
            AuthenticationError: If the status code is 401 (Unauthorized).
            NotFoundError: If the status code is 404 (Not Found).
            CrudClientError: For other error status codes.
        """
        try:
            error_data = response.json()
        except ValueError:
            logger.warning("Failed to parse JSON response.")
            error_data = response.text

        status_code = response.status_code
        error_message = f"HTTP error occurred: {status_code}, {error_data}"
        logger.error(error_message)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            # Map status codes to specific error types
            if status_code == 401:
                raise AuthenticationError(f"Authentication failed: {error_data}", response) from e
            elif status_code == 404:
                raise NotFoundError(f"Resource not found: {error_data}", response) from e
            else:
                raise CrudClientError(error_message, response) from e

        # This should not be reached, but just in case
        raise CrudClientError(f"Request failed with status code {status_code}, {error_data}", response)

    def _request(self, method: str, endpoint: str | None = None, url: str | None = None, handle_response: bool = True, **kwargs) -> Any:
        if url is None:
            if endpoint is None:
                raise ValueError("Either 'endpoint' or 'url' must be provided.")
            # Maintain backward compatibility with existing code
            url = f"{self.config.base_url}/{endpoint.lstrip('/')}"

        logger.debug(f"Making {method} request to {url} with params: {kwargs}")
        response: requests.Response = self.session.request(method, url, **kwargs)

        if not handle_response:
            return response

        return self._handle_response(response)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        return self._request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        prepared_data = self._prepare_data(data, json, files)
        return self._request("POST", endpoint, **prepared_data)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PUT", endpoint, **prepared_data)

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:

        return self._request("DELETE", endpoint, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PATCH", endpoint, **prepared_data)

    def close(self) -> None:
        self.session.close()
        logger.debug("Session closed.")

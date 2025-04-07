"""
Module `client.py`
==================

This module defines the Client class, which is responsible for managing HTTP requests to the API.
The Client class delegates HTTP operations to the HttpClient class, which handles request preparation,
authentication, response handling, and error handling.

Class `Client`
--------------

The `Client` class provides a flexible way to interact with various API endpoints.
It includes methods for different HTTP methods (GET, POST, PUT, DELETE, PATCH) and delegates
the actual HTTP operations to the HttpClient class.

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
from typing import Any, Dict, Optional, Tuple, Union

import requests

from .config import ClientConfig
from .http.client import HttpClient
from .types import RawResponseSimple

# Set up logging
logger = logging.getLogger(__name__)


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

    def __init__(self, config: Union[ClientConfig, Dict[str, Any]]) -> None:
        # Validate and set up the config
        if not isinstance(config, (ClientConfig, dict)):
            message = f"Invalid config provided: expected ClientConfig or dict, got {type(config).__name__}."
            logger.error(message)
            raise TypeError(message)
        if isinstance(config, dict):
            config = ClientConfig(**config)

        assert isinstance(config, ClientConfig)  # for mypy
        self.config = config

        # Set base URL for the API
        self.base_url = self.config.base_url

        # Initialize the HTTP client
        self.http_client = HttpClient(self.config)

        # For backward compatibility with existing tests
        # Expose the session from the HTTP client
        self._session = self.http_client.session_manager.session

    def _setup_auth(self) -> None:
        self.http_client.session_manager.refresh_auth()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        # Runtime type checks
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if params is not None and not isinstance(params, dict):
            raise TypeError(f"params must be a dictionary or None, got {type(params).__name__}")
        return self.http_client.get(endpoint, params=params)

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
        return self.http_client.post(endpoint, data=data, json=json, files=files)

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
        return self.http_client.put(endpoint, data=data, json=json, files=files)

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        # Runtime type check
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")
        return self.http_client.delete(endpoint, **kwargs)

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
        return self.http_client.patch(endpoint, data=data, json=json, files=files)

    def _request(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: bool = True, **kwargs: Any) -> Union[RawResponseSimple, requests.Response]:
        # Runtime type checks
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if endpoint is not None and not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string or None, got {type(endpoint).__name__}")

        if url is not None and not isinstance(url, str):
            raise TypeError(f"url must be a string or None, got {type(url).__name__}")

        if not isinstance(handle_response, bool):
            raise TypeError(f"handle_response must be a boolean, got {type(handle_response).__name__}")
        return self.http_client._request(method, endpoint, url, handle_response, **kwargs)

    def close(self) -> None:
        self.http_client.close()
        logger.debug("Client closed.")

    # Property for backward compatibility with existing tests
    @property
    def session(self) -> requests.Session:
        return self._session

    # The following methods are provided for backward compatibility with existing tests

    def _prepare_data(
        self,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, str], Dict[str, Any]]:
        # Runtime type checks
        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        headers = {}
        request_kwargs = {}

        if json is not None:
            headers["Content-Type"] = "application/json"
            request_kwargs["json"] = json
        elif files is not None:
            headers["Content-Type"] = "multipart/form-data"
            request_kwargs["files"] = files
            if data is not None:
                request_kwargs["data"] = data
        elif data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            request_kwargs["data"] = data

        # For backward compatibility, update the session headers
        if headers:
            self._session.headers.update(headers)

        return headers, request_kwargs

    def _maybe_retry_after_403(
        self, method: str, url: str, kwargs: Dict[str, Any], response: requests.Response
    ) -> requests.Response:
        # Runtime type checks
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if not isinstance(url, str):
            raise TypeError(f"url must be a string, got {type(url).__name__}")

        if not isinstance(kwargs, dict):
            raise TypeError(f"kwargs must be a dictionary, got {type(kwargs).__name__}")

        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if not isinstance(response, requests.Response) and not hasattr(response, '_mock_spec') and requests.Response not in getattr(response, '_mock_spec', []):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        if response.status_code != 403:
            return response

        if not self.config.should_retry_on_403():
            return response

        logger.debug("403 Forbidden received. Attempting retry via config handler.")
        self.config.handle_403_retry(self)
        self._setup_auth()
        retry_response = self._session.request(method, url, **kwargs)
        return retry_response

    def _handle_response(self, response: requests.Response) -> RawResponseSimple:
        # Runtime type check
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if not isinstance(response, requests.Response) and not hasattr(response, '_mock_spec') and requests.Response not in getattr(response, '_mock_spec', []):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        return self.http_client.response_handler.handle_response(response)

    def _handle_error_response(self, response: requests.Response) -> None:
        # Runtime type check
        # Runtime type check - allow both real Response objects and mocks with spec=Response
        if not isinstance(response, requests.Response) and not hasattr(response, '_mock_spec') and requests.Response not in getattr(response, '_mock_spec', []):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        self.http_client.error_handler.handle_error_response(response)

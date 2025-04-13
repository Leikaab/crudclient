import json
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Literal, Optional, Type, Union, overload

import requests

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.spy.enhanced import EnhancedSpyBase
from crudclient.types import RawResponseSimple

from .stubs import StubResponse

class StubClient(EnhancedSpyBase, Client):
    """
    A stub implementation of the Client for testing purposes.

    This client allows configuring responses based on request patterns (method and URL)
    and simulates network conditions like latency and errors. It also records
    request history for verification.
    """

    _default_response: Union[Dict[str, Any], List[Dict[str, Any]], str]
    _response_map: Dict[str, Any]
    _error_rate: float
    _latency_ms: int

    def configure_get(self, response: Optional[Any] = None, handler: Optional[Callable] = None) -> None:
        """
        Configure the response or handler for GET requests matching a pattern.

        Args:
            response: The static response to return for matching GET requests.
            handler: A callable function to generate the response dynamically.
                     The handler should accept (endpoint, params) arguments.
        """
        ...

    def configure_post(self, response: Optional[Any] = None, handler: Optional[Callable] = None) -> None:
        """
        Configure the response or handler for POST requests matching a pattern.

        Args:
            response: The static response to return for matching POST requests.
            handler: A callable function to generate the response dynamically.
                     The handler should accept (endpoint, data, json, params) arguments.
        """
        ...

    def __init__(
        self,
        config: Union[ClientConfig, Dict[str, Any]],
        default_response: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None,
        response_map: Optional[Dict[str, Any]] = None,
        error_rate: float = 0.0,
        latency_ms: int = 0,
    ) -> None:
        """
        Initialize the StubClient.

        Args:
            config: Client configuration (ClientConfig object or dictionary).
            default_response: The response to return if no pattern matches.
                              Defaults to {"message": "Stub response"}.
            response_map: A dictionary mapping regex patterns to responses or handlers.
                          Patterns starting with '^METHOD:' (e.g., '^GET:') are method-specific.
                          Other patterns match against the full URL.
            error_rate: The probability (0.0 to 1.0) of simulating a connection error.
            latency_ms: The simulated network latency in milliseconds.
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
    def _build_full_url(self, endpoint: Optional[str], url: Optional[str]) -> str:
        """
        Build the full URL from endpoint or use provided URL.

        Args:
            endpoint: The API endpoint path.
            url: The full URL (overrides endpoint if provided).

        Returns:
            The complete URL to use for the request.
        """
        ...

    def _simulate_network_conditions(self) -> None:
        """
        Simulate network latency.

        Introduces a delay based on the configured latency_ms value.
        """
        ...

    def _handle_simulated_error(self, handle_response: bool) -> Optional[str]:
        """
        Handle simulated network errors based on error rate.

        Args:
            handle_response: If True, raise exceptions for simulated errors.
                             If False, return error as JSON string.

        Returns:
            A JSON error string if an error is simulated and handle_response is False,
            otherwise None.

        Raises:
            requests.ConnectionError: If error simulation is triggered and handle_response is True.
        """
        ...

    def _find_matching_response(self, method: str, url: str) -> Any:
        """
        Find a matching response from the response map.

        First tries to find a method-specific pattern, then falls back to generic URL patterns.

        Args:
            method: The HTTP method (e.g., 'GET', 'POST').
            url: The full URL for the request.

        Returns:
            The matching response or the default response if no match is found.
        """
        ...

    def _process_callable_response(self, response: Any, method: str, endpoint: Optional[str], url: str, kwargs: Dict[str, Any]) -> Any:
        """
        Process response if it's a callable.

        Handles different HTTP methods by passing appropriate arguments to the callable.

        Args:
            response: The response object or callable.
            method: The HTTP method (e.g., 'GET', 'POST').
            endpoint: The API endpoint path.
            url: The full URL for the request.
            kwargs: Additional request parameters.

        Returns:
            The result of calling the response function with appropriate arguments.
        """
        ...

    def _convert_response_to_string(self, response: Any, handle_response: bool) -> str:
        """
        Convert the response object to a string.

        Handles different response types (dict, list, StubResponse, etc.).

        Args:
            response: The response object to convert.
            handle_response: If True, raise exceptions for error status codes.

        Returns:
            The response as a string.

        Raises:
            requests.HTTPError: If a StubResponse with a >= 400 status code is returned
                                and handle_response is True.
        """
        ...

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Simulate a GET request.

        Args:
            endpoint: The API endpoint path.
            params: Optional query parameters.

        Returns:
            The parsed JSON response or the raw response string if not valid JSON.
        """
        ...

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Simulate a POST request.

        Args:
            endpoint: The API endpoint path.
            data: Optional form data.
            json: Optional JSON payload.
            files: Optional files to upload.

        Returns:
            The parsed JSON response or the raw response string if not valid JSON.
        """
        ...

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Simulate a PUT request.

        Args:
            endpoint: The API endpoint path.
            data: Optional form data.
            json: Optional JSON payload.
            files: Optional files to upload.

        Returns:
            The parsed JSON response or the raw response string if not valid JSON.
        """
        ...

    def delete(self, endpoint: str, **kwargs: Any) -> Any:
        """
        Simulate a DELETE request.

        Args:
            endpoint: The API endpoint path.
            **kwargs: Additional request parameters.

        Returns:
            The parsed JSON response or the raw response string if not valid JSON.
        """
        ...

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Simulate a PATCH request.

        Args:
            endpoint: The API endpoint path.
            data: Optional form data.
            json: Optional JSON payload.
            files: Optional files to upload.

        Returns:
            The parsed JSON response or the raw response string if not valid JSON.
        """
        ...

    def add_response(self, pattern: str, response: Any) -> None:
        """
        Add or update a response mapping.

        Args:
            pattern: The regex pattern to match against the URL or '^METHOD:...' pattern.
            response: The response object, dictionary, list, string, or callable handler.
        """
        ...

    def set_default_response(self, response: Any) -> None:
        """
        Set the default response to return when no pattern matches.

        Args:
            response: The default response object, dictionary, list, string, or callable handler.
        """
        ...

    def set_error_rate(self, error_rate: float) -> None:
        """
        Set the simulated connection error rate.

        Args:
            error_rate: The probability (0.0 to 1.0) of simulating an error.
        """
        ...

    def set_latency(self, latency_ms: int) -> None:
        """
        Set the simulated network latency.

        Args:
            latency_ms: The latency in milliseconds.
        """
        ...

import json
import random
import re
import time
from typing import Any, Dict, List, Optional, Union

import requests

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.spy.enhanced import EnhancedSpyBase

from .stubs import StubResponse  # Assuming StubResponse remains in stubs.py


class StubClient(EnhancedSpyBase, Client):

    def configure_get(self, response=None, handler=None):
        if handler:
            # Store the handler with a pattern that matches GET requests
            self.add_response("^GET:", handler)
        elif response:
            # Store the response with a pattern that matches GET requests
            self.add_response("^GET:", response)

    def configure_post(self, response=None, handler=None):
        if handler:
            # Store the handler with a pattern that matches POST requests
            self.add_response("^POST:", handler)
        elif response:
            # Store the response with a pattern that matches POST requests
            self.add_response("^POST:", response)

    def __init__(
        self,
        config: Union[ClientConfig, Dict[str, Any]],
        default_response: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None,
        response_map: Optional[Dict[str, Any]] = None,
        error_rate: float = 0.0,
        latency_ms: int = 0,
    ):
        # Initialize EnhancedSpyBase first
        EnhancedSpyBase.__init__(self)
        # Then initialize Client
        Client.__init__(self, config)

        # Default response
        if default_response is None:
            self._default_response = {"message": "Stub response"}
        else:
            self._default_response = default_response

        # Response map (endpoint pattern -> response)
        self._response_map = response_map or {}

        # Error simulation
        self._error_rate = max(0.0, min(1.0, error_rate))
        self._latency_ms = max(0, latency_ms)

    def _build_full_url(self, endpoint: Optional[str], url: Optional[str]) -> str:
        if url is None and endpoint is not None:
            return f"{self.base_url}/{endpoint.lstrip('/')}"
        return url or self.base_url

    def _simulate_network_conditions(self) -> None:
        if self._latency_ms > 0:
            time.sleep(self._latency_ms / 1000.0)

    def _handle_simulated_error(self, handle_response: bool) -> Optional[str]:
        if self._error_rate > 0 and random.random() < self._error_rate:
            error = requests.ConnectionError("Simulated network error")
            if handle_response:
                raise error
            return json.dumps({"error": "Simulated network error"})
        return None

    def _find_matching_response(self, method: str, url: str) -> Any:
        method_prefix = f"{method}:"

        # First try to find a method-specific pattern
        for pattern, resp in self._response_map.items():
            if pattern.startswith("^") and pattern[1:].startswith(method_prefix):
                return resp

        # If no method-specific pattern found, try generic patterns
        for pattern, resp in self._response_map.items():
            if not pattern.startswith("^") and re.search(pattern, url):
                return resp

        # Use default response if no match found
        return self._default_response

    def _process_callable_response(self, response: Any, method: str, endpoint: Optional[str], url: str, kwargs: Dict[str, Any]) -> Any:
        if not callable(response):
            return response

        # Extract the endpoint from the URL if not provided
        endpoint_value = endpoint or url.split("/")[-1]

        # Handle different HTTP methods
        if method == "GET":
            params = kwargs.get("params", {})
            return response(endpoint_value, params)
        elif method == "POST":
            data = kwargs.get("data", {})
            json_data = kwargs.get("json", {})
            params = kwargs.get("params", {})
            return response(endpoint_value, data=data, json=json_data, params=params)
        else:
            # For other methods, pass all kwargs
            return response(endpoint_value, **kwargs)

    def _convert_response_to_string(self, response: Any, handle_response: bool) -> str:
        # Handle dict or list responses
        if isinstance(response, (dict, list)):
            return json.dumps(response)

        # Handle StubResponse objects
        elif isinstance(response, StubResponse):
            if response.status_code >= 400 and handle_response:
                response.raise_for_status()

            if hasattr(response, "_json_data") and response._json_data:
                return json.dumps(response._json_data)

            # Handle text response
            response_str = response.text
            # Try to parse as JSON if it looks like JSON
            if response_str.strip().startswith("{") or response_str.strip().startswith("["):
                try:
                    json.loads(response_str)  # Just to validate it's valid JSON
                except json.JSONDecodeError:
                    pass  # Not valid JSON, leave as text
            return response_str

        # Handle other response types
        else:
            return str(response)

    def _request(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: bool = True, **kwargs: Any) -> str:
        # Build the full URL
        url = self._build_full_url(endpoint, url)

        # Capture start time for duration measurement
        start_time = time.time()

        # Initialize variables for try-except-finally block
        result = None
        exception = None

        try:
            # Simulate network conditions (latency)
            self._simulate_network_conditions()

            # Handle simulated errors
            error_response = self._handle_simulated_error(handle_response)
            if error_response:
                result = error_response
                return result

            # Find a matching response
            response = self._find_matching_response(method, url)

            # Process callable responses
            if callable(response):
                response = self._process_callable_response(response, method, endpoint, url, kwargs)

            # Convert response to string
            result = self._convert_response_to_string(response, handle_response)
            return result
        except Exception as e:
            exception = e
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time

            # Record the call using EnhancedSpyBase's _record_call method
            try:
                self._record_call(
                    method_name=method,
                    args=(url,),
                    kwargs=kwargs,
                    result=result if "result" in locals() else None,
                    exception=exception,
                    duration=duration,
                )
            except UnboundLocalError:
                # Handle case where result might not be defined
                self._record_call(method_name=method, args=(url,), kwargs=kwargs, result=None, exception=exception, duration=duration)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        import json as json_module

        response_str = self._request("GET", endpoint=endpoint, params=params)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Any] = None,  # Renamed to avoid conflict
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        import json as json_module

        response_str = self._request("POST", endpoint=endpoint, data=data, json=json_payload, files=files)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Any] = None,  # Renamed to avoid conflict
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        import json as json_module

        response_str = self._request("PUT", endpoint=endpoint, data=data, json=json_payload, files=files)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def delete(self, endpoint: str, **kwargs: Any) -> Any:
        import json as json_module

        response_str = self._request("DELETE", endpoint=endpoint, **kwargs)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_payload: Optional[Any] = None,  # Renamed to avoid conflict
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        import json as json_module

        response_str = self._request("PATCH", endpoint=endpoint, data=data, json=json_payload, files=files)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def add_response(self, pattern: str, response: Any) -> None:
        self._response_map[pattern] = response

    def set_default_response(self, response: Any) -> None:
        self._default_response = response

    def set_error_rate(self, error_rate: float) -> None:
        self._error_rate = max(0.0, min(1.0, error_rate))

    def set_latency(self, latency_ms: int) -> None:
        self._latency_ms = max(0, latency_ms)

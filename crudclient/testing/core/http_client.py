import json
import re
import time  # Added
from typing import Any, Dict, List, Optional, Pattern, Tuple, Union  # Added List, Pattern, Union
from urllib.parse import urljoin

import requests
from requests import Response

from ..exceptions import RequestNotConfiguredError
from ..types import Headers, HttpMethod, QueryParams, RequestBody, ResponseBody, StatusCode


class MockHTTPClient:

    def __init__(self, base_url: str = "https://api.example.com") -> None:
        self.base_url = base_url
        # Store exact path matches
        self._configured_responses: Dict[Tuple[HttpMethod, str], Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]] = {}
        # Store path patterns (regex) - LIFO (last added pattern checked first)
        self._configured_patterns: List[Tuple[HttpMethod, Pattern, Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]]] = []
        # Network conditions
        self._latency_ms: float = 0.0

    def reset(self) -> None:
        self._configured_responses = {}
        self._configured_patterns = []
        self._latency_ms = 0.0

    def configure_response(
        self,
        method: HttpMethod,
        path: str,
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None:
        # Normalize the method to uppercase
        method = method.upper()

        # Normalize the path to remove leading slash if present
        path = path.lstrip("/")

        # Store the configured response
        self._configured_responses[(method, path)] = (status_code, data if error is None else (data or {}), headers or {}, error)

    def with_response_pattern(
        self,
        method: HttpMethod,
        path_pattern: Union[str, Pattern],
        status_code: StatusCode = 200,
        data: Optional[ResponseBody] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None,
    ) -> None:
        # Normalize the method to uppercase
        method = method.upper()

        # Compile pattern if it's a string
        if isinstance(path_pattern, str):
            # Ensure pattern doesn't start with / for consistency with path normalization
            if path_pattern.startswith("/"):
                # Simple adjustment, might need refinement based on usage
                path_pattern = path_pattern.lstrip("/")
            pattern = re.compile(path_pattern)
        else:
            pattern = path_pattern

        # Store the configured pattern and response
        self._configured_patterns.append((method, pattern, (status_code, data or {}, headers or {}, error)))

    def with_network_condition(
        self,
        latency_ms: float = 0.0,
        # Future: packet_loss_rate: float = 0.0
    ) -> None:
        if latency_ms < 0:
            raise ValueError("Latency cannot be negative.")
        self._latency_ms = latency_ms
        # self._packet_loss_rate = packet_loss_rate

    def _get_configured_response(self, method: HttpMethod, path: str) -> Tuple[StatusCode, ResponseBody, Headers, Optional[Exception]]:
        # Normalize the method to uppercase
        method = method.upper()

        # Normalize the path to remove leading slash if present
        path = path.lstrip("/")

        # 1. Check for exact match
        exact_key = (method, path)
        if exact_key in self._configured_responses:
            return self._configured_responses[exact_key]

        # 2. Check for pattern match (LIFO - iterate in reverse)
        for pattern_method, pattern, response_config in reversed(self._configured_patterns):
            if pattern_method == method and pattern.search(path):
                return response_config

        # 3. No match found
        raise RequestNotConfiguredError(method, path)

    def request(
        self,
        method: HttpMethod,
        path: str,
        headers: Optional[Headers] = None,
        params: Optional[QueryParams] = None,
        data: Optional[RequestBody] = None,
        **kwargs: Any,
    ) -> Response:
        # Simulate latency if configured
        if self._latency_ms > 0:
            time.sleep(self._latency_ms / 1000.0)

        # Find the configured response (checks exact then patterns)
        status_code, response_body, response_headers, error = self._get_configured_response(method=method, path=path)

        # If an error is configured, raise it
        if error is not None:
            raise error

        # Create a Response object with the configured response
        url = urljoin(self.base_url, path)  # Use original path for URL
        response = requests.Response()
        response.status_code = status_code
        response.headers.update(response_headers or {})

        # Handle different response body types
        # Handle different response body types
        if response_body is None:
            response._content = None
        elif isinstance(response_body, bytes):
            response._content = response_body
        elif isinstance(response_body, str):
            response._content = response_body.encode("utf-8")
        else:
            # Assume JSON serializable if dict/list, convert to string then bytes
            # Note: 'import json' moved to top of file
            try:
                response._content = json.dumps(response_body).encode("utf-8")
                if "content-type" not in (h.lower() for h in response.headers):
                    response.headers["Content-Type"] = "application/json"
            except TypeError:  # Handle non-serializable types if necessary
                response._content = str(response_body).encode("utf-8")

        response.url = url
        # Set request on response for potential inspection
        response.request = requests.Request(method=method.upper(), url=url, headers=headers, data=data, params=params).prepare()

        return response

    # Convenience methods for common HTTP methods

    def get(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Response:
        return self.request(method="GET", path=path, headers=headers, params=params, **kwargs)

    def post(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Response:
        return self.request(method="POST", path=path, headers=headers, params=params, data=data, **kwargs)

    def put(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Response:
        return self.request(method="PUT", path=path, headers=headers, params=params, data=data, **kwargs)

    def delete(self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, **kwargs: Any) -> Response:
        return self.request(method="DELETE", path=path, headers=headers, params=params, **kwargs)

    def patch(
        self, path: str, headers: Optional[Headers] = None, params: Optional[QueryParams] = None, data: Optional[RequestBody] = None, **kwargs: Any
    ) -> Response:
        return self.request(method="PATCH", path=path, headers=headers, params=params, data=data, **kwargs)

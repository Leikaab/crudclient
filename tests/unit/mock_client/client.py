"""
Mock Client implementation for testing.
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional, Union

import requests
from requests import Response

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.types import RawResponseSimple

from .response import MockResponse
from .patterns import ResponsePattern
from .network import NetworkCondition
from .pagination import PaginationHelper
from .rate_limit import RateLimitHelper
from .partial_response import PartialResponseHelper
from .request_record import RequestRecord


class MockClient(Client):
    """
    Enhanced mock Client implementation with configurable behavior.

    Features:
    - Configurable response patterns
    - Chainable mock configuration
    - Network condition simulation
    - Support for pagination, rate limiting, and partial responses
    - Helpers for verifying client usage patterns
    """

    def __init__(self, config: Union[ClientConfig, Dict[str, Any]]):
        """
        Initialize the MockClient.

        Args:
            config: Client configuration
        """
        # Initialize with a real Client to maintain compatibility
        super().__init__(config)

        # Mock configuration
        self.response_patterns: List[ResponsePattern] = []
        self.network_condition: Optional[NetworkCondition] = None
        self.rate_limiter: Optional[RateLimitHelper] = None

        # Replace the HTTP client with our mock HTTP client
        # We need to do this after super().__init__() so we can reference self
        from .http_client import MockHttpClient
        self.http_client = MockHttpClient(self.config, self)

        # Request history
        self.request_history: List[RequestRecord] = []

        # Default response if no pattern matches
        self.default_response = MockResponse(
            status_code=404,
            json_data={"error": "No matching mock response configured"}
        )

    def with_response_pattern(
        self,
        method: str,
        url_pattern: str,
        response: Union[MockResponse, Dict[str, Any], str, Callable[..., MockResponse]],
        **kwargs: Any
    ) -> 'MockClient':
        """Add a response pattern to the mock client."""
        # Convert dict/string responses to MockResponse
        if isinstance(response, dict):
            response = MockResponse(json_data=response)
        elif isinstance(response, str):
            response = MockResponse(text=response)

        pattern = ResponsePattern(
            method=method,
            url_pattern=url_pattern,
            response=response,
            params_matcher=kwargs.get('params'),
            data_matcher=kwargs.get('data'),
            json_matcher=kwargs.get('json'),
            headers_matcher=kwargs.get('headers'),
            max_calls=kwargs.get('max_calls')
        )

        self.response_patterns.append(pattern)
        return self

    def with_network_condition(
        self,
        latency_ms: int = 0,
        packet_loss_percentage: float = 0.0,
        error_rate_percentage: float = 0.0,
        error_factory: Optional[Callable[[], Exception]] = None
    ) -> 'MockClient':
        """Configure network conditions for the mock client."""
        self.network_condition = NetworkCondition(
            latency_ms=latency_ms,
            packet_loss_percentage=packet_loss_percentage,
            error_rate_percentage=error_rate_percentage,
            error_factory=error_factory
        )
        return self

    def with_rate_limiter(
        self,
        limit: int = 60,
        window_seconds: int = 60
    ) -> 'MockClient':
        """Configure rate limiting for the mock client."""
        self.rate_limiter = RateLimitHelper(limit=limit, window_seconds=window_seconds)
        return self

    def with_default_response(
        self,
        response: Union[MockResponse, Dict[str, Any], str]
    ) -> 'MockClient':
        """Set the default response for unmatched requests."""
        if isinstance(response, dict):
            self.default_response = MockResponse(json_data=response)
        elif isinstance(response, str):
            self.default_response = MockResponse(text=response)
        else:
            self.default_response = response
        return self

    def reset(self) -> 'MockClient':
        """Reset the mock client to its initial state."""
        self.response_patterns = []
        self.network_condition = None
        self.rate_limiter = None
        self.request_history = []
        self.default_response = MockResponse(
            status_code=404,
            json_data={"error": "No matching mock response configured"}
        )
        return self

    def create_paginated_response(
        self,
        items: List[Any],
        page_size: int = 10,
        base_url: str = ""
    ) -> PaginationHelper:
        """Create a pagination helper for simulating paginated responses."""
        if not base_url:
            base_url = f"{self.config.base_url}"

        return PaginationHelper(
            items=items,
            page_size=page_size,
            base_url=base_url
        )

    def create_partial_response_helper(
        self,
        full_response: Dict[str, Any]
    ) -> PartialResponseHelper:
        """Create a helper for generating partial responses."""
        return PartialResponseHelper(full_response)

    def _request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        handle_response: bool = True,
        **kwargs: Any
    ) -> Union[RawResponseSimple, Response]:
        """Mock implementation of the _request method to handle mock responses."""
        # Determine the full URL
        if url is None and endpoint is not None:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        elif url is None:
            url = self.base_url

        # Record the request
        record = RequestRecord(
            method=method,
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Apply network conditions if configured
        if self.network_condition:
            self.network_condition.apply_latency()

            if self.network_condition.should_drop_packet():
                error = requests.ConnectionError("Simulated packet loss")
                if handle_response:
                    raise error
                mock_response = MockResponse(error=error)
                record.response = mock_response
                return mock_response

            if self.network_condition.should_raise_error():
                error = self.network_condition.error_factory()
                if handle_response:
                    raise error
                mock_response = MockResponse(error=error)
                record.response = mock_response
                return mock_response

        # Apply rate limiting if configured
        if self.rate_limiter:
            is_allowed, headers = self.rate_limiter.check_rate_limit()
            if not is_allowed:
                mock_response = MockResponse(
                    status_code=429,
                    json_data={"error": "Rate limit exceeded"},
                    headers=headers
                )
                record.response = mock_response
                if handle_response:
                    # Convert to RawResponseSimple
                    return mock_response.text
                return mock_response

        # Find a matching response pattern
        for pattern in self.response_patterns:
            if pattern.matches(
                method=method,
                url=url,
                params=kwargs.get('params'),
                data=kwargs.get('data'),
                json=kwargs.get('json'),
                headers=kwargs.get('headers')
            ):
                mock_response = pattern.get_response(**kwargs)
                record.response = mock_response
                if handle_response:
                    # Convert to RawResponseSimple
                    if hasattr(mock_response, '_json_data') and mock_response._json_data:
                        return json.dumps(mock_response._json_data)
                    return mock_response.text
                return mock_response

        # No pattern matched, use default response
        record.response = self.default_response
        if handle_response:
            # Convert to RawResponseSimple
            if hasattr(self.default_response, '_json_data') and self.default_response._json_data:
                return json.dumps(self.default_response._json_data)
            return self.default_response.text
        return self.default_response

    def assert_request_count(self, count: int, method: Optional[str] = None, url_pattern: Optional[str] = None) -> None:
        """Assert that a specific number of matching requests were made."""
        matching_requests = self._filter_requests(method, url_pattern)
        actual_count = len(matching_requests)

        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. "
            f"Filters: method={method}, url_pattern={url_pattern}"
        )

    def assert_request_sequence(
        self,
        sequence: List[Dict[str, Any]],
        strict: bool = False
    ) -> None:
        """Assert that requests were made in a specific sequence."""
        if not sequence:
            return

        if strict and len(sequence) != len(self.request_history):
            raise AssertionError(
                f"Expected {len(sequence)} requests, but found {len(self.request_history)}"
            )

        # Find subsequence match
        history_idx = 0
        sequence_idx = 0

        while history_idx < len(self.request_history) and sequence_idx < len(sequence):
            request = self.request_history[history_idx]
            matcher = sequence[sequence_idx]

            method_match = True
            if 'method' in matcher:
                method_match = request.method == matcher['method'].upper()

            url_match = True
            if 'url_pattern' in matcher:
                url_match = bool(re.search(matcher['url_pattern'], request.url))

            params_match = True
            if 'params' in matcher and matcher['params'] is not None:
                params_match = ResponsePattern._dict_matches(matcher['params'], request.params or {})

            data_match = True
            if 'data' in matcher and matcher['data'] is not None:
                data_match = ResponsePattern._dict_matches(matcher['data'], request.data or {})

            json_match = True
            if 'json' in matcher and matcher['json'] is not None:
                json_match = ResponsePattern._dict_matches(matcher['json'], request.json or {})

            if method_match and url_match and params_match and data_match and json_match:
                sequence_idx += 1

            history_idx += 1

        if sequence_idx < len(sequence):
            raise AssertionError(
                f"Request sequence not found. Matched {sequence_idx} of {len(sequence)} expected requests."
            )

    def assert_request_params(
        self,
        params: Dict[str, Any],
        method: Optional[str] = None,
        url_pattern: Optional[str] = None,
        match_all: bool = False
    ) -> None:
        """Assert that requests were made with specific parameters."""
        matching_requests = self._filter_requests(method, url_pattern)

        if not matching_requests:
            raise AssertionError(
                f"No matching requests found. Filters: method={method}, url_pattern={url_pattern}"
            )

        if match_all:
            for i, request in enumerate(matching_requests):
                request_params = request.params or {}
                for key, value in params.items():
                    if key not in request_params:
                        raise AssertionError(
                            f"Request {i} missing parameter '{key}'. "
                            f"Method: {request.method}, URL: {request.url}"
                        )
                    if callable(value):
                        if not value(request_params[key]):
                            raise AssertionError(
                                f"Request {i} parameter '{key}' failed validation. "
                                f"Method: {request.method}, URL: {request.url}"
                            )
                    elif request_params[key] != value:
                        raise AssertionError(
                            f"Request {i} parameter '{key}' has value '{request_params[key]}', "
                            f"expected '{value}'. Method: {request.method}, URL: {request.url}"
                        )
        else:
            # At least one request must match all params
            for i, request in enumerate(matching_requests):
                all_match = True
                request_params = request.params or {}
                for key, value in params.items():
                    if key not in request_params:
                        all_match = False
                        break
                    if callable(value):
                        if not value(request_params[key]):
                            all_match = False
                            break
                    elif request_params[key] != value:
                        all_match = False
                        break

                if all_match:
                    return  # Found a match

            raise AssertionError(
                f"No request matched all parameters {params}. "
                f"Filters: method={method}, url_pattern={url_pattern}"
            )

    def assert_auth_usage(
        self,
        auth_header_name: str = "Authorization",
        auth_header_pattern: Optional[str] = None
    ) -> None:
        """Assert that requests were made with proper authentication."""
        if not self.request_history:
            raise AssertionError("No requests were made")

        for i, request in enumerate(self.request_history):
            headers = request.headers or {}

            if auth_header_name not in headers:
                raise AssertionError(
                    f"Request {i} missing authentication header '{auth_header_name}'. "
                    f"Method: {request.method}, URL: {request.url}"
                )

            if auth_header_pattern and not re.search(auth_header_pattern, headers[auth_header_name]):
                raise AssertionError(
                    f"Request {i} authentication header '{auth_header_name}' value '{headers[auth_header_name]}' "
                    f"does not match pattern '{auth_header_pattern}'. "
                    f"Method: {request.method}, URL: {request.url}"
                )

    def _filter_requests(
        self,
        method: Optional[str] = None,
        url_pattern: Optional[str] = None
    ) -> List[RequestRecord]:
        """Filter request history by method and URL pattern."""
        result = self.request_history

        if method:
            result = [r for r in result if r.method == method.upper()]

        if url_pattern:
            pattern = re.compile(url_pattern)
            result = [r for r in result if pattern.search(r.url)]

        return result

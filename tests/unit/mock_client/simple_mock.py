"""
Simple mock client for testing.
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional, Union

from .response import MockResponse
from .request_record import RequestRecord


class SimpleMockClient:
    """
    A simple mock client that doesn't inherit from the real Client class.
    This avoids all the complexities of the real HTTP client.
    """

    def __init__(self):
        """Initialize the simple mock client."""
        self.response_patterns = []
        self.request_history = []
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
    ) -> 'SimpleMockClient':
        """Add a response pattern to the mock client."""
        # Convert dict/string responses to MockResponse
        if isinstance(response, dict):
            response = MockResponse(json_data=response)
        elif isinstance(response, str):
            response = MockResponse(text=response)

        self.response_patterns.append({
            'method': method.upper(),
            'url_pattern': url_pattern,
            'response': response,
            'params': kwargs.get('params'),
            'data': kwargs.get('data'),
            'json': kwargs.get('json'),
            'headers': kwargs.get('headers'),
            'max_calls': kwargs.get('max_calls', float('inf')),
            'call_count': 0
        })
        return self

    def with_default_response(
        self,
        response: Union[MockResponse, Dict[str, Any], str]
    ) -> 'SimpleMockClient':
        """Set the default response for unmatched requests."""
        if isinstance(response, dict):
            self.default_response = MockResponse(json_data=response)
        elif isinstance(response, str):
            self.default_response = MockResponse(text=response)
        else:
            self.default_response = response
        return self

    def _request(self, method: str, url: str, **kwargs: Any) -> str:
        """Process a request and return a mock response."""
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

        # Find a matching response pattern
        for pattern in self.response_patterns:
            if (pattern['method'] == method.upper()
                    and re.search(pattern['url_pattern'], url)):

                # Check if we've reached the max calls for this pattern
                if pattern['call_count'] >= pattern['max_calls']:
                    continue

                # Check params matcher
                params_match = True
                if pattern['params'] is not None:
                    request_params = kwargs.get('params', {})
                    for key, value in pattern['params'].items():
                        if key not in request_params or request_params[key] != value:
                            params_match = False
                            break

                # Check data matcher
                data_match = True
                if pattern['data'] is not None:
                    request_data = kwargs.get('data', {})
                    for key, value in pattern['data'].items():
                        if key not in request_data or request_data[key] != value:
                            data_match = False
                            break

                # Check json matcher
                json_match = True
                if pattern['json'] is not None:
                    request_json = kwargs.get('json', {})
                    for key, value in pattern['json'].items():
                        if key not in request_json or request_json[key] != value:
                            json_match = False
                            break

                # Check headers matcher
                headers_match = True
                if pattern['headers'] is not None:
                    request_headers = kwargs.get('headers', {})
                    for key, value in pattern['headers'].items():
                        if key not in request_headers or request_headers[key] != value:
                            headers_match = False
                            break

                # If all matchers pass, return the response
                if params_match and data_match and json_match and headers_match:
                    pattern['call_count'] += 1
                    response_obj = pattern['response']

                    # Handle callable responses
                    if callable(response_obj):
                        response_obj = response_obj(**kwargs)

                    # Ensure it's a MockResponse
                    if not isinstance(response_obj, MockResponse):
                        if isinstance(response_obj, dict):
                            response_obj = MockResponse(json_data=response_obj)
                        elif isinstance(response_obj, list):
                            # Convert list to JSON string
                            response_obj = MockResponse(text=json.dumps(response_obj))
                        elif isinstance(response_obj, str):
                            response_obj = MockResponse(text=response_obj)
                        else:
                            response_obj = MockResponse(text=str(response_obj))

                    record.response = response_obj

                    # Convert to string
                    if hasattr(response_obj, '_json_data') and response_obj._json_data:
                        return json.dumps(response_obj._json_data)
                    return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        # Convert to string
        if hasattr(self.default_response, '_json_data') and self.default_response._json_data:
            return json.dumps(self.default_response._json_data)
        return self.default_response.text

    def get(self, url: str, **kwargs: Any) -> str:
        """Perform a GET request."""
        return self._request('GET', url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> str:
        """Perform a POST request."""
        return self._request('POST', url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> str:
        """Perform a PUT request."""
        return self._request('PUT', url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> str:
        """Perform a DELETE request."""
        return self._request('DELETE', url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> str:
        """Perform a PATCH request."""
        return self._request('PATCH', url, **kwargs)

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

            if method_match and url_match:
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

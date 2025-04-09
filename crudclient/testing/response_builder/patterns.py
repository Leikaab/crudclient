"""
Response pattern matching for mock HTTP requests.

This module provides a pattern matching system for HTTP requests in testing scenarios.
It allows for defining patterns that match specific HTTP requests based on method, URL,
query parameters, form data, JSON data, and headers. When a request matches a pattern,
a predefined or dynamically generated response is returned.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Union

from crudclient.testing.response_builder.response import MockResponse


class ResponsePattern:
    """
    Defines a pattern for matching HTTP requests and returning specific responses.

    This class provides a flexible way to define patterns that match HTTP requests
    based on various criteria such as HTTP method, URL pattern, query parameters,
    form data, JSON data, and headers. When a request matches the pattern, a
    predefined or dynamically generated response is returned.

    The pattern matching can be further customized with additional conditions
    that can examine the entire request context. This allows for complex
    matching logic that can't be expressed through the standard matchers.

    Each pattern can also be configured with a maximum number of calls,
    after which it will no longer match requests even if all other criteria match.
    This is useful for simulating changing API behavior over time.
    """

    def __init__(
        self,
        method: str,
        url_pattern: str,
        response: Union[MockResponse, Callable[..., MockResponse]],
        params_matcher: Optional[Dict[str, Any]] = None,
        data_matcher: Optional[Dict[str, Any]] = None,
        json_matcher: Optional[Dict[str, Any]] = None,
        headers_matcher: Optional[Dict[str, Any]] = None,
        call_count: int = 0,
        max_calls: Optional[int] = None,
        conditions: Optional[List[Callable[[Dict[str, Any]], bool]]] = None,
    ):
        """
        Initialize a response pattern with matching criteria and response.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.) to match
            url_pattern: Regular expression pattern to match request URLs
            response: Either a MockResponse object to return or a factory function
                      that returns a MockResponse when called
            params_matcher: Dictionary to match query parameters against
            data_matcher: Dictionary to match form data against
            json_matcher: Dictionary to match JSON request body against
            headers_matcher: Dictionary to match request headers against
            call_count: Initial call count for this pattern (usually starts at 0)
            max_calls: Maximum number of times this pattern can match before it stops matching
            conditions: List of additional functions that take the request context and
                        return a boolean indicating whether the pattern matches
        """
        self.method = method.upper()
        self.url_pattern = re.compile(url_pattern)
        self.response = response
        self.params_matcher = params_matcher
        self.data_matcher = data_matcher
        self.json_matcher = json_matcher
        self.headers_matcher = headers_matcher
        self.call_count = call_count
        self.max_calls = max_calls
        self.conditions = conditions or []

    def matches(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if this pattern matches the given HTTP request.

        This method evaluates all matching criteria defined for this pattern
        against the provided request details. All criteria must match for the
        pattern to be considered a match.

        Args:
            method: HTTP method of the request (GET, POST, etc.)
            url: Full URL of the request
            params: Query parameters included in the request
            data: Form data included in the request body
            json: JSON data included in the request body
            headers: HTTP headers included in the request

        Returns:
            True if the pattern matches all criteria, False otherwise
        """
        if self.method != method.upper():
            return False

        if not self.url_pattern.search(url):
            return False

        if self.max_calls is not None and self.call_count >= self.max_calls:
            return False

        if self.params_matcher and not self._dict_matches(self.params_matcher, params or {}):
            return False

        if self.data_matcher and not self._dict_matches(self.data_matcher, data or {}):
            return False

        if self.json_matcher and not self._dict_matches(self.json_matcher, json or {}):
            return False

        if self.headers_matcher and not self._dict_matches(self.headers_matcher, headers or {}):
            return False

        # Check additional conditions
        request_context = {
            'method': method,
            'url': url,
            'params': params or {},
            'data': data or {},
            'json': json or {},
            'headers': headers or {},
        }

        for condition in self.conditions:
            if not condition(request_context):
                return False

        return True

    def get_response(self, **kwargs: Any) -> MockResponse:
        """
        Get the response for this pattern and increment the call count.

        This method returns either the predefined MockResponse object or
        calls the response factory function to generate a dynamic response.
        It also increments the call count for this pattern, which is used
        to enforce the max_calls limit if one is set.

        Args:
            **kwargs: Additional keyword arguments to pass to the response
                      factory function if the response is callable

        Returns:
            A MockResponse object representing the HTTP response
        """
        self.call_count += 1
        if callable(self.response):
            return self.response(**kwargs)
        return self.response

    @staticmethod
    def _dict_matches(matcher: Dict[str, Any], actual: Dict[str, Any]) -> bool:
        """
        Check if the actual dictionary matches the matcher dictionary.

        This method implements a flexible dictionary matching algorithm that
        supports both exact value matching and callable predicates for values.
        For a match to succeed, all keys in the matcher dictionary must be
        present in the actual dictionary, and the corresponding values must
        either be equal or, if the matcher value is callable, the callable
        must return True when passed the actual value.

        Args:
            matcher: Dictionary with expected values or callable predicates
            actual: Dictionary with actual values to check against

        Returns:
            True if all matcher keys are in actual and values match or
            predicates return True, False otherwise
        """
        for key, value in matcher.items():
            if key not in actual:
                return False
            if callable(value):
                if not value(actual[key]):
                    return False
            elif value != actual[key]:
                return False
        return True

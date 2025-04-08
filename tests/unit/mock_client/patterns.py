"""
Response pattern matching for mock client.
"""

import re
from typing import Any, Callable, Dict, Optional, Union

from .response import MockResponse


class ResponsePattern:
    """Defines a pattern for matching requests and returning specific responses."""

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
    ):
        """
        Initialize a response pattern.

        Args:
            method: HTTP method (GET, POST, etc.)
            url_pattern: Regex pattern to match URLs
            response: Response to return or factory function
            params_matcher: Dict to match query parameters
            data_matcher: Dict to match form data
            json_matcher: Dict to match JSON data
            headers_matcher: Dict to match headers
            call_count: Current call count (usually starts at 0)
            max_calls: Maximum number of times this pattern can match
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
        Check if this pattern matches the given request.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            data: Form data
            json: JSON data
            headers: HTTP headers

        Returns:
            True if the pattern matches, False otherwise
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

        return True

    def get_response(self, **kwargs: Any) -> MockResponse:
        """
        Get the response for this pattern, incrementing the call count.

        Args:
            **kwargs: Additional arguments to pass to the response factory

        Returns:
            MockResponse instance
        """
        self.call_count += 1
        if callable(self.response):
            return self.response(**kwargs)
        return self.response

    @staticmethod
    def _dict_matches(matcher: Dict[str, Any], actual: Dict[str, Any]) -> bool:
        """
        Check if the actual dictionary matches the matcher dictionary.

        Args:
            matcher: Dictionary with expected values or callables
            actual: Dictionary with actual values

        Returns:
            True if all matcher keys are in actual and values match
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

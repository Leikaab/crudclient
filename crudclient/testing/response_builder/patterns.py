import re
from typing import Any, Callable, Dict, List, Optional, Union

from crudclient.testing.response_builder.response import MockResponse


class ResponsePattern:

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
            "method": method,
            "url": url,
            "params": params or {},
            "data": data or {},
            "json": json or {},
            "headers": headers or {},
        }

        for condition in self.conditions:
            if not condition(request_context):
                return False

        return True

    def get_response(self, **kwargs: Any) -> MockResponse:
        self.call_count += 1
        if callable(self.response):
            return self.response(**kwargs)
        return self.response

    @staticmethod
    def _dict_matches(matcher: Dict[str, Any], actual: Dict[str, Any]) -> bool:
        for key, value in matcher.items():
            if key not in actual:
                return False
            if callable(value):
                if not value(actual[key]):
                    return False
            elif value != actual[key]:
                return False
        return True

from typing import Any, Callable, Dict, Union

from crudclient.testing.response_builder.response import MockResponse


class SimpleMockClientCore:

    def __init__(self):
        self.response_patterns = []
        self.request_history = []
        self.default_response = MockResponse(status_code=404, json_data={"error": "No matching mock response configured"})

    def with_response_pattern(
        self, method: str, url_pattern: str, response: Union[MockResponse, Dict[str, Any], str, Callable[..., MockResponse]], **kwargs: Any
    ) -> "SimpleMockClientCore":
        # Convert dict/string responses to MockResponse
        if isinstance(response, dict):
            response = MockResponse(status_code=200, json_data=response)
        elif isinstance(response, str):
            response = MockResponse(status_code=200, text=response)

        self.response_patterns.append(
            {
                "method": method.upper(),
                "url_pattern": url_pattern,
                "response": response,
                "params": kwargs.get("params"),
                "data": kwargs.get("data"),
                "json": kwargs.get("json"),
                "headers": kwargs.get("headers"),
                "max_calls": kwargs.get("max_calls", float("inf")),
                "call_count": 0,
            }
        )
        return self

    def with_default_response(self, response: Union[MockResponse, Dict[str, Any], str]) -> "SimpleMockClientCore":
        if isinstance(response, dict):
            self.default_response = MockResponse(status_code=200, json_data=response)
        elif isinstance(response, str):
            self.default_response = MockResponse(status_code=200, text=response)
        else:
            self.default_response = response
        return self

import json
import re
from typing import Any, Dict, List, Optional, Union

from crudclient.testing.crud.request_record import RequestRecord
from crudclient.testing.response_builder.response import MockResponse
from crudclient.testing.simple_mock.core import SimpleMockClientCore


class SimpleMockClientRequestHandling(SimpleMockClientCore):

    def _request(self, method: str, url: str, **kwargs: Any) -> str:
        # Record the request
        record = self._create_request_record(method, url, kwargs)

        # Try to find a matching pattern
        for pattern in self.response_patterns:
            if self._is_basic_match(pattern, method, url):
                # Skip if max calls reached
                if pattern["call_count"] >= pattern["max_calls"]:
                    continue

                # Check detailed matchers
                if self._matches_request_details(pattern, kwargs):
                    # Pattern matched - prepare and return response
                    return self._handle_matching_pattern(pattern, record, kwargs)

        # No pattern matched, use default response
        return self._handle_default_response(record)

    def _create_request_record(self, method: str, url: str, kwargs: Dict[str, Any]) -> RequestRecord:
        record = RequestRecord(
            method=method, url=url, params=kwargs.get("params"), data=kwargs.get("data"), json=kwargs.get("json"), headers=kwargs.get("headers")
        )
        self.request_history.append(record)
        return record

    def _is_basic_match(self, pattern: Dict[str, Any], method: str, url: str) -> bool:
        return pattern["method"] == method.upper() and re.search(pattern["url_pattern"], url) is not None

    def _matches_request_details(self, pattern: Dict[str, Any], kwargs: Dict[str, Any]) -> bool:
        matchers = [
            self._check_params_match(pattern["params"], kwargs.get("params", {})),
            self._check_data_match(pattern["data"], kwargs.get("data", {})),
            self._check_json_match(pattern["json"], kwargs.get("json", {})),
            self._check_headers_match(pattern["headers"], kwargs.get("headers", {})),
        ]
        return all(matchers)

    def _check_params_match(self, pattern_params: Optional[Dict[str, Any]], request_params: Dict[str, Any]) -> bool:
        if pattern_params is None:
            return True

        for key, value in pattern_params.items():
            if key not in request_params or request_params[key] != value:
                return False
        return True

    def _check_data_match(self, pattern_data: Optional[Dict[str, Any]], request_data: Dict[str, Any]) -> bool:
        if pattern_data is None:
            return True

        for key, value in pattern_data.items():
            if key not in request_data or request_data[key] != value:
                return False
        return True

    def _check_json_match(self, pattern_json: Optional[Dict[str, Any]], request_json: Dict[str, Any]) -> bool:
        if pattern_json is None:
            return True

        for key, value in pattern_json.items():
            if key not in request_json or request_json[key] != value:
                return False
        return True

    def _check_headers_match(self, pattern_headers: Optional[Dict[str, Any]], request_headers: Dict[str, Any]) -> bool:
        if pattern_headers is None:
            return True

        for key, value in pattern_headers.items():
            if key not in request_headers or request_headers[key] != value:
                return False
        return True

    def _handle_matching_pattern(self, pattern: Dict[str, Any], record: RequestRecord, kwargs: Dict[str, Any]) -> str:
        # Increment call count
        pattern["call_count"] += 1

        # Get response object (handle callable responses)
        response_obj = pattern["response"]
        if callable(response_obj):
            response_obj = response_obj(**kwargs)

        # Convert to MockResponse if needed
        response_obj = self._ensure_mock_response(response_obj)

        # Store response in record
        record.response = response_obj

        # Return response as string
        return self._response_to_string(response_obj)

    def _ensure_mock_response(self, response_obj: Union[MockResponse, Dict[str, Any], List[Any], str, Any]) -> MockResponse:
        if isinstance(response_obj, MockResponse):
            return response_obj

        if isinstance(response_obj, dict):
            return MockResponse(status_code=200, json_data=response_obj)
        elif isinstance(response_obj, list):
            return MockResponse(status_code=200, text=json.dumps(response_obj))
        elif isinstance(response_obj, str):
            return MockResponse(status_code=200, text=response_obj)
        else:
            return MockResponse(status_code=200, text=str(response_obj))

    def _handle_default_response(self, record: RequestRecord) -> str:
        record.response = self.default_response
        return self._response_to_string(self.default_response)

    def _response_to_string(self, response: MockResponse) -> str:
        if response.json_data is not None:
            return json.dumps(response.json_data)
        return response.text or ""

    def get(self, url: str, **kwargs: Any) -> str:
        return self._request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> str:
        return self._request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> str:
        return self._request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> str:
        return self._request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> str:
        return self._request("PATCH", url, **kwargs)

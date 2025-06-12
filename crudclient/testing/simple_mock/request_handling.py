"""
Simple mock client request handling methods for testing.

This module provides request handling functionality for the SimpleMockClient,
implementing methods to process HTTP requests and return appropriate mock responses
based on configured patterns.
"""

import json
import re
from typing import Any, Dict, List, Optional, Union

from crudclient.testing.crud.request_record import RequestRecord
from crudclient.testing.response_builder.response import MockResponse
from crudclient.testing.simple_mock.core import SimpleMockClientCore


class SimpleMockClientRequestHandling(SimpleMockClientCore):
    """Request handling methods for the simple mock client.

    This class extends SimpleMockClientCore to provide methods for handling
    different types of HTTP requests (GET, POST, PUT, DELETE, PATCH). It
    processes incoming requests, matches them against configured patterns,
    and returns appropriate mock responses.
    """

    def _request(self, method: str, url: str, **kwargs: Any) -> str:
        """Process a request and return a mock response.

        This internal method handles the core request processing logic:
            1. Records the request details
            2. Finds a matching response pattern
            3. Applies any matching criteria (params, data, json, headers)
            4. Returns the appropriate response

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            url: Request URL
            **kwargs: Additional request parameters (params, data, json, headers)

        Returns:
            String representation of the response (JSON or text)
        """
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
        """Create a record of the request for history tracking.

        This method creates a RequestRecord object from the request details and
        adds it to the request history for later verification.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            url: Request URL
            kwargs: Additional request parameters (params, data, json, headers)

        Returns:
            A RequestRecord object containing the request details
        """
        record = RequestRecord(
            method=method, url=url, params=kwargs.get("params"), data=kwargs.get("data"), json=kwargs.get("json"), headers=kwargs.get("headers")
        )
        self.request_history.append(record)
        return record

    def _is_basic_match(self, pattern: Dict[str, Any], method: str, url: str) -> bool:
        """Check if a request matches the basic pattern criteria.

        This method checks if the request method and URL match the pattern.

        Args:
            pattern: Response pattern configuration
            method: HTTP method of the request
            url: URL of the request

        Returns:
            True if the request matches the basic pattern criteria, False otherwise
        """
        return pattern["method"] == method.upper() and re.search(pattern["url_pattern"], url) is not None

    def _matches_request_details(self, pattern: Dict[str, Any], kwargs: Dict[str, Any]) -> bool:
        """Check if a request matches the detailed pattern criteria.

        This method checks if the request parameters, data, JSON, and headers
        match the pattern.

        Args:
            pattern: Response pattern configuration
            kwargs: Request parameters

        Returns:
            True if the request matches all detailed pattern criteria, False otherwise
        """
        matchers = [
            self._check_params_match(pattern["params"], kwargs.get("params", {})),
            self._check_data_match(pattern["data"], kwargs.get("data", {})),
            self._check_json_match(pattern["json"], kwargs.get("json", {})),
            self._check_headers_match(pattern["headers"], kwargs.get("headers", {})),
        ]
        return all(matchers)

    def _check_params_match(self, pattern_params: Optional[Dict[str, Any]], request_params: Dict[str, Any]) -> bool:
        """Check if request parameters match the pattern parameters.

        Args:
            pattern_params: Parameters specified in the pattern
            request_params: Parameters from the request

        Returns:
            True if the parameters match or pattern_params is None, False otherwise
        """
        if pattern_params is None:
            return True

        for key, value in pattern_params.items():
            if key not in request_params or request_params[key] != value:
                return False
        return True

    def _check_data_match(self, pattern_data: Optional[Dict[str, Any]], request_data: Dict[str, Any]) -> bool:
        """Check if request form data matches the pattern data.

        Args:
            pattern_data: Form data specified in the pattern
            request_data: Form data from the request

        Returns:
            True if the data matches or pattern_data is None, False otherwise
        """
        if pattern_data is None:
            return True

        for key, value in pattern_data.items():
            if key not in request_data or request_data[key] != value:
                return False
        return True

    def _check_json_match(self, pattern_json: Optional[Dict[str, Any]], request_json: Dict[str, Any]) -> bool:
        """Check if request JSON data matches the pattern JSON.

        Args:
            pattern_json: JSON data specified in the pattern
            request_json: JSON data from the request

        Returns:
            True if the JSON data matches or pattern_json is None, False otherwise
        """
        if pattern_json is None:
            return True

        for key, value in pattern_json.items():
            if key not in request_json or request_json[key] != value:
                return False
        return True

    def _check_headers_match(self, pattern_headers: Optional[Dict[str, Any]], request_headers: Dict[str, Any]) -> bool:
        """Check if request headers match the pattern headers.

        Args:
            pattern_headers: Headers specified in the pattern
            request_headers: Headers from the request

        Returns:
            True if the headers match or pattern_headers is None, False otherwise
        """
        if pattern_headers is None:
            return True

        for key, value in pattern_headers.items():
            if key not in request_headers or request_headers[key] != value:
                return False
        return True

    def _handle_matching_pattern(self, pattern: Dict[str, Any], record: RequestRecord, kwargs: Dict[str, Any]) -> str:
        """Handle a request that matches a pattern.

        This method:
            1. Increments the pattern call count
            2. Gets the response object (handling callable responses)
            3. Converts the response to a MockResponse if needed
            4. Stores the response in the request record
            5. Returns the response as a string

        Args:
            pattern: The matching response pattern
            record: The request record
            kwargs: The request parameters

        Returns:
            String representation of the response
        """
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
        """Ensure that a response object is a MockResponse.

        This method converts various response types to MockResponse objects:
            - Dict -> MockResponse with status_code=200 and json_data=dict
            - List -> MockResponse with status_code=200 and text=json.dumps(list)
            - Str -> MockResponse with status_code=200 and text=str
            - Other -> MockResponse with status_code=200 and text=str(obj)

        Args:
            response_obj: The response object to convert

        Returns:
            A MockResponse object
        """
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
        """Handle a request that doesn't match any pattern.

        This method:
            1. Sets the default response in the request record
            2. Returns the default response as a string

        Args:
            record: The request record

        Returns:
            String representation of the default response
        """
        record.response = self.default_response
        return self._response_to_string(self.default_response)

    def _response_to_string(self, response: MockResponse) -> str:
        """Convert a MockResponse to a string.

        This method:
            - Returns JSON.dumps(response.json_data) if json_data is not None
            - Otherwise returns response.text or empty string if text is None

        Args:
            response: The MockResponse to convert

        Returns:
            String representation of the response
        """
        if response.json_data is not None:
            return json.dumps(response.json_data)

        text = response.text
        if isinstance(text, bytes):
            text = text.decode()
        return text or ""

    def get(self, url: str, **kwargs: Any) -> str:
        """Perform a GET request.

        Args:
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            String representation of the response
        """
        return self._request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> str:
        """Perform a POST request.

        Args:
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            String representation of the response
        """
        return self._request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> str:
        """Perform a PUT request.

        Args:
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            String representation of the response
        """
        return self._request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> str:
        """Perform a DELETE request.

        Args:
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            String representation of the response
        """
        return self._request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> str:
        """Perform a PATCH request.

        Args:
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            String representation of the response
        """
        return self._request("PATCH", url, **kwargs)

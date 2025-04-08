"""
Verification helpers for mock client.

This module provides utilities for verifying API interactions.
"""

from typing import Any, Callable, Dict, List, Optional, Pattern, Union
import re
import json
from datetime import datetime

from .request_record import RequestRecord


class RequestVerifier:
    """Utilities for verifying API requests."""

    @staticmethod
    def verify_request_count(
        request_history: List[RequestRecord],
        count: int,
        method: Optional[str] = None,
        url_pattern: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Verify that a specific number of matching requests were made.

        Args:
            request_history: List of request records
            count: Expected number of matching requests
            method: HTTP method to match
            url_pattern: URL pattern to match
            params: Query parameters to match
            data: Form data to match
            json_data: JSON data to match
            headers: Headers to match

        Raises:
            AssertionError: If the number of matching requests doesn't match the expected count
        """
        matching_requests = RequestVerifier.filter_requests(
            request_history,
            method=method,
            url_pattern=url_pattern,
            params=params,
            data=data,
            json_data=json_data,
            headers=headers
        )

        actual_count = len(matching_requests)
        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. "
            f"Filters: method={method}, url_pattern={url_pattern}, "
            f"params={params}, data={data}, json={json_data}, headers={headers}"
        )

    @staticmethod
    def verify_request_sequence(
        request_history: List[RequestRecord],
        sequence: List[Dict[str, Any]],
        strict: bool = False,
        allow_extra_requests: bool = True,
    ) -> None:
        """
        Verify that requests were made in a specific sequence.

        Args:
            request_history: List of request records
            sequence: List of request matchers in expected order
            strict: Whether to require exact sequence matching
            allow_extra_requests: Whether to allow extra requests between matched requests

        Raises:
            AssertionError: If the request sequence doesn't match the expected sequence
        """
        if not sequence:
            return

        if strict and len(sequence) != len(request_history):
            raise AssertionError(
                f"Expected {len(sequence)} requests, but found {len(request_history)}"
            )

        # Find subsequence match
        history_idx = 0
        sequence_idx = 0
        matched_indices = []

        while history_idx < len(request_history) and sequence_idx < len(sequence):
            request = request_history[history_idx]
            matcher = sequence[sequence_idx]

            if RequestVerifier._request_matches(request, matcher):
                matched_indices.append(history_idx)
                sequence_idx += 1
                if not allow_extra_requests:
                    history_idx += 1
                    continue

            history_idx += 1

        if sequence_idx < len(sequence):
            # Create a detailed error message
            matched_count = sequence_idx
            unmatched_patterns = sequence[sequence_idx:]

            error_msg = (
                f"Request sequence not found. Matched {matched_count} of {len(sequence)} expected requests.\n"
                f"Unmatched patterns: {unmatched_patterns}\n"
                f"Request history: {[str(r) for r in request_history]}"
            )

            raise AssertionError(error_msg)

        # Check for strict ordering if required
        if strict and matched_indices != list(range(len(matched_indices))):
            raise AssertionError(
                f"Requests were not in the expected strict order. "
                f"Matched indices: {matched_indices}"
            )

    @staticmethod
    def verify_request_params(
        request_history: List[RequestRecord],
        params: Dict[str, Any],
        method: Optional[str] = None,
        url_pattern: Optional[str] = None,
        match_all: bool = False,
    ) -> None:
        """
        Verify that requests were made with specific parameters.

        Args:
            request_history: List of request records
            params: Parameters to match
            method: HTTP method to match
            url_pattern: URL pattern to match
            match_all: Whether all matching requests must have the parameters

        Raises:
            AssertionError: If the request parameters don't match the expected parameters
        """
        matching_requests = RequestVerifier.filter_requests(
            request_history,
            method=method,
            url_pattern=url_pattern
        )

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

    @staticmethod
    def verify_request_json(
        request_history: List[RequestRecord],
        json_data: Dict[str, Any],
        method: Optional[str] = None,
        url_pattern: Optional[str] = None,
        partial_match: bool = False,
    ) -> None:
        """
        Verify that requests were made with specific JSON data.

        Args:
            request_history: List of request records
            json_data: JSON data to match
            method: HTTP method to match
            url_pattern: URL pattern to match
            partial_match: Whether to allow partial matching of JSON data

        Raises:
            AssertionError: If the request JSON data doesn't match the expected data
        """
        matching_requests = RequestVerifier.filter_requests(
            request_history,
            method=method,
            url_pattern=url_pattern
        )

        if not matching_requests:
            raise AssertionError(
                f"No matching requests found. Filters: method={method}, url_pattern={url_pattern}"
            )

        for i, request in enumerate(matching_requests):
            request_json = request.json or {}

            if partial_match:
                # Check if all expected keys/values are in the request JSON
                match = True
                for key, value in json_data.items():
                    if key not in request_json or request_json[key] != value:
                        match = False
                        break

                if match:
                    return  # Found a match
            else:
                # Check for exact match
                if request_json == json_data:
                    return  # Found a match

        # No match found
        raise AssertionError(
            f"No request matched the JSON data {json_data}. "
            f"Filters: method={method}, url_pattern={url_pattern}, partial_match={partial_match}"
        )

    @staticmethod
    def verify_request_headers(
        request_history: List[RequestRecord],
        headers: Dict[str, Any],
        method: Optional[str] = None,
        url_pattern: Optional[str] = None,
        match_all: bool = False,
    ) -> None:
        """
        Verify that requests were made with specific headers.

        Args:
            request_history: List of request records
            headers: Headers to match
            method: HTTP method to match
            url_pattern: URL pattern to match
            match_all: Whether all matching requests must have the headers

        Raises:
            AssertionError: If the request headers don't match the expected headers
        """
        matching_requests = RequestVerifier.filter_requests(
            request_history,
            method=method,
            url_pattern=url_pattern
        )

        if not matching_requests:
            raise AssertionError(
                f"No matching requests found. Filters: method={method}, url_pattern={url_pattern}"
            )

        if match_all:
            for i, request in enumerate(matching_requests):
                request_headers = request.headers or {}
                for key, value in headers.items():
                    if key not in request_headers:
                        raise AssertionError(
                            f"Request {i} missing header '{key}'. "
                            f"Method: {request.method}, URL: {request.url}"
                        )
                    if callable(value):
                        if not value(request_headers[key]):
                            raise AssertionError(
                                f"Request {i} header '{key}' failed validation. "
                                f"Method: {request.method}, URL: {request.url}"
                            )
                    elif request_headers[key] != value:
                        raise AssertionError(
                            f"Request {i} header '{key}' has value '{request_headers[key]}', "
                            f"expected '{value}'. Method: {request.method}, URL: {request.url}"
                        )
        else:
            # At least one request must match all headers
            for i, request in enumerate(matching_requests):
                all_match = True
                request_headers = request.headers or {}
                for key, value in headers.items():
                    if key not in request_headers:
                        all_match = False
                        break
                    if callable(value):
                        if not value(request_headers[key]):
                            all_match = False
                            break
                    elif request_headers[key] != value:
                        all_match = False
                        break

                if all_match:
                    return  # Found a match

            raise AssertionError(
                f"No request matched all headers {headers}. "
                f"Filters: method={method}, url_pattern={url_pattern}"
            )

    @staticmethod
    def verify_auth_usage(
        request_history: List[RequestRecord],
        auth_header_name: str = "Authorization",
        auth_header_pattern: Optional[str] = None,
    ) -> None:
        """
        Verify that requests were made with proper authentication.

        Args:
            request_history: List of request records
            auth_header_name: Name of the authentication header
            auth_header_pattern: Pattern to match in the authentication header

        Raises:
            AssertionError: If the requests don't have proper authentication
        """
        if not request_history:
            raise AssertionError("No requests were made")

        for i, request in enumerate(request_history):
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

    @staticmethod
    def verify_request_timing(
        request_history: List[RequestRecord],
        min_interval_seconds: Optional[float] = None,
        max_interval_seconds: Optional[float] = None,
        method: Optional[str] = None,
        url_pattern: Optional[str] = None,
    ) -> None:
        """
        Verify the timing between requests.

        Args:
            request_history: List of request records
            min_interval_seconds: Minimum interval between requests
            max_interval_seconds: Maximum interval between requests
            method: HTTP method to match
            url_pattern: URL pattern to match

        Raises:
            AssertionError: If the request timing doesn't meet the criteria
        """
        matching_requests = RequestVerifier.filter_requests(
            request_history,
            method=method,
            url_pattern=url_pattern
        )

        if len(matching_requests) < 2:
            return  # Need at least 2 requests to check timing

        # Sort by timestamp
        sorted_requests = sorted(matching_requests, key=lambda r: r.timestamp)

        for i in range(1, len(sorted_requests)):
            prev_request = sorted_requests[i - 1]
            curr_request = sorted_requests[i]
            interval = curr_request.timestamp - prev_request.timestamp

            if min_interval_seconds is not None and interval < min_interval_seconds:
                raise AssertionError(
                    f"Interval between requests {i - 1} and {i} was {interval:.2f} seconds, "
                    f"which is less than the minimum of {min_interval_seconds} seconds."
                )

            if max_interval_seconds is not None and interval > max_interval_seconds:
                raise AssertionError(
                    f"Interval between requests {i - 1} and {i} was {interval:.2f} seconds, "
                    f"which is more than the maximum of {max_interval_seconds} seconds."
                )

    @staticmethod
    def filter_requests(
        request_history: List[RequestRecord],
        method: Optional[str] = None,
        url_pattern: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> List[RequestRecord]:
        """
        Filter request history by various criteria.

        Args:
            request_history: List of request records
            method: HTTP method to match
            url_pattern: URL pattern to match
            params: Query parameters to match
            data: Form data to match
            json_data: JSON data to match
            headers: Headers to match

        Returns:
            Filtered list of request records
        """
        result = request_history

        if method:
            result = [r for r in result if r.method == method.upper()]

        if url_pattern:
            pattern = re.compile(url_pattern)
            result = [r for r in result if pattern.search(r.url)]

        if params:
            result = [r for r in result if RequestVerifier._dict_matches(params, r.params or {})]

        if data:
            result = [r for r in result if RequestVerifier._dict_matches(data, r.data or {})]

        if json_data:
            result = [r for r in result if RequestVerifier._dict_matches(json_data, r.json or {})]

        if headers:
            result = [r for r in result if RequestVerifier._dict_matches(headers, r.headers or {})]

        return result

    @staticmethod
    def _request_matches(
        request: RequestRecord,
        matcher: Dict[str, Any],
    ) -> bool:
        """
        Check if a request matches a matcher.

        Args:
            request: Request record
            matcher: Matcher dictionary

        Returns:
            True if the request matches, False otherwise
        """
        # Check method
        if 'method' in matcher and request.method != matcher['method'].upper():
            return False

        # Check URL pattern
        if 'url_pattern' in matcher and not re.search(matcher['url_pattern'], request.url):
            return False

        # Check params
        if 'params' in matcher and matcher['params'] is not None:
            if not RequestVerifier._dict_matches(matcher['params'], request.params or {}):
                return False

        # Check data
        if 'data' in matcher and matcher['data'] is not None:
            if not RequestVerifier._dict_matches(matcher['data'], request.data or {}):
                return False

        # Check JSON
        if 'json' in matcher and matcher['json'] is not None:
            if not RequestVerifier._dict_matches(matcher['json'], request.json or {}):
                return False

        # Check headers
        if 'headers' in matcher and matcher['headers'] is not None:
            if not RequestVerifier._dict_matches(matcher['headers'], request.headers or {}):
                return False

        return True

    @staticmethod
    def _dict_matches(
        matcher: Dict[str, Any],
        actual: Dict[str, Any],
    ) -> bool:
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
            elif isinstance(value, Pattern):
                if not value.search(str(actual[key])):
                    return False
            elif value != actual[key]:
                return False

        return True


class ResponseVerifier:
    """Utilities for verifying API responses."""

    @staticmethod
    def verify_response_status(
        response: Any,
        expected_status: int,
    ) -> None:
        """
        Verify that a response has the expected status code.

        Args:
            response: Response object
            expected_status: Expected status code

        Raises:
            AssertionError: If the response status doesn't match the expected status
        """
        status_code = getattr(response, 'status_code', None)
        if status_code is None:
            # Try to parse JSON string
            try:
                if isinstance(response, str):
                    data = json.loads(response)
                    if isinstance(data, dict) and 'status_code' in data:
                        status_code = data['status_code']
            except (json.JSONDecodeError, TypeError):
                pass

        assert status_code == expected_status, (
            f"Expected status code {expected_status}, but got {status_code}"
        )

    @staticmethod
    def verify_response_json(
        response: Any,
        expected_data: Dict[str, Any],
        partial_match: bool = False,
    ) -> None:
        """
        Verify that a response has the expected JSON data.

        Args:
            response: Response object
            expected_data: Expected JSON data
            partial_match: Whether to allow partial matching of JSON data

        Raises:
            AssertionError: If the response JSON doesn't match the expected data
        """
        # Extract JSON data from response
        json_data = None
        if hasattr(response, 'json') and callable(response.json):
            try:
                json_data = response.json()
            except Exception:
                pass
        elif hasattr(response, '_json_data'):
            json_data = response._json_data
        elif isinstance(response, str):
            try:
                json_data = json.loads(response)
            except json.JSONDecodeError:
                pass
        elif isinstance(response, dict):
            json_data = response

        assert json_data is not None, "Could not extract JSON data from response"

        if partial_match:
            # Check if all expected keys/values are in the response JSON
            for key, value in expected_data.items():
                assert isinstance(json_data, dict) and key in json_data, f"Expected key '{key}' not found in response JSON"
                if isinstance(value, dict) and isinstance(json_data.get(key), dict):
                    # Recursively check nested dictionaries
                    ResponseVerifier.verify_response_json(json_data.get(key), value, partial_match=True)
                else:
                    assert json_data.get(key) == value, (
                        f"Expected value '{value}' for key '{key}', but got '{json_data.get(key)}'"
                    )
        else:
            # Check for exact match
            assert json_data == expected_data, (
                f"Expected JSON data {expected_data}, but got {json_data}"
            )

    @staticmethod
    def verify_response_headers(
        response: Any,
        expected_headers: Dict[str, Any],
        case_insensitive: bool = True,
    ) -> None:
        """
        Verify that a response has the expected headers.

        Args:
            response: Response object
            expected_headers: Expected headers
            case_insensitive: Whether to ignore case in header names

        Raises:
            AssertionError: If the response headers don't match the expected headers
        """
        # Extract headers from response
        headers = None
        if hasattr(response, 'headers'):
            headers = response.headers
        elif isinstance(response, dict) and 'headers' in response:
            headers = response['headers']

        assert headers is not None, "Could not extract headers from response"

        # Convert to dict if it's not already
        if not isinstance(headers, dict):
            headers = dict(headers)

        # Case-insensitive comparison if needed
        if case_insensitive:
            headers = {k.lower(): v for k, v in headers.items()}
            expected_headers = {k.lower(): v for k, v in expected_headers.items()}

        for key, value in expected_headers.items():
            assert key in headers, f"Expected header '{key}' not found in response headers"

            if callable(value):
                assert value(headers[key]), (
                    f"Header '{key}' with value '{headers[key]}' failed validation"
                )
            elif isinstance(value, Pattern):
                assert value.search(str(headers[key])), (
                    f"Header '{key}' with value '{headers[key]}' does not match pattern '{value.pattern}'"
                )
            else:
                assert headers[key] == value, (
                    f"Expected header '{key}' to have value '{value}', but got '{headers[key]}'"
                )

    @staticmethod
    def verify_response_time(
        response: Any,
        max_time_ms: Optional[float] = None,
    ) -> None:
        """
        Verify that a response was received within the expected time.

        Args:
            response: Response object
            max_time_ms: Maximum acceptable response time in milliseconds

        Raises:
            AssertionError: If the response time exceeds the maximum
        """
        if max_time_ms is None:
            return

        # Extract elapsed time from response
        elapsed_ms = None
        if hasattr(response, 'elapsed'):
            elapsed_ms = response.elapsed.total_seconds() * 1000
        elif hasattr(response, '_elapsed_ms'):
            elapsed_ms = response._elapsed_ms
        elif isinstance(response, dict) and 'elapsed_ms' in response:
            elapsed_ms = response['elapsed_ms']

        if elapsed_ms is not None:
            assert elapsed_ms <= max_time_ms, (
                f"Response time {elapsed_ms:.2f}ms exceeds maximum of {max_time_ms}ms"
            )

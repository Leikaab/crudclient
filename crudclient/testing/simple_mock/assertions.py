"""
Simple mock client assertion methods for testing.

This module provides assertion methods for the SimpleMockClient, allowing
verification of request patterns, sequences, and parameters in tests.
"""

import re
from typing import Any, Dict, List, Optional

from crudclient.testing.crud.request_record import RequestRecord
from crudclient.testing.simple_mock.request_handling import (
    SimpleMockClientRequestHandling,
)


class SimpleMockClientAssertions(SimpleMockClientRequestHandling):
    """Assertion methods for the simple mock client.

    This class extends SimpleMockClientRequestHandling to provide methods for
    verifying that requests were made with expected patterns, sequences, and
    parameters. These methods are useful for testing that code interacts with
    APIs in the expected way.
    """

    def assert_request_count(self, count: int, method: Optional[str] = None, url_pattern: Optional[str] = None) -> None:
        """Assert that a specific number of matching requests were made.

        This method verifies that the number of requests matching the specified
        criteria (method and/or URL pattern) matches the expected count.

        Args:
            count: Expected number of matching requests
            method: Optional HTTP method to filter by (e.g., GET, POST)
            url_pattern: Optional regex pattern to match request URLs

        Raises:
            AssertionError: If the actual count doesn't match the expected count
        """
        matching_requests = self._filter_requests(method, url_pattern)
        actual_count = len(matching_requests)

        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. " f"Filters: method={method}, url_pattern={url_pattern}"
        )

    def assert_request_sequence(self, sequence: List[Dict[str, Any]], strict: bool = False) -> None:
        """Assert that requests were made in a specific sequence.

        This method verifies that requests matching the specified sequence
        were made in the expected order. In non-strict mode, it checks for
        the sequence as a subsequence of all requests. In strict mode, it
        requires an exact match of the entire request history.

        Args:
            sequence: List of request matchers, each containing 'method' and/or 'url_pattern'
            strict: If True, requires exact match of entire request history

        Raises:
            AssertionError: If the sequence wasn't found in the request history
        """
        if not sequence:
            return

        if strict and len(sequence) != len(self.request_history):
            raise AssertionError(f"Expected {len(sequence)} requests, but found {len(self.request_history)}")

        # Find subsequence match
        history_idx = 0
        sequence_idx = 0

        while history_idx < len(self.request_history) and sequence_idx < len(sequence):
            request = self.request_history[history_idx]
            matcher = sequence[sequence_idx]

            method_match = True
            if "method" in matcher:
                method_match = request.method == matcher["method"].upper()

            url_match = True
            if "url_pattern" in matcher:
                url_match = bool(re.search(matcher["url_pattern"], request.url))

            if method_match and url_match:
                sequence_idx += 1

            history_idx += 1

        if sequence_idx < len(sequence):
            raise AssertionError(f"Request sequence not found. Matched {sequence_idx} of {len(sequence)} expected requests.")

    def assert_request_params(
        self, params: Dict[str, Any], method: Optional[str] = None, url_pattern: Optional[str] = None, match_all: bool = False
    ) -> None:
        """Assert that requests were made with specific parameters.

        This method verifies that requests matching the specified criteria
        (method and/or URL pattern) were made with the expected parameters.

        Args:
            params: Dictionary of expected parameter names and values
            method: Optional HTTP method to filter by (e.g., GET, POST)
            url_pattern: Optional regex pattern to match request URLs
            match_all: If True, all matching requests must have the parameters;
                      if False, at least one matching request must have them

        Raises:
            AssertionError: If no matching requests are found or if the
                           parameter requirements aren't met
        """
        matching_requests = self._filter_requests(method, url_pattern)

        if not matching_requests:
            raise AssertionError(f"No matching requests found. Filters: method={method}, url_pattern={url_pattern}")

        if match_all:
            for i, request in enumerate(matching_requests):
                request_params = request.params or {}
                for key, value in params.items():
                    if key not in request_params:
                        raise AssertionError(f"Request {i} missing parameter '{key}'. " f"Method: {request.method}, URL: {request.url}")
                    if callable(value):
                        if not value(request_params[key]):
                            raise AssertionError(f"Request {i} parameter '{key}' failed validation. " f"Method: {request.method}, URL: {request.url}")
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

            raise AssertionError(f"No request matched all parameters {params}. " f"Filters: method={method}, url_pattern={url_pattern}")

    def _filter_requests(self, method: Optional[str] = None, url_pattern: Optional[str] = None) -> List[RequestRecord]:
        """Filter request history by method and URL pattern.

        This internal method filters the request history based on the
        specified criteria, returning only the matching requests.

        Args:
            method: Optional HTTP method to filter by (e.g., GET, POST)
            url_pattern: Optional regex pattern to match request URLs

        Returns:
            List of RequestRecord objects matching the criteria
        """
        result = self.request_history

        if method:
            result = [r for r in result if r.method == method.upper()]

        if url_pattern:
            pattern = re.compile(url_pattern)
            result = [r for r in result if pattern.search(r.url)]

        return result

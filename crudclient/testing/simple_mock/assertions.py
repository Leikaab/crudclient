import re
from typing import Any, Dict, List, Optional

from crudclient.testing.crud.request_record import RequestRecord
from crudclient.testing.simple_mock.request_handling import (
    SimpleMockClientRequestHandling,
)


class SimpleMockClientAssertions(SimpleMockClientRequestHandling):

    def assert_request_count(self, count: int, method: Optional[str] = None, url_pattern: Optional[str] = None) -> None:
        matching_requests = self._filter_requests(method, url_pattern)
        actual_count = len(matching_requests)

        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. " f"Filters: method={method}, url_pattern={url_pattern}"
        )

    def assert_request_sequence(self, sequence: List[Dict[str, Any]], strict: bool = False) -> None:
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
        result = self.request_history

        if method:
            result = [r for r in result if r.method == method.upper()]

        if url_pattern:
            pattern = re.compile(url_pattern)
            result = [r for r in result if pattern.search(r.url)]

        return result

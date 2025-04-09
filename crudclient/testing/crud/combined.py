"""
Combined mock implementation for all CRUD operations.

This module provides a combined mock that integrates all CRUD operation mocks
into a single class for convenience.
"""

import re
from typing import Any, Dict, List, Optional, Union

from .create import CreateMock
from .read import ReadMock
from .update import UpdateMock
from .delete import DeleteMock


class CombinedCrudMock:
    """
    Combined mock for all CRUD operations.

    This class integrates all CRUD operation mocks (Create, Read, Update, Delete)
    into a single class for convenience. It delegates method calls to the appropriate
    mock based on the HTTP method.
    """

    def __init__(self):
        """
        Initialize the combined CRUD mock.

        Creates instances of all CRUD operation mocks and sets up request history tracking.
        """
        self.create_mock = CreateMock()
        self.read_mock = ReadMock()
        self.update_mock = UpdateMock()
        self.delete_mock = DeleteMock()
        self.request_history = []
        self._parent_id_handling = True

    def get(self, url: str, **kwargs: Any) -> Any:
        """
        Handle GET requests.

        Delegates to the ReadMock and updates the request history.

        Args:
            url: Request URL
            **kwargs: Request parameters

        Returns:
            Response data from the ReadMock
        """
        result = self.read_mock.get(url, **kwargs)
        self.request_history.extend(self.read_mock.request_history)
        return result

    def post(self, url: str, **kwargs: Any) -> Any:
        """
        Handle POST requests.

        Delegates to the CreateMock and updates the request history.

        Args:
            url: Request URL
            **kwargs: Request parameters

        Returns:
            Response data from the CreateMock
        """
        result = self.create_mock.post(url, **kwargs)
        self.request_history.extend(self.create_mock.request_history)
        return result

    def put(self, url: str, **kwargs: Any) -> Any:
        """
        Handle PUT requests.

        Delegates to the UpdateMock and updates the request history.

        Args:
            url: Request URL
            **kwargs: Request parameters

        Returns:
            Response data from the UpdateMock
        """
        result = self.update_mock.put(url, **kwargs)
        self.request_history.extend(self.update_mock.request_history)
        return result

    def patch(self, url: str, **kwargs: Any) -> Any:
        """
        Handle PATCH requests.

        Delegates to the UpdateMock and updates the request history.

        Args:
            url: Request URL
            **kwargs: Request parameters

        Returns:
            Response data from the UpdateMock
        """
        result = self.update_mock.patch(url, **kwargs)
        self.request_history.extend(self.update_mock.request_history)
        return result

    def delete(self, url: str, **kwargs: Any) -> Any:
        """
        Handle DELETE requests.

        Delegates to the DeleteMock and updates the request history.

        Args:
            url: Request URL
            **kwargs: Request parameters

        Returns:
            Response data from the DeleteMock
        """
        result = self.delete_mock.delete(url, **kwargs)
        self.request_history.extend(self.delete_mock.request_history)
        return result

    def with_parent_id_handling(self, enabled: bool = True) -> 'CombinedCrudMock':
        """
        Enable or disable parent_id handling for all CRUD mocks.

        Args:
            enabled: Whether to enable parent_id handling

        Returns:
            Self for method chaining
        """
        self._parent_id_handling = enabled
        self.create_mock.with_parent_id_handling(enabled)
        self.read_mock.with_parent_id_handling(enabled)
        self.update_mock.with_parent_id_handling(enabled)
        self.delete_mock.with_parent_id_handling(enabled)
        return self

    def assert_request_count(self, count: int, url_pattern: Optional[str] = None) -> None:
        """
        Assert that a specific number of matching requests were made.

        Args:
            count: Expected number of requests
            url_pattern: Optional URL pattern to filter requests

        Raises:
            AssertionError: If the actual count doesn't match the expected count
        """
        matching_requests = self.request_history
        if url_pattern:
            pattern = re.compile(url_pattern)
            matching_requests = [r for r in matching_requests if pattern.search(r.url)]

        actual_count = len(matching_requests)
        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. "
            f"Filter: url_pattern={url_pattern}"
        )

    def assert_request_sequence(
        self,
        sequence: List[Dict[str, Any]],
        strict: bool = False
    ) -> None:
        """
        Assert that requests were made in a specific sequence.

        Args:
            sequence: List of request matchers, each containing criteria like 'url_pattern'
            strict: If True, the number of requests must match exactly

        Raises:
            AssertionError: If the sequence doesn't match
        """
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

    def assert_crud_operation_sequence(
        self,
        operations: List[str],
        resource_id: Optional[str] = None,
        url_pattern: Optional[str] = None
    ) -> None:
        """
        Assert that CRUD operations were performed in a specific sequence.

        Args:
            operations: List of operation names ('create', 'read', 'update', 'partial_update', 'delete')
            resource_id: Optional resource ID to include in URL patterns
            url_pattern: Optional base URL pattern to match

        Raises:
            AssertionError: If the sequence doesn't match
        """
        # Map operation names to HTTP methods
        method_map = {
            "create": "POST",
            "read": "GET",
            "update": "PUT",
            "partial_update": "PATCH",
            "delete": "DELETE"
        }

        # Build sequence matchers
        sequence = []
        for op in operations:
            matcher = {'method': method_map.get(op, op.upper())}
            if url_pattern:
                matcher['url_pattern'] = url_pattern
            if resource_id and op != "create":
                # For non-create operations, include resource_id in the URL pattern
                if 'url_pattern' in matcher:
                    matcher['url_pattern'] = f"{matcher['url_pattern']}.*{resource_id}"
                else:
                    matcher['url_pattern'] = f".*{resource_id}"
            sequence.append(matcher)

        self.assert_request_sequence(sequence)

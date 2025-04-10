"""
Combined CRUD mock for testing.

This module provides a combined mock for all CRUD operations (Create, Read, Update, Delete),
allowing for comprehensive testing of API clients with a single mock object.
"""

import re
from typing import Any, Dict, List, Optional

from .create import CreateMock
from .delete import DeleteMock
from .read import ReadMock
from .update import UpdateMock


class CombinedCrudMock:
    """
    Combined mock for all CRUD operations.

    This class combines the functionality of CreateMock, ReadMock, UpdateMock, and DeleteMock
    into a single mock object, allowing for comprehensive testing of API clients that use
    multiple CRUD operations. It maintains a unified request history and provides methods
    for asserting request patterns across all operation types.
    """

    def __init__(self) -> None:
        """
        Initialize the combined CRUD mock.

        Creates instances of all individual CRUD mocks and sets up a unified request history.
        """
        self.create_mock: CreateMock
        self.read_mock: ReadMock
        self.update_mock: UpdateMock
        self.delete_mock: DeleteMock
        self.request_history: List[Any]
        self._parent_id_handling: bool
        ...

    def get(self, url: str, **kwargs: Any) -> Any:
        """
        Handle GET requests.

        Delegates to the read_mock and adds the request to the unified history.

        Args:
            url: The URL to request
            **kwargs: Additional request parameters

        Returns:
            The mock response data
        """
        ...

    def post(self, url: str, **kwargs: Any) -> Any:
        """
        Handle POST requests.

        Delegates to the create_mock and adds the request to the unified history.

        Args:
            url: The URL to request
            **kwargs: Additional request parameters

        Returns:
            The mock response data
        """
        ...

    def put(self, url: str, **kwargs: Any) -> Any:
        """
        Handle PUT requests.

        Delegates to the update_mock and adds the request to the unified history.

        Args:
            url: The URL to request
            **kwargs: Additional request parameters

        Returns:
            The mock response data
        """
        ...

    def patch(self, url: str, **kwargs: Any) -> Any:
        """
        Handle PATCH requests.

        Delegates to the update_mock and adds the request to the unified history.

        Args:
            url: The URL to request
            **kwargs: Additional request parameters

        Returns:
            The mock response data
        """
        ...

    def delete(self, url: str, **kwargs: Any) -> Any:
        """
        Handle DELETE requests.

        Delegates to the delete_mock and adds the request to the unified history.

        Args:
            url: The URL to request
            **kwargs: Additional request parameters

        Returns:
            The mock response data
        """
        ...

    def with_parent_id_handling(self, enabled: bool = True) -> 'CombinedCrudMock':
        """
        Enable or disable parent_id handling for all CRUD mocks.

        When enabled, the mocks will process parent_id parameters to build
        URLs in the format 'parents/{parent_id}/{resource_path}'.

        Args:
            enabled: Whether to enable parent_id handling

        Returns:
            Self for method chaining
        """
        ...

    def assert_request_count(self, count: int, url_pattern: Optional[str] = None) -> None:
        """
        Assert that a specific number of matching requests were made.

        Args:
            count: Expected number of requests
            url_pattern: Optional URL pattern to filter requests

        Raises:
            AssertionError: If the actual count doesn't match the expected count
        """
        ...

    def assert_request_sequence(
        self,
        sequence: List[Dict[str, Any]],
        strict: bool = False
    ) -> None:
        """
        Assert that requests were made in a specific sequence.

        Args:
            sequence: List of request matchers, each containing criteria like 'method' and 'url_pattern'
            strict: If True, the number of requests must match exactly

        Raises:
            AssertionError: If the sequence doesn't match
        """
        ...

    def assert_crud_operation_sequence(
        self,
        operations: List[str],
        resource_id: Optional[str] = None,
        url_pattern: Optional[str] = None
    ) -> None:
        """
        Assert that CRUD operations were performed in a specific sequence.

        This method provides a higher-level way to assert operation sequences using
        operation names like "create", "read", "update", "partial_update", and "delete".

        Args:
            operations: List of operation names in expected sequence
            resource_id: Optional resource ID to include in URL patterns for non-create operations
            url_pattern: Optional base URL pattern to match

        Raises:
            AssertionError: If the operation sequence doesn't match
        """
        ...

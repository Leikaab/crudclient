"""
Combined mock implementation for all CRUD operations.

This module provides a unified mock implementation that combines
the individual Create, Read, Update, and Delete mocks into a single
interface for testing complete CRUD workflows.
"""

import re
from typing import Any, Dict, List, Optional, Union

from .create import CreateMock
from .delete import DeleteMock
from .read import ReadMock
from .request_record import RequestRecord
from .update import UpdateMock

class CombinedCrudMock:
    """
    Combined mock implementation for all CRUD operations.

    This class provides a unified interface for mocking all CRUD operations,
    delegating to specialized mocks for each operation type while maintaining
    a combined request history.
    """

    create_mock: CreateMock
    read_mock: ReadMock
    update_mock: UpdateMock
    delete_mock: DeleteMock
    request_history: List[RequestRecord]
    _parent_id_handling: bool

    def __init__(self) -> None:
        """
        Initialize the combined CRUD mock.

        Creates individual mocks for each CRUD operation and sets up
        a combined request history.
        """
        ...

    def get(self, url: str, **kwargs: Any) -> Any:
        """
        Handle GET requests by delegating to the read mock.

        Args:
            url: The URL to send the GET request to
            **kwargs: Additional arguments to pass to the request

        Returns:
            The response from the read mock
        """
        ...

    def post(self, url: str, **kwargs: Any) -> Any:
        """
        Handle POST requests by delegating to the create mock.

        Args:
            url: The URL to send the POST request to
            **kwargs: Additional arguments to pass to the request

        Returns:
            The response from the create mock
        """
        ...

    def put(self, url: str, **kwargs: Any) -> Any:
        """
        Handle PUT requests by delegating to the update mock.

        Args:
            url: The URL to send the PUT request to
            **kwargs: Additional arguments to pass to the request

        Returns:
            The response from the update mock
        """
        ...

    def patch(self, url: str, **kwargs: Any) -> Any:
        """
        Handle PATCH requests by delegating to the update mock.

        Args:
            url: The URL to send the PATCH request to
            **kwargs: Additional arguments to pass to the request

        Returns:
            The response from the update mock
        """
        ...

    def delete(self, url: str, **kwargs: Any) -> Any:
        """
        Handle DELETE requests by delegating to the delete mock.

        Args:
            url: The URL to send the DELETE request to
            **kwargs: Additional arguments to pass to the request

        Returns:
            The response from the delete mock
        """
        ...

    def with_parent_id_handling(self, enabled: bool = True) -> "CombinedCrudMock":
        """
        Enable or disable parent_id handling for all mocks.

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

    def assert_request_sequence(self, sequence: List[Dict[str, Any]], strict: bool = False) -> None:
        """
        Assert that requests were made in a specific sequence.

        Args:
            sequence: List of request matchers, each containing criteria like 'method' and 'url_pattern'
            strict: If True, the number of requests must match exactly

        Raises:
            AssertionError: If the sequence doesn't match
        """
        ...

    def assert_crud_operation_sequence(self, operations: List[str], resource_id: Optional[str] = None, url_pattern: Optional[str] = None) -> None:
        """
        Assert that CRUD operations were performed in a specific sequence.

        Args:
            operations: List of operation names ('create', 'read', 'update', 'partial_update', 'delete')
            resource_id: Optional resource ID to include in URL patterns for non-create operations
            url_pattern: Optional base URL pattern to match

        Raises:
            AssertionError: If the operation sequence doesn't match
        """
        ...

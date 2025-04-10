"""
Mock implementation for delete operations in CRUD testing.

This module provides a mock implementation for testing delete operations,
with support for dependency tracking, cascading deletes, and soft deletes.
"""

import copy
import json
import re
from typing import Any, Dict, List, Optional, Set, Union

from crudclient.exceptions import CrudClientError
from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock
from .request_record import RequestRecord


class DeleteMock(BaseCrudMock):
    """
    Mock implementation for delete operations.

    This class provides a configurable mock for testing delete operations,
    with support for dependency tracking, cascading deletes, and soft deletes.
    It allows for detailed control over the behavior of delete operations during testing.
    """

    def __init__(self) -> None:
        """
        Initialize a new DeleteMock instance.

        Sets up the default response, resource storage, and dependency tracking.
        """
        self.default_response: MockResponse
        self._stored_resources: Dict[str, Dict[str, Any]]
        self._dependencies: Dict[str, List[str]]
        self._soft_deleted_resources: Dict[str, Dict[str, Any]]
        self._cascade_enabled: bool
        self._soft_delete_enabled: bool
        ...

    def delete(self, url: str, **kwargs: Any) -> Any:
        """
        Handle a DELETE request to delete a resource.

        This method processes the request, records it, and returns an appropriate response.

        Args:
            url: The URL for the request
            **kwargs: Request parameters (params, data, json, headers)

        Returns:
            The response data (typically None for successful deletes)
        """
        ...

    def with_success(
        self,
        url_pattern: str,
        **kwargs: Any
    ) -> 'DeleteMock':
        """
        Configure a successful response for a specific URL pattern.

        This method sets up the mock to return a success response when
        a DELETE request matching the URL pattern is received.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def with_resource_in_use_error(
        self,
        url_pattern: str,
        **kwargs: Any
    ) -> 'DeleteMock':
        """
        Configure a resource-in-use error response for a specific URL pattern.

        This method sets up the mock to return an error response when
        a DELETE request is made for a resource that is in use.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def with_stored_resource(self, resource_id: Union[str, int], resource: Dict[str, Any]) -> 'DeleteMock':
        """
        Add a resource to the mock's storage.

        This method adds a resource to the mock's internal storage,
        making it available for delete operations.

        Args:
            resource_id: The ID of the resource
            resource: The resource data

        Returns:
            Self for method chaining
        """
        ...

    def with_dependency(
        self,
        resource_id: Union[str, int],
        dependent_id: Union[str, int]
    ) -> 'DeleteMock':
        """
        Configure a dependency between resources.

        This method sets up a dependency relationship where one resource
        depends on another, which can affect delete operations.

        Args:
            resource_id: The ID of the resource being depended on
            dependent_id: The ID of the dependent resource

        Returns:
            Self for method chaining
        """
        ...

    def with_cascading_delete(self, enabled: bool = True) -> 'DeleteMock':
        """
        Enable or disable cascading deletes.

        When enabled, deleting a resource will also delete its dependent resources.

        Args:
            enabled: Whether to enable cascading deletes

        Returns:
            Self for method chaining
        """
        ...

    def with_soft_delete(self, enabled: bool = True) -> 'DeleteMock':
        """
        Enable or disable soft deletes.

        When enabled, deleted resources are stored in a separate collection
        rather than being permanently removed.

        Args:
            enabled: Whether to enable soft deletes

        Returns:
            Self for method chaining
        """
        ...

    def with_referential_integrity_check(self, url_pattern: str) -> 'DeleteMock':
        """
        Configure referential integrity checking for a specific URL pattern.

        This method sets up the mock to check for dependencies before allowing
        a resource to be deleted, preventing deletion if dependencies exist.

        Args:
            url_pattern: Regular expression pattern to match request URLs

        Returns:
            Self for method chaining
        """
        ...

    def assert_resource_deleted(self, resource_id: Union[str, int], soft_delete: bool = False) -> None:
        """
        Assert that a resource has been deleted.

        This method checks that a resource with the given ID has been deleted,
        optionally checking for soft deletion.

        Args:
            resource_id: The ID of the resource to check
            soft_delete: Whether to check for soft deletion

        Raises:
            AssertionError: If the resource has not been deleted
        """
        ...

    def assert_dependencies_deleted(self, resource_id: Union[str, int], soft_delete: bool = False) -> None:
        """
        Assert that a resource's dependencies have been deleted.

        This method checks that all dependencies of a resource with the given ID
        have been deleted, optionally checking for soft deletion.

        Args:
            resource_id: The ID of the resource whose dependencies to check
            soft_delete: Whether to check for soft deletion

        Raises:
            AssertionError: If any dependencies have not been deleted
        """
        ...

"""
Mock implementation for DELETE operations in CRUD APIs.

This module provides a mock implementation for DELETE operations,
with support for various deletion scenarios including cascading deletes,
soft deletes, and referential integrity checks.
"""

from typing import Any, Dict, List, Optional, Union

from requests import PreparedRequest

from crudclient.exceptions import CrudClientError
from crudclient.testing.response_builder.response import MockResponse

from .base import BaseCrudMock
from .request_record import RequestRecord

class DeleteMock(BaseCrudMock):
    """
    Mock implementation for DELETE operations in CRUD APIs.

    This class provides functionality for mocking DELETE operations,
    including support for cascading deletes, soft deletes, and
    referential integrity checks.
    """

    _stored_resources: Dict[str, Dict[str, Any]]
    _dependencies: Dict[str, List[str]]
    _soft_deleted_resources: Dict[str, Dict[str, Any]]
    _cascade_enabled: bool
    _soft_delete_enabled: bool

    def __init__(self) -> None:
        """
        Initialize the DeleteMock with default settings.

        Sets up a default 204 No Content response and initializes
        tracking for stored resources, dependencies, and soft-deleted resources.
        """
        ...

    def delete(self, url: str, **kwargs: Any) -> Any:
        """
        Handle DELETE requests to the mock API.

        Args:
            url: The URL to send the DELETE request to
            **kwargs: Additional arguments to pass to the request

        Returns:
            The response data or text, depending on the response format
        """
        ...

    def with_success(self, url_pattern: str, **kwargs: Any) -> "DeleteMock":
        """
        Configure a successful deletion response.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def with_resource_in_use_error(self, url_pattern: str, **kwargs: Any) -> "DeleteMock":
        """
        Configure a resource-in-use error response.

        This simulates the scenario where a resource cannot be deleted
        because it is currently in use by another resource.

        Args:
            url_pattern: Regular expression pattern to match request URLs
            **kwargs: Additional criteria for matching requests

        Returns:
            Self for method chaining
        """
        ...

    def with_stored_resource(self, resource_id: Union[str, int], resource: Dict[str, Any]) -> "DeleteMock":
        """
        Add a resource to the mock's stored resources.

        Args:
            resource_id: ID of the resource to store
            resource: Resource data to store

        Returns:
            Self for method chaining
        """
        ...

    def with_dependency(self, resource_id: Union[str, int], dependent_id: Union[str, int]) -> "DeleteMock":
        """
        Configure a dependency relationship between resources.

        Args:
            resource_id: ID of the parent resource
            dependent_id: ID of the dependent resource

        Returns:
            Self for method chaining
        """
        ...

    def with_cascading_delete(self, enabled: bool = True) -> "DeleteMock":
        """
        Enable or disable cascading deletes.

        When enabled, deleting a resource will also delete its dependencies.

        Args:
            enabled: Whether to enable cascading deletes

        Returns:
            Self for method chaining
        """
        ...

    def with_soft_delete(self, enabled: bool = True) -> "DeleteMock":
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

    def with_referential_integrity_check(self, url_pattern: str) -> "DeleteMock":
        """
        Configure referential integrity checking for deletions.

        When enabled, attempting to delete a resource with dependencies
        will result in an error unless cascading deletes are also enabled.

        Args:
            url_pattern: Regular expression pattern to match request URLs

        Returns:
            Self for method chaining
        """
        ...

    def assert_resource_deleted(self, resource_id: Union[str, int], soft_delete: bool = False) -> None:
        """
        Assert that a resource has been deleted.

        Args:
            resource_id: ID of the resource to check
            soft_delete: Whether to check soft-deleted resources

        Raises:
            AssertionError: If the resource has not been deleted
        """
        ...

    def assert_dependencies_deleted(self, resource_id: Union[str, int], soft_delete: bool = False) -> None:
        """
        Assert that a resource's dependencies have been deleted.

        Args:
            resource_id: ID of the parent resource
            soft_delete: Whether to check soft-deleted resources

        Raises:
            AssertionError: If any dependencies have not been deleted
        """
        ...

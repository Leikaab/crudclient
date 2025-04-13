"""
Concrete Test Spy for the `CrudBase` Interface using Enhanced Spying.

This module provides `CrudSpy`, a specific implementation of the **Test Spy
pattern** tailored for the `crudclient.crud.base.Crud` interface. It utilizes
the `EnhancedSpyBase` and `ClassSpy` mechanisms to record and verify
interactions made with the CRUD endpoint component.
"""

from typing import Any, Dict, List, Optional, Type, Union

from crudclient.client import Client
from crudclient.crud.base import Crud as CrudBase
from crudclient.crud.base import T
from crudclient.models import ApiResponse
from crudclient.types import JSONDict, JSONList

from ..exceptions import VerificationError
from .enhanced import EnhancedSpyBase

class CrudSpy(EnhancedSpyBase, CrudBase[T]):  # Inherits from EnhancedSpyBase and conforms to CrudBase interface
    """
    A **Test Spy** specifically for the `crudclient.crud.base.Crud` interface.

    This class acts as a test double that conforms to the `CrudBase` interface but
    also inherits from `EnhancedSpyBase` to record method calls made to it (e.g.,
    `list`, `get`, `create`). It uses composition internally, wrapping a
    real `CrudBase` instance and spying on its methods using `ClassSpy`.

    Tests can use the verification methods inherited from `EnhancedSpyBase` or
    the dedicated `Verifier` class (`crudclient.testing.verification.Verifier`)
    to assert how the CRUD endpoint was interacted with. Custom verification methods
    specific to CRUD interactions are also provided.
    """

    def __init__(self, client: Client, resource_path: str = "/test", datamodel: Optional[Type[T]] = None, **kwargs: Any):
        """
        Initialize a CrudSpy instance.

        Args:
            client: Client instance (real, spy, or mock) for the underlying CrudBase.
            resource_path: The resource path for the underlying CrudBase.
            datamodel: The data model for the underlying CrudBase.
            **kwargs: Additional keyword arguments (currently unused by CrudBase).
        """
        ...
    # --- CrudBase Interface Methods (for type checking) ---
    # These methods are implemented via ClassSpy or __getattr__ in the .py file,
    # but are declared here to satisfy the CrudBase interface for type checkers.

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None) -> Union[List[T], ApiResponse[List[T]]]:
        """
        Spy on a list operation.

        Args:
            parent_id: Optional parent resource ID.
            params: Optional query parameters.

        Returns:
            List of resources or ApiResponse (typically mocked or from a wrapped CrudBase).
        """
        ...

    def get(self, resource_id: str, parent_id: Optional[str] = None) -> T:
        """
        Spy on a get operation.

        Args:
            resource_id: ID of the resource to retrieve.
            parent_id: Optional parent resource ID.

        Returns:
            The retrieved resource (typically mocked or from a wrapped CrudBase).
        """
        ...

    def create(self, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> T:
        """
        Spy on a create operation.

        Args:
            data: Data for the new resource.
            parent_id: Optional parent resource ID.

        Returns:
            The created resource (typically mocked or from a wrapped CrudBase).
        """
        ...

    def update(self, resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> T:
        """
        Spy on an update operation.

        Args:
            resource_id: ID of the resource to update.
            data: Updated data for the resource.
            parent_id: Optional parent resource ID.

        Returns:
            The updated resource (typically mocked or from a wrapped CrudBase).
        """
        ...

    def delete(self, resource_id: str, parent_id: Optional[str] = None) -> None:
        """
        Spy on a delete operation.

        Args:
            resource_id: ID of the resource to delete.
            parent_id: Optional parent resource ID.
        """
        ...

    def bulk_create(self, data: List[Union[JSONDict, T]], parent_id: Optional[str] = None) -> List[T]:
        """
        Spy on a bulk_create operation.

        Args:
            data: List of data for the new resources.
            parent_id: Optional parent resource ID.

        Returns:
            List of created resources (typically mocked or from a wrapped CrudBase).
        """
        ...

    def bulk_update(self, data: List[Union[JSONDict, T]], parent_id: Optional[str] = None) -> List[T]:
        """
        Spy on a bulk_update operation.

        Args:
            data: List of updated data for the resources (must include identifiers).
            parent_id: Optional parent resource ID.

        Returns:
            List of updated resources (typically mocked or from a wrapped CrudBase).
        """
        ...

    def bulk_delete(self, ids: List[str], parent_id: Optional[str] = None) -> None:
        """
        Spy on a bulk_delete operation.

        Args:
            ids: List of IDs of the resources to delete.
            parent_id: Optional parent resource ID.
        """
        ...
    # --- Custom Verification Methods ---

    def verify_resource_created(self, data: Any) -> None:
        """
        Verify that a resource was created with specific data via the `create` method.

        Args:
            data: Expected resource data (first argument to `create`).

        Raises:
            VerificationError: If `create` was not called with the specified data.
        """
        ...

    def verify_resource_updated(self, id: Any, data: Any) -> None:
        """
        Verify that a resource was updated with a specific ID and data via the `update` method.

        Args:
            id: Expected resource ID (first argument to `update`).
            data: Expected updated resource data (second argument to `update`).

        Raises:
            VerificationError: If `update` was not called with the specified ID and data.
        """
        ...

    def verify_resource_deleted(self, id: Any) -> None:
        """
        Verify that a resource was deleted with a specific ID via the `delete` method.

        Args:
            id: Expected resource ID (first argument to `delete`).

        Raises:
            VerificationError: If `delete` was not called with the specified ID.
        """
        ...
    # --- Magic Methods ---

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the spy wrapper, base class, or target CrudBase."""
        ...

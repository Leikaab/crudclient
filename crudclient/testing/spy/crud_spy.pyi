"""
CRUD spy implementation for recording and verifying CRUD operations.

This module provides a spy implementation of the Crud class that records
all method calls for later verification.
"""

from typing import Any, Dict, List, Optional, Union

from crudclient.crud.base import Crud as CrudBase
from crudclient.crud.base import T
from crudclient.models import ApiResponse
from crudclient.types import JSONDict, JSONList

from .base import SpyBase

class CrudSpy(CrudBase, SpyBase):
    """
    Spy implementation of the Crud class.

    This class wraps a Crud instance and records all method calls for later verification.
    It can be used to verify that the expected methods were called with the expected
    arguments during testing.
    """

    _resource_path: str
    delegate: CrudBase

    def __init__(
        self,
        delegate: Optional[CrudBase] = None,
        **kwargs: Any
    ):
        """
        Initialize a CrudSpy instance.

        Args:
            delegate: Optional delegate Crud to forward calls to
            **kwargs: Additional keyword arguments to pass to the Crud constructor

        Raises:
            ValueError: If client is not provided
        """
        ...

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None) -> Any:  # Return type kept as Any for spy simplicity
        """
        Record and forward a call to list.

        Args:
            **kwargs: Keyword arguments for the list operation

        Returns:
            Result from the delegate Crud

        Raises:
            Any exception raised by the delegate Crud
        """
        ...

    def get(self, id: Any, **kwargs: Any) -> Any:
        """
        Record and forward a call to get.

        Args:
            id: Resource ID
            **kwargs: Keyword arguments for the get operation

        Returns:
            Result from the delegate Crud

        Raises:
            Any exception raised by the delegate Crud
        """
        ...

    def create(self, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Any:  # Return type kept as Any
        """
        Record and forward a call to create.

        Args:
            data: Resource data
            **kwargs: Keyword arguments for the create operation

        Returns:
            Result from the delegate Crud

        Raises:
            Any exception raised by the delegate Crud
        """
        ...

    def update(self, resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Any:  # Return type kept as Any
        """
        Record and forward a call to update.

        Args:
            id: Resource ID
            data: Updated resource data
            **kwargs: Keyword arguments for the update operation

        Returns:
            Result from the delegate Crud

        Raises:
            Any exception raised by the delegate Crud
        """
        ...

    def delete(self, id: Any, **kwargs: Any) -> Any:
        """
        Record and forward a call to delete.

        Args:
            id: Resource ID
            **kwargs: Keyword arguments for the delete operation

        Returns:
            Result from the delegate Crud

        Raises:
            Any exception raised by the delegate Crud
        """
        ...

    def bulk_create(self, data: List[Any], **kwargs: Any) -> Any:
        """
        Record and forward a call to bulk_create.

        Args:
            data: List of resource data
            **kwargs: Keyword arguments for the bulk_create operation

        Returns:
            Result from the delegate Crud

        Raises:
            Any exception raised by the delegate Crud
        """
        ...

    def bulk_update(self, data: List[Dict[str, Any]], **kwargs: Any) -> Any:
        """
        Record and forward a call to bulk_update.

        Args:
            data: List of resource data with IDs
            **kwargs: Keyword arguments for the bulk_update operation

        Returns:
            Result from the delegate Crud

        Raises:
            Any exception raised by the delegate Crud
        """
        ...

    def bulk_delete(self, ids: List[Any], **kwargs: Any) -> Any:
        """
        Record and forward a call to bulk_delete.

        Args:
            ids: List of resource IDs
            **kwargs: Keyword arguments for the bulk_delete operation

        Returns:
            Result from the delegate Crud

        Raises:
            Any exception raised by the delegate Crud
        """
        ...

    # Helper methods for verification

    def assert_resource_created(self, data: Any) -> None:
        """
        Assert that a resource was created with specific data.

        Args:
            data: Expected resource data

        Raises:
            AssertionError: If the resource was not created with the specified data
        """
        ...

    def assert_resource_updated(self, id: Any, data: Any) -> None:
        """
        Assert that a resource was updated with specific data.

        Args:
            id: Resource ID
            data: Expected updated resource data

        Raises:
            AssertionError: If the resource was not updated with the specified data
        """
        ...

    def assert_resource_deleted(self, id: Any) -> None:
        """
        Assert that a resource was deleted.

        Args:
            id: Resource ID

        Raises:
            AssertionError: If the resource was not deleted
        """
        ...

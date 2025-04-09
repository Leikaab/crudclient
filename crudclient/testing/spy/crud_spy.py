"""
CRUD spy implementation for verification-focused testing.

This module provides a spy implementation of the CRUD interface that records
all method calls for later verification in tests. It can be used to verify
that specific CRUD operations were called with the expected arguments.
"""

from typing import Any, Dict, List, Optional

from crudclient.crud.base import Crud as CrudBase

from .base import SpyBase


class CrudSpy(CrudBase, SpyBase):
    """
    Spy implementation of the CRUD interface.

    This class records all method calls to the CRUD interface for verification
    in tests, while delegating to a real or mock implementation. It can be used
    to verify that specific CRUD operations were called with the expected arguments,
    without affecting the actual behavior of the CRUD operations.

    Example:
        >>> from crudclient.testing.spy import CrudSpy
        >>> from unittest.mock import MagicMock
        >>> client = MagicMock()
        >>> crud_spy = CrudSpy(client=client)
        >>> crud_spy.create({"name": "Test"})
        >>> crud_spy.assert_resource_created({"name": "Test"})
    """

    # Set a default resource path as a class attribute
    _resource_path = "/test"

    def __init__(
        self,
        delegate: Optional[CrudBase] = None,
        **kwargs: Any
    ):
        """
        Initialize the CRUD spy.

        Args:
            delegate: Optional delegate CRUD implementation to forward method calls to.
                If not provided, the parent class implementation will be used.
            **kwargs: Additional arguments to pass to the CrudBase constructor.
                Must include 'client' if delegate is not provided.
        """
        # Create a mock client if not provided in kwargs
        if 'client' not in kwargs:
            from unittest.mock import MagicMock
            if delegate is not None and hasattr(delegate, 'client') and delegate.client is not None:
                kwargs['client'] = delegate.client
            else:
                kwargs['client'] = MagicMock()

        # Initialize with the client
        client = kwargs.get('client')
        if client is None:
            raise ValueError("Client must be provided")
        CrudBase.__init__(self, client)
        SpyBase.__init__(self)

        # Create a delegate CRUD if not provided
        self.delegate = delegate or super()

    def list(self, **kwargs: Any) -> Any:
        """
        Record and delegate list method call.

        This method records the call to list with the provided
        arguments and delegates to the delegate implementation.

        Args:
            **kwargs: Query parameters and other options for the list operation

        Returns:
            List of resources from the API
        """
        try:
            result = self.delegate.list(**kwargs)
            self._record_call('list', (), kwargs, result)
            return result
        except Exception as e:
            self._record_call('list', (), kwargs, exception=e)
            raise

    def get(self, id: Any, **kwargs: Any) -> Any:
        """
        Record and delegate get method call.

        This method records the call to get with the provided
        arguments and delegates to the delegate implementation.

        Args:
            id: Resource ID to retrieve
            **kwargs: Additional options for the get operation

        Returns:
            Resource from the API
        """
        try:
            result = self.delegate.get(id, **kwargs)
            self._record_call('get', (id,), kwargs, result)
            return result
        except Exception as e:
            self._record_call('get', (id,), kwargs, exception=e)
            raise

    def create(self, data: Any, **kwargs: Any) -> Any:
        """
        Record and delegate create method call.

        This method records the call to create with the provided
        arguments and delegates to the delegate implementation.

        Args:
            data: Resource data to create
            **kwargs: Additional options for the create operation

        Returns:
            Created resource from the API
        """
        try:
            result = self.delegate.create(data, **kwargs)
            self._record_call('create', (data,), kwargs, result)
            return result
        except Exception as e:
            self._record_call('create', (data,), kwargs, exception=e)
            raise

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        """
        Record and delegate update method call.

        This method records the call to update with the provided
        arguments and delegates to the delegate implementation.

        Args:
            id: Resource ID to update
            data: Resource data to update with
            **kwargs: Additional options for the update operation

        Returns:
            Updated resource from the API
        """
        try:
            result = self.delegate.update(id, data, **kwargs)
            self._record_call('update', (id, data), kwargs, result)
            return result
        except Exception as e:
            self._record_call('update', (id, data), kwargs, exception=e)
            raise

    def delete(self, id: Any, **kwargs: Any) -> Any:
        """
        Record and delegate delete method call.

        This method records the call to delete with the provided
        arguments and delegates to the delegate implementation.

        Args:
            id: Resource ID to delete
            **kwargs: Additional options for the delete operation

        Returns:
            Deletion result from the API
        """
        try:
            result = self.delegate.delete(id, **kwargs)
            self._record_call('delete', (id,), kwargs, result)
            return result
        except Exception as e:
            self._record_call('delete', (id,), kwargs, exception=e)
            raise

    def bulk_create(self, data: List[Any], **kwargs: Any) -> Any:
        """
        Record and delegate bulk_create method call.

        This method records the call to bulk_create with the provided
        arguments and delegates to the delegate implementation.

        Args:
            data: List of resource data to create
            **kwargs: Additional options for the bulk create operation

        Returns:
            Created resources from the API
        """
        try:
            result = self.delegate.bulk_create(data, **kwargs)
            self._record_call('bulk_create', (data,), kwargs, result)
            return result
        except Exception as e:
            self._record_call('bulk_create', (data,), kwargs, exception=e)
            raise

    def bulk_update(self, data: List[Dict[str, Any]], **kwargs: Any) -> Any:
        """
        Record and delegate bulk_update method call.

        This method records the call to bulk_update with the provided
        arguments and delegates to the delegate implementation.

        Args:
            data: List of resource data with IDs to update
            **kwargs: Additional options for the bulk update operation

        Returns:
            Updated resources from the API
        """
        try:
            result = self.delegate.bulk_update(data, **kwargs)
            self._record_call('bulk_update', (data,), kwargs, result)
            return result
        except Exception as e:
            self._record_call('bulk_update', (data,), kwargs, exception=e)
            raise

    def bulk_delete(self, ids: List[Any], **kwargs: Any) -> Any:
        """
        Record and delegate bulk_delete method call.

        This method records the call to bulk_delete with the provided
        arguments and delegates to the delegate implementation.

        Args:
            ids: List of resource IDs to delete
            **kwargs: Additional options for the bulk delete operation

        Returns:
            Deletion result from the API
        """
        try:
            result = self.delegate.bulk_delete(ids, **kwargs)
            self._record_call('bulk_delete', (ids,), kwargs, result)
            return result
        except Exception as e:
            self._record_call('bulk_delete', (ids,), kwargs, exception=e)
            raise

    # Helper methods for verification

    def assert_resource_created(self, data: Any) -> None:
        """
        Assert that a resource was created with specific data.

        This method checks if the create method was called with the specified data.

        Args:
            data: Expected resource data

        Raises:
            AssertionError: If a resource with the specified data was not created
        """
        for call in self.calls:
            if call.method_name == 'create' and call.args and call.args[0] == data:
                return

        raise AssertionError(f"Resource with data {data} was not created")

    def assert_resource_updated(self, id: Any, data: Any) -> None:
        """
        Assert that a resource was updated with specific data.

        This method checks if the update method was called with the specified ID and data.

        Args:
            id: Resource ID
            data: Expected resource data

        Raises:
            AssertionError: If a resource with the specified ID was not updated with the specified data
        """
        for call in self.calls:
            if (
                call.method_name == 'update'
                and call.args
                and len(call.args) >= 2
                and call.args[0] == id
                and call.args[1] == data
            ):
                return

        raise AssertionError(f"Resource with ID {id} was not updated with data {data}")

    def assert_resource_deleted(self, id: Any) -> None:
        """
        Assert that a resource was deleted.

        This method checks if the delete method was called with the specified ID.

        Args:
            id: Resource ID

        Raises:
            AssertionError: If a resource with the specified ID was not deleted
        """
        for call in self.calls:
            if call.method_name == 'delete' and call.args and call.args[0] == id:
                return

        raise AssertionError(f"Resource with ID {id} was not deleted")

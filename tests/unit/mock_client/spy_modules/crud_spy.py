"""
CRUD spy implementation for verification-focused testing.
"""

from typing import Any, Dict, List, Optional, Type, Union

from crudclient.crud.base import CrudBase
from crudclient.crud.operations import CrudOperations

from .base import SpyBase


class CrudSpy(CrudBase, SpyBase):
    """
    Spy implementation of the CRUD interface.

    This class records all method calls to the CRUD interface for verification
    in tests, while delegating to a real or mock implementation.
    """

    def __init__(
        self,
        delegate: Optional[CrudBase] = None,
        **kwargs: Any
    ):
        """
        Initialize the CRUD spy.

        Args:
            delegate: Optional delegate CRUD implementation
            **kwargs: Additional arguments
        """
        CrudBase.__init__(self, **kwargs)
        SpyBase.__init__(self)

        # Create a delegate CRUD if not provided
        self.delegate = delegate or super()

    def list(self, **kwargs: Any) -> Any:
        """
        Record and delegate list method call.

        Args:
            **kwargs: Query parameters

        Returns:
            List of resources
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

        Args:
            id: Resource ID
            **kwargs: Additional arguments

        Returns:
            Resource
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

        Args:
            data: Resource data
            **kwargs: Additional arguments

        Returns:
            Created resource
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

        Args:
            id: Resource ID
            data: Resource data
            **kwargs: Additional arguments

        Returns:
            Updated resource
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

        Args:
            id: Resource ID
            **kwargs: Additional arguments

        Returns:
            Deletion result
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

        Args:
            data: List of resource data
            **kwargs: Additional arguments

        Returns:
            Created resources
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

        Args:
            data: List of resource data with IDs
            **kwargs: Additional arguments

        Returns:
            Updated resources
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

        Args:
            ids: List of resource IDs
            **kwargs: Additional arguments

        Returns:
            Deletion result
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

        Args:
            data: Expected resource data
        """
        for call in self.calls:
            if call.method_name == 'create' and call.args and call.args[0] == data:
                return

        raise AssertionError(f"Resource with data {data} was not created")

    def assert_resource_updated(self, id: Any, data: Any) -> None:
        """
        Assert that a resource was updated with specific data.

        Args:
            id: Resource ID
            data: Expected resource data
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

        Args:
            id: Resource ID
        """
        for call in self.calls:
            if call.method_name == 'delete' and call.args and call.args[0] == id:
                return

        raise AssertionError(f"Resource with ID {id} was not deleted")

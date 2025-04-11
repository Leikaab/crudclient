from typing import Any, Dict, List, Optional

from crudclient.crud.base import Crud as CrudBase

from .base import SpyBase


class CrudSpy(CrudBase, SpyBase):

    # Set a default resource path as a class attribute
    _resource_path = "/test"

    def __init__(self, delegate: Optional[CrudBase] = None, **kwargs: Any):
        # Create a mock client if not provided in kwargs
        if "client" not in kwargs:
            from unittest.mock import MagicMock

            if delegate is not None and hasattr(delegate, "client") and delegate.client is not None:
                kwargs["client"] = delegate.client
            else:
                kwargs["client"] = MagicMock()

        # Initialize with the client
        client = kwargs.get("client")
        if client is None:
            raise ValueError("Client must be provided")
        CrudBase.__init__(self, client)
        SpyBase.__init__(self)

        # Create a delegate CRUD if not provided
        self.delegate = delegate or super()

    def list(self, **kwargs: Any) -> Any:
        try:
            result = self.delegate.list(**kwargs)
            self._record_call("list", (), kwargs, result)
            return result
        except Exception as e:
            self._record_call("list", (), kwargs, exception=e)
            raise

    def get(self, id: Any, **kwargs: Any) -> Any:
        try:
            result = self.delegate.get(id, **kwargs)  # type: ignore
            self._record_call("get", (id,), kwargs, result)
            return result
        except Exception as e:
            self._record_call("get", (id,), kwargs, exception=e)
            raise

    def create(self, data: Any, **kwargs: Any) -> Any:
        try:
            result = self.delegate.create(data, **kwargs)
            self._record_call("create", (data,), kwargs, result)
            return result
        except Exception as e:
            self._record_call("create", (data,), kwargs, exception=e)
            raise

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        try:
            result = self.delegate.update(id, data, **kwargs)
            self._record_call("update", (id, data), kwargs, result)
            return result
        except Exception as e:
            self._record_call("update", (id, data), kwargs, exception=e)
            raise

    def delete(self, id: Any, **kwargs: Any) -> Any:
        try:
            result = self.delegate.delete(id, **kwargs)  # type: ignore
            self._record_call("delete", (id,), kwargs, result)
            return result
        except Exception as e:
            self._record_call("delete", (id,), kwargs, exception=e)
            raise

    def bulk_create(self, data: List[Any], **kwargs: Any) -> Any:
        try:
            result = self.delegate.bulk_create(data, **kwargs)  # type: ignore
            self._record_call("bulk_create", (data,), kwargs, result)
            return result
        except Exception as e:
            self._record_call("bulk_create", (data,), kwargs, exception=e)
            raise

    def bulk_update(self, data: List[Dict[str, Any]], **kwargs: Any) -> Any:
        try:
            result = self.delegate.bulk_update(data, **kwargs)  # type: ignore
            self._record_call("bulk_update", (data,), kwargs, result)
            return result
        except Exception as e:
            self._record_call("bulk_update", (data,), kwargs, exception=e)
            raise

    def bulk_delete(self, ids: List[Any], **kwargs: Any) -> Any:
        try:
            result = self.delegate.bulk_delete(ids, **kwargs)  # type: ignore
            self._record_call("bulk_delete", (ids,), kwargs, result)
            return result
        except Exception as e:
            self._record_call("bulk_delete", (ids,), kwargs, exception=e)
            raise

    # Helper methods for verification

    def assert_resource_created(self, data: Any) -> None:
        for call in self.calls:
            if call.method_name == "create" and call.args and call.args[0] == data:
                return

        raise AssertionError(f"Resource with data {data} was not created")

    def assert_resource_updated(self, id: Any, data: Any) -> None:
        for call in self.calls:
            if call.method_name == "update" and call.args and len(call.args) >= 2 and call.args[0] == id and call.args[1] == data:
                return

        raise AssertionError(f"Resource with ID {id} was not updated with data {data}")

    def assert_resource_deleted(self, id: Any) -> None:
        for call in self.calls:
            if call.method_name == "delete" and call.args and call.args[0] == id:
                return

        raise AssertionError(f"Resource with ID {id} was not deleted")

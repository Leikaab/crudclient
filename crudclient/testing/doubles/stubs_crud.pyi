from typing import Any, Callable, Dict, List, Optional, Type, Union

from crudclient.client import Client

class CrudBase:
    """
    Abstract base class defining the standard interface for CRUD operations
    on a specific API endpoint resource.

    Attributes:
        client: The client instance used for making API requests.
        endpoint: The base API endpoint path for the resource.
        model: The Pydantic model or class used to represent the resource data.
    """

    client: Optional[Client]
    endpoint: str
    model: Optional[Type[Any]]

    def __init__(self, client: Optional[Client] = None, endpoint: str = "", model: Optional[Type[Any]] = None) -> None:
        """
        Initialize the CrudBase.

        Args:
            client: The API client instance.
            endpoint: The specific API endpoint path for this resource.
            model: The data model class associated with this resource.
        """
        ...

    def list(self, **kwargs: Any) -> List[Any]:
        """
        Retrieve a list of resources, potentially filtered or paginated.

        Args:
            **kwargs: Filtering, sorting, or pagination parameters specific
                      to the API endpoint.

        Returns:
            A list of resource instances (or dictionaries if no model is set).

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def get(self, id: Any, **kwargs: Any) -> Any:
        """
        Retrieve a single resource by its unique identifier.

        Args:
            id: The unique identifier of the resource to retrieve.
            **kwargs: Additional parameters specific to the API endpoint.

        Returns:
            The resource instance (or dictionary if no model is set),
            or None if not found.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def create(self, data: Any, **kwargs: Any) -> Any:
        """
        Create a new resource.

        Args:
            data: The data for the new resource (model instance or dictionary).
            **kwargs: Additional parameters specific to the API endpoint.

        Returns:
            The newly created resource instance (or dictionary if no model is set).

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        """
        Update an existing resource identified by its ID.

        Args:
            id: The unique identifier of the resource to update.
            data: The data containing the updates (model instance or dictionary).
            **kwargs: Additional parameters specific to the API endpoint.

        Returns:
            The updated resource instance (or dictionary if no model is set),
            or None if the resource was not found.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """
        Delete a resource identified by its ID.

        Args:
            id: The unique identifier of the resource to delete.
            **kwargs: Additional parameters specific to the API endpoint.

        Returns:
            True if the deletion was successful, False otherwise (e.g., not found).

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

class StubCrud(CrudBase):
    """
    A stub implementation of CrudBase for testing, using an in-memory data store.

    Provides methods to configure responses/handlers for specific operations and
    hooks to inject custom logic before or after CRUD actions. Simulates basic
    filtering, sorting, and pagination for the `list` operation.

    Attributes:
        _default_data: Default data used if no specific response is configured.
        _data_store: The in-memory dictionary storing resources keyed by ID.
        _next_id: Counter for generating auto-incrementing IDs.
        _before_list_hook, _after_list_hook, ...: Optional hooks for operations.
        _list_response, _list_handler, ...: Configured static responses or dynamic handlers.
    """

    _default_data: Dict[str, Any]
    _data_store: Dict[str, Dict[str, Any]]
    _next_id: int
    _before_list_hook: Optional[Callable]
    _after_list_hook: Optional[Callable]
    _before_get_hook: Optional[Callable]
    _after_get_hook: Optional[Callable]
    _before_create_hook: Optional[Callable]
    _after_create_hook: Optional[Callable]
    _before_update_hook: Optional[Callable]
    _after_update_hook: Optional[Callable]
    _before_delete_hook: Optional[Callable]
    _after_delete_hook: Optional[Callable]
    _list_response: Optional[Any]
    _list_handler: Optional[Callable]
    _get_response: Optional[Any]
    _get_handler: Optional[Callable]
    _create_response: Optional[Any]
    _create_handler: Optional[Callable]

    def configure_list(self, response: Optional[Any] = None, handler: Optional[Callable] = None) -> None:
        """
        Configure a static response or a dynamic handler for the `list` operation.

        Args:
            response: The static list to return.
            handler: A callable that takes `**kwargs` and returns the list.
        """
        ...

    def configure_get(self, response: Optional[Any] = None, handler: Optional[Callable] = None) -> None:
        """
        Configure a static response or a dynamic handler for the `get` operation.

        Args:
            response: The static resource object/dict to return.
            handler: A callable that takes `id, **kwargs` and returns the resource.
        """
        ...

    def configure_create(self, response: Optional[Any] = None, handler: Optional[Callable] = None) -> None:
        """
        Configure a static response or a dynamic handler for the `create` operation.

        Args:
            response: The static created resource object/dict to return.
            handler: A callable that takes `data, **kwargs` and returns the created resource.
        """
        ...

    def __init__(
        self,
        client_or_name: Union[Client, str, None] = None,
        endpoint: str = "",
        model: Optional[Type[Any]] = None,
        default_data: Optional[Dict[str, Any]] = None,
        data_store: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        """
        Initialize the StubCrud instance.

        Args:
            client_or_name: The API client instance or a string used as the endpoint name
                            if `endpoint` is not provided.
            endpoint: The specific API endpoint path for this resource.
            model: The data model class associated with this resource.
            default_data: Default data for a single resource if needed.
            data_store: An optional external dictionary to use as the data store.
                        If None, an internal one is created.
        """
        ...

    def list(self, **kwargs: Any) -> List[Any]:
        """
        Simulate retrieving a list of resources from the in-memory store.

        Supports filtering by exact match on keyword arguments, sorting via
        `sort_by` and `sort_desc`, and pagination via `page` and `page_size`.
        Uses configured response/handler if set, otherwise operates on `_data_store`.

        Args:
            **kwargs: Filtering, sorting, and pagination parameters.

        Returns:
            A list of resource instances (or dictionaries).
        """
        ...

    def get(self, id: Any, **kwargs: Any) -> Any:
        """
        Simulate retrieving a single resource by ID from the in-memory store.

        Uses configured response/handler if set, otherwise looks up in `_data_store`.

        Args:
            id: The ID of the resource to retrieve.
            **kwargs: Additional parameters (ignored by default implementation).

        Returns:
            The resource instance (or dictionary), or None if not found.
        """
        ...

    def create(self, data: Any, **kwargs: Any) -> Any:
        """
        Simulate creating a new resource in the in-memory store.

        Assigns an auto-incrementing integer ID if 'id' is not present in `data`.
        Uses configured response/handler if set, otherwise adds to `_data_store`.

        Args:
            data: The data for the new resource (model instance or dictionary).
            **kwargs: Additional parameters (ignored by default implementation).

        Returns:
            The created resource instance (or dictionary).
        """
        ...

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        """
        Simulate updating an existing resource in the in-memory store.

        Merges the provided `data` into the existing resource data.

        Args:
            id: The ID of the resource to update.
            data: The data containing updates (model instance or dictionary).
            **kwargs: Additional parameters (ignored by default implementation).

        Returns:
            The updated resource instance (or dictionary), or None if not found.
        """
        ...

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """
        Simulate deleting a resource from the in-memory store.

        Args:
            id: The ID of the resource to delete.
            **kwargs: Additional parameters (ignored by default implementation).

        Returns:
            True if the resource was found and deleted, False otherwise.
        """
        ...

    def set_before_list_hook(self, hook: Callable[[Dict[str, Any]], None]) -> None:
        """Set a hook to run before the list operation."""
        ...

    def set_after_list_hook(self, hook: Callable[[List[Any], Dict[str, Any]], List[Any]]) -> None:
        """Set a hook to run after the list operation, modifying the result."""
        ...

    def set_before_get_hook(self, hook: Callable[[Any, Dict[str, Any]], None]) -> None:
        """Set a hook to run before the get operation."""
        ...

    def set_after_get_hook(self, hook: Callable[[Any, Any, Dict[str, Any]], Any]) -> None:
        """Set a hook to run after the get operation, modifying the result."""
        ...

    def set_before_create_hook(self, hook: Callable[[Any, Dict[str, Any]], Any]) -> None:
        """Set a hook to run before the create operation, modifying the input data."""
        ...

    def set_after_create_hook(self, hook: Callable[[Any, Dict[str, Any]], Any]) -> None:
        """Set a hook to run after the create operation, modifying the result."""
        ...

    def set_before_update_hook(self, hook: Callable[[Any, Any, Dict[str, Any]], Any]) -> None:
        """Set a hook to run before the update operation, modifying the input data."""
        ...

    def set_after_update_hook(self, hook: Callable[[Any, Any, Dict[str, Any]], Any]) -> None:
        """Set a hook to run after the update operation, modifying the result."""
        ...

    def set_before_delete_hook(self, hook: Callable[[Any, Dict[str, Any]], None]) -> None:
        """Set a hook to run before the delete operation."""
        ...

    def set_after_delete_hook(self, hook: Callable[[Any, Dict[str, Any]], None]) -> None:
        """Set a hook to run after the delete operation."""
        ...

    def verify_deleted(self, id: Any) -> bool:
        """
        Check if a resource with the given ID is absent from the data store.

        Args:
            id: The ID to check.

        Returns:
            True if the ID is not found in the data store, False otherwise.
        """
        ...

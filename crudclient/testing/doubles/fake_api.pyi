# crudclient/testing/doubles/fake_api.pyi
from typing import Any, Dict, List, Optional, Type, Union

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig

from .data_store import DataStore


class FakeCrud:
    """
    A mock implementation of CRUD operations for testing purposes.

    Simulates database operations using an in-memory DataStore.
    Supports standard CRUD operations, filtering, pagination, and bulk operations.
    """
    database: DataStore
    collection: str
    model: Optional[Type[Any]]

    def __init__(
        self,
        database: DataStore,
        collection: str,
        model: Optional[Type[Any]] = None
    ) -> None:
        """
        Initialize a FakeCrud instance.

        Args:
            database: The DataStore instance to use for storage
            collection: The name of the collection to operate on
            model: Optional model class to convert data to/from
        """
        ...

    def list(self, **kwargs: Any) -> Any:
        """
        List items from the collection with optional filtering and pagination.

        Args:
            **kwargs: Supports the following parameters:
                filters: Dict[str, Any] - Filter criteria
                sort_by: Optional[Union[str, List[str]]] - Field(s) to sort by
                sort_desc: Union[bool, List[bool]] - Sort direction(s)
                page: int - Page number (1-based)
                page_size: Optional[int] - Items per page
                include_deleted: bool - Whether to include soft-deleted items
                include_related: Optional[List[str]] - Related collections to include
                fields: Optional[List[str]] - Fields to include in the response

        Returns:
            If a model is provided, a list of model instances.
            Otherwise, a list of dictionaries.
        """
        ...

    def get(self, id: Any, **kwargs: Any) -> Any:
        """
        Get a single item by ID.

        Args:
            id: The ID of the item to retrieve
            **kwargs: Supports the following parameters:
                include_deleted: bool - Whether to include soft-deleted items
                include_related: Optional[List[str]] - Related collections to include
                fields: Optional[List[str]] - Fields to include in the response

        Returns:
            If a model is provided, a model instance.
            Otherwise, a dictionary or None if not found.
        """
        ...

    def create(self, data: Any, **kwargs: Any) -> Any:
        """
        Create a new item in the collection.

        Args:
            data: The data to create (model instance or dictionary)
            **kwargs: Supports the following parameters:
                skip_validation: bool - Whether to skip validation

        Returns:
            If a model is provided, a model instance of the created item.
            Otherwise, a dictionary of the created item.
        """
        ...

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        """
        Update an existing item by ID.

        Args:
            id: The ID of the item to update
            data: The data to update (model instance or dictionary)
            **kwargs: Supports the following parameters:
                skip_validation: bool - Whether to skip validation
                check_version: bool - Whether to check version for optimistic locking

        Returns:
            If a model is provided, a model instance of the updated item.
            Otherwise, a dictionary of the updated item, or None if not found.
        """
        ...

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """
        Delete an item by ID.

        Args:
            id: The ID of the item to delete
            **kwargs: Supports the following parameters:
                soft_delete: bool - Whether to perform a soft delete
                cascade: bool - Whether to cascade the delete to related items

        Returns:
            True if the item was deleted, False otherwise.
        """
        ...

    def bulk_create(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """
        Create multiple items in the collection.

        Args:
            data: List of items to create (model instances or dictionaries)
            **kwargs: Supports the following parameters:
                skip_validation: bool - Whether to skip validation

        Returns:
            If a model is provided, a list of model instances of the created items.
            Otherwise, a list of dictionaries of the created items.
        """
        ...

    def bulk_update(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """
        Update multiple items in the collection.

        Args:
            data: List of items to update (model instances or dictionaries)
            **kwargs: Supports the following parameters:
                skip_validation: bool - Whether to skip validation
                check_version: bool - Whether to check version for optimistic locking

        Returns:
            If a model is provided, a list of model instances of the updated items.
            Otherwise, a list of dictionaries of the updated items.
            Items that were not found will be None.
        """
        ...

    def bulk_delete(self, ids: List[Any], **kwargs: Any) -> int:
        """
        Delete multiple items by ID.

        Args:
            ids: List of IDs of items to delete
            **kwargs: Supports the following parameters:
                soft_delete: bool - Whether to perform a soft delete
                cascade: bool - Whether to cascade the delete to related items

        Returns:
            The number of items successfully deleted.
        """
        ...


class FakeAPI(API):
    """
    A mock implementation of the API class for testing purposes.

    Provides an in-memory implementation of an API with endpoints
    that operate on a DataStore. Useful for testing without making
    actual HTTP requests.
    """
    client_class: Type[Client]
    database: DataStore
    endpoints: Dict[str, FakeCrud]

    def __init__(
        self,
        client: Optional[Client] = None,
        client_config: Optional[ClientConfig] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize a FakeAPI instance.

        Args:
            client: Optional client instance to use
            client_config: Optional client configuration
            **kwargs: Additional arguments to pass to the API constructor
        """
        ...

    def register_endpoint(
        self,
        name: str,
        endpoint: str,
        model: Optional[Type[Any]] = None,
        **kwargs: Any
    ) -> FakeCrud:
        """
        Register a new endpoint with the API.

        Args:
            name: The name of the endpoint
            endpoint: The endpoint path
            model: Optional model class to convert data to/from
            **kwargs: Additional arguments for endpoint configuration

        Returns:
            The created FakeCrud instance.
        """
        ...

    def define_relationship(
        self,
        source_collection: str,
        target_collection: str,
        relationship_type: str,
        **kwargs: Any
    ) -> 'FakeAPI':
        """
        Define a relationship between two collections.

        Args:
            source_collection: The name of the source collection
            target_collection: The name of the target collection
            relationship_type: The type of relationship
            **kwargs: Additional relationship parameters

        Returns:
            The FakeAPI instance for chaining.
        """
        ...

    def add_validation_rule(
        self,
        field: str,
        validator_func: Any,
        error_message: str,
        collection: Optional[str] = None
    ) -> 'FakeAPI':
        """
        Add a validation rule for a field.

        Args:
            field: The name of the field to validate
            validator_func: A function that validates the field value
            error_message: The error message to show if validation fails
            collection: Optional collection to apply the rule to

        Returns:
            The FakeAPI instance for chaining.
        """
        ...

    def add_unique_constraint(
        self,
        fields: Union[str, List[str]],
        error_message: Optional[str] = None,
        collection: Optional[str] = None
    ) -> 'FakeAPI':
        """
        Add a unique constraint for one or more fields.

        Args:
            fields: The field(s) that should be unique
            error_message: Optional custom error message
            collection: Optional collection to apply the constraint to

        Returns:
            The FakeAPI instance for chaining.
        """
        ...

    def set_timestamp_tracking(self, enabled: bool) -> 'FakeAPI':
        """
        Enable or disable automatic timestamp tracking.

        Args:
            enabled: Whether to enable timestamp tracking

        Returns:
            The FakeAPI instance for chaining.
        """
        ...

    def __getattr__(self, name: str) -> Any:
        """
        Get an endpoint by name.

        Args:
            name: The name of the endpoint

        Returns:
            The FakeCrud instance for the endpoint.

        Raises:
            AttributeError: If the endpoint does not exist.
        """
        ...

    def _register_endpoints(self) -> None:
        """
        Register default endpoints. This is a no-op in FakeAPI.
        """
        ...

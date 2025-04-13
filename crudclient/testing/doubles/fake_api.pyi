# crudclient/testing/doubles/fake_api.pyi
from typing import Any, Callable, Dict, List, Optional, Type, Union

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig

from .data_store import DataStore

class FakeCrud:
    """
    Internal helper simulating a single CRUD endpoint's operations for `FakeAPI`.

    This class acts as the bridge between a registered endpoint name on a `FakeAPI`
    instance (e.g., `fake_api.users`) and the underlying `DataStore`. It handles
    CRUD operations for a specific `collection` within the `DataStore`.

    Key responsibilities:
    - Delegates CRUD calls (`list`, `get`, `create`, etc.) to the `DataStore`.
    - Handles optional conversion between raw dictionaries (from `DataStore`) and
      Pydantic models (if a `model` type was provided during registration).
    - Receives keyword arguments (`**kwargs`) in its methods and passes them
      transparently to the corresponding `DataStore` methods (e.g., for filtering,
      sorting, pagination, validation control).

    Instances are created by `FakeAPI.register_endpoint` and should typically not
    be instantiated directly by users. Access them via attributes on the `FakeAPI`
    instance (e.g., `my_api.users.list()`).
    """

    database: DataStore
    collection: str
    model: Optional[Type[Any]]

    def __init__(self, database: DataStore, collection: str, model: Optional[Type[Any]] = None) -> None:
        """
        Initialize a FakeCrud instance (typically called by `FakeAPI.register_endpoint`).

        Args:
            database: The shared `DataStore` instance used by the parent `FakeAPI`.
            collection: The name of the collection within the `DataStore` this instance manages.
            model: Optional Pydantic model class for data conversion. If provided, methods
                   will attempt to return model instances instead of dictionaries, and accept
                   model instances as input for create/update.
        """
        ...

    def list(self, **kwargs: Any) -> Union[List[Any], Dict[str, Any]]:
        """
        Simulates listing items, delegating to `DataStore.list`.

        Applies filters, sorting, pagination etc., specified in `**kwargs`.
        If `self.model` is set, converts dictionaries in the result's 'data'
        list into model instances.

        Args:
            **kwargs: Keyword arguments passed directly to `DataStore.list`.
                      See `DataStore.list` documentation for available options
                      (e.g., `filters`, `sort_by`, `page`, `page_size`, `include_related`).

        Returns:
            - If `page_size` kwarg is provided: A dictionary {'data': [...], 'meta': {...}}
              where 'data' contains model instances (if `self.model` is set) or dicts.
            - If `page_size` kwarg is *not* provided: A flat list of model instances
              (if `self.model` is set) or dictionaries.

        Example (accessed via FakeAPI):
            >>> fake_api = FakeAPI()
            >>> users_crud = fake_api.register_endpoint("users", "/users", model=UserModel)
            >>> # Assuming UserModel is a Pydantic model and DataStore has users
            >>> # Get active users, page 1, size 10
            >>> users_page = fake_api.users.list(page=1, page_size=10, filters={'is_active': True})
            >>> if users_page['data']: # Check if list is not empty
            ...     print(isinstance(users_page['data'][0], UserModel))
            True
            >>> # Get all users as a flat list
            >>> all_users = fake_api.users.list() # No page_size
            >>> if all_users:
            ...     print(isinstance(all_users[0], UserModel))
            True
        """
        ...

    def get(self, id: Any, **kwargs: Any) -> Optional[Any]:
        """
        Simulates retrieving a single item by ID, delegating to `DataStore.get`.

        If `self.model` is set and the item is found, converts the dictionary
        result into a model instance.

        Args:
            id: The unique identifier of the item to retrieve.
            **kwargs: Keyword arguments passed directly to `DataStore.get`.
                      See `DataStore.get` documentation for available options
                      (e.g., `include_deleted`, `include_related`, `fields`).

        Returns:
            - A model instance if `self.model` is set and the item is found.
            - A dictionary if `self.model` is None and the item is found.
            - `None` if the item is not found.

        Example (accessed via FakeAPI):
            >>> # Assuming fake_api.users is registered with UserModel
            >>> user = fake_api.users.get(1)
            >>> if user:
            ...     print(isinstance(user, UserModel))
            True
            ...     print(user.name) # Access model attributes
        """
        ...

    def create(self, data: Any, **kwargs: Any) -> Any:
        """
        Simulates creating an item, delegating to `DataStore.create`.

        If `data` is a Pydantic model instance, it's converted to a dictionary
        before being passed to `DataStore.create`.
        If `self.model` is set, the dictionary returned by `DataStore.create`
        is converted back into a model instance.

        Args:
            data: The item data to create. Can be a Pydantic model instance (if `self.model`
                  is set) or a dictionary. Must contain required fields, including the ID.
            **kwargs: Keyword arguments passed directly to `DataStore.create`.
                      See `DataStore.create` documentation (e.g., `skip_validation`).

        Returns:
            - A model instance of the created item if `self.model` is set.
            - A dictionary of the created item if `self.model` is None.

        Raises:
            ValidationException: If DataStore validation fails and `skip_validation` is False.

        Example (accessed via FakeAPI):
            >>> # Assuming fake_api.users is registered with UserModel
            >>> new_user_model = UserModel(id=2, name="Bob", is_active=True)
            >>> created_user = fake_api.users.create(new_user_model)
            >>> print(isinstance(created_user, UserModel))
            True
            >>> print(created_user.id)
            2
            >>> # Can also create with a dictionary
            >>> created_dict_user = fake_api.users.create({"id": 3, "name": "Charlie"})
            >>> print(isinstance(created_dict_user, UserModel)) # Still returns model if registered
            True
            >>> print(created_dict_user.id)
            3
        """
        ...

    def update(self, id: Any, data: Any, **kwargs: Any) -> Optional[Any]:
        """
        Simulates updating an item by ID, delegating to `DataStore.update`.

        Performs a **partial update**: only fields present in `data` are modified.
        If `data` is a Pydantic model instance, it's converted to a dictionary first
        (using `exclude_unset=True` if available, otherwise all fields).
        If `self.model` is set, the dictionary returned by `DataStore.update`
        is converted back into a model instance.

        Args:
            id: The unique identifier of the item to update.
            data: Data containing updates. Can be a Pydantic model instance or a dictionary.
                  If using optimistic locking (`check_version=True`, default), `data` must
                  include the correct version field (e.g., `_version`).
            **kwargs: Keyword arguments passed directly to `DataStore.update`.
                      See `DataStore.update` documentation (e.g., `skip_validation`, `check_version`).

        Returns:
            - A model instance of the updated item if `self.model` is set and update succeeds.
            - A dictionary of the updated item if `self.model` is None and update succeeds.
            - `None` if the item with the given `id` was not found.

        Raises:
            ValidationException: If DataStore validation fails and `skip_validation` is False.
            ValueError: If `check_version` is True and the version mismatches.

        Example (accessed via FakeAPI):
            >>> # Assuming user id=1 exists, _version=1, registered with UserModel
            >>> update_payload = {"name": "Alice Smith", "_version": 1}
            >>> updated_user = fake_api.users.update(1, update_payload)
            >>> if updated_user:
            ...     print(isinstance(updated_user, UserModel))
            True
            ...     print(updated_user.name)
            Alice Smith
            ...     print(updated_user._version) # Version incremented by DataStore
            2
        """
        ...

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """
        Simulates deleting an item by ID, delegating directly to `DataStore.delete`.

        Args:
            id: The unique identifier of the item to delete.
            **kwargs: Keyword arguments passed directly to `DataStore.delete`.
                      See `DataStore.delete` documentation (e.g., `soft_delete`, `cascade`).

        Returns:
            `True` if the item was found and deleted (or soft-deleted), `False` otherwise.

        Example (accessed via FakeAPI):
            >>> # Assuming user id=1 exists
            >>> was_deleted = fake_api.users.delete(1, soft_delete=True)
            >>> print(was_deleted)
            True
            >>> # Verify deletion
            >>> user = fake_api.users.get(1)
            >>> print(user is None)
            True
            >>> # Can still retrieve if soft-deleted
            >>> soft_deleted_user = fake_api.users.get(1, include_deleted=True)
            >>> print(soft_deleted_user is not None)
            True
        """
        ...

    def bulk_create(self, data: List[Any], **kwargs: Any) -> List[Any]:
        """
        Simulates creating multiple items, delegating to `DataStore.bulk_create`.

        Converts Pydantic model instances in `data` to dictionaries if needed.
        If `self.model` is set, converts the dictionaries returned by `DataStore`
        back into model instances.
        Inherits atomicity from `DataStore.bulk_create`: if any item fails
        validation, no items are created.

        Args:
            data: List of items to create (Pydantic models or dictionaries).
            **kwargs: Keyword arguments passed directly to `DataStore.bulk_create`.
                      See `DataStore.bulk_create` documentation (e.g., `skip_validation`).

        Returns:
            List of created items (model instances if `self.model` is set, else dicts).

        Raises:
            ValidationException: If validation fails for any item and `skip_validation` is False.

        Example (accessed via FakeAPI):
            >>> # Assuming fake_api.users registered with UserModel
            >>> new_users = [UserModel(id=10, name="Eve"), UserModel(id=11, name="Frank")]
            >>> created_list = fake_api.users.bulk_create(new_users)
            >>> print(len(created_list))
            2
            >>> if created_list:
            ...     print(isinstance(created_list[0], UserModel))
            True
        """
        ...

    def bulk_update(self, data: List[Any], **kwargs: Any) -> List[Optional[Any]]:
        """
        Simulates updating multiple items, delegating to `DataStore.bulk_update`.

        Converts Pydantic model instances in `data` to dictionaries if needed. Each
        item dictionary/model must include the 'id'.
        If `self.model` is set, converts successful update results back to models.
        Inherits atomicity from `DataStore.bulk_update`: if any item fails
        validation or version check, no items are updated.

        Args:
            data: List of items to update (Pydantic models or dictionaries). Each must
                  contain 'id' and potentially the version field if `check_version=True`.
            **kwargs: Keyword arguments passed directly to `DataStore.bulk_update`.
                      See `DataStore.bulk_update` documentation (e.g., `skip_validation`, `check_version`).

        Returns:
            List containing updated items (models or dicts) or `None` for items not found.
            Order matches the input `data`.

        Raises:
            ValidationException: If validation fails for any item and `skip_validation` is False.
            ValueError: If `check_version` is True and a version conflict occurs.

        Example (accessed via FakeAPI):
            >>> # Assuming users 10, 11 exist with _version=1
            >>> updates = [
            ...     {"id": 10, "name": "Eve Smith", "_version": 1},
            ...     {"id": 11, "is_active": False, "_version": 1},
            ...     {"id": 99, "name": "Ghost", "_version": 1} # Non-existent ID
            ... ]
            >>> updated_list = fake_api.users.bulk_update(updates)
            >>> print(len(updated_list))
            3
            >>> if updated_list[0]: print(updated_list[0].name)
            Eve Smith
            >>> if updated_list[1]: print(updated_list[1].is_active)
            False
            >>> print(updated_list[2]) # Item 99 not found
            None
        """
        ...

    def bulk_delete(self, ids: List[Any], **kwargs: Any) -> int:
        """
        Simulates deleting multiple items by ID, delegating to `DataStore.bulk_delete`.

        Note: Inherits non-atomic behavior from `DataStore.bulk_delete`. Deletes
        are attempted individually.

        Args:
            ids: List of unique identifiers for items to delete.
            **kwargs: Keyword arguments passed directly to `DataStore.bulk_delete`.
                      See `DataStore.bulk_delete` documentation (e.g., `soft_delete`, `cascade`).

        Returns:
            The number of items successfully deleted (or soft-deleted) from the
            primary collection (cascaded deletes in other collections are not counted).

        Example (accessed via FakeAPI):
            >>> # Assuming users 10, 11 exist
            >>> deleted_count = fake_api.users.bulk_delete([10, 11, 99]) # ID 99 doesn't exist
            >>> print(deleted_count)
            2
        """
        ...

class FakeAPI(API):
    """
    A test double (fake) implementation of `crudclient.api.API` for testing.

    Simulates the `API` interface but uses an in-memory `DataStore` instead of
    making real HTTP requests. Ideal for integration tests of services that depend
    on the `API`, providing speed and isolation from external services.

    Core Components:
    *   `self.database`: An instance of `DataStore` holding all the fake data.
        Accessible for direct manipulation during test setup or assertions.
    *   `self.endpoints`: A dictionary mapping registered endpoint names to
        `FakeCrud` instances.
    *   `FakeCrud` instances: Created via `register_endpoint`, these handle CRUD
        operations for a specific `DataStore` collection and manage optional
        Pydantic model conversion. Accessed as attributes (e.g., `fake_api.users`).

    Workflow:
    1.  Initialize `FakeAPI()`. This creates an internal `DataStore`.
    2.  Use `register_endpoint()` to define the API resources you need to simulate.
        Specify the attribute name (`name`), the `DataStore` collection (`collection`),
        and optionally a Pydantic `model`.
    3.  Interact with the registered endpoints as attributes on the `FakeAPI` instance
        (e.g., `fake_api.users.create(...)`, `fake_api.products.list(...)`).
    4.  Optionally use convenience methods (`define_relationship`, `add_validation_rule`, etc.)
        to configure the underlying `DataStore` directly through the `FakeAPI` instance.
    5.  Directly access `fake_api.database` to pre-populate data or assert state
        after operations.

    Example:
        >>> from crudclient.models import BaseModel # Assuming a Pydantic base
        >>> from crudclient.testing import FakeAPI, DataStore

        >>> class User(BaseModel):
        ...     id: int
        ...     name: str
        ...     is_active: bool = True

        >>> # 1. Initialize
        >>> fake_api = FakeAPI()

        >>> # 2. Register endpoint 'users' linked to 'user_data' collection using User model
        >>> users_crud = fake_api.register_endpoint(
        ...     name="users",          # Access via fake_api.users
        ...     endpoint="/api/v1/users", # Path (mostly informational for FakeAPI)
        ...     collection="user_data", # Collection name in fake_api.database
        ...     model=User             # Use User model for conversion
        ... )
        >>> # users_crud is the FakeCrud instance, also accessible as fake_api.users

        >>> # (Optional) Configure DataStore via FakeAPI convenience methods
        >>> fake_api.add_unique_constraint(fields="name", collection="user_data")

        >>> # 3. Interact via registered endpoint attribute
        >>> new_user = User(id=1, name="Alice")
        >>> created_user = fake_api.users.create(new_user)
        >>> print(isinstance(created_user, User))
        True

        >>> # 4. Retrieve data
        >>> retrieved_user = fake_api.users.get(1)
        >>> print(retrieved_user.name)
        Alice

        >>> # 5. List data
        >>> user_list_page = fake_api.users.list(page_size=10, filters={"is_active": True})
        >>> print(len(user_list_page['data']))
        1

        >>> # 6. Access underlying DataStore for assertions/setup
        >>> assert fake_api.database.get("user_data", 1)['name'] == "Alice"
        >>> # Pre-populate data directly
        >>> fake_api.database.create("user_data", {"id": 2, "name": "Bob", "is_active": False, "_version": 1})
        >>> bob = fake_api.users.get(2)
        >>> print(bob.name, bob.is_active)
        Bob False
    """

    client_class: Type[Client]
    database: DataStore
    endpoints: Dict[str, FakeCrud]

    def __init__(
        self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, database: Optional[DataStore] = None, **kwargs: Any
    ) -> None:
        """
        Initialize a FakeAPI instance.

        Creates an internal `DataStore` to manage fake data, unless an existing
        `DataStore` instance is provided.

        Args:
            client: Ignored by FakeAPI, present for interface compatibility.
            client_config: Ignored by FakeAPI, present for interface compatibility.
            database: Optional `DataStore` instance to use. If `None`, a new
                      `DataStore` is created internally. Useful for sharing state
                      between multiple `FakeAPI` instances or pre-configuring the store.
            **kwargs: Additional arguments passed to the parent `API` constructor (mostly ignored).
        """
        ...

    def register_endpoint(
        self,
        name: str,
        endpoint: str,
        collection: Optional[str] = None,
        model: Optional[Type[Any]] = None,
        **kwargs: Any,
    ) -> FakeCrud:
        """
        Registers a simulated CRUD endpoint, making it accessible as an attribute.

        This is the primary way to configure the `FakeAPI`. It creates a `FakeCrud`
        instance that links the attribute `name` to a specific `collection` in the
        `DataStore`, optionally using a `model` for data conversion.

        Args:
            name: The attribute name used to access this endpoint on the `FakeAPI`
                  instance (e.g., "users" makes `fake_api.users` available).
            endpoint: The simulated API path string (e.g., "/api/v1/users"). This is
                      primarily for documentation or potential future use; it's not
                      used for routing within `FakeAPI` itself.
            collection: The name of the collection within the internal `DataStore`
                        (`self.database`) that this endpoint will interact with.
                        If `None`, defaults to the `name` argument.
            model: Optional Pydantic model class. If provided, the associated `FakeCrud`
                   instance will automatically convert data between dictionaries
                   (used by `DataStore`) and instances of this model.
            **kwargs: Additional keyword arguments (currently ignored, for future compatibility).

        Returns:
            The newly created and registered `FakeCrud` instance, which is also
            accessible via `getattr(fake_api, name)`.

        Raises:
            AttributeError: If the `name` conflicts with an existing attribute.

        Example:
            >>> fake_api = FakeAPI()
            >>> # Register endpoint 'products', linked to 'product_catalog' collection, using Product model
            >>> products_crud = fake_api.register_endpoint(
            ...     name="products",
            ...     endpoint="/v2/products",
            ...     collection="product_catalog", # Use specific collection name in DataStore
            ...     model=ProductModel
            ... )
            >>> # Now interact using fake_api.products
            >>> new_product = ProductModel(id='xyz', name='Widget', price=10.0)
            >>> created = fake_api.products.create(new_product)
            >>> print(isinstance(created, ProductModel))
            True
            >>> # DataStore now contains the item in the 'product_catalog' collection
            >>> assert fake_api.database.get("product_catalog", 'xyz')['name'] == 'Widget'
        """
        ...

    def define_relationship(
        self,
        source_collection: str,
        source_field: str,
        target_collection: str,
        target_field: str,
        relationship_type: str,
        cascade_delete: bool = False,
    ) -> "FakeAPI":
        """
        Convenience method to define a relationship in the underlying DataStore.

        Delegates directly to `self.database.define_relationship(...)`. Useful for
        setting up referential integrity or cascade deletes within the test data.

        See `DataStore.define_relationship` for detailed parameter descriptions.

        Args:
            source_collection: Name of the collection with the foreign key.
            source_field: The foreign key field name.
            target_collection: Name of the collection being referenced.
            target_field: The primary key field name in the target collection.
            relationship_type: Relationship type ('one_to_one', 'many_to_one', etc.).
            cascade_delete: Enable cascade deletes from target to source.

        Returns:
            The FakeAPI instance for chaining configuration calls.
        """
        ...

    def add_validation_rule(
        self,
        field: str,
        validator_func: Callable[[Any], bool],
        error_message: str,
        collection: Optional[str] = None,
    ) -> "FakeAPI":
        """
        Convenience method to add a validation rule to the underlying DataStore.

        Delegates directly to `self.database.add_validation_rule(...)`. Useful for
        enforcing custom data constraints within the test data.

        See `DataStore.add_validation_rule` for detailed parameter descriptions.

        Args:
            field: Field name to validate.
            validator_func: Function `(value) -> bool` returning True if valid.
            error_message: Message for `ValidationException` if validation fails.
            collection: Optional specific collection name to apply rule to (default: all).

        Returns:
            The FakeAPI instance for chaining configuration calls.
        """
        ...

    def add_unique_constraint(
        self,
        fields: Union[str, List[str]],
        error_message: Optional[str] = None,
        collection: Optional[str] = None,
    ) -> "FakeAPI":
        """
        Convenience method to add a unique constraint to the underlying DataStore.

        Delegates directly to `self.database.add_unique_constraint(...)`. Useful for
        enforcing uniqueness constraints within the test data.

        See `DataStore.add_unique_constraint` for detailed parameter descriptions.

        Args:
            fields: Field name string or list of field name strings for the constraint.
            error_message: Optional custom error message for `ValidationException`.
            collection: Optional specific collection name to apply constraint to (default: all).

        Returns:
            The FakeAPI instance for chaining configuration calls.
        """
        ...

    def set_timestamp_tracking(
        self,
        enabled: bool,
        created_field: str = "_created_at",
        updated_field: str = "_updated_at",
    ) -> "FakeAPI":
        """
        Convenience method to configure timestamp tracking in the underlying DataStore.

        Delegates directly to `self.database.set_timestamp_tracking(...)`. Controls
        automatic population of creation/update timestamps in the test data.

        See `DataStore.set_timestamp_tracking` for detailed parameter descriptions.

        Args:
            enabled: `True` to enable automatic timestamps, `False` to disable.
            created_field: Field name for creation timestamp (default: `_created_at`).
            updated_field: Field name for update timestamp (default: `_updated_at`).

        Returns:
            The FakeAPI instance for chaining configuration calls.
        """
        ...

    def __getattr__(self, name: str) -> FakeCrud:
        """
        Provides access to registered endpoints via attribute lookup.

        Allows accessing `FakeCrud` instances using the `name` provided during
        `register_endpoint` (e.g., `fake_api.users`).

        Args:
            name: The name of the registered endpoint.

        Returns:
            The corresponding `FakeCrud` instance.

        Raises:
            AttributeError: If no endpoint with the given `name` has been registered.
        """
        ...

    def _register_endpoints(self) -> None:
        """
        Register default endpoints. This is a no-op in FakeAPI.
        """
        ...

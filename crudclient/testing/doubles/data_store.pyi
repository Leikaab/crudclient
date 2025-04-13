# crudclient/testing/doubles/data_store.pyi
from typing import Any, Callable, Dict, List, Optional, Union

from .data_store_definitions import (
    Relationship,
    UniqueConstraint,
    ValidationException,
    ValidationRule,
)

class DataStore:
    """
    An in-memory data store simulating a relational database backend.

    Designed primarily for integration testing, often used internally by `FakeAPI`
    or directly when needing fine-grained control over test data state without
    external dependencies like a real database.

    It allows defining collections (tables), relationships (foreign keys),
    validation rules, and unique constraints. It supports standard CRUD operations
    (Create, Read, Update, Delete) and their bulk counterparts.

    Key Features:
    *   **Collections:** Stores data in named lists of dictionaries (e.g., `store.collections['users']`).
    *   **Relationships:** Defines connections (one-to-one, one-to-many, etc.)
        between collections, enforcing referential integrity and enabling cascade deletes.
    *   **Validation:** Enforces custom rules (`add_validation_rule`) and unique
        constraints (`add_unique_constraint`) during data modification.
    *   **CRUD Operations:** Provides `list`, `get`, `create`, `update`, `delete` methods.
    *   **Bulk Operations:** `bulk_create`, `bulk_update`, `bulk_delete` for efficiency.
    *   **Filtering & Sorting:** Advanced filtering (e.g., `field__in`, `field__gt`) and
        multi-field sorting in `list`.
    *   **Pagination:** Built-in pagination for `list` operations.
    *   **Soft Deletes:** Option to mark items as deleted (`_deleted` field by default)
        instead of removing them permanently.
    *   **Optimistic Locking:** Version tracking (`_version` field by default) to prevent
        lost updates using `check_version=True` in `update`/`bulk_update`.
    *   **Timestamps:** Automatic tracking of creation and update times
        (`_created_at`, `_updated_at` fields by default) if enabled via
        `set_timestamp_tracking`.

    Default Internal Fields (configurable):
    *   `_version`: For optimistic locking.
    *   `_deleted`: Boolean flag for soft deletes.
    *   `_created_at`: Timestamp of creation.
    *   `_updated_at`: Timestamp of last update.

    Example (Basic Usage):
        >>> store = DataStore().set_timestamp_tracking(True)
        >>> store.get_collection("users") # Implicitly creates 'users' collection
        >>> user = store.create("users", {"id": 1, "name": "Alice", "email": "alice@example.com"})
        >>> print(user) # doctest: +SKIP
        {'id': 1, 'name': 'Alice', 'email': 'alice@example.com', '_version': 1, '_created_at': ..., '_updated_at': ...}
        >>> users_page = store.list("users", page_size=10, sort_by="name")
        >>> print(users_page['data'][0]['name'])
        Alice
    """

    collections: Dict[str, List[Dict[str, Any]]]
    relationships: List[Relationship]
    validation_rules: List[ValidationRule]
    unique_constraints: List[UniqueConstraint]
    deleted_items: Dict[str, List[Dict[str, Any]]]
    version_field: str
    deleted_field: str
    created_at_field: str
    updated_at_field: str
    track_timestamps: bool

    def __init__(self) -> None:
        """Initializes an empty DataStore."""
        ...

    def get_collection(self, name: str) -> List[Dict[str, Any]]:
        """
        Retrieves a collection by name, creating it if it doesn't exist.

        Args:
            name: The name of the collection.

        Returns:
            A list representing the collection's data.
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
    ) -> "DataStore":
        """
        Defines a relationship between two collections, simulating foreign keys.

        This enforces referential integrity:
        - Prevents creating/updating source items pointing to non-existent target items.
        - Prevents deleting target items that are referenced by source items (unless
          `cascade_delete` is True).
        - `relationship_type` influences cardinality checks (e.g., 'one_to_one' ensures
          a target item is referenced by at most one source item via this relationship).

        Note:
            Relationship checks can add overhead, especially on bulk operations or
            large datasets. Define them judiciously based on testing needs.

        Args:
            source_collection: Name of the collection containing the foreign key (e.g., 'orders').
            source_field: The field in the source collection holding the foreign key (e.g., 'user_id').
            target_collection: Name of the collection being referenced (e.g., 'users').
            target_field: The field in the target collection being referenced (usually the primary key, e.g., 'id').
            relationship_type: Type of relationship ('one_to_one', 'one_to_many', 'many_to_one', 'many_to_many').
                               Determines cardinality checks and validation behavior.
            cascade_delete: If True, deleting an item in the `target_collection` will trigger
                            the deletion (hard or soft, matching the original delete) of all
                            referencing items in the `source_collection` via this relationship.
                            Defaults to False.

        Returns:
            The DataStore instance for chaining.

        Example:
            >>> store = DataStore()
            >>> store.get_collection("users")
            >>> store.get_collection("orders")
            >>> # An order belongs to a user (users.id <- orders.user_id)
            >>> store.define_relationship(
            ...     source_collection='orders',      # Table with the foreign key
            ...     source_field='user_id',        # The foreign key column
            ...     target_collection='users',       # Table being referenced
            ...     target_field='id',             # The primary key column in the target
            ...     relationship_type='many_to_one', # Many orders can belong to one user
            ...     cascade_delete=True            # If user is deleted, delete their orders
            ... )
            >>> user = store.create("users", {"id": 1, "name": "Alice"})
            >>> order = store.create("orders", {"id": 101, "user_id": 1, "item": "Book"})
            >>> # store.create("orders", {"id": 102, "user_id": 99, "item": "Pen"}) # Raises ValidationException (user 99 doesn't exist)
            >>> store.delete("users", 1, cascade=True) # Deletes user 1 AND order 101
            >>> store.list("orders")['data']
            []
        """
        ...

    def add_validation_rule(
        self,
        field: str,
        validator_func: Callable[[Any], bool],
        error_message: str,
        collection: Optional[str] = None,
    ) -> "DataStore":
        """
        Adds a custom validation rule for a specific field within a collection.

        The rule is checked during `create` and `update` operations unless
        `skip_validation` is set to True for those operations.

        Args:
            field: The name of the field to validate (e.g., 'email').
            validator_func: A callable (function, lambda) that accepts the field's value
                            and returns `True` if the value is valid, `False` otherwise.
            error_message: The message for the `ValidationException` raised if the
                           `validator_func` returns `False`.
            collection: The specific collection name to apply this rule to. If `None`,
                        the rule applies to the specified `field` in *all* collections
                        where it exists. Defaults to None.

        Returns:
            The DataStore instance for chaining.

        Example:
            >>> store = DataStore()
            >>> def is_positive(value): return isinstance(value, (int, float)) and value > 0
            >>> store.add_validation_rule(
            ...     field='quantity',
            ...     validator_func=is_positive,
            ...     error_message='Quantity must be a positive number.',
            ...     collection='order_items'
            ... )
            >>> # This would raise ValidationException if quantity <= 0
            >>> # store.create('order_items', {'id': 1, 'product': 'apple', 'quantity': -5})
        """
        ...

    def add_unique_constraint(
        self,
        fields: Union[str, List[str]],
        error_message: Optional[str] = None,
        collection: Optional[str] = None,
    ) -> "DataStore":
        """
        Adds a unique constraint across one or more fields within a collection.

        Ensures that no two items in the specified collection have the same value (or
        combination of values) for the given field(s). Checked during `create` and
        `update` operations unless `skip_validation` is True.

        Note:
            Adding a constraint to a collection that already contains duplicate data
            for the specified fields will immediately raise a `ValidationException`.

        Args:
            fields: A single field name (e.g., 'email') or a list of field names
                    (e.g., ['first_name', 'last_name']) that must be unique together.
            error_message: An optional custom error message for the `ValidationException`.
                           If None, a default message is generated.
            collection: The specific collection name to apply this constraint to. If `None`,
                        the constraint applies to the specified `field(s)` in *all*
                        collections where they exist. Defaults to None.

        Returns:
            The DataStore instance for chaining.

        Raises:
            ValidationException: If pre-existing data violates the new constraint.

        Example:
            >>> store = DataStore()
            >>> store.get_collection("users")
            >>> store.add_unique_constraint(fields='email', collection='users')
            >>> store.create("users", {"id": 1, "email": "test@example.com"})
            >>> # This would raise ValidationException:
            >>> # store.create("users", {"id": 2, "email": "test@example.com"})
        """
        ...

    def set_timestamp_tracking(
        self,
        enabled: bool,
        created_field: str = "_created_at",
        updated_field: str = "_updated_at",
    ) -> "DataStore":
        """
        Enables or disables automatic timestamp tracking for item creation and updates.

        When enabled, the specified fields will be automatically added and populated
        with the current UTC timestamp (using `datetime.utcnow()`) during `create`
        and `update` operations.

        Args:
            enabled: Set to `True` to enable timestamp tracking, `False` to disable.
            created_field: The name of the field to store the creation timestamp.
                           Defaults to `_created_at`.
            updated_field: The name of the field to store the last update timestamp.
                           Defaults to `_updated_at`.

        Returns:
            The DataStore instance for chaining.

        Example:
            >>> store = DataStore().set_timestamp_tracking(True)
            >>> item = store.create("items", {"id": 1, "value": "A"})
            >>> print(item['_created_at']) # Shows creation timestamp
            >>> print(item['_updated_at']) # Shows creation timestamp initially
            >>> updated_item = store.update("items", 1, {"value": "B"})
            >>> print(updated_item['_updated_at']) # Shows a later timestamp
        """
        ...
    # --- Core CRUD Operations ---

    def list(
        self,
        collection: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[Union[str, List[str]]] = None,
        sort_desc: Union[bool, List[bool]] = False,
        page: int = 1,
        page_size: Optional[int] = None,
        include_deleted: bool = False,
        include_related: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Lists items from a collection with filtering, sorting, and pagination.

        Provides flexible querying of the in-memory data.

        Args:
            collection: The name of the collection to query.
            filters: Dictionary for filtering. Keys are field names, values are filter criteria.
                - Simple match: `{'status': 'active'}`
                - Nested fields (dot notation): `{'address.city': 'London'}`
                - Special suffixes (double underscore):
                    - `field__in`: Value is a list. `{'id__in': [1, 2, 3]}`
                    - `field__contains`: Value is string/list. `{'tags__contains': 'urgent'}` (case-sensitive substring/element check)
                    - `field__gt`, `field__gte`, `field__lt`, `field__lte`: Comparisons. `{'price__gt': 100}`
                    - `field__isnull`: Value is boolean. `{'manager_id__isnull': True}`
            sort_by: Field name or list of field names for sorting. Dot notation supported.
            sort_desc: Boolean or list of booleans corresponding to `sort_by`. `True` for descending.
                       If single bool, applies to all `sort_by` fields.
            page: Page number (1-based). Defaults to 1.
            page_size: Items per page. `None` disables pagination.
            include_deleted: If `True`, includes soft-deleted items. Requires `deleted_field` setting.
            include_related: List of relationship *source* collection names to embed related data.
                             Requires relationships to be defined. Simulates JOINs/eager loading.
                             E.g., if `orders` relates to `users`, listing `users` with
                             `include_related=['orders']` would embed matching orders in each user.
            fields: Optional list of field names to include in results. `None` returns all fields.

        Returns:
            Dict with 'data' (list of items) and 'meta' (pagination info):
            - `meta['total_items']`: Total matching items (pre-pagination).
            - `meta['total_pages']`: Total pages available.
            - `meta['current_page']`: Requested page number.
            - `meta['page_size']`: Requested page size.

        Examples:
            >>> store = DataStore()
            >>> store.bulk_create("products", [
            ...     {"id": 1, "name": "Laptop", "price": 1200, "category": "Electronics", "tags": ["tech", "sale"]},
            ...     {"id": 2, "name": "Mouse", "price": 25, "category": "Electronics", "tags": ["tech"]},
            ...     {"id": 3, "name": "Keyboard", "price": 75, "category": "Electronics", "tags": ["tech", "new"]},
            ...     {"id": 4, "name": "Desk Chair", "price": 150, "category": "Furniture", "tags": ["office"]},
            ... ])
            >>> # Electronics cheaper than $100, sorted by price ascending
            >>> result1 = store.list("products", filters={"category": "Electronics", "price__lt": 100}, sort_by="price")
            >>> print([p['name'] for p in result1['data']])
            ['Mouse', 'Keyboard']
            >>> # Products with 'tech' tag OR 'office' tag (using __in)
            >>> result2 = store.list("products", filters={"tags__contains": ["tech", "office"]}) # Note: __contains checks elements in list
            >>> print(len(result2['data']))
            4
            >>> # Page 2 of products, 2 per page, sorted by name descending
            >>> result3 = store.list("products", sort_by="name", sort_desc=True, page=2, page_size=2)
            >>> print([p['name'] for p in result3['data']])
            ['Keyboard', 'Desk Chair']
            >>> print(result3['meta'])
            {'total_items': 4, 'total_pages': 2, 'current_page': 2, 'page_size': 2}

            >>> # Example with include_related
            >>> store.get_collection("orders")
            >>> store.define_relationship('orders', 'product_id', 'products', 'id', 'many_to_one')
            >>> store.create("orders", {"id": 101, "product_id": 1, "qty": 1})
            >>> store.create("orders", {"id": 102, "product_id": 3, "qty": 2})
            >>> # List products and include their orders
            >>> result4 = store.list("products", include_related=["orders"], fields=["id", "name", "orders"])
            >>> laptop = next(p for p in result4['data'] if p['id'] == 1)
            >>> keyboard = next(p for p in result4['data'] if p['id'] == 3)
            >>> print(laptop['orders'][0]['id'])
            101
            >>> print(keyboard['orders'][0]['id'])
            102
        """
        ...

    def get(
        self,
        collection: str,
        id: Any,
        include_deleted: bool = False,
        include_related: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single item from a collection by its primary identifier ('id').

        Args:
            collection: The name of the collection where the item resides.
            id: The unique identifier of the item to retrieve. The field used as ID
                is typically 'id', but depends on the data structure.
            include_deleted: If `True`, allows retrieval even if the item is marked
                             as soft-deleted. Defaults to `False`.
            include_related: A list of relationship names to embed in the result.
                             See `list()` method for details.
            fields: An optional list of field names to include in the returned item.
                    If `None` (default), all fields are returned.

        Returns:
            A deep copy of the item dictionary if found and not filtered out (by soft
            delete status unless `include_deleted` is True), otherwise `None`.

        Example:
            >>> store = DataStore()
            >>> store.create("users", {"id": "u1", "name": "Bob"})
            >>> user = store.get("users", "u1")
            >>> print(user)
            {'id': 'u1', 'name': 'Bob', '_version': 1}
            >>> non_existent = store.get("users", "u2")
            >>> print(non_existent)
            None
        """
        ...

    def create(self, collection: str, data: Dict[str, Any], skip_validation: bool = False) -> Dict[str, Any]:
        """
        Creates a new item in the specified collection.

        Assigns an initial version (default field `_version` = 1) and adds timestamps
        (default fields `_created_at`, `_updated_at`) if timestamp tracking is enabled.
        Performs validation checks unless `skip_validation` is True.

        Args:
            collection: The name of the collection to add the item to.
            data: A dictionary representing the item's data. Must include the primary
                  identifier field (usually 'id') unless it's auto-generated (not
                  a built-in feature of DataStore itself).
            skip_validation: If `True`, bypasses all defined validation rules, unique
                             constraints, and relationship integrity checks. Defaults to `False`.

        Returns:
            A deep copy of the newly created item dictionary, including any
            automatically added fields like version or timestamps.

        Raises:
            ValidationException: If any validation rule, unique constraint, or
                                 referential integrity check fails and `skip_validation` is `False`.
            KeyError: If the collection does not exist (use `get_collection` first if unsure).

        Example:
            >>> store = DataStore().set_timestamp_tracking(True)
            >>> store.get_collection("products")
            >>> new_product = store.create(
            ...     "products",
            ...     {"id": 10, "name": "Widget", "price": 9.99}
            ... )
            >>> print(new_product)
            {'id': 10, 'name': 'Widget', 'price': 9.99, '_version': 1, '_created_at': ..., '_updated_at': ...}
        """
        ...

    def update(
        self,
        collection: str,
        id: Any,
        data: Dict[str, Any],
        skip_validation: bool = False,
        check_version: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing item in a collection identified by its ID.

        Performs a **partial update**: only fields present in the `data` dictionary
        are modified. Other existing fields remain untouched.

        Increments the version field (default `_version`) and updates the timestamp
        field (default `_updated_at`) if enabled. Performs validation checks unless
        `skip_validation` is True. Supports optimistic locking via `check_version`.

        Args:
            collection: The name of the collection containing the item.
            id: The identifier of the item to update.
            data: Dictionary containing fields and their new values. **Do not include 'id'.**
                  Must include the version field (e.g., `_version`) if `check_version` is True.
            skip_validation: If `True`, bypasses validation rules, unique constraints,
                             and relationship checks. Defaults to `False`.
            check_version: If `True` (default), enables optimistic locking. Requires `data`
                           to include the version field (e.g., `_version`) with a value
                           matching the item's current version in the store.
                           If `False`, version checking is skipped.

        Returns:
            A deep copy of the fully updated item dictionary if found and updated
            successfully, otherwise `None` (if item with `id` not found).

        Raises:
            ValidationException: If validation fails and `skip_validation` is `False`.
            ValueError: If `check_version` is `True` and the version field is missing
                        in `data` or its value doesn't match the stored item's version.
            KeyError: If the collection does not exist.

        Example:
            >>> store = DataStore()
            >>> item = store.create("items", {"id": 5, "status": "pending", "value": 10})
            >>> print(item['_version'])
            1
            >>> # Update status, providing the current version for optimistic lock check
            >>> update_payload = {"status": "completed", "_version": 1}
            >>> updated_item = store.update("items", 5, update_payload)
            >>> print(updated_item) # Value is preserved, version incremented
            {'id': 5, 'status': 'completed', 'value': 10, '_version': 2}
            >>> # Attempting the same update again fails due to version mismatch
            >>> try:
            ...     store.update("items", 5, update_payload) # Still using _version: 1
            ... except ValueError as e:
            ...     print(e) # doctest: +SKIP
            Optimistic lock failed for item 5 in collection items. Expected version 1, found 2.
            >>> # Update without version check
            >>> updated_again = store.update("items", 5, {"value": 20}, check_version=False)
            >>> print(updated_again['value'], updated_again['_version'])
            20 3
        """
        ...

    def delete(
        self,
        collection: str,
        id: Any,
        soft_delete: bool = False,
        cascade: bool = False,
    ) -> bool:
        """
        Deletes an item from a collection by its ID.

        Supports hard deletes (removing the item) and soft deletes (marking with a flag).
        Can optionally cascade deletes to related items based on defined relationships.

        Args:
            collection: The name of the collection containing the item.
            id: The identifier of the item to delete.
            soft_delete: If `True`, marks the item using the `deleted_field` (default `_deleted`)
                         and updates `updated_at_field` (if enabled). The item is moved
                         from the main collection list to an internal `deleted_items` store
                         for potential retrieval via `get(..., include_deleted=True)` or
                         `list(..., include_deleted=True)`. Defaults to `False` (hard delete).
            cascade: If `True`, checks relationships where this collection is the *target*
                     and `cascade_delete` was set to `True` during definition. It then
                     performs deletes on the referencing items in the *source* collections.
                     The type of delete (hard or soft) performed on related items matches
                     the `soft_delete` argument used for the initial delete.
                     Defaults to `False`.

        Returns:
            `True` if an item with the given ID was found in the active collection and
            deleted (or marked as deleted), `False` otherwise. Note that cascading
            deletes do not affect the return value of the *initial* delete operation.

        Example:
            >>> store = DataStore().set_timestamp_tracking(True)
            >>> store.create("users", {"id": 1, "name": "Charlie"})
            >>> store.create("tasks", {"id": 101, "title": "Task 1", "user_id": 1})
            >>> store.create("tasks", {"id": 102, "title": "Task 2", "user_id": 1})
            >>> store.define_relationship(
            ...     'tasks', 'user_id', 'users', 'id', 'many_to_one', cascade_delete=True
            ... )
            >>> # Soft delete user 1, cascading to tasks
            >>> deleted = store.delete("users", 1, soft_delete=True, cascade=True)
            >>> print(deleted) # User 1 was found and soft-deleted
            True
            >>> print(store.get("users", 1)) # Not found in active collection
            None
            >>> print(store.get("users", 1, include_deleted=True)['_deleted']) # Found in deleted items
            True
            >>> # Tasks were also soft-deleted due to cascade=True and soft_delete=True
            >>> print(store.list("tasks")['data'])
            []
            >>> print(len(store.list("tasks", include_deleted=True)['data']))
            2
            >>> print(store.get("tasks", 101, include_deleted=True)['_deleted'])
            True

            >>> # Hard delete example (no cascade needed here)
            >>> store.create("items", {"id": 99})
            >>> deleted_hard = store.delete("items", 99, soft_delete=False)
            >>> print(deleted_hard)
            True
            >>> print(store.get("items", 99))
            None
            >>> print(store.get("items", 99, include_deleted=True)) # Also None for hard delete
            None
        """
        ...
    # --- Bulk Operations ---

    def bulk_create(
        self,
        collection: str,
        items: List[Dict[str, Any]],
        skip_validation: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Creates multiple items in the specified collection efficiently.

        Applies validation to all items before creating any. If validation fails
        for *any* item (and `skip_validation` is False), a `ValidationException`
        is raised, and **no items** from the batch are created (atomic behavior).

        Assigns initial versions and timestamps (if enabled) to each item.

        Args:
            collection: The name of the collection.
            items: A list of dictionaries, each representing an item to create.
                   Must conform to the structure expected by `create`.
            skip_validation: If `True`, bypasses validation for all items. Defaults to `False`.

        Returns:
            A list containing deep copies of the newly created item dictionaries,
            in the same order as the input `items`.

        Raises:
            ValidationException: If validation fails for any item and `skip_validation` is `False`.
            KeyError: If the collection does not exist.

        Example:
            >>> store = DataStore()
            >>> store.get_collection("logs")
            >>> store.add_unique_constraint("id", collection="logs")
            >>> new_logs = store.bulk_create("logs", [
            ...     {"id": "l1", "level": "info", "message": "Started"},
            ...     {"id": "l2", "level": "warn", "message": "Deprecated API used"},
            ... ])
            >>> print(len(new_logs))
            2
            >>> # This would raise ValidationException because 'l1' already exists
            >>> # store.bulk_create("logs", [{"id": "l3", "level": "error"}, {"id": "l1", "level": "info"}])
        """
        ...

    def bulk_update(
        self,
        collection: str,
        items: List[Dict[str, Any]],
        skip_validation: bool = False,
        check_version: bool = True,
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Updates multiple items in the specified collection efficiently.

        Performs partial updates for each item based on the provided dictionaries.
        Applies validation and version checks (if enabled) to all items before
        applying any updates. If validation or version check fails for *any* item,
        an exception is raised, and **no updates** from the batch are applied (atomic behavior).

        Args:
            collection: The name of the collection.
            items: List of dictionaries. Each must contain 'id' and the fields to update.
                   If `check_version` is True, each must also contain the correct `_version`.
            skip_validation: If `True`, bypasses validation for all updates. Defaults to `False`.
            check_version: If `True` (default), performs optimistic locking checks for all items.

        Returns:
            List containing deep copies of updated items, or `None` for items not found.
            Order matches the input `items`. Returns an empty list if the operation
            failed validation/version checks before applying changes.

        Raises:
            ValidationException: If validation fails for any item and `skip_validation` is `False`.
            ValueError: If `check_version` is `True` and a version conflict occurs for any item.
            KeyError: If collection doesn't exist or an item dict lacks 'id'.

        Example:
            >>> store = DataStore()
            >>> store.bulk_create("tasks", [
            ...     {"id": 1, "status": "todo", "priority": 1},
            ...     {"id": 2, "status": "todo", "priority": 2},
            ...     {"id": 3, "status": "todo", "priority": 3},
            ... ]) # Versions are now 1
            >>> updates = [
            ...     {"id": 1, "status": "done", "_version": 1},
            ...     {"id": 2, "status": "inprogress", "_version": 1},
            ...     {"id": 99, "status": "failed", "_version": 1}, # ID 99 doesn't exist
            ... ]
            >>> updated_tasks = store.bulk_update("tasks", updates)
            >>> print(updated_tasks[0]['status'], updated_tasks[0]['_version'])
            done 2
            >>> print(updated_tasks[1]['status'], updated_tasks[1]['_version'])
            inprogress 2
            >>> print(updated_tasks[2]) # Item not found
            None
            >>> # Example of atomic failure (version mismatch on id: 1)
            >>> failing_updates = [
            ...     {"id": 1, "status": "cancelled", "_version": 1}, # Wrong version (now 2)
            ...     {"id": 3, "status": "done", "_version": 1},      # Correct version
            ... ]
            >>> try:
            ...    store.bulk_update("tasks", failing_updates)
            ... except ValueError as e:
            ...    print("Update failed as expected.") # doctest: +SKIP
            Update failed as expected.
            >>> # Verify task 3 was NOT updated due to failure on task 1
            >>> print(store.get("tasks", 3)['status'])
            todo
        """
        ...

    def bulk_delete(
        self,
        collection: str,
        ids: List[Any],
        soft_delete: bool = False,
        cascade: bool = False,
    ) -> int:
        """
        Deletes multiple items from a collection identified by their IDs.

        Calls `delete` individually for each ID in the list. Cascading behavior
        (if `cascade=True`) also applies individually for each delete.

        **Note:** Unlike `bulk_create` and `bulk_update`, this operation is **not atomic**.
        Deletes are attempted for each ID sequentially. If an error occurs during
        a cascade for one ID, it does not prevent subsequent deletes for other IDs
        in the list.

        Args:
            collection: The name of the collection.
            ids: A list of identifiers for the items to be deleted.
            soft_delete: If `True`, performs a soft delete for each item. Defaults to `False`.
            cascade: If `True`, performs cascading deletes for each item based on
                     defined relationships. Defaults to `False`.

        Returns:
            The total number of items successfully deleted (or marked as deleted)
            from the primary collection specified. This count **does not** include
            items deleted via cascading from *other* collections. It may be less
            than `len(ids)` if some IDs were not found in the target collection.

        Raises:
            KeyError: If the collection does not exist. (Relationship errors during
                      cascade might raise other exceptions, but won't stop the loop).

        Example:
            >>> store = DataStore()
            >>> store.bulk_create("items", [{"id": i, "name": f"Item {i}"} for i in range(5)])
            >>> # Delete items 1, 3, and 5 (which doesn't exist)
            >>> deleted_count = store.bulk_delete("items", [1, 3, 5])
            >>> print(deleted_count) # Only items 1 and 3 were found and deleted
            2
            >>> result = store.list("items", sort_by="id")
            >>> print([item['id'] for item in result['data']])
            [0, 2, 4]
        """
        ...

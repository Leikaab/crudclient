# crudclient/testing/doubles/data_store.pyi
from typing import Any, Callable, Dict, List, Optional, Union

from .data_store_definitions import (
    Relationship,
    UniqueConstraint,
    ValidationRule,
)


class DataStore:
    """
    An in-memory data store simulating a database for testing purposes.

    Supports collections, relationships, validation, CRUD operations,
    and bulk operations. Mimics common database features like filtering,
    sorting, pagination, soft deletes, versioning, and timestamps.
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
        target_collection: str,
        relationship_type: str,
        **kwargs: Any
    ) -> 'DataStore':
        """
        Defines a relationship between two collections.

        Args:
            source_collection: Name of the source collection.
            target_collection: Name of the target collection.
            relationship_type: Type of relationship (e.g., 'one_to_many').
            **kwargs: Additional relationship parameters (see Relationship class).

        Returns:
            The DataStore instance for chaining.
        """
        ...

    def add_validation_rule(
        self,
        field: str,
        validator_func: Callable[[Any], bool],
        error_message: str,
        collection: Optional[str] = None
    ) -> 'DataStore':
        """
        Adds a validation rule for a specific field.

        Args:
            field: The field name to validate.
            validator_func: A function that takes the field value and returns True if valid.
            error_message: The error message to raise if validation fails.
            collection: Optional collection name to apply the rule to (applies to all if None).

        Returns:
            The DataStore instance for chaining.
        """
        ...

    def add_unique_constraint(
        self,
        fields: Union[str, List[str]],
        error_message: Optional[str] = None,
        collection: Optional[str] = None
    ) -> 'DataStore':
        """
        Adds a unique constraint across one or more fields.

        Args:
            fields: A single field name or a list of field names for the constraint.
            error_message: Optional custom error message.
            collection: Optional collection name to apply the constraint to (applies to all if None).

        Returns:
            The DataStore instance for chaining.
        """
        ...

    def set_timestamp_tracking(self, enabled: bool) -> 'DataStore':
        """
        Enables or disables automatic timestamp tracking (_created_at, _updated_at).

        Args:
            enabled: True to enable, False to disable.

        Returns:
            The DataStore instance for chaining.
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
        Lists items from a collection with optional filtering, sorting, pagination,
        relationship inclusion, and field selection.

        Args:
            collection: The name of the collection to list items from.
            filters: A dictionary of filters to apply.
            sort_by: Field name(s) to sort by.
            sort_desc: Direction(s) for sorting (True for descending).
            page: The page number for pagination (1-based).
            page_size: The number of items per page.
            include_deleted: Whether to include soft-deleted items.
            include_related: List of related collection names to embed.
            fields: List of specific fields to return for each item.

        Returns:
            A dictionary containing 'data' (list of items) and 'meta' (pagination info).
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
        Retrieves a single item by its ID.

        Args:
            collection: The name of the collection.
            id: The ID of the item to retrieve.
            include_deleted: Whether to include the item if it's soft-deleted.
            include_related: List of related collection names to embed.
            fields: List of specific fields to return.

        Returns:
            The item dictionary, or None if not found or filtered out.
        """
        ...

    def create(
        self,
        collection: str,
        data: Dict[str, Any],
        skip_validation: bool = False
    ) -> Dict[str, Any]:
        """
        Creates a new item in the specified collection.

        Args:
            collection: The name of the collection.
            data: The dictionary representing the item data.
            skip_validation: If True, bypasses validation rules and constraints.

        Returns:
            A deep copy of the created item dictionary.
        """
        ...

    def update(
        self,
        collection: str,
        id: Any,
        data: Dict[str, Any],
        skip_validation: bool = False,
        check_version: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Updates an existing item by its ID.

        Args:
            collection: The name of the collection.
            id: The ID of the item to update.
            data: A dictionary containing the fields to update.
            skip_validation: If True, bypasses validation rules and constraints.
            check_version: If True, checks the '_version' field for optimistic locking.

        Returns:
            A deep copy of the updated item dictionary, or None if not found.
        """
        ...

    def delete(
        self,
        collection: str,
        id: Any,
        soft_delete: bool = False,
        cascade: bool = False
    ) -> bool:
        """
        Deletes an item by its ID.

        Args:
            collection: The name of the collection.
            id: The ID of the item to delete.
            soft_delete: If True, marks the item as deleted instead of removing it.
            cascade: If True, performs cascading deletes based on defined relationships.

        Returns:
            True if the item was deleted, False otherwise.
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
        Creates multiple items in the specified collection.

        Args:
            collection: The name of the collection.
            items: A list of dictionaries representing the items to create.
            skip_validation: If True, bypasses validation for all items.

        Returns:
            A list of deep copies of the created item dictionaries.
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
        Updates multiple items in the specified collection. Items must contain an 'id'.

        Args:
            collection: The name of the collection.
            items: A list of dictionaries representing the updates. Each must have an 'id'.
            skip_validation: If True, bypasses validation for all items.
            check_version: If True, checks the '_version' field for optimistic locking.

        Returns:
            A list containing deep copies of updated items or None for items not found/updated.
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
        Deletes multiple items by their IDs.

        Args:
            collection: The name of the collection.
            ids: A list of IDs of the items to delete.
            soft_delete: If True, marks items as deleted instead of removing them.
            cascade: If True, performs cascading deletes.

        Returns:
            The number of items successfully deleted.
        """
        ...

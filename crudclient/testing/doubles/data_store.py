"""
Enhanced in-memory data store for FakeAPI.

This module provides a sophisticated in-memory data store with support for:
- Entity relationships
- Advanced filtering, sorting, and pagination
- Data validation and constraints
"""

import copy
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from .data_store_helpers import (
    RelationshipType,
    apply_field_selection,
    apply_filters,
    apply_pagination,
    apply_sorting,
    cascade_delete,
    include_related_data,
    include_related_item,
    validate_item,
)


class ValidationException(Exception):
    """Exception raised when data validation fails."""

    def __init__(self, message: str, errors: Optional[Dict[str, List[str]]] = None):
        """
        Initialize ValidationException.

        Args:
            message: Error message
            errors: Dictionary of field errors
        """
        super().__init__(message)
        self.errors = errors or {}


class Relationship:
    """Defines a relationship between two collections."""

    def __init__(
        self,
        source_collection: str,
        target_collection: str,
        relationship_type: str,
        source_key: str = "id",
        target_key: Optional[str] = None,
        cascade_delete: bool = False,
        bidirectional: bool = False,
        junction_collection: Optional[str] = None,
        source_junction_key: Optional[str] = None,
        target_junction_key: Optional[str] = None,
    ):
        """
        Initialize a relationship.

        Args:
            source_collection: Name of the source collection
            target_collection: Name of the target collection
            relationship_type: Type of relationship (ONE_TO_ONE, ONE_TO_MANY, MANY_TO_MANY)
            source_key: Key in the source collection to join on (default: "id")
            target_key: Key in the target collection that references the source
            cascade_delete: Whether deletes should cascade
            bidirectional: Whether the relationship is bidirectional
            junction_collection: For many-to-many, the junction collection name
            source_junction_key: For many-to-many, the key in junction that references source
            target_junction_key: For many-to-many, the key in junction that references target
        """
        self.source_collection = source_collection
        self.target_collection = target_collection
        self.relationship_type = relationship_type
        self.source_key = source_key

        # For one-to-many, target_key is the foreign key in the target collection
        # For many-to-many, target_key is the key in the target collection to join on
        self.target_key = target_key or f"{source_collection}_{source_key}"

        self.cascade_delete = cascade_delete
        self.bidirectional = bidirectional

        # For many-to-many relationships
        self.junction_collection = junction_collection
        self.source_junction_key = source_junction_key or f"{source_collection}_{source_key}"
        self.target_junction_key = target_junction_key or f"{target_collection}_{self.target_key}"


class ValidationRule:
    """Defines a validation rule for a field."""

    def __init__(
        self,
        field: str,
        validator_func: Callable[[Any], bool],
        error_message: str,
        collection: Optional[str] = None,
    ):
        """
        Initialize a validation rule.

        Args:
            field: Field name to validate
            validator_func: Function that takes a value and returns True if valid
            error_message: Error message if validation fails
            collection: Optional collection name to restrict validation to
        """
        self.field = field
        self.validator_func = validator_func
        self.error_message = error_message
        self.collection = collection

    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a value against this rule.

        Args:
            value: Value to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        is_valid = self.validator_func(value)
        return is_valid, None if is_valid else self.error_message


class UniqueConstraint:
    """Defines a unique constraint for a field or combination of fields."""

    def __init__(
        self,
        fields: Union[str, List[str]],
        error_message: Optional[str] = None,
        collection: Optional[str] = None,
    ):
        """
        Initialize a unique constraint.

        Args:
            fields: Field name or list of field names that must be unique together
            error_message: Custom error message
            collection: Optional collection name to restrict constraint to
        """
        self.fields = [fields] if isinstance(fields, str) else fields
        self.error_message = error_message or f"Values for {', '.join(self.fields)} must be unique"
        self.collection = collection
        self._values: Set[str] = set()

    def validate(self, item: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate an item against this constraint.

        Args:
            item: Item to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Create a composite key for multi-field uniqueness
        key_parts = []
        for field in self.fields:
            if field not in item:
                # If any required field is missing, we can't validate
                return True, None
            key_parts.append(str(item[field]))

        composite_key = "|".join(key_parts)

        if composite_key in self._values:
            return False, self.error_message

        # Add to tracked values
        self._values.add(composite_key)
        return True, None

    def remove_value(self, item: Dict[str, Any]) -> None:
        """
        Remove a value from the tracked set.

        Args:
            item: Item whose value should be removed
        """
        key_parts = []
        for field in self.fields:
            if field not in item:
                return
            key_parts.append(str(item[field]))

        composite_key = "|".join(key_parts)
        if composite_key in self._values:
            self._values.remove(composite_key)


class DataStore:
    """
    Enhanced in-memory data store with support for relationships, validation, and constraints.

    Features:
    - Entity relationships (one-to-one, one-to-many, many-to-many)
    - Advanced filtering with operators and nested fields
    - Sorting by multiple fields
    - Pagination with metadata
    - Data validation rules
    - Unique constraints
    - Soft deletes
    - Optimistic concurrency control
    """

    def __init__(self):
        """Initialize the enhanced data store."""
        self.collections: Dict[str, List[Dict[str, Any]]] = {}
        self.relationships: List[Relationship] = []
        self.validation_rules: List[ValidationRule] = []
        self.unique_constraints: List[UniqueConstraint] = []
        self.deleted_items: Dict[str, List[Dict[str, Any]]] = {}  # For soft deletes
        self.version_field = "_version"
        self.deleted_field = "_deleted"
        self.created_at_field = "_created_at"
        self.updated_at_field = "_updated_at"
        self.track_timestamps = True

    def get_collection(self, name: str) -> List[Dict[str, Any]]:
        """
        Get a collection by name.

        Args:
            name: Collection name

        Returns:
            List of resources
        """
        if name not in self.collections:
            self.collections[name] = []

        return self.collections[name]

    def define_relationship(
        self,
        source_collection: str,
        target_collection: str,
        relationship_type: str,
        **kwargs: Any
    ) -> 'DataStore':
        """
        Define a relationship between collections.

        Args:
            source_collection: Name of the source collection
            target_collection: Name of the target collection
            relationship_type: Type of relationship
            **kwargs: Additional relationship parameters

        Returns:
            Self for method chaining
        """
        relationship = Relationship(
            source_collection=source_collection,
            target_collection=target_collection,
            relationship_type=relationship_type,
            **kwargs
        )
        self.relationships.append(relationship)

        # For many-to-many relationships, create the junction collection if it doesn't exist
        if relationship_type == RelationshipType.MANY_TO_MANY and relationship.junction_collection:
            self.get_collection(relationship.junction_collection)

        return self

    def add_validation_rule(
        self,
        field: str,
        validator_func: Callable[[Any], bool],
        error_message: str,
        collection: Optional[str] = None
    ) -> 'DataStore':
        """
        Add a validation rule.

        Args:
            field: Field name to validate
            validator_func: Function that takes a value and returns True if valid
            error_message: Error message if validation fails
            collection: Optional collection name to restrict validation to

        Returns:
            Self for method chaining
        """
        rule = ValidationRule(
            field=field,
            validator_func=validator_func,
            error_message=error_message,
            collection=collection
        )
        self.validation_rules.append(rule)
        return self

    def add_unique_constraint(
        self,
        fields: Union[str, List[str]],
        error_message: Optional[str] = None,
        collection: Optional[str] = None
    ) -> 'DataStore':
        """
        Add a unique constraint.

        Args:
            fields: Field name or list of field names that must be unique together
            error_message: Custom error message
            collection: Optional collection name to restrict constraint to

        Returns:
            Self for method chaining
        """
        constraint = UniqueConstraint(
            fields=fields,
            error_message=error_message,
            collection=collection
        )
        self.unique_constraints.append(constraint)

        # Initialize the constraint with existing values
        if collection:
            if collection in self.collections:
                for item in self.collections[collection]:
                    constraint.validate(item)
        else:
            for collection_items in self.collections.values():
                for item in collection_items:
                    constraint.validate(item)

        return self

    def set_timestamp_tracking(self, enabled: bool) -> 'DataStore':
        """
        Enable or disable automatic timestamp tracking.

        Args:
            enabled: Whether to track creation and update timestamps

        Returns:
            Self for method chaining
        """
        self.track_timestamps = enabled
        return self

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
        List resources in a collection with filtering, sorting, and pagination.

        Args:
            collection: Collection name
            filters: Optional filters
            sort_by: Optional field(s) to sort by
            sort_desc: Sort in descending order (single bool or list matching sort_by)
            page: Page number (1-based)
            page_size: Page size
            include_deleted: Whether to include soft-deleted items
            include_related: List of related collections to include
            fields: List of fields to include in the response

        Returns:
            Dict with data and metadata
        """
        data = self.get_collection(collection)

        # Filter out soft-deleted items unless explicitly included
        if not include_deleted and self.deleted_field:
            data = [item for item in data if not item.get(self.deleted_field, False)]

        # Apply filters
        if filters:
            data = apply_filters(data, filters)

        # Get total count before pagination
        total_count = len(data)

        # Apply sorting
        if sort_by:
            data = apply_sorting(data, sort_by, sort_desc)

        # Apply pagination
        if page_size:
            data, pagination = apply_pagination(data, page, page_size)
        else:
            pagination = {
                "page": 1,
                "page_size": total_count,
                "total_count": total_count,
                "total_pages": 1
            }

        # Apply field selection
        if fields:
            data = apply_field_selection(data, fields)

        # Include related data if requested
        if include_related:
            data = include_related_data(
                collection, data, include_related,
                self.relationships, self.collections, self.deleted_field
            )

        # Return a deep copy to prevent modification of the original data
        return {
            "data": copy.deepcopy(data),
            "meta": pagination
        }

    def get(
        self,
        collection: str,
        id: Any,
        include_deleted: bool = False,
        include_related: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a resource by ID.

        Args:
            collection: Collection name
            id: Resource ID
            include_deleted: Whether to include soft-deleted items
            include_related: List of related collections to include
            fields: List of fields to include in the response

        Returns:
            Resource or None if not found
        """
        data = self.get_collection(collection)

        for item in data:
            if item.get('id') == id:
                # Check if item is soft-deleted
                if not include_deleted and item.get(self.deleted_field, False):
                    return None

                result = copy.deepcopy(item)

                # Include related data if requested
                if include_related:
                    result = include_related_item(
                        collection, result, include_related,
                        self.relationships, self.collections, self.deleted_field
                    )

                # Apply field selection
                if fields:
                    result = {k: v for k, v in result.items() if k in fields}

                return result

        return None

    def create(
        self,
        collection: str,
        data: Dict[str, Any],
        skip_validation: bool = False
    ) -> Dict[str, Any]:
        """
        Create a resource.

        Args:
            collection: Collection name
            data: Resource data
            skip_validation: Whether to skip validation

        Returns:
            Created resource

        Raises:
            ValidationException: If validation fails
        """
        collection_data = self.get_collection(collection)

        # Create a copy to avoid modifying the original
        new_item = copy.deepcopy(data)

        # Generate ID if not provided
        if 'id' not in new_item:
            new_item['id'] = str(uuid.uuid4())

        # Add version if tracking is enabled
        if self.version_field:
            new_item[self.version_field] = 1

        # Add timestamps if tracking is enabled
        if self.track_timestamps:
            now = datetime.now().isoformat()
            new_item[self.created_at_field] = now
            new_item[self.updated_at_field] = now

        # Validate the item
        if not skip_validation:
            validate_item(collection, new_item, self.validation_rules, self.unique_constraints)

        # Add the item to the collection
        collection_data.append(new_item)

        # Return a deep copy to prevent modification of the original
        return copy.deepcopy(new_item)

    def update(
        self,
        collection: str,
        id: Any,
        data: Dict[str, Any],
        skip_validation: bool = False,
        check_version: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Update a resource.

        Args:
            collection: Collection name
            id: Resource ID
            data: Resource data
            skip_validation: Whether to skip validation
            check_version: Whether to check version for concurrency control

        Returns:
            Updated resource or None if not found

        Raises:
            ValidationException: If validation fails
            ValueError: If version check fails
        """
        collection_data = self.get_collection(collection)

        for i, item in enumerate(collection_data):
            if item.get('id') == id:
                # Check if item is soft-deleted
                if item.get(self.deleted_field, False):
                    return None

                # Check version if enabled
                if check_version and self.version_field:
                    current_version = item.get(self.version_field, 1)
                    if self.version_field in data:
                        provided_version = data.get(self.version_field)
                        if provided_version != current_version:
                            raise ValueError(
                                f"Version conflict: expected {current_version}, got {provided_version}"
                            )

                # Create a copy of the original item
                updated_item = copy.deepcopy(item)

                # Update with new data
                updated_item.update(data)

                # Ensure ID is preserved
                updated_item['id'] = id

                # Update version if tracking is enabled
                if self.version_field:
                    updated_item[self.version_field] = item.get(self.version_field, 1) + 1

                # Update timestamp if tracking is enabled
                if self.track_timestamps and self.updated_at_field:
                    updated_item[self.updated_at_field] = datetime.now().isoformat()

                # Validate the updated item
                if not skip_validation:
                    # First remove the old item's values from unique constraints
                    for constraint in self.unique_constraints:
                        if constraint.collection is None or constraint.collection == collection:
                            constraint.remove_value(item)

                    # Then validate the new item
                    validate_item(collection, updated_item, self.validation_rules, self.unique_constraints)

                # Replace the item in the collection
                collection_data[i] = updated_item

                return copy.deepcopy(updated_item)

        return None

    def delete(
        self,
        collection: str,
        id: Any,
        soft_delete: bool = False,
        cascade: bool = False
    ) -> bool:
        """
        Delete a resource.

        Args:
            collection: Collection name
            id: Resource ID
            soft_delete: Whether to perform a soft delete
            cascade: Whether to cascade the delete to related items

        Returns:
            True if deleted, False if not found
        """
        collection_data = self.get_collection(collection)

        for i, item in enumerate(collection_data):
            if item.get('id') == id:
                # Check if already soft-deleted
                if item.get(self.deleted_field, False):
                    return False

                # Handle cascading deletes if enabled
                if cascade:
                    cascade_delete(
                        collection, item, self.relationships, self.collections,
                        soft_delete, self.deleted_field, self.updated_at_field
                    )

                if soft_delete:
                    # Perform soft delete
                    item[self.deleted_field] = True
                    item[self.updated_at_field] = datetime.now().isoformat()

                    # Add to deleted items collection
                    if collection not in self.deleted_items:
                        self.deleted_items[collection] = []
                    self.deleted_items[collection].append(copy.deepcopy(item))
                else:
                    # Perform hard delete
                    # Remove the item's values from unique constraints
                    for constraint in self.unique_constraints:
                        if constraint.collection is None or constraint.collection == collection:
                            constraint.remove_value(item)

                    del collection_data[i]

                return True

        return False

    def bulk_create(
        self,
        collection: str,
        items: List[Dict[str, Any]],
        skip_validation: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Create multiple resources.

        Args:
            collection: Collection name
            items: List of resource data
            skip_validation: Whether to skip validation

        Returns:
            List of created resources

        Raises:
            ValidationException: If validation fails for any item
        """
        created_items = []

        # First validate all items to ensure atomicity
        if not skip_validation:
            for item in items:
                # Create a copy for validation
                item_copy = copy.deepcopy(item)

                # Generate ID if not provided
                if 'id' not in item_copy:
                    item_copy['id'] = str(uuid.uuid4())

                # Validate without adding to the collection
                validate_item(collection, item_copy, self.validation_rules, self.unique_constraints, add_to_constraints=False)

        # Then create all items
        for item in items:
            created_item = self.create(collection, item, skip_validation=True)
            created_items.append(created_item)

        return created_items

    def bulk_update(
        self,
        collection: str,
        items: List[Dict[str, Any]],
        skip_validation: bool = False,
        check_version: bool = True
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Update multiple resources.

        Args:
            collection: Collection name
            items: List of resource data with IDs
            skip_validation: Whether to skip validation
            check_version: Whether to check version for concurrency control

        Returns:
            List of updated resources or None for items not found

        Raises:
            ValidationException: If validation fails for any item
            ValueError: If version check fails for any item
        """
        updated_items = []

        # First validate all items to ensure atomicity
        if not skip_validation:
            for item in items:
                if 'id' not in item:
                    updated_items.append(None)
                    continue

                # Get the existing item
                existing_item = self.get(collection, item['id'])
                if not existing_item:
                    updated_items.append(None)
                    continue

                # Create a copy for validation
                updated_item = copy.deepcopy(existing_item)
                updated_item.update(item)

                # Validate without updating the collection
                validate_item(collection, updated_item, self.validation_rules, self.unique_constraints, add_to_constraints=False)

        # Then update all items
        updated_items = []
        for item in items:
            if 'id' not in item:
                updated_items.append(None)
                continue

            updated_item = self.update(
                collection, item['id'], item,
                skip_validation=True, check_version=check_version
            )
            updated_items.append(updated_item)

        return updated_items

    def bulk_delete(
        self,
        collection: str,
        ids: List[Any],
        soft_delete: bool = False,
        cascade: bool = False
    ) -> int:
        """
        Delete multiple resources.

        Args:
            collection: Collection name
            ids: List of resource IDs
            soft_delete: Whether to perform soft deletes
            cascade: Whether to cascade the deletes to related items

        Returns:
            Number of deleted resources
        """
        deleted_count = 0

        for id in ids:
            if self.delete(collection, id, soft_delete, cascade):
                deleted_count += 1

        return deleted_count

    def _validate_item(self, collection: str, item: Dict[str, Any]) -> None:
        """
        Validate an item against all rules and constraints.

        Args:
            collection: Collection name
            item: Item to validate

        Raises:
            ValidationException: If validation fails
        """
        validate_item(collection, item, self.validation_rules, self.unique_constraints)

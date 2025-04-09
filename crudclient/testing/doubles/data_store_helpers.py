"""
Helper methods for the DataStore class.

This module provides utility functions for filtering, sorting, pagination, and
relationship handling in the in-memory data store.
"""

import copy
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union


class RelationshipType:
    """Enum-like class for relationship types."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"


def apply_filters(data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply filters to data.

    Args:
        data: List of resources
        filters: Filters to apply

    Returns:
        Filtered data
    """
    filtered_data = []

    for item in data:
        match = True

        for key, value in filters.items():
            # Handle nested keys with dot notation
            if '.' in key:
                parts = key.split('.')
                item_value = item
                for part in parts:
                    if isinstance(item_value, dict) and part in item_value:
                        item_value = item_value[part]
                    else:
                        item_value = None
                        break
            else:
                item_value = item.get(key)

            # Handle different filter types
            if callable(value):
                # Function filter
                if not value(item_value):
                    match = False
                    break
            elif isinstance(value, dict):
                # Operator filter
                if not apply_operator_filter(item_value, value):
                    match = False
                    break
            elif isinstance(value, str) and value.startswith('regex:'):
                # Regex filter
                pattern = value[6:]
                if not isinstance(item_value, str) or not re.search(pattern, item_value):
                    match = False
                    break
            elif item_value != value:
                # Exact match filter
                match = False
                break

        if match:
            filtered_data.append(item)

    return filtered_data


def apply_operator_filter(value: Any, operators: Dict[str, Any]) -> bool:
    """
    Apply operator filters.

    Args:
        value: Value to filter
        operators: Operator filters

    Returns:
        True if value matches all operators
    """
    for op, op_value in operators.items():
        if op == '$eq':
            if value != op_value:
                return False
        elif op == '$ne':
            if value == op_value:
                return False
        elif op == '$gt':
            if not value > op_value:
                return False
        elif op == '$gte':
            if not value >= op_value:
                return False
        elif op == '$lt':
            if not value < op_value:
                return False
        elif op == '$lte':
            if not value <= op_value:
                return False
        elif op == '$in':
            if value not in op_value:
                return False
        elif op == '$nin':
            if value in op_value:
                return False
        elif op == '$exists':
            if op_value and value is None:
                return False
            if not op_value and value is not None:
                return False
        elif op == '$regex':
            if not isinstance(value, str) or not re.search(op_value, value):
                return False

    return True


def apply_sorting(
    data: List[Dict[str, Any]],
    sort_by: Union[str, List[str]],
    sort_desc: Union[bool, List[bool]]
) -> List[Dict[str, Any]]:
    """
    Apply sorting to data.

    Args:
        data: List of resources
        sort_by: Field(s) to sort by
        sort_desc: Sort in descending order

    Returns:
        Sorted data
    """
    if not data:
        return data

    # Convert single field to list
    if isinstance(sort_by, str):
        sort_by = [sort_by]
        sort_desc = [sort_desc] if isinstance(sort_desc, bool) else sort_desc

    # Ensure sort_desc is a list of the same length as sort_by
    if isinstance(sort_desc, bool):
        sort_desc = [sort_desc] * len(sort_by)
    elif len(sort_desc) < len(sort_by):
        sort_desc = sort_desc + [False] * (len(sort_by) - len(sort_desc))

    # Define a key function for sorting
    def get_sort_key(item: Dict[str, Any]) -> Tuple[Any, ...]:
        result = []
        for i, field in enumerate(sort_by):
            # Handle nested keys with dot notation
            if '.' in field:
                parts = field.split('.')
                value = item
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        value = None
                        break
            else:
                value = item.get(field)

            # Handle None values for sorting
            if value is None:
                # Put None values at the end regardless of sort direction
                result.append((1, None))
            else:
                result.append((0, value))

        return tuple(result)

    # Sort the data
    sorted_data = sorted(data, key=get_sort_key)

    # Apply reverse for descending sort
    for i, reverse in enumerate(sort_desc):
        if reverse:
            # Create a key function that only considers the current field
            def key_func(item: Dict[str, Any], idx=i) -> Any:
                return get_sort_key(item)[idx]

            # Find ranges of items with the same values for previous fields
            if i == 0:
                # For the first field, reverse the entire list if needed
                sorted_data.reverse()
            else:
                # For subsequent fields, find groups with the same values for previous fields
                j = 0
                while j < len(sorted_data):
                    # Find the end of the current group
                    k = j + 1
                    while k < len(sorted_data) and all(get_sort_key(sorted_data[j])[l] == get_sort_key(sorted_data[k])[l] for l in range(i)):
                        k += 1

                    # Reverse the current group for this field
                    sorted_data[j:k] = sorted(sorted_data[j:k], key=key_func, reverse=True)

                    # Move to the next group
                    j = k

    return sorted_data


def apply_pagination(
    data: List[Dict[str, Any]],
    page: int,
    page_size: int
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Apply pagination to data.

    Args:
        data: List of resources
        page: Page number (1-based)
        page_size: Page size

    Returns:
        Tuple of (paginated data, pagination metadata)
    """
    total_count = len(data)
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1

    # Ensure page is within valid range
    page = max(1, min(page, total_pages))

    # Calculate slice indices
    start = (page - 1) * page_size
    end = min(start + page_size, total_count)

    # Create pagination metadata
    pagination = {
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages
    }

    return data[start:end], pagination


def apply_field_selection(
    data: List[Dict[str, Any]],
    fields: List[str]
) -> List[Dict[str, Any]]:
    """
    Apply field selection to data.

    Args:
        data: List of resources
        fields: List of fields to include

    Returns:
        Data with only selected fields
    """
    return [{k: v for k, v in item.items() if k in fields} for item in data]


def validate_item(
    collection: str,
    item: Dict[str, Any],
    validation_rules: List,
    unique_constraints: List,
    add_to_constraints: bool = True
) -> None:
    """
    Validate an item against all rules and constraints.

    Args:
        collection: Collection name
        item: Item to validate
        validation_rules: List of validation rules
        unique_constraints: List of unique constraints
        add_to_constraints: Whether to add the item to unique constraints

    Raises:
        ValidationException: If validation fails
    """
    errors = {}

    # Apply validation rules
    for rule in validation_rules:
        if rule.collection is None or rule.collection == collection:
            if rule.field in item:
                is_valid, error_message = rule.validate(item[rule.field])
                if not is_valid:
                    if rule.field not in errors:
                        errors[rule.field] = []
                    errors[rule.field].append(error_message)

    # Apply unique constraints
    for constraint in unique_constraints:
        if constraint.collection is None or constraint.collection == collection:
            is_valid, error_message = constraint.validate(item)
            if not is_valid:
                # If validation failed, remove the value from the constraint
                # since we're not going to add this item
                constraint.remove_value(item)

                # Add the error
                field_name = constraint.fields[0] if len(constraint.fields) == 1 else "combined_fields"
                if field_name not in errors:
                    errors[field_name] = []
                errors[field_name].append(error_message)

    # If there are errors, raise an exception
    if errors:
        from .data_store import ValidationException
        raise ValidationException("Validation failed", errors)


def cascade_delete(
    collection: str,
    item: Dict[str, Any],
    relationships: List,
    collections: Dict[str, List[Dict[str, Any]]],
    soft_delete: bool = False,
    deleted_field: str = "_deleted",
    updated_at_field: str = "_updated_at"
) -> None:
    """
    Cascade delete to related items.

    Args:
        collection: Collection name
        item: Item being deleted
        relationships: List of relationships
        collections: Dictionary of collections
        soft_delete: Whether to perform soft deletes
        deleted_field: Field name for soft deletes
        updated_at_field: Field name for update timestamps
    """
    # Find relationships where this collection is the source
    for relationship in relationships:
        if relationship.source_collection == collection and relationship.cascade_delete:
            source_key_value = item.get(relationship.source_key)
            if source_key_value is None:
                continue

            target_collection = relationship.target_collection
            if target_collection not in collections:
                continue

            target_items = collections[target_collection]

            if relationship.relationship_type == RelationshipType.ONE_TO_ONE:
                # For one-to-one, find the single related item
                for i, target_item in enumerate(target_items):
                    if target_item.get(relationship.target_key) == source_key_value:
                        if soft_delete:
                            # Perform soft delete
                            target_item[deleted_field] = True
                            target_item[updated_at_field] = datetime.now().isoformat()
                        else:
                            # Perform hard delete
                            del target_items[i]
                        break

            elif relationship.relationship_type == RelationshipType.ONE_TO_MANY:
                # For one-to-many, find all related items
                indices_to_delete = []
                for i, target_item in enumerate(target_items):
                    if target_item.get(relationship.target_key) == source_key_value:
                        if soft_delete:
                            # Perform soft delete
                            target_item[deleted_field] = True
                            target_item[updated_at_field] = datetime.now().isoformat()
                        else:
                            # Mark for hard delete
                            indices_to_delete.append(i)

                # Perform hard deletes in reverse order to avoid index issues
                for i in reversed(indices_to_delete):
                    del target_items[i]

            elif relationship.relationship_type == RelationshipType.MANY_TO_MANY:
                # For many-to-many, we need to handle the junction table
                if not relationship.junction_collection:
                    continue

                junction_collection = relationship.junction_collection
                if junction_collection not in collections:
                    continue

                junction_items = collections[junction_collection]

                # Find all junction items that reference this source item
                junction_indices_to_delete = []
                target_ids = []

                for i, junction_item in enumerate(junction_items):
                    if junction_item.get(relationship.source_junction_key) == source_key_value:
                        target_ids.append(junction_item.get(relationship.target_junction_key))
                        if soft_delete:
                            # Perform soft delete on junction item
                            junction_item[deleted_field] = True
                            junction_item[updated_at_field] = datetime.now().isoformat()
                        else:
                            # Mark for hard delete
                            junction_indices_to_delete.append(i)

                # Perform hard deletes on junction items in reverse order
                for i in reversed(junction_indices_to_delete):
                    del junction_items[i]

                # Now handle the target items if needed
                # In many-to-many, we typically don't cascade delete to the target items
                # unless explicitly configured to do so
                if relationship.cascade_delete:
                    target_indices_to_delete = []
                    for i, target_item in enumerate(target_items):
                        target_key_value = target_item.get(relationship.target_key)
                        if target_key_value in target_ids:
                            if soft_delete:
                                # Perform soft delete
                                target_item[deleted_field] = True
                                target_item[updated_at_field] = datetime.now().isoformat()
                            else:
                                # Mark for hard delete
                                target_indices_to_delete.append(i)

                    # Perform hard deletes in reverse order
                    for i in reversed(target_indices_to_delete):
                        del target_items[i]


def include_related_data(
    collection: str,
    data: List[Dict[str, Any]],
    include_related: List[str],
    relationships: List,
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str = "_deleted"
) -> List[Dict[str, Any]]:
    """
    Include related data in the response.

    Args:
        collection: Collection name
        data: List of resources
        include_related: List of related collections to include
        relationships: List of relationships
        collections: Dictionary of collections
        deleted_field: Field name for soft deletes

    Returns:
        Data with related collections included
    """
    result = []

    for item in data:
        result.append(include_related_item(
            collection, item, include_related, relationships, collections, deleted_field
        ))

    return result


def include_related_item(
    collection: str,
    item: Dict[str, Any],
    include_related: List[str],
    relationships: List,
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str = "_deleted"
) -> Dict[str, Any]:
    """
    Include related data for a single item.

    Args:
        collection: Collection name
        item: Resource data
        include_related: List of related collections to include
        relationships: List of relationships
        collections: Dictionary of collections
        deleted_field: Field name for soft deletes

    Returns:
        Item with related collections included
    """
    result = copy.deepcopy(item)

    for related_name in include_related:
        # Find the relationship
        relationship = None
        for rel in relationships:
            if (rel.source_collection == collection and rel.target_collection == related_name) or \
               (rel.bidirectional and rel.target_collection == collection and rel.source_collection == related_name):
                relationship = rel
                break

        if not relationship:
            # No relationship defined, skip
            continue

        # Get the related data
        if relationship.relationship_type == RelationshipType.ONE_TO_ONE:
            # For one-to-one, get the single related item
            if relationship.source_collection == collection:
                # Forward relationship
                if related_name not in collections:
                    result[related_name] = None
                    continue

                target_items = collections[related_name]
                related_items = [
                    i for i in target_items
                    if i.get(relationship.target_key) == item.get(relationship.source_key)
                    and not i.get(deleted_field, False)
                ]
            else:
                # Reverse relationship (bidirectional)
                if relationship.source_collection not in collections:
                    result[related_name] = None
                    continue

                target_items = collections[relationship.source_collection]
                related_items = [
                    i for i in target_items
                    if i.get(relationship.source_key) == item.get(relationship.target_key)
                    and not i.get(deleted_field, False)
                ]

            # There should be at most one related item
            if related_items:
                result[related_name] = copy.deepcopy(related_items[0])
            else:
                result[related_name] = None

        elif relationship.relationship_type == RelationshipType.ONE_TO_MANY:
            if relationship.source_collection == collection:
                # Forward relationship (one-to-many)
                if related_name not in collections:
                    result[related_name] = []
                    continue

                target_items = collections[related_name]
                related_items = [
                    i for i in target_items
                    if i.get(relationship.target_key) == item.get(relationship.source_key)
                    and not i.get(deleted_field, False)
                ]
            else:
                # Reverse relationship (many-to-one)
                if relationship.source_collection not in collections:
                    result[related_name] = None
                    continue

                target_items = collections[relationship.source_collection]
                related_items = [
                    i for i in target_items
                    if item.get(relationship.target_key) == i.get(relationship.source_key)
                    and not i.get(deleted_field, False)
                ]

                # For many-to-one, there should be at most one related item
                if related_items:
                    result[related_name] = copy.deepcopy(related_items[0])
                else:
                    result[related_name] = None
                continue

            # For one-to-many, include all related items
            result[related_name] = copy.deepcopy(related_items)

        elif relationship.relationship_type == RelationshipType.MANY_TO_MANY:
            # For many-to-many, use the junction table
            if not relationship.junction_collection:
                result[related_name] = []
                continue

            if relationship.junction_collection not in collections:
                result[related_name] = []
                continue

            junction_items = collections[relationship.junction_collection]

            if relationship.source_collection == collection:
                # Forward relationship
                junction_matches = [
                    i for i in junction_items
                    if i.get(relationship.source_junction_key) == item.get(relationship.source_key)
                    and not i.get(deleted_field, False)
                ]

                target_ids = [i.get(relationship.target_junction_key) for i in junction_matches]

                if related_name not in collections:
                    result[related_name] = []
                    continue

                target_items = collections[related_name]
                related_items = [
                    i for i in target_items
                    if i.get(relationship.target_key) in target_ids
                    and not i.get(deleted_field, False)
                ]
            else:
                # Reverse relationship
                junction_matches = [
                    i for i in junction_items
                    if i.get(relationship.target_junction_key) == item.get(relationship.target_key)
                    and not i.get(deleted_field, False)
                ]

                source_ids = [i.get(relationship.source_junction_key) for i in junction_matches]

                if relationship.source_collection not in collections:
                    result[related_name] = []
                    continue

                target_items = collections[relationship.source_collection]
                related_items = [
                    i for i in target_items
                    if i.get(relationship.source_key) in source_ids
                    and not i.get(deleted_field, False)
                ]

            # Include all related items
            result[related_name] = copy.deepcopy(related_items)

    return result

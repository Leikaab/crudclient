# crudclient/testing/doubles/data_store_relationship_helpers.pyi
from datetime import datetime
from typing import Any, Dict, List

from .data_store_definitions import Relationship

def perform_soft_delete(item: Dict[str, Any], deleted_field: str = "_deleted", updated_at_field: str = "_updated_at") -> None:
    """Mark an item as deleted (soft delete).

    Args:
        item: The item to mark as deleted
        deleted_field: The field name to use for marking deletion
        updated_at_field: The field name to use for the timestamp
    """
    ...

def delete_items_by_indices(items: List[Dict[str, Any]], indices: List[int]) -> None:
    """Delete items from a list using their indices in reverse order.

    Args:
        items: The list of items to delete from
        indices: The indices of items to delete, in any order
    """
    ...

def handle_one_to_one_cascade(
    source_key_value: Any,
    relationship: Relationship,
    target_items: List[Dict[str, Any]],
    soft_delete: bool,
    deleted_field: str,
    updated_at_field: str,
) -> None:
    """Handle cascade delete for one-to-one relationships.

    Args:
        source_key_value: The value of the source key in the source item
        relationship: The relationship definition
        target_items: The list of target items to process
        soft_delete: Whether to perform a soft delete
        deleted_field: The field name to use for marking deletion
        updated_at_field: The field name to use for the timestamp
    """
    ...

def handle_one_to_many_cascade(
    source_key_value: Any,
    relationship: Relationship,
    target_items: List[Dict[str, Any]],
    soft_delete: bool,
    deleted_field: str,
    updated_at_field: str,
) -> None:
    """Handle cascade delete for one-to-many relationships.

    Args:
        source_key_value: The value of the source key in the source item
        relationship: The relationship definition
        target_items: The list of target items to process
        soft_delete: Whether to perform a soft delete
        deleted_field: The field name to use for marking deletion
        updated_at_field: The field name to use for the timestamp
    """
    ...

def handle_many_to_many_junction(
    source_key_value: Any,
    relationship: Relationship,
    junction_items: List[Dict[str, Any]],
    soft_delete: bool,
    deleted_field: str,
    updated_at_field: str,
) -> List[Any]:
    """Handle junction table for many-to-many relationships and return target IDs.

    Args:
        source_key_value: The value of the source key in the source item
        relationship: The relationship definition
        junction_items: The list of junction items to process
        soft_delete: Whether to perform a soft delete
        deleted_field: The field name to use for marking deletion
        updated_at_field: The field name to use for the timestamp

    Returns:
        A list of target IDs from the junction table
    """
    ...

def handle_many_to_many_targets(
    target_ids: List[Any],
    relationship: Relationship,
    target_items: List[Dict[str, Any]],
    soft_delete: bool,
    deleted_field: str,
    updated_at_field: str,
) -> None:
    """Handle target items deletion for many-to-many relationships.

    Args:
        target_ids: The list of target IDs to process
        relationship: The relationship definition
        target_items: The list of target items to process
        soft_delete: Whether to perform a soft delete
        deleted_field: The field name to use for marking deletion
        updated_at_field: The field name to use for the timestamp
    """
    ...

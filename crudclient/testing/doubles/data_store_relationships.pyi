# crudclient/testing/doubles/data_store_relationships.pyi
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from .data_store_definitions import Relationship

class RelationshipType:
    """Defines the types of relationships between collections."""

    ONE_TO_ONE: str
    ONE_TO_MANY: str
    MANY_TO_MANY: str

def include_related_data(
    collection: str,
    data: List[Dict[str, Any]],
    include_related: List[str],
    relationships: List["Relationship"],
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str = "_deleted",
) -> List[Dict[str, Any]]:
    """Includes related data for a list of items based on defined relationships."""
    ...

def include_related_item(
    collection: str,
    item: Dict[str, Any],
    include_related: List[str],
    relationships: List["Relationship"],
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str = "_deleted",
) -> Dict[str, Any]:
    """Includes related data for a single item based on defined relationships."""
    ...

def cascade_delete(
    collection: str,
    item: Dict[str, Any],
    relationships: List["Relationship"],
    collections: Dict[str, List[Dict[str, Any]]],
    soft_delete: bool = False,
    deleted_field: str = "_deleted",
    updated_at_field: str = "_updated_at",
) -> None:
    """
    Performs cascading deletes based on relationship definitions.

    Handles one-to-one, one-to-many, and many-to-many relationships,
    supporting both soft and hard deletes.

    Args:
        collection: The name of the source collection where the item is being deleted.
        item: The item being deleted from the source collection.
        relationships: A list of all defined relationships.
        collections: A dictionary containing all data collections.
        soft_delete: If True, performs a soft delete (marks as deleted).
                     If False, performs a hard delete (removes the item).
        deleted_field: The field name used to mark items as soft-deleted.
        updated_at_field: The field name used to store the last update timestamp.
    """
    ...

# Note: Private helper functions (_get_related_*) are not included in the stub file
# as they are not part of the public interface of this module.

# crudclient/testing/doubles/data_store_relationships.py
import copy
from datetime import datetime  # Added for cascade_delete
from typing import TYPE_CHECKING, Any, Dict, List

from .data_store_definitions import Relationship  # Import Relationship

# RelationshipType is now defined in this file
# from .data_store_helpers import RelationshipType # Removed import

if TYPE_CHECKING:
    # Avoid circular import with DataStore if Relationship definition moves
    # from .data_store import DataStore
    pass


class RelationshipType:
    # Docstring moved to .pyi
    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_MANY = "many_to_many"


def include_related_data(
    collection: str,
    data: List[Dict[str, Any]],
    include_related: List[str],
    relationships: List[Relationship],  # Use imported Relationship
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str = "_deleted"
) -> List[Dict[str, Any]]:
    # Docstring moved to .pyi
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
    relationships: List[Relationship],  # Use imported Relationship
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str = "_deleted"
) -> Dict[str, Any]:
    # Docstring moved to .pyi
    result = copy.deepcopy(item)

    for related_name in include_related:
        # Find the relationship definition
        relationship = None
        for rel in relationships:
            # Check both forward and bidirectional reverse relationships
            if (rel.source_collection == collection and rel.target_collection == related_name) or \
               (rel.bidirectional and rel.target_collection == collection and rel.source_collection == related_name):
                relationship = rel
                break

        if not relationship:
            # No relationship defined for this include, skip
            continue

        # Determine if we are looking forward (source=collection) or backward (target=collection)
        is_forward_relation = relationship.source_collection == collection

        # Get the related data based on relationship type
        if relationship.relationship_type == RelationshipType.ONE_TO_ONE:
            related_items = _get_related_one_to_one(
                item, relationship, collections, deleted_field, is_forward_relation, related_name
            )
            result[related_name] = copy.deepcopy(related_items[0]) if related_items else None

        elif relationship.relationship_type == RelationshipType.ONE_TO_MANY:
            related_items = _get_related_one_to_many(
                item, relationship, collections, deleted_field, is_forward_relation, related_name
            )
            if is_forward_relation:  # one-to-many returns a list
                result[related_name] = copy.deepcopy(related_items)
            else:  # many-to-one returns a single item or None
                result[related_name] = copy.deepcopy(related_items[0]) if related_items else None

        elif relationship.relationship_type == RelationshipType.MANY_TO_MANY:
            related_items = _get_related_many_to_many(
                item, relationship, collections, deleted_field, is_forward_relation, related_name
            )
            result[related_name] = copy.deepcopy(related_items)

    return result


# --- Helper functions for include_related_item ---

def _get_related_one_to_one(
    item: Dict[str, Any],
    relationship: Relationship,
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str,
    is_forward_relation: bool,
    related_name: str
) -> List[Dict[str, Any]]:
    # Docstring moved to .pyi
    if is_forward_relation:
        target_collection_name = related_name
        source_key = relationship.source_key
        target_key = relationship.target_key
        item_key_value = item.get(source_key)
    else:  # Reverse relationship
        target_collection_name = relationship.source_collection
        source_key = relationship.target_key  # Key in the 'item' (which is the target in the relationship def)
        target_key = relationship.source_key  # Key in the related items (source in relationship def)
        item_key_value = item.get(source_key)

    if target_collection_name not in collections or item_key_value is None:
        return []

    target_items = collections[target_collection_name]
    return [
        i for i in target_items
        if i.get(target_key) == item_key_value
        and not i.get(deleted_field, False)
    ]


def _get_related_one_to_many(
    item: Dict[str, Any],
    relationship: Relationship,
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str,
    is_forward_relation: bool,
    related_name: str
) -> List[Dict[str, Any]]:
    # Docstring moved to .pyi
    if is_forward_relation:  # one(item)-to-many(related_name)
        target_collection_name = related_name
        source_key = relationship.source_key
        target_key = relationship.target_key
        item_key_value = item.get(source_key)
    else:  # many(related_name)-to-one(item)
        target_collection_name = relationship.source_collection
        source_key = relationship.target_key  # Key in the 'item'
        target_key = relationship.source_key  # Key in the related items
        item_key_value = item.get(source_key)

    if target_collection_name not in collections or item_key_value is None:
        return []

    target_items = collections[target_collection_name]
    return [
        i for i in target_items
        if i.get(target_key) == item_key_value
        and not i.get(deleted_field, False)
    ]


def _get_related_many_to_many(
    item: Dict[str, Any],
    relationship: Relationship,
    collections: Dict[str, List[Dict[str, Any]]],
    deleted_field: str,
    is_forward_relation: bool,
    related_name: str
) -> List[Dict[str, Any]]:
    # Docstring moved to .pyi
    if not relationship.junction_collection or relationship.junction_collection not in collections:
        return []

    junction_items = collections[relationship.junction_collection]

    if is_forward_relation:
        source_key = relationship.source_key
        junction_source_key = relationship.source_junction_key
        junction_target_key = relationship.target_junction_key
        target_collection_name = related_name
        target_key = relationship.target_key
        item_key_value = item.get(source_key)
    else:  # Reverse relationship
        source_key = relationship.target_key  # Key in the 'item'
        junction_source_key = relationship.target_junction_key  # Key in junction table pointing to 'item'
        junction_target_key = relationship.source_junction_key  # Key in junction table pointing to related items
        target_collection_name = relationship.source_collection
        target_key = relationship.source_key  # Key in the related items
        item_key_value = item.get(source_key)

    if item_key_value is None:
        return []

    # Find matching entries in the junction table
    junction_matches = [
        i for i in junction_items
        if i.get(junction_source_key) == item_key_value
        and not i.get(deleted_field, False)
    ]

    # Get the IDs of the related items from the junction table
    related_ids = {i.get(junction_target_key) for i in junction_matches if i.get(junction_target_key) is not None}

    if target_collection_name not in collections:
        return []

    # Get the actual related items
    target_items = collections[target_collection_name]
    return [
        i for i in target_items
        if i.get(target_key) in related_ids
        and not i.get(deleted_field, False)
    ]


def cascade_delete(
    collection: str,
    item: Dict[str, Any],
    relationships: List[Relationship],  # Use imported Relationship
    collections: Dict[str, List[Dict[str, Any]]],
    soft_delete: bool = False,
    deleted_field: str = "_deleted",
    updated_at_field: str = "_updated_at"
) -> None:
    # Docstring moved to .pyi
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

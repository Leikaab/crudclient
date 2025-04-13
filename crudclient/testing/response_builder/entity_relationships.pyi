"""
Entity relationship builder utilities for mock client.

This module provides utilities for creating related entities and entity graphs
for testing API responses that involve relationships between different resources.
"""

import random
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from .response import MockResponse

class EntityRelationshipBuilder:
    """
    Builder for creating related entities and entity graphs.

    This class provides static methods for generating mock API responses that
    represent relationships between different entities, supporting both embedded
    and referenced relationships.
    """

    @staticmethod
    def create_related_entities(
        primary_entity: Dict[str, Any],
        related_entities: List[Dict[str, Any]],
        relation_key: str,
        foreign_key: str = "id",
        embed: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a primary entity with relationships to other entities.

        This method establishes relationships between a primary entity and a list
        of related entities, either by embedding the full related entities or by
        including only their IDs.

        Args:
            primary_entity: The main entity to which relationships will be added
            related_entities: List of entities to relate to the primary entity
            relation_key: The key in the primary entity where the relationship will be stored
            foreign_key: The key in the related entities to use for reference (typically "id")
            embed: If True, embeds the full related entities; if False, includes only their IDs

        Returns:
            A copy of the primary entity with the relationships added
        """
        ...

    @staticmethod
    def create_entity_graph(
        entities_by_type: Dict[str, List[Dict[str, Any]]],
        relationships: Dict[str, Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create a graph of related entities based on defined relationships.

        This method generates a complex entity graph with various types of relationships
        (one-to-one, one-to-many) between different entity types. It supports both
        embedded and referenced relationships.

        Args:
            entities_by_type: Dictionary mapping entity types to lists of entities
            relationships: Dictionary defining the relationships between entity types.
                           Format: {
                               "source_type": {
                                   "relation_key": {
                                       "target_type": "target_entity_type",
                                       "cardinality": "one" or "many",
                                       "embed": True or False,
                                       "foreign_key": "id",
                                       "count": optional count for "many" relationships
                                   }
                               }
                           }

        Returns:
            A dictionary containing all entities with their relationships established
        """
        ...

def _extract_entity_id_from_url(url: str, entity_type: str) -> Tuple[str, Optional[MockResponse]]:
    """
    Extract entity ID from URL or return error response if not possible.

    Args:
        url: The URL to extract the ID from
        entity_type: The type of entity (used in error messages)

    Returns:
        A tuple containing the extracted ID and an optional error response.
        If extraction is successful, the second element will be None.
        If extraction fails, the first element will be an empty string and
        the second element will be a 404 error response.
    """
    ...

def _create_entity_not_found_response(entity_type: str, entity_id: str) -> MockResponse:
    """
    Create a standard 404 response for entity not found.

    Args:
        entity_type: The type of entity (used in error messages)
        entity_id: The ID of the entity that was not found

    Returns:
        A MockResponse with a 404 status code and appropriate error message
    """
    ...

def _create_list_factory(entities: List[Dict[str, Any]], entity_type: str) -> Callable[..., MockResponse]:
    """
    Create a factory function for list operation.

    Args:
        entities: The list of entities to return
        entity_type: The type of entity (used in error messages)

    Returns:
        A factory function that returns a MockResponse with the entities
    """
    ...

def _create_get_factory(entity_map: Dict[str, Dict[str, Any]], entity_type: str) -> Callable[..., MockResponse]:
    """
    Create a factory function for get operation.

    Args:
        entity_map: A dictionary mapping entity IDs to entity data
        entity_type: The type of entity (used in error messages)

    Returns:
        A factory function that extracts an entity ID from the URL and
        returns the corresponding entity or an error response
    """
    ...

def _create_create_factory(
    entities: List[Dict[str, Any]], entity_map: Dict[str, Dict[str, Any]], entity_type: str, id_field: str
) -> Callable[..., MockResponse]:
    """
    Create a factory function for create operation.

    Args:
        entities: The list of entities to add the new entity to
        entity_map: A dictionary mapping entity IDs to entity data
        entity_type: The type of entity (used in error messages)
        id_field: The field name used as the identifier in the entities

    Returns:
        A factory function that creates a new entity and returns it
        in a MockResponse with a 201 status code
    """
    ...

def _create_update_factory(entity_map: Dict[str, Dict[str, Any]], entity_type: str) -> Callable[..., MockResponse]:
    """
    Create a factory function for update operation.

    Args:
        entity_map: A dictionary mapping entity IDs to entity data
        entity_type: The type of entity (used in error messages)

    Returns:
        A factory function that updates an existing entity and returns it
        in a MockResponse with a 200 status code
    """
    ...

def _create_delete_factory(entities: List[Dict[str, Any]], entity_map: Dict[str, Dict[str, Any]], entity_type: str) -> Callable[..., MockResponse]:
    """
    Create a factory function for delete operation.

    Args:
        entities: The list of entities to remove the entity from
        entity_map: A dictionary mapping entity IDs to entity data
        entity_type: The type of entity (used in error messages)

    Returns:
        A factory function that deletes an entity and returns a
        MockResponse with a 204 status code
    """
    ...

def create_consistent_response_sequence(
    entity_type: str,
    base_entities: List[Dict[str, Any]],
    operations: List[str],
    id_field: str = "id",
) -> List[Callable[..., MockResponse]]:
    """
    Create a sequence of response factories that maintain consistency across CRUD operations.

    This method generates a list of response factory functions that simulate a consistent
    API behavior across a sequence of operations (list, get, create, update, delete).
    Each operation maintains the state changes from previous operations.

    Args:
        entity_type: The type of entity being operated on (used in error messages)
        base_entities: The initial set of entities to use as the data source
        operations: List of operations to include in the sequence ("list", "get",
                    "create", "update", "delete")
        id_field: The field name used as the identifier in the entities

    Returns:
        A list of callable factory functions that generate MockResponse objects.
        Each factory accepts kwargs that may include:
        - url: The URL of the request (used to extract IDs for get/update/delete)
        - json: The request body data (used for create/update operations)
    """
    ...

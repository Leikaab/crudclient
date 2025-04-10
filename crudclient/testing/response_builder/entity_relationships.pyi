"""
Entity relationship builder utilities for mock client.

This module provides utilities for creating related entities and entity graphs
for testing API responses that involve relationships between different resources.
"""

import random
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List

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

    @staticmethod
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

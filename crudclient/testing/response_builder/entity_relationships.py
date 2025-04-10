
import random
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List

from .response import MockResponse


class EntityRelationshipBuilder:

    @staticmethod
    def create_related_entities(
        primary_entity: Dict[str, Any],
        related_entities: List[Dict[str, Any]],
        relation_key: str,
        foreign_key: str = "id",
        embed: bool = False,
    ) -> Dict[str, Any]:
        result = primary_entity.copy()

        if embed:
            # Embed the full related entities
            result[relation_key] = related_entities
        else:
            # Just include the IDs of related entities
            result[relation_key] = [
                entity[foreign_key] for entity in related_entities
                if foreign_key in entity
            ]

        return result

    @staticmethod
    def create_entity_graph(
        entities_by_type: Dict[str, List[Dict[str, Any]]],
        relationships: Dict[str, Dict[str, Any]],
    ) -> Dict[str, List[Dict[str, Any]]]:
        result = {k: [item.copy() for item in v] for k, v in entities_by_type.items()}

        # Process each relationship
        for source_type, relations in relationships.items():
            if source_type not in result:
                continue

            source_entities = result[source_type]

            for relation_key, relation_config in relations.items():
                target_type = relation_config.get("target_type")
                if target_type not in result:
                    continue

                target_entities = result[target_type]
                cardinality = relation_config.get("cardinality", "many")
                embed = relation_config.get("embed", False)
                foreign_key = relation_config.get("foreign_key", "id")

                # Update each source entity with the relationship
                for source_entity in source_entities:
                    if cardinality == "one":
                        # One-to-one relationship
                        if target_entities:
                            target = random.choice(target_entities)
                            if embed:
                                source_entity[relation_key] = target
                            else:
                                source_entity[relation_key] = target.get(foreign_key)
                    else:
                        # One-to-many or many-to-many relationship
                        count = relation_config.get("count", random.randint(0, min(3, len(target_entities))))
                        related = random.sample(target_entities, min(count, len(target_entities)))

                        if embed:
                            source_entity[relation_key] = related
                        else:
                            source_entity[relation_key] = [
                                entity.get(foreign_key) for entity in related
                                if foreign_key in entity
                            ]

        return result

    @staticmethod
    def create_consistent_response_sequence(
        entity_type: str,
        base_entities: List[Dict[str, Any]],
        operations: List[str],
        id_field: str = "id",
    ) -> List[Callable[..., MockResponse]]:
        # Create a mutable copy of entities that will be modified by operations
        entities = [entity.copy() for entity in base_entities]
        entity_map = {str(entity.get(id_field)): entity for entity in entities if id_field in entity}

        response_factories = []

        for operation in operations:
            if operation == "list":
                # Factory for list operation
                def list_factory(**kwargs):
                    return MockResponse(
                        status_code=200,
                        json_data={"data": entities, "count": len(entities)}
                    )
                response_factories.append(list_factory)

            elif operation == "get":
                # Factory for get operation
                def get_factory(**kwargs):
                    url = kwargs.get("url", "")
                    # Extract ID from URL
                    parts = url.rstrip("/").split("/")
                    if not parts:
                        return MockResponse(
                            status_code=404,
                            json_data={"error": f"{entity_type} not found"}
                        )

                    entity_id = parts[-1]
                    if entity_id in entity_map:
                        return MockResponse(
                            status_code=200,
                            json_data=entity_map[entity_id]
                        )
                    else:
                        return MockResponse(
                            status_code=404,
                            json_data={"error": f"{entity_type} not found with id {entity_id}"}
                        )
                response_factories.append(get_factory)

            elif operation == "create":
                # Factory for create operation
                def create_factory(**kwargs):
                    json_data = kwargs.get("json", {})
                    if not json_data:
                        return MockResponse(
                            status_code=400,
                            json_data={"error": f"Invalid {entity_type} data"}
                        )

                    # Generate a new ID if not provided
                    if id_field not in json_data:
                        json_data[id_field] = str(uuid.uuid4())

                    # Add created_at timestamp
                    if "created_at" not in json_data:
                        json_data["created_at"] = datetime.now().isoformat()

                    # Add to entities
                    entity_id = str(json_data[id_field])
                    entity_map[entity_id] = json_data
                    entities.append(json_data)

                    return MockResponse(
                        status_code=201,
                        json_data=json_data
                    )
                response_factories.append(create_factory)

            elif operation == "update":
                # Factory for update operation
                def update_factory(**kwargs):
                    url = kwargs.get("url", "")
                    json_data = kwargs.get("json", {})

                    # Extract ID from URL
                    parts = url.rstrip("/").split("/")
                    if not parts:
                        return MockResponse(
                            status_code=404,
                            json_data={"error": f"{entity_type} not found"}
                        )

                    entity_id = parts[-1]
                    if entity_id not in entity_map:
                        return MockResponse(
                            status_code=404,
                            json_data={"error": f"{entity_type} not found with id {entity_id}"}
                        )

                    # Update entity
                    entity = entity_map[entity_id]
                    entity.update(json_data)

                    # Add updated_at timestamp
                    entity["updated_at"] = datetime.now().isoformat()

                    return MockResponse(
                        status_code=200,
                        json_data=entity
                    )
                response_factories.append(update_factory)

            elif operation == "delete":
                # Factory for delete operation
                def delete_factory(**kwargs):
                    url = kwargs.get("url", "")

                    # Extract ID from URL
                    parts = url.rstrip("/").split("/")
                    if not parts:
                        return MockResponse(
                            status_code=404,
                            json_data={"error": f"{entity_type} not found"}
                        )

                    entity_id = parts[-1]
                    if entity_id not in entity_map:
                        return MockResponse(
                            status_code=404,
                            json_data={"error": f"{entity_type} not found with id {entity_id}"}
                        )

                    # Remove entity
                    entity = entity_map.pop(entity_id)
                    entities.remove(entity)

                    return MockResponse(
                        status_code=204,
                        json_data=None
                    )
                response_factories.append(delete_factory)

        return response_factories

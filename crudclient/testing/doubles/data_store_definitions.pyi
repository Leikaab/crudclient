# crudclient/testing/doubles/data_store_definitions.pyi
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

class ValidationException(Exception):
    """Exception raised for data validation errors."""

    errors: Dict[str, List[str]]

    def __init__(self, message: str, errors: Optional[Dict[str, List[str]]] = None) -> None: ...

class Relationship:
    """Defines a relationship between two collections in the DataStore."""

    source_collection: str
    target_collection: str
    relationship_type: str
    source_key: str
    target_key: str
    cascade_delete: bool
    bidirectional: bool
    junction_collection: Optional[str]
    source_junction_key: Optional[str]
    target_junction_key: Optional[str]

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
    ) -> None: ...

class ValidationRule:
    """Defines a validation rule for a specific field in a collection."""

    field: str
    validator_func: Callable[[Any], bool]
    error_message: str
    collection: Optional[str]

    def __init__(
        self,
        field: str,
        validator_func: Callable[[Any], bool],
        error_message: str,
        collection: Optional[str] = None,
    ) -> None: ...
    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """Validates a value using the defined function."""
        ...

class UniqueConstraint:
    """Defines a unique constraint across one or more fields in a collection."""

    fields: List[str]
    error_message: str
    collection: Optional[str]
    _values: Set[str]

    def __init__(
        self,
        fields: Union[str, List[str]],
        error_message: Optional[str] = None,
        collection: Optional[str] = None,
    ) -> None: ...
    def validate(self, item: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Checks if the item violates the unique constraint.
        Adds the item's value combination if it's unique.
        """
        ...

    def remove_value(self, item: Dict[str, Any]) -> None:
        """Removes an item's value combination from the tracked set."""
        ...

    def _get_composite_key(self, item: Dict[str, Any]) -> Optional[str]:
        """Generates the composite key string for an item."""
        ...

# crudclient/testing/doubles/data_store_helpers.pyi
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from .data_store_definitions import ValidationRule, UniqueConstraint


def apply_filters(data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Applies various filters to a list of dictionaries.

    Supports exact match, callable, operator ($eq, $ne, $gt, etc.),
    regex, and nested key filters.
    """
    ...


def apply_operator_filter(value: Any, operators: Dict[str, Any]) -> bool:
    """
    Applies operator-based filters ($eq, $ne, $gt, etc.) to a single value.
    """
    ...


def apply_pagination(
    data: List[Dict[str, Any]],
    page: int,
    page_size: int
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Applies pagination to a list of data.

    Returns the paginated data slice and pagination metadata.
    """
    ...


def apply_field_selection(
    data: List[Dict[str, Any]],
    fields: List[str]
) -> List[Dict[str, Any]]:
    """
    Selects only the specified fields from a list of dictionaries.
    """
    ...


def validate_item(
    collection: str,
    item: Dict[str, Any],
    validation_rules: List["ValidationRule"],
    unique_constraints: List["UniqueConstraint"],
    add_to_constraints: bool = True
) -> None:
    """
    Validates an item against defined rules and unique constraints.

    Raises ValidationException if validation fails.
    """
    ...

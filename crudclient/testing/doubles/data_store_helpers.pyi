# crudclient/testing/doubles/data_store_helpers.pyi
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    # from .data_store_definitions import UniqueConstraint, ValidationRule # No longer needed directly
    from .data_store import DataStore  # Import DataStore for type hinting

def apply_filters(data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Applies various filters to a list of dictionaries.

    Supports exact match, callable, operator ($eq, $ne, $gt, etc.),
    regex, and nested key filters.
    """
    ...

def _op_eq(value: Any, op_value: Any) -> bool:
    """
    Check if value equals op_value.

    Args:
        value: The value to compare
        op_value: The value to compare against

    Returns:
        bool: True if value equals op_value, False otherwise
    """
    ...

def _op_ne(value: Any, op_value: Any) -> bool:
    """
    Check if value does not equal op_value.

    Args:
        value: The value to compare
        op_value: The value to compare against

    Returns:
        bool: True if value does not equal op_value, False otherwise
    """
    ...

def _op_gt(value: Any, op_value: Any) -> bool:
    """
    Check if value is greater than op_value.

    Args:
        value: The value to compare
        op_value: The value to compare against

    Returns:
        bool: True if value is greater than op_value, False otherwise
    """
    ...

def _op_gte(value: Any, op_value: Any) -> bool:
    """
    Check if value is greater than or equal to op_value.

    Args:
        value: The value to compare
        op_value: The value to compare against

    Returns:
        bool: True if value is greater than or equal to op_value, False otherwise
    """
    ...

def _op_lt(value: Any, op_value: Any) -> bool:
    """
    Check if value is less than op_value.

    Args:
        value: The value to compare
        op_value: The value to compare against

    Returns:
        bool: True if value is less than op_value, False otherwise
    """
    ...

def _op_lte(value: Any, op_value: Any) -> bool:
    """
    Check if value is less than or equal to op_value.

    Args:
        value: The value to compare
        op_value: The value to compare against

    Returns:
        bool: True if value is less than or equal to op_value, False otherwise
    """
    ...

def _op_in(value: Any, op_value: Any) -> bool:
    """
    Check if value is in op_value.

    Args:
        value: The value to check
        op_value: The collection to check against (must support 'in' operator)

    Returns:
        bool: True if value is in op_value, False otherwise
    """
    ...

def _op_nin(value: Any, op_value: Any) -> bool:
    """
    Check if value is not in op_value.

    Args:
        value: The value to check
        op_value: The collection to check against (must support 'in' operator)

    Returns:
        bool: True if value is not in op_value, False otherwise
    """
    ...

def _op_exists(value: Any, op_value: bool) -> bool:
    """
    Check if value exists (is not None) when op_value is True,
    or does not exist (is None) when op_value is False.

    Args:
        value: The value to check for existence
        op_value: Boolean indicating expected existence state

    Returns:
        bool: True if existence state matches expectation, False otherwise
    """
    ...

def _op_regex(value: Any, op_value: str) -> bool:
    """
    Check if value matches the regex pattern in op_value.

    Args:
        value: The string value to check
        op_value: The regex pattern to match against

    Returns:
        bool: True if value is a string and matches the pattern, False otherwise
    """
    ...

def apply_operator_filter(value: Any, operators: Dict[str, Any]) -> bool:
    """
    Applies MongoDB-style operators to filter a value.

    Supports the following operators:
    - $eq: Equal to
    - $ne: Not equal to
    - $gt: Greater than
    - $gte: Greater than or equal to
    - $lt: Less than
    - $lte: Less than or equal to
    - $in: In collection
    - $nin: Not in collection
    - $exists: Checks if value exists (is not None)
    - $regex: Matches regex pattern

    Args:
        value: The value to filter
        operators: Dictionary of operators and their values

    Returns:
        bool: True if the value passes all operator filters, False otherwise
    """
    ...

def apply_pagination(data: List[Dict[str, Any]], page: int, page_size: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Applies pagination to a list of data.

    Returns the paginated data slice and pagination metadata.
    """
    ...

def apply_field_selection(data: List[Dict[str, Any]], fields: List[str]) -> List[Dict[str, Any]]:
    """
    Selects only the specified fields from a list of dictionaries.
    """
    ...

def validate_item(data_store: "DataStore", collection: str, item: Dict[str, Any], add_to_constraints: bool = True) -> None:
    """
    Validates an item against defined validation rules, unique constraints,
    and referential integrity (foreign key constraints).

    Args:
        data_store: The DataStore instance containing rules, constraints, and collections.
        collection: The name of the collection the item belongs to.
        item: The item data to validate.
        add_to_constraints: If True (default), adds the item's values to unique constraints
                            if validation passes. Set to False for validation checks without
                            modifying constraint state (e.g., during updates before commit).

    Raises:
        ValidationException: If any validation rule, unique constraint, or
                             referential integrity check fails.
    """
    ...

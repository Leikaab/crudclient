# import copy # No longer used directly here
import re
from typing import Any, Dict, List, Optional, Tuple  # Removed Callable, Union, TYPE_CHECKING, datetime

# RelationshipType class moved to data_store_relationships.py


# if TYPE_CHECKING: # Relationship import no longer needed
#     from .data_store_definitions import Relationship # RelationshipType moved

def apply_filters(data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    filtered_data = []

    for item in data:
        match = True

        for key, value in filters.items():
            item_value: Optional[Any] = None  # Declare once before if/else
            # Handle nested keys with dot notation
            if '.' in key:
                parts = key.split('.')
                current_val: Any = item
                for part in parts:
                    if isinstance(current_val, dict) and part in current_val:
                        current_val = current_val[part]
                    else:
                        current_val = None
                        break
                item_value = current_val
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
                # Nested check to ensure item_value is str before regex search
                if isinstance(item_value, str):
                    if not re.search(pattern, item_value):
                        match = False
                        break
                else:  # If not a string, it's not a match for regex
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


# Function apply_sorting moved to data_store_sorting.py


def apply_pagination(
    data: List[Dict[str, Any]],
    page: int,
    page_size: int
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
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
    return [{k: v for k, v in item.items() if k in fields} for item in data]


def validate_item(
    collection: str,
    item: Dict[str, Any],
    validation_rules: List,
    unique_constraints: List,
    add_to_constraints: bool = True
) -> None:
    errors: Dict[str, List[str]] = {}  # Added type annotation

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
        # Import ValidationException at the top level if needed by other functions
        from .data_store_definitions import ValidationException
        raise ValidationException("Validation failed", errors)


# cascade_delete function moved to data_store_relationships.py


# Functions include_related_data and include_related_item moved to data_store_relationships.py
# Import them if needed elsewhere, or adjust calls in data_store_crud.py etc.
# (Note: They are already used in data_store_crud.py, which imports them directly)
# cascade_delete is now also imported in data_store_crud.py from data_store_relationships.py

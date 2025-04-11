# crudclient/testing/doubles/data_store_bulk.pyi
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from .data_store import DataStore

def bulk_create_items(
    data_store: "DataStore",
    collection: str,
    items: List[Dict[str, Any]],
    skip_validation: bool = False,
) -> List[Dict[str, Any]]:
    """
    Creates multiple items in the specified collection.

    Handles validation atomically before creating items.
    """
    ...

def bulk_update_items(
    data_store: "DataStore",
    collection: str,
    items: List[Dict[str, Any]],
    skip_validation: bool = False,
    check_version: bool = True,
) -> List[Optional[Dict[str, Any]]]:
    """
    Updates multiple items in the specified collection.

    Handles validation atomically before updating items.
    """
    ...

def bulk_delete_items(
    data_store: "DataStore",
    collection: str,
    ids: List[Any],
    soft_delete: bool = False,
    cascade: bool = False,
) -> int:
    """Deletes multiple items by ID."""
    ...

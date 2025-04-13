# crudclient/testing/doubles/data_store_crud.pyi
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

if TYPE_CHECKING:
    from .data_store import DataStore

def list_items(
    data_store: "DataStore",
    collection: str,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Optional[Union[str, List[str]]] = None,
    sort_desc: Union[bool, List[bool]] = False,
    page: int = 1,
    page_size: Optional[int] = None,
    include_deleted: bool = False,
    include_related: Optional[List[str]] = None,
    fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Lists items from a collection with filtering, sorting, pagination,
    relationship inclusion, and field selection.
    """
    ...

def get_item(
    data_store: "DataStore",
    collection: str,
    id: Any,
    include_deleted: bool = False,
    include_related: Optional[List[str]] = None,
    fields: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    """Gets a single item by ID."""
    ...

def create_item(data_store: "DataStore", collection: str, data: Dict[str, Any], skip_validation: bool = False) -> Dict[str, Any]:
    """Creates a single item in a collection."""
    ...

def update_item(
    data_store: "DataStore", collection: str, id: Any, data: Dict[str, Any], skip_validation: bool = False, check_version: bool = True
) -> Optional[Dict[str, Any]]:
    """Updates a single item by ID."""
    ...

def delete_item(data_store: "DataStore", collection: str, id: Any, soft_delete: bool = False, cascade: bool = False) -> bool:
    """Deletes a single item by ID."""
    ...

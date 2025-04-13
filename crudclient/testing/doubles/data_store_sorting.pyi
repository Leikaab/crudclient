# crudclient/testing/doubles/data_store_sorting.pyi
from typing import Any, Dict, List, Union

def apply_sorting(data: List[Dict[str, Any]], sort_by: Union[str, List[str]], sort_desc: Union[bool, List[bool]]) -> List[Dict[str, Any]]:
    """Sorts a list of dictionaries based on specified fields and directions."""
    ...

# Note: Inner helper functions (get_sort_key, get_single_level_key) are not part of the public interface
# and are therefore not included in the stub file.

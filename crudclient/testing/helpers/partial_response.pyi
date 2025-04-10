# crudclient/testing/helpers/partial_response.pyi
import copy
from typing import Any, Dict, List, Optional, Set


class PartialResponseHelper:
    """
    Helper class for creating partial API responses by selecting specific fields.

    Allows clients to request only the fields they need, reducing response size
    and improving performance. Supports field selection using dot notation,
    wildcards, exclusions, and depth limiting.
    """
    full_response: Dict[str, Any]
    field_separator: str
    wildcard_char: str
    default_fields: List[str]

    def __init__(
        self,
        full_response: Dict[str, Any],
        field_separator: str = ".",
        wildcard_char: str = "*",
        default_fields: Optional[List[str]] = None
    ) -> None:
        """
        Initialize a PartialResponseHelper instance.

        Args:
            full_response: The complete response data
            field_separator: Character used to separate nested field paths (e.g., "user.address.city")
            wildcard_char: Character used for wildcard matching (e.g., "user.*.name")
            default_fields: Default fields to include if none are specified
        """
        ...

    def get_partial_response(
        self,
        fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a partial response containing only the requested fields.

        Args:
            fields: List of field paths to include (using dot notation)
            exclude_fields: List of field paths to exclude
            max_depth: Maximum depth of nested objects to include
            include_metadata: Whether to include metadata about the partial response

        Returns:
            A dictionary containing only the requested fields from the full response.
            If include_metadata is True, the result will be wrapped in a dictionary
            with 'data' and '_metadata' keys.

        Examples:
            ```python
            # Include specific fields
            helper.get_partial_response(fields=["id", "name", "address.city"])

            # Use wildcards to include all fields at a certain level
            helper.get_partial_response(fields=["user.*"])

            # Include fields but exclude some
            helper.get_partial_response(
                fields=["user.*"], 
                exclude_fields=["user.password"]
            )

            # Limit depth of nested objects
            helper.get_partial_response(max_depth=2)
            ```
        """
        ...

    def _process_wildcard_field(self, result: Dict[str, Any], field_path: str) -> None:
        """
        Process a field path containing wildcards and add matching fields to the result.

        Args:
            result: The result dictionary to update
            field_path: The field path with wildcards
        """
        ...

    def _find_matching_paths(self, data: Dict[str, Any], pattern_parts: List[str], current_path: str = "") -> Set[str]:
        """
        Find all paths in the data that match the given pattern parts.

        Args:
            data: The data to search in
            pattern_parts: The parts of the pattern to match
            current_path: The current path being built

        Returns:
            A set of field paths that match the pattern
        """
        ...

    def _remove_field(self, data: Dict[str, Any], field_path: str) -> None:
        """
        Remove a field from the data by its path.

        Args:
            data: The data to modify
            field_path: The path of the field to remove
        """
        ...

    def _limit_depth(self, data: Dict[str, Any], max_depth: int, current_depth: int = 0) -> Dict[str, Any]:
        """
        Limit the depth of nested objects in the data.

        Args:
            data: The data to limit
            max_depth: The maximum depth to allow
            current_depth: The current depth in the recursion

        Returns:
            A copy of the data with depth limited to max_depth
        """
        ...

    def _add_metadata(
        self,
        result: Dict[str, Any],
        included_fields: Optional[List[str]],
        excluded_fields: Optional[List[str]],
        max_depth: Optional[int]
    ) -> Dict[str, Any]:
        """
        Add metadata about the partial response.

        Args:
            result: The partial response data
            included_fields: The fields that were included
            excluded_fields: The fields that were excluded
            max_depth: The maximum depth that was applied

        Returns:
            A dictionary with 'data' and '_metadata' keys
        """
        ...

    def _count_fields(self, data: Dict[str, Any], prefix: str = "") -> int:
        """
        Count the total number of fields in the data.

        Args:
            data: The data to count fields in
            prefix: The prefix for the current path

        Returns:
            The total number of fields
        """
        ...

    def _deep_copy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deep copy of the data.

        Args:
            data: The data to copy

        Returns:
            A deep copy of the data
        """
        ...

"""
Partial response helper for the crudclient testing framework.

This module provides utilities for simulating partial API responses where only
specific fields are included in the response. It supports field selection using
dot notation, wildcards, exclusions, and depth limiting, allowing tests to verify
client behavior with different response structures.
"""

from typing import Any, Dict, List, Optional, Set, Union
import copy


class PartialResponseHelper:
    """
    Helper for simulating partial responses in tests.

    This class provides a flexible way to generate partial API responses by
    selecting specific fields from a complete response object. It supports
    advanced field selection using dot notation for nested fields, wildcards
    for pattern matching, field exclusions, and depth limiting.

    The helper is particularly useful for testing APIs that support field
    filtering capabilities (like Google API's fields parameter or GraphQL-style
    field selection), allowing tests to verify that clients correctly handle
    responses with varying levels of completeness.
    """

    def __init__(
        self,
        full_response: Dict[str, Any],
        field_separator: str = ".",
        wildcard_char: str = "*",
        default_fields: Optional[List[str]] = None
    ):
        """
        Initialize the partial response helper with configuration options.

        This constructor sets up the partial response helper with a complete
        response object and configuration for how field selection should be handled.
        It supports customization of field path notation and default fields to include.

        Args:
            full_response: Complete response data that will be filtered
            field_separator: Character used to separate nested fields in field paths
                (e.g., "user.address.city" with "." as separator)
            wildcard_char: Character used as wildcard in field paths
                (e.g., "user.*.name" to select all name fields under user)
            default_fields: Default fields to include if none specified in get_partial_response
        """
        self.full_response = full_response
        self.field_separator = field_separator
        self.wildcard_char = wildcard_char
        self.default_fields = default_fields or []

    def get_partial_response(
        self,
        fields: Optional[List[str]] = None,
        exclude_fields: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        Get a partial response containing only the specified fields.

        This method filters the full response to include only the requested fields,
        applying any exclusions and depth limitations. It supports complex field
        selection patterns including nested fields via dot notation and wildcards
        for matching multiple fields.

        Args:
            fields: List of field paths to include (using dot notation for nested fields)
                Example: ["id", "user.name", "items.*.id"]
            exclude_fields: List of field paths to exclude from the result
                Example: ["user.email", "sensitive_data"]
            max_depth: Maximum depth of nested objects to include
                (useful for limiting response complexity)
            include_metadata: Whether to include metadata about the partial response
                (adds a _metadata object with information about the filtering)

        Returns:
            Dict containing only the requested fields from the full response
        """
        # Use default fields if none provided
        fields_to_use = fields or self.default_fields

        # If no fields specified and no defaults, return empty response
        if not fields_to_use and exclude_fields:
            # If only exclusions provided, start with full response and remove excluded fields
            result = self._deep_copy(self.full_response)
            for field_path in exclude_fields:
                self._remove_field(result, field_path)

            # Apply max depth if specified
            if max_depth is not None:
                result = self._limit_depth(result, max_depth)

            # Add metadata if requested
            if include_metadata:
                result = self._add_metadata(result, fields_to_use, exclude_fields, max_depth)

            return result
        elif not fields_to_use:
            # If no fields specified and no exclusions, return empty dict
            result = {}
        else:
            # Process included fields
            result = {}

            for field_path in fields_to_use:
                # Handle wildcards in field paths
                if self.wildcard_char in field_path:
                    self._process_wildcard_field(result, field_path)
                else:
                    parts = field_path.split(self.field_separator)
                    value = self.full_response

                    try:
                        # Navigate to the nested value
                        for part in parts[:-1]:
                            if isinstance(value, dict) and part in value:
                                value = value[part]
                            else:
                                # Path doesn't exist
                                break
                        else:
                            # We got through all parts except the last one
                            last_part = parts[-1]
                            if isinstance(value, dict) and last_part in value:
                                # Build the nested structure in the result
                                current = result
                                for i, part in enumerate(parts[:-1]):
                                    if part not in current:
                                        current[part] = {}
                                    current = current[part]
                                current[last_part] = value[last_part]
                    except (KeyError, TypeError):
                        # Skip fields that don't exist or can't be accessed
                        pass

            # Apply exclusions if specified
            if exclude_fields:
                for field_path in exclude_fields:
                    self._remove_field(result, field_path)

            # Apply max depth if specified
            if max_depth is not None:
                result = self._limit_depth(result, max_depth)

            # Add metadata if requested
            if include_metadata:
                result = self._add_metadata(result, fields_to_use, exclude_fields, max_depth)

        return result

    def _process_wildcard_field(self, result: Dict[str, Any], field_path: str) -> None:
        """
        Process a field path containing wildcards.

        This method handles field paths that contain wildcard characters,
        expanding them to match all applicable fields in the full response
        and adding the matching fields to the result.

        Args:
            result: Result dictionary to update with matching fields
            field_path: Field path with wildcards (e.g., "users.*.name")
        """
        parts = field_path.split(self.field_separator)

        # Find all matching paths
        matching_paths = self._find_matching_paths(self.full_response, parts)

        # Add each matching path to the result
        for path in matching_paths:
            path_parts = path.split(self.field_separator)
            value = self.full_response

            # Navigate to the value
            for part in path_parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    break
            else:
                # Build the nested structure in the result
                current = result
                for i, part in enumerate(path_parts[:-1]):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[path_parts[-1]] = value

    def _find_matching_paths(self, data: Dict[str, Any], pattern_parts: List[str], current_path: str = "") -> Set[str]:
        """
        Find all paths in the data that match the pattern.

        This method recursively searches through the data structure to find
        all paths that match the given pattern, handling wildcards by expanding
        them to match all keys at that level.

        Args:
            data: Data structure to search through
            pattern_parts: Parts of the pattern to match (split by separator)
            current_path: Current path being built during recursion

        Returns:
            Set of matching field paths as strings
        """
        if not isinstance(data, dict):
            return set()

        if not pattern_parts:
            return {current_path} if current_path else set()

        result = set()
        current_part = pattern_parts[0]
        remaining_parts = pattern_parts[1:]

        if current_part == self.wildcard_char:
            # Wildcard matches all keys at this level
            for key in data:
                new_path = key if not current_path else f"{current_path}{self.field_separator}{key}"
                if remaining_parts:
                    # Continue matching with remaining parts
                    if isinstance(data[key], dict):
                        result.update(self._find_matching_paths(data[key], remaining_parts, new_path))
                else:
                    # End of pattern, add this path
                    result.add(new_path)
        elif current_part in data:
            # Exact match
            new_path = current_part if not current_path else f"{current_path}{self.field_separator}{current_part}"
            if remaining_parts:
                # Continue matching with remaining parts
                if isinstance(data[current_part], dict):
                    result.update(self._find_matching_paths(data[current_part], remaining_parts, new_path))
            else:
                # End of pattern, add this path
                result.add(new_path)

        return result

    def _remove_field(self, data: Dict[str, Any], field_path: str) -> None:
        """
        Remove a field from the data structure.

        This method removes a field specified by its path from the data structure,
        handling nested fields by navigating through the structure using the
        field separator.

        Args:
            data: Data structure to modify
            field_path: Path of the field to remove (e.g., "user.address.phone")
        """
        parts = field_path.split(self.field_separator)

        if len(parts) == 1:
            # Direct field at the top level
            if parts[0] in data:
                del data[parts[0]]
        else:
            # Nested field
            current = data
            for part in parts[:-1]:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    # Path doesn't exist
                    return

            # Remove the last part
            last_part = parts[-1]
            if isinstance(current, dict) and last_part in current:
                del current[last_part]

    def _limit_depth(self, data: Dict[str, Any], max_depth: int, current_depth: int = 0) -> Dict[str, Any]:
        """
        Limit the depth of nested objects in the response.

        This method recursively processes the data structure to ensure it doesn't
        exceed the specified maximum depth, replacing deeper nested objects with
        summary information.

        Args:
            data: Data structure to limit depth for
            max_depth: Maximum depth to include (0 = top level only)
            current_depth: Current depth in the recursion

        Returns:
            Data structure with depth limited to max_depth
        """
        if not isinstance(data, dict) or current_depth >= max_depth:
            return data

        result = {}
        for key, value in data.items():
            if isinstance(value, dict):
                if current_depth < max_depth - 1:
                    result[key] = self._limit_depth(value, max_depth, current_depth + 1)
                else:
                    # At max depth, include only a summary
                    result[key] = {"_summary": f"Object with {len(value)} properties"}
            else:
                result[key] = value

        return result

    def _add_metadata(
        self,
        result: Dict[str, Any],
        included_fields: Optional[List[str]],
        excluded_fields: Optional[List[str]],
        max_depth: Optional[int]
    ) -> Dict[str, Any]:
        """
        Add metadata about the partial response.

        This method adds metadata to the response indicating that it's a partial
        response and providing information about the filtering that was applied.

        Args:
            result: Result data to add metadata to
            included_fields: Fields that were included in the filter
            excluded_fields: Fields that were excluded from the filter
            max_depth: Maximum depth that was applied

        Returns:
            Data structure with added metadata
        """
        metadata = {
            "partial_response": True,
            "total_fields_in_full_response": self._count_fields(self.full_response),
            "fields_included": len(included_fields) if included_fields else 0,
            "fields_excluded": len(excluded_fields) if excluded_fields else 0,
        }

        if max_depth is not None:
            metadata["max_depth"] = max_depth

        return {
            "data": result,
            "_metadata": metadata
        }

    def _count_fields(self, data: Dict[str, Any], prefix: str = "") -> int:
        """
        Count the total number of fields in the data structure.

        This method recursively counts all fields in the data structure,
        including nested fields, to provide an accurate count for metadata.

        Args:
            data: Data structure to count fields in
            prefix: Current field prefix for recursion

        Returns:
            Total number of fields in the data structure
        """
        if not isinstance(data, dict):
            return 1

        count = 0
        for key, value in data.items():
            field_name = key if not prefix else f"{prefix}{self.field_separator}{key}"
            if isinstance(value, dict):
                count += self._count_fields(value, field_name)
            else:
                count += 1

        return count

    def _deep_copy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deep copy of the data structure.

        This method creates a deep copy of the data structure to ensure that
        modifications to the partial response don't affect the original data.

        Args:
            data: Data structure to copy

        Returns:
            Deep copy of the data structure
        """
        return copy.deepcopy(data)

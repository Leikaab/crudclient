"""
Partial response helper for mock client.
"""

from typing import Any, Dict, List


class PartialResponseHelper:
    """Helper for simulating partial responses."""

    def __init__(self, full_response: Dict[str, Any]):
        """
        Initialize partial response helper.

        Args:
            full_response: Complete response data
        """
        self.full_response = full_response

    def get_partial_response(self, fields: List[str]) -> Dict[str, Any]:
        """
        Get a partial response containing only the specified fields.

        Args:
            fields: List of field paths (dot notation supported)

        Returns:
            Dict containing only the requested fields
        """
        result = {}

        for field_path in fields:
            parts = field_path.split('.')
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

        return result

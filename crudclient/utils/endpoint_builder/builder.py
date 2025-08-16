"""
Main EndpointBuilder class for orchestrating endpoint construction.

This module contains the EndpointBuilder class which coordinates
endpoint path construction by utilizing the utility functions from
other modules in this package.
"""

from typing import Any, List, Optional, Union

from .path_utils import join_path_segments
from .segments import build_resource_segments
from .validators import validate_path_segments

# Type alias for path arguments
PathArgs = Optional[Union[str, int]]


class EndpointBuilder:
    """
    Builder class for constructing API endpoint paths using declarative configuration.

    This class encapsulates the logic for building complete endpoint paths
    by combining parent paths, prefixes, resource paths, and additional
    path segments. Configuration is done via class attributes in a declarative
    style similar to Django REST Framework serializers.

    Class Attributes
    ----------------
    resource_path : Optional[str]
        The base resource path (e.g., "users", "posts"). Set this in subclasses.
    endpoint_prefix : Optional[Union[str, List[str]]]
        Custom prefix to prepend to endpoints. Can be a string or list of segments.
    prefix_mode : str
        How to handle parent/child prefix combination. Options: "override", "append".
        - "override": Child prefix replaces parent prefix
        - "append": Child prefix is added after parent prefix

    Instance Attributes
    -------------------
    parent_builder : Optional[EndpointBuilder]
        Reference to the parent resource's endpoint builder for nested resources.
    """

    # Declarative class attributes (like DRF serializers)
    resource_path: Optional[str] = None
    endpoint_prefix: Optional[Union[str, List[str]]] = None
    prefix_mode: str = "override"

    def __init__(self, parent_builder: Optional["EndpointBuilder"] = None):
        """
        Initialize the EndpointBuilder with minimal instance configuration.

        Parameters
        ----------
        parent_builder : Optional[EndpointBuilder]
            Reference to the parent resource's endpoint builder for nested resources.
        """
        self.parent_builder = parent_builder

        # Copy class attributes to instance for runtime access
        self.resource_path = self.__class__.resource_path
        self.endpoint_prefix = self.__class__.endpoint_prefix
        self.prefix_mode = self.__class__.prefix_mode

    def build_endpoint(self, *args: PathArgs, parent_args: Optional[List[PathArgs]] = None, crud_instance: Optional[Any] = None) -> str:
        """
        Build a complete endpoint path.

        This is the main orchestration method that combines all path components
        to create the final endpoint URL path.

        Parameters
        ----------
        *args : PathArgs
            Additional path segments (e.g., resource IDs, sub-resources).
        parent_args : Optional[List[PathArgs]]
            Arguments to pass to parent endpoint builder for nested resources.
        crud_instance : Optional[Any]
            The CRUD instance that may provide dynamic prefix data.

        Returns
        -------
        str
            The complete endpoint path.

        Examples
        --------
        >>> builder = EndpointBuilder(resource_path="users")
        >>> builder.build_endpoint()
        'users'

        >>> builder.build_endpoint(123, "posts")
        'users/123/posts'

        >>> child_builder = EndpointBuilder(resource_path="posts", parent_builder=builder)
        >>> child_builder.build_endpoint(456, parent_args=[123])
        'users/123/posts/456'
        """
        # Validate the path segments
        validate_path_segments(*args)

        # Get prefix segments
        prefix_segments = self.get_prefix_segments(crud_instance=crud_instance)

        # Get parent path if this is a nested resource
        parent_path = self.get_parent_path(parent_args)

        # Build resource segments
        resource_segments = build_resource_segments(self.resource_path, *args)

        # Combine all segments
        all_segments: List[str] = []

        # Add prefix segments
        all_segments.extend(prefix_segments)

        # Add parent path segments (already includes parent prefix)
        if parent_path:
            all_segments.append(parent_path)

        # Add resource segments
        all_segments.extend(resource_segments)

        # Join all segments into final path
        # Cast to PathArgs for type safety
        path_args = [segment for segment in all_segments]
        return join_path_segments(*path_args)

    def get_parent_path(self, parent_args: Optional[List[PathArgs]] = None) -> Optional[str]:
        """
        Get the parent path for nested resources.

        Parameters
        ----------
        parent_args : Optional[List[PathArgs]]
            Arguments to pass to parent endpoint builder.

        Returns
        -------
        Optional[str]
            The parent path or None if this is not a nested resource.
        """
        if not self.parent_builder:
            return None

        # If no parent args provided, return parent's base path
        if not parent_args:
            return self.parent_builder.build_endpoint()

        # Build parent path with provided arguments
        return self.parent_builder.build_endpoint(*parent_args)

    def get_prefix_segments(self, crud_instance: Optional[Any] = None) -> List[str]:
        """
        Get the prefix segments to prepend to the endpoint with proper parent handling.

        This method implements the declarative prefix combination logic based on
        the prefix_mode setting.

        Parameters
        ----------
        crud_instance : Optional[Any]
            The CRUD instance that may provide dynamic prefix data.
            Used for backward compatibility with existing patterns.

        Returns
        -------
        List[str]
            List of prefix segments. Empty list if no prefix.
        """
        segments = []

        # Get parent prefix if exists and mode is append
        if self.parent_builder and self.prefix_mode == "append":
            segments.extend(self.parent_builder.get_prefix_segments(crud_instance))

        # Add own prefix
        if self.endpoint_prefix:
            if isinstance(self.endpoint_prefix, str):
                # Split string prefix by '/' and filter out empty segments
                segments.extend([seg for seg in self.endpoint_prefix.split("/") if seg])
            elif isinstance(self.endpoint_prefix, list):
                # Add list of segments directly
                segments.extend([str(seg) for seg in self.endpoint_prefix if seg])

        # If override mode and no own prefix, use parent's
        elif self.parent_builder and self.prefix_mode == "override":
            segments.extend(self.parent_builder.get_prefix_segments(crud_instance))

        return segments

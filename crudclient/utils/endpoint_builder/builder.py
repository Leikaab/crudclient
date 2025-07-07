"""
Main EndpointBuilder class for orchestrating endpoint construction.

This module contains the EndpointBuilder class which coordinates
endpoint path construction by utilizing the utility functions from
other modules in this package.
"""

from typing import List, Optional, Union

from .validators import validate_path_segments
from .path_utils import join_path_segments
from .segments import build_resource_segments

# Type alias for path arguments
PathArgs = Optional[Union[str, int]]


class EndpointBuilder:
    """
    Builder class for constructing API endpoint paths.

    This class encapsulates the logic for building complete endpoint paths
    by combining parent paths, prefixes, resource paths, and additional
    path segments.

    Attributes
    ----------
    resource_path : Optional[str]
        The base resource path (e.g., "users", "posts").
    parent_builder : Optional[EndpointBuilder]
        Reference to the parent resource's endpoint builder for nested resources.
    endpoint_prefix : Optional[str]
        Custom prefix to prepend to endpoints.
    """

    def __init__(
        self,
        resource_path: Optional[str] = None,
        parent_builder: Optional['EndpointBuilder'] = None,
        endpoint_prefix: Optional[str] = None
    ):
        """
        Initialize the EndpointBuilder.

        Parameters
        ----------
        resource_path : Optional[str]
            The base resource path (e.g., "users", "posts").
        parent_builder : Optional[EndpointBuilder]
            Reference to the parent resource's endpoint builder for nested resources.
        endpoint_prefix : Optional[str]
            Custom prefix to prepend to endpoints. If None, will attempt to get
            from parent builder if available.
        """
        self.resource_path = resource_path
        self.parent_builder = parent_builder
        self._endpoint_prefix = endpoint_prefix

    def build_endpoint(self, *args: PathArgs, parent_args: Optional[List[PathArgs]] = None) -> str:
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
        prefix_segments = self.get_prefix_segments()

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

    def _get_endpoint_prefix(self) -> Optional[str]:
        """
        Get the endpoint prefix for this resource.

        Returns the explicitly set prefix, or attempts to get it from
        the parent builder if available.

        Returns
        -------
        Optional[str]
            The endpoint prefix or None if not set.
        """
        # Use explicitly set prefix if available
        if self._endpoint_prefix is not None:
            return self._endpoint_prefix

        # Try to get prefix from parent
        if self.parent_builder:
            return self.parent_builder._get_endpoint_prefix()

        return None

    def get_prefix_segments(self) -> List[str]:
        """
        Get the prefix segments to prepend to the endpoint.

        Returns
        -------
        List[str]
            List of prefix segments. Empty list if no prefix.
        """
        prefix = self._get_endpoint_prefix()

        if not prefix:
            return []

        # Split prefix by '/' and filter out empty segments
        return [seg for seg in prefix.split('/') if seg]

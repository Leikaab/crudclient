"""
Module `endpoint.py`
===================

This module provides functions for building and manipulating API endpoints.
It handles the construction of resource paths, including nested resources,
and ensures proper formatting of URL paths.
"""

import logging
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

if TYPE_CHECKING:
    from .base import Crud

from ..types import JSONDict

# Type alias for path arguments
PathArgs = Optional[Union[str, int]]

def _endpoint_prefix(self: "Crud") -> Union[Tuple[Optional[str], Optional[str]], List[Optional[str]]]:
    """
    Construct the endpoint prefix.

    This method can be overridden in subclasses to provide a custom endpoint prefix.

    Returns:
        Union[Tuple[Optional[str], Optional[str]], List[Optional[str]]]: The endpoint prefix segments.
    """
    ...

def _validate_path_segments(self: "Crud", *args: PathArgs) -> None:
    """
    Validate the types of path segments.

    Args:
        *args: Variable number of path segments (e.g., resource IDs, actions).

    Raises:
        TypeError: If any arg is not None, str, or int.
    """
    ...

def _get_parent_path(self: "Crud", parent_args: Optional[tuple] = None) -> str:
    """
    Get the parent path if a parent exists.

    Args:
        parent_args: Optional tuple containing path segments for the parent resource.

    Returns:
        str: The parent path or empty string if no parent exists.
    """
    ...

def _build_resource_path(self: "Crud", *args: PathArgs) -> List[str]:
    """
    Build the current resource path segments.

    Args:
        *args: Variable number of path segments (e.g., resource IDs, actions).

    Returns:
        List[str]: The resource path segments.
    """
    ...

def _get_prefix_segments(self: "Crud") -> List[str]:
    """
    Get the prefix segments for the endpoint.

    Returns:
        List[str]: The prefix segments.
    """
    ...

def _join_path_segments(self: "Crud", segments: List[str]) -> str:
    """
    Join path segments into a URL.

    Args:
        segments: List of path segments.

    Returns:
        str: The joined URL path.
    """
    ...

def _get_endpoint(self: "Crud", *args: Optional[Union[str, int]], parent_args: Optional[tuple] = None) -> str:
    """
    Construct the endpoint path.

    Args:
        *args: Variable number of path segments (e.g., resource IDs, actions).
        parent_args: Optional tuple containing path segments for the parent resource.

    Returns:
        str: The constructed endpoint path.

    Raises:
        TypeError: If arg in args or parent_args is not None, str, or int.
    """
    ...

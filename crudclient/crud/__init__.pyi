"""
Module `crud`
============

This module defines the Crud class, which provides a generic implementation of CRUD
(Create, Read, Update, Delete) operations for API resources. It supports both top-level
and nested resources, and can be easily extended for specific API endpoints.
"""

from .base import Crud, CrudInstance, CrudType, HttpMethodString, T
from .endpoint import (
    PathArgs,
    _build_resource_path,
    _endpoint_prefix,
    _get_endpoint,
    _get_parent_path,
    _get_prefix_segments,
    _join_path_segments,
    _validate_path_segments,
)
from .operations import (
    create_operation,
    custom_action_operation,
    destroy_operation,
    list_operation,
    partial_update_operation,
    read_operation,
    update_operation,
)
from .response_conversion import (
    _convert_to_list_model,
    _convert_to_model,
    _dump_data,
    _fallback_list_conversion,
    _init_response_strategy,
    _validate_list_return,
    _validate_response,
)

__all__ = ["Crud"]

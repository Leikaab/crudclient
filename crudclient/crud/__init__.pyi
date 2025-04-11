"""
Module `crud`
============

This module defines the Crud class, which provides a generic implementation of CRUD
(Create, Read, Update, Delete) operations for API resources. It supports both top-level
and nested resources, and can be easily extended for specific API endpoints.
"""

from .base import Crud, HttpMethodString, CrudInstance, CrudType, T
from .endpoint import (
    PathArgs,
    _endpoint_prefix,
    _validate_path_segments,
    _get_parent_path,
    _build_resource_path,
    _get_prefix_segments,
    _join_path_segments,
    _get_endpoint,
)
from .operations import (
    list_operation,
    create_operation,
    read_operation,
    update_operation,
    partial_update_operation,
    destroy_operation,
    custom_action_operation,
)
from .response_conversion import (
    _init_response_strategy,
    _validate_response,
    _convert_to_model,
    _convert_to_list_model,
    _validate_list_return,
    _fallback_list_conversion,
    _dump_data,
)

__all__ = ["Crud"]

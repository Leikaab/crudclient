"""
Module `base.py`
===============

This module defines the Crud class, which is the base class for all CRUD operations.
It provides a generic implementation of CRUD (Create, Read, Update, Delete) operations
for API resources. It supports both top-level and nested resources, and can be easily
extended for specific API endpoints.
"""

import logging
from typing import Any, Generic, List, Literal, Optional, Tuple, Type, TypeVar, Union, cast
from typing_extensions import TypeAlias

from ..client import Client
from ..exceptions import ModelConversionError, ValidationError
from ..models import ApiResponse
from ..response_strategies import (
    DefaultResponseModelStrategy,
    ModelDumpable,
    PathBasedResponseModelStrategy,
    ResponseModelStrategy,
    ResponseTransformer,
)
from ..types import JSONDict, JSONList, RawResponse

T = TypeVar("T", bound=ModelDumpable)
HttpMethodString: TypeAlias = Literal["get", "post", "put", "patch", "delete", "head", "options", "trace"]
CrudInstance: TypeAlias = "Crud[Any]"
CrudType: TypeAlias = Type[CrudInstance]
PathArgs = Optional[Union[str, int]]


class Crud(Generic[T]):
    """
    Base class for CRUD operations on API resources, supporting both top-level and nested resources.

    This class provides a generic implementation of common CRUD operations and can be
    easily extended for specific API endpoints.

    Attributes:
        _resource_path: The base path for the resource in the API.
        _datamodel: The data model class for the resource.
        _api_response_model: Custom API response model, if any.
        _response_strategy: The strategy to use for converting responses.
        _list_return_keys: Possible keys for list data in API responses.
        allowed_actions: List of allowed methods for this resource.
    """

    _resource_path: str
    _datamodel: Optional[Type[T]]
    _api_response_model: Optional[Type[ApiResponse]]
    _response_strategy: Optional[ResponseModelStrategy[T]]
    _list_return_keys: List[str]
    allowed_actions: List[str]
    client: Client
    parent: Optional["Crud"]

    def __init__(self, client: Client, parent: Optional["Crud"] = None) -> None:
        """
        Initialize the CRUD resource.

        Args:
            client: An instance of the API client.
            parent: Optional parent Crud instance for nested resources.

        Raises:
            ValueError: If the resource path is not set.
        """
        ...

    # Methods imported from other modules
    from .endpoint import (
        _endpoint_prefix,
        _validate_path_segments,
        _get_parent_path,
        _build_resource_path,
        _get_prefix_segments,
        _join_path_segments,
        _get_endpoint,
    )

    from .operations import (
        list,
        create,
        read,
        update,
        partial_update,
        destroy,
        custom_action,
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

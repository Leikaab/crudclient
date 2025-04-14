"""
Module `base.py`
===============

This module defines the Crud class, which is the base class for all CRUD operations.
It provides a generic implementation of CRUD (Create, Read, Update, Delete) operations
for API resources. It supports both top-level and nested resources, and can be easily
extended for specific API endpoints.
"""

import logging
from typing import (
    Any,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from typing_extensions import TypeAlias

from ..client import Client
from ..exceptions import (
    DataValidationError,  # Replaced ModelConversionError, ValidationError
)
from ..models import ApiResponse
from ..response_strategies import (
    DefaultResponseModelStrategy,
    ModelDumpable,
    PathBasedResponseModelStrategy,
    ResponseModelStrategy,
    ResponseTransformer,
)
from ..types import JSONDict, JSONList, RawResponse

# Type alias for path arguments used in endpoint methods
PathArgs = Optional[Union[str, int]]

T = TypeVar("T", bound=ModelDumpable)
HttpMethodString: TypeAlias = Literal["get", "post", "put", "patch", "delete", "head", "options", "trace"]
CrudInstance: TypeAlias = "Crud[Any]"
CrudType: TypeAlias = Type[CrudInstance]

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
    # --- Endpoint Methods ---
    def _endpoint_prefix(self: "Crud") -> Union[Tuple[Optional[str], Optional[str]], List[Optional[str]]]: ...
    def _validate_path_segments(self: "Crud", *args: Optional[Union[str, int]]) -> None: ...
    def _get_parent_path(self: "Crud", parent_args: Optional[tuple] = None) -> str: ...
    def _build_resource_path(self: "Crud", *args: Optional[Union[str, int]]) -> List[str]: ...
    def _get_prefix_segments(self: "Crud") -> List[str]: ...
    def _join_path_segments(self: "Crud", segments: List[str]) -> str: ...
    def _get_endpoint(self: "Crud", *args: Optional[Union[str, int]], parent_args: Optional[tuple] = None) -> str: ...

    # --- Operations Methods ---
    def list(self: "Crud", parent_id: Optional[str] = None, params: Optional[JSONDict] = None) -> Union[JSONList, List[T], ApiResponse]: ...
    def create(self: "Crud", data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]: ...
    def read(self: "Crud", resource_id: str, parent_id: Optional[str] = None) -> Union[T, JSONDict]: ...
    def update(self: "Crud", resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]: ...
    def partial_update(self: "Crud", resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]: ...
    def destroy(self: "Crud", resource_id: str, parent_id: Optional[str] = None) -> None: ...
    def custom_action(
        self: "Crud",
        action: str,
        method: str = "post",
        resource_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        data: Optional[Union[JSONDict, T]] = None,
        params: Optional[JSONDict] = None,
    ) -> Union[T, JSONDict, List[JSONDict]]: ...

    # --- Response Conversion Methods ---
    def _init_response_strategy(self: "Crud") -> None: ...
    def _validate_response(self: "Crud", data: RawResponse) -> Union[JSONDict, JSONList]: ...
    def _convert_to_model(self: "Crud", data: RawResponse) -> Union[T, JSONDict]: ...
    def _convert_to_list_model(self: "Crud", data: JSONList) -> Union[List[T], JSONList]: ...
    def _validate_list_return(self: "Crud", data: RawResponse) -> Union[JSONList, List[T], ApiResponse]: ...
    def _fallback_list_conversion(self: "Crud", data: RawResponse) -> Union[JSONList, List[T], ApiResponse]: ...
    def _dump_data(self: "Crud", data: Optional[Union[JSONDict, T]], partial: bool = False) -> JSONDict: ...

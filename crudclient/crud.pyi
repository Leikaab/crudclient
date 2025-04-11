"""
Module `crud.py`
================

This module defines the Crud class, which provides a generic implementation of CRUD
(Create, Read, Update, Delete) operations for API resources. It supports both top-level
and nested resources, and can be easily extended for specific API endpoints.

Class `Crud`
------------

The `Crud` class is a generic base class that implements common CRUD operations.
It can be subclassed to create specific resource classes for different API endpoints.

To use the Crud class:
    1. Subclass `Crud` for your specific resource.
    2. Set the `_resource_path`, `_datamodel`, and other class attributes as needed.
    3. Optionally override methods to customize behavior.

Example:
    class UsersCrud(Crud[User]):
        _resource_path = "users"
        _datamodel = User

    users_crud = UsersCrud(client)
    user_list = users_crud.list()

Classes:
    - Crud: Generic base class for CRUD operations on API resources.

Type Variables:
    - T: The type of the data model used for the resource.
"""

import logging
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Literal,
    Optional,
    Protocol,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
    Union,
    cast,
)

from pydantic import ValidationError as PydanticValidationError

from .client import Client
from .exceptions import ModelConversionError, ValidationError
from .models import ApiResponse
from .response_strategies import (
    DefaultResponseModelStrategy,
    ModelDumpable,
    PathBasedResponseModelStrategy,
    ResponseModelStrategy,
    ResponseTransformer,
)
from .types import JSONDict, JSONList, RawResponse

T = TypeVar("T", bound=ModelDumpable)
HttpMethodString: TypeAlias = Literal["get", "post", "put", "patch", "delete", "head", "options", "trace"]
CrudInstance: TypeAlias = "Crud[Any]"
CrudType: TypeAlias = Type[CrudInstance]
ApiResponseInstance: TypeAlias = "ApiResponse[Any]"
ApiResponseType: TypeAlias = Type[ApiResponseInstance]
PathArgs: TypeAlias = str | int | None

class Crud(Generic[T]):
    """
    Base class for CRUD operations on API resources, supporting both top-level and nested resources.

    This class provides a generic implementation of common CRUD operations and can be
    easily extended for specific API endpoints.

    :ivar _resource_path: str The base path for the resource in the API.
    :ivar _datamodel: Optional[Type[T]] The data model class for the resource.
    :ivar _methods: List[str] List of allowed methods for this resource.
    :ivar _api_response_model: Optional[Type[ApiResponse]] Custom API response model, if any.
    :ivar _list_return_keys: List[str] Possible keys for list data in API responses.

    Methods:
        __init__: Initialize the CRUD resource.
        list: Retrieve a list of resources.
        create: Create a new resource.
        read: Retrieve a specific resource.
        update: Update a specific resource.
        partial_update: Partially update a specific resource.
        destroy: Delete a specific resource.
        custom_action: Perform a custom action on the resource.
    """

    _resource_path: str
    _datamodel: Optional[Type[T]]
    _parent_resource: Optional[CrudType]
    _methods: List[str]
    _api_response_model: Optional[ApiResponseType]
    _list_return_keys: List[str]
    _response_model_strategy: Optional[Type[ResponseModelStrategy[T]]]
    _single_item_path: Optional[str]
    _list_item_path: Optional[str]
    _response_pre_transform: Optional[ResponseTransformer]
    client: Client
    _parent: Optional["Crud"]
    _strategy: ResponseModelStrategy[T]

    def __init__(self, client: Client, parent: Optional["Crud"] = None) -> None:
        """
        Initialize the CRUD resource.

        :param client: Client An instance of the API client.
        :param parent: Optional[Crud] Optional parent Crud instance for nested resources.
        """
        ...

    def _init_response_strategy(self) -> None:
        """
        Initialize the response model strategy.

        This method creates an instance of the appropriate response model strategy
        based on the class configuration.
        """
        ...

    def _endpoint_prefix(self) -> Union[Tuple[Optional[str]], List[Optional[str]]]:
        """
        Construct the endpoint prefix.

        This method can be overridden in subclasses to provide a custom endpoint prefix.

        Example:
        ```python
            @classmethod
            def _endpoint_prefix(self):
                return ["companies", "mycompany-ltd"]
        ```

        :return: List[str] The endpoint prefix segments.
        """
        ...

    def _validate_path_segments(self, *args: PathArgs) -> None:
        """
        Validate the types of path segments.

        :param args: Variable number of path segments (e.g., resource IDs, actions).
        :raises TypeError: If any arg is not None, str, or int.
        """
        ...

    def _get_parent_path(self, parent_args: Optional[tuple] = None) -> str:
        """
        Get the parent path if a parent exists.

        :param parent_args: Optional tuple containing path segments for the parent resource.
        :return: str The parent path or empty string if no parent exists.
        """
        ...

    def _build_resource_path(self, *args: PathArgs) -> List[str]:
        """
        Build the current resource path segments.

        :param args: Variable number of path segments (e.g., resource IDs, actions).
        :return: List[str] The resource path segments.
        """
        ...

    def _get_prefix_segments(self) -> List[str]:
        """
        Get the prefix segments for the endpoint.

        :return: List[str] The prefix segments.
        """
        ...

    def _join_path_segments(self, segments: List[str]) -> str:
        """
        Join path segments into a URL.

        :param segments: List of path segments.
        :return: str The joined URL path.
        """
        ...

    def _get_endpoint(self, *args: Optional[Union[str, int]], parent_args: Optional[tuple] = None) -> str:
        """
        Construct the endpoint path.

        :param args: Variable number of path segments (e.g., resource IDs, actions).
        :param parent_args: Optional tuple containing path segments for the parent resource.
        :return: str The constructed endpoint path.
        :raises TypeError: If arg in args or parent_args is not None, str, or int.
        """
        ...

    def _validate_response(self, data: RawResponse) -> Union[JSONDict, JSONList]:
        """
        Validate the API response data.

        :param data: RawResponse The API response data.
        :return: Union[JSONDict, JSONList] The validated data.
        :raises ValueError: If the response is an unexpected type.
        """
        ...

    def _convert_to_model(self, data: RawResponse) -> Union[T, JSONDict]:
        """
        Convert the API response to the datamodel type.

        This method uses the configured response model strategy to convert the data.
        The strategy handles extracting data from the response and converting it to
        the appropriate model type.

        :param data: RawResponse The API response data.
        :return: Union[T, JSONDict] An instance of the datamodel or a dictionary.
        :raises ValueError: If the response is an unexpected type or conversion fails.
        """
        ...

    def _convert_to_list_model(self, data: JSONList) -> Union[List[T], JSONList]:
        """
        Convert the API response to a list of datamodel types.

        :param data: JSONList The API response data.
        :return: Union[List[T], JSONList] A list of instances of the datamodel or the original list.
        :raises ValueError: If the response is an unexpected type.
        """
        ...

    def _validate_list_return(self, data: RawResponse) -> Union[JSONList, List[T], ApiResponse]:
        """
        Validate and convert the list response data.

        This method uses the configured response model strategy to validate and convert
        the list response data. It handles different response formats and extracts list
        data according to the strategy.

        :param data: RawResponse The API response data.
        :return: Union[JSONList, List[T], ApiResponse] Validated and converted list data.
        :raises ValueError: If the response format is unexpected or conversion fails.
        """
        ...

    def _fallback_list_conversion(
        self, validated_data: Union[JSONDict, JSONList], original_error: Exception
    ) -> Union[JSONList, List[T], ApiResponse]:
        """
        Fallback conversion logic for list responses when the strategy fails.

        This method implements the original behavior for backward compatibility.

        :param validated_data: The validated response data.
        :param original_error: The original exception from the strategy.
        :return: Union[JSONList, List[T], ApiResponse] Converted list data.
        :raises ValueError: If the response format is unexpected or conversion fails.
        """
        ...

    def _dump_data(self, data: Optional[Union[JSONDict, T]], partial: bool = False) -> JSONDict:
        """
        Dump the data model to a JSON-serializable dictionary.

        :param data: Optional[Union[JSONDict, T]] The data to dump.
        :param partial: bool Whether this is a partial update (default: False).
        :return: JSONDict The dumped data.
        :raises ValueError: If the data is not a dict, None, or an instance of the datamodel.
        :raises TypeError: If the data is not of the expected type.
        :raises ValidationError: If the data fails validation.
        """
        ...

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None) -> Union[JSONList, List[T], ApiResponse]:
        """
        Retrieve a list of resources.

        :param parent_id: Optional[str] ID of the parent resource for nested resources.
        :param params: Optional[JSONDict] Optional query parameters.
        :return: Union[JSONList, List[T], ApiResponse] List of resources.
        """
        ...

    def create(self, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]:
        """
        Create a new resource.

        :param data: Union[JSONDict, T] The data for the new resource.
        :param parent_id: Optional[str] ID of the parent resource for nested resources.
        :return: Union[T, JSONDict] The created resource.
        :raises ValidationError: If the input data fails validation.
        :raises ModelConversionError: If the response data fails conversion.
        """
        ...

    def read(self, resource_id: str, parent_id: Optional[str] = None) -> Union[T, JSONDict]:
        """
        Retrieve a specific resource.

        :param resource_id: str The ID of the resource to retrieve.
        :param parent_id: Optional[str] ID of the parent resource for nested resources.
        :return: Union[T, JSONDict] The retrieved resource.
        :raises ModelConversionError: If the response data fails conversion.
        """
        ...

    def update(self, resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]:
        """
        Update a specific resource.

        :param resource_id: str The ID of the resource to update.
        :param data: Union[JSONDict, T] The updated data for the resource.
        :param parent_id: Optional[str] ID of the parent resource for nested resources.
        :return: Union[T, JSONDict] The updated resource.
        :raises ValidationError: If the input data fails validation.
        :raises ModelConversionError: If the response data fails conversion.
        """
        ...

    def partial_update(self, resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]:
        """
        Partially update a specific resource.

        :param resource_id: str The ID of the resource to update.
        :param data: Union[JSONDict, T] The partial updated data for the resource.
        :param parent_id: Optional[str] ID of the parent resource for nested resources.
        :return: Union[T, JSONDict] The updated resource.
        :raises ValidationError: If the input data fails validation.
        :raises ModelConversionError: If the response data fails conversion.
        """
        ...

    def destroy(self, resource_id: str, parent_id: Optional[str] = None) -> None:
        """
        Delete a specific resource.

        :param resource_id: str The ID of the resource to delete.
        :param parent_id: Optional[str] ID of the parent resource for nested resources.
        """
        ...

    def custom_action(
        self,
        action: str,
        method: HttpMethodString = "post",
        resource_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        data: Optional[Union[JSONDict, T]] = None,
        params: Optional[JSONDict] = None,
    ) -> Union[T, JSONDict, List[JSONDict]]:
        """
        Perform a custom action on the resource.

        :param action: str The name of the custom action.
        :param method: HttpMethodString The HTTP method to use. Defaults to "post".
        :param resource_id: Optional[str] Optional resource ID if the action is for a specific resource.
        :param parent_id: Optional[str] ID of the parent resource for nested resources.
        :param data: Optional[Union[JSONDict, T]] Optional data to send with the request.
        :param params: Optional[JSONDict] Optional query parameters.
        :return: Union[T, JSONDict, List[JSONDict]] The API response.
        :raises ValidationError: If the input data fails validation.
        :raises ModelConversionError: If the response data fails conversion.
        :raises TypeError: If the parameters are of incorrect types.
        """
        ...

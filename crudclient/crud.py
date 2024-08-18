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

from typing import Generic, List, Optional, Type, TypeVar, Union, cast
from urllib.parse import urljoin

from .client import Client
from .models import ApiResponse
from .types import JSONDict, JSONList, RawResponse

T = TypeVar("T")


class Crud(Generic[T]):
    """
    Base class for CRUD operations on API resources, supporting both top-level and nested resources.

    This class provides a generic implementation of common CRUD operations and can be
    easily extended for specific API endpoints.

    :ivar _resource_path: The base path for the resource in the API.
    :ivar _datamodel: The data model class for the resource.
    :ivar _methods: List of allowed methods for this resource.
    :ivar _api_response_model: Custom API response model, if any.
    :ivar _list_return_keys: Possible keys for list data in API responses.
    """

    _resource_path: str = ""
    _datamodel: Optional[Type[T]] = None
    _methods: List[str] = ["list", "create", "read", "update", "partial_update", "destroy"]
    _api_response_model: Optional[Type[ApiResponse]] = None
    _list_return_keys: List[str] = ["data", "results", "items"]

    def __init__(self, client: Client, parent: Optional["Crud"] = None):
        """
        Initialize the CRUD resource.

        :param client: An instance of the API client.
        :param parent: Optional parent Crud instance for nested resources.
        """
        self.client = client
        self.parent = parent

        # Remove methods that are not allowed
        if self._methods != ["*"]:
            for method in ["list", "create", "read", "update", "partial_update", "destroy"]:
                if method not in self._methods:
                    setattr(self, method, None)

    def _get_endpoint(self, *args: Optional[str]) -> str:
        """
        Construct the endpoint path.

        :param args: Variable number of path segments (e.g., resource IDs, actions).
        :return: The constructed endpoint path.
        """
        path_segments = [self._resource_path] + [seg for seg in args if seg is not None]

        if self.parent:
            path_segments = [self.parent._get_endpoint()] + path_segments

        return urljoin("/", "/".join(segment.strip("/") for segment in path_segments if segment))

    def _validate_response(self, data: RawResponse) -> JSONDict | JSONList:
        """
        Validate the API response data.

        :param data: The API response data.
        :return: The validated data.
        :raises ValueError: If the response is an unexpected type.
        """
        if isinstance(data, (bytes, str)):
            raise ValueError(f"Unexpected {type(data)} response: {data!r}")
        return data

    def _convert_to_model(self, data: RawResponse) -> T | JSONDict:
        """
        Convert the API response to the datamodel type.

        :param data: The API response data.
        :return: An instance of the datamodel or a dictionary.
        :raises ValueError: If the response is an unexpected type.
        """
        validated_data = self._validate_response(data)

        if not isinstance(validated_data, dict):
            raise ValueError(f"Unexpected response type: {type(validated_data)}")

        return self._datamodel(**validated_data) if self._datamodel else validated_data

    def _convert_to_list_model(self, data: JSONList) -> List[T] | JSONList:
        """
        Convert the API response to a list of datamodel types.

        :param data: The API response data.
        :return: A list of instances of the datamodel or the original list.
        :raises ValueError: If the response is an unexpected type.
        """
        if not self._datamodel:
            return data

        if isinstance(data, list):
            return [self._datamodel(**item) for item in data]

        raise ValueError(f"Unexpected response type: {type(data)}")

    def _validate_list_return(self, data: RawResponse) -> JSONList | List[T] | ApiResponse:
        """
        Validate and convert the list response data.

        :param data: The API response data.
        :return: Validated and converted list data.
        :raises ValueError: If the response format is unexpected.
        """
        validated_data: JSONList | JSONDict = self._validate_response(data)

        if isinstance(validated_data, dict):
            if self._api_response_model:
                value: ApiResponse = self._api_response_model(**validated_data)
                return value

            for key in self._list_return_keys:
                if key in validated_data:
                    return cast(JSONList | List[T], self._convert_to_list_model(validated_data[key]))
            else:
                raise ValueError(f"Unexpected response format: {validated_data}")

        if isinstance(validated_data, list):
            return cast(JSONList | List[T], self._convert_to_list_model(validated_data))

        raise ValueError(f"Unexpected response format: {validated_data}")

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None) -> JSONList | List[T] | ApiResponse:
        """
        Retrieve a list of resources.

        :param parent_id: ID of the parent resource for nested resources.
        :param params: Optional query parameters.
        :return: List of resources.
        """
        endpoint = self._get_endpoint(parent_id)
        response = self.client.get(endpoint, params=params)
        return self._validate_list_return(response)

    def create(self, data: JSONDict, parent_id: Optional[str] = None) -> T | JSONDict:
        """
        Create a new resource.

        :param data: The data for the new resource.
        :param parent_id: ID of the parent resource for nested resources.
        :return: The created resource.
        """
        endpoint = self._get_endpoint(parent_id)
        response = self.client.post(endpoint, json=data)
        return self._convert_to_model(response)

    def read(self, resource_id: str, parent_id: Optional[str] = None) -> T | JSONDict:
        """
        Retrieve a specific resource.

        :param resource_id: The ID of the resource to retrieve.
        :param parent_id: ID of the parent resource for nested resources.
        :return: The retrieved resource.
        """
        endpoint = self._get_endpoint(parent_id, resource_id)
        response = self.client.get(endpoint)
        return self._convert_to_model(response)

    def update(self, resource_id: str, data: JSONDict, parent_id: Optional[str] = None) -> T | JSONDict:
        """
        Update a specific resource.

        :param resource_id: The ID of the resource to update.
        :param data: The updated data for the resource.
        :param parent_id: ID of the parent resource for nested resources.
        :return: The updated resource.
        """
        endpoint = self._get_endpoint(parent_id, resource_id)
        response = self.client.put(endpoint, json=data)
        return self._convert_to_model(response)

    def partial_update(self, resource_id: str, data: JSONDict, parent_id: Optional[str] = None) -> T | JSONDict:
        """
        Partially update a specific resource.

        :param resource_id: The ID of the resource to update.
        :param data: The partial updated data for the resource.
        :param parent_id: ID of the parent resource for nested resources.
        :return: The updated resource.
        """
        endpoint = self._get_endpoint(parent_id, resource_id)
        response = self.client.patch(endpoint, json=data)
        return self._convert_to_model(response)

    def destroy(self, resource_id: str, parent_id: Optional[str] = None) -> None:
        """
        Delete a specific resource.

        :param resource_id: The ID of the resource to delete.
        :param parent_id: ID of the parent resource for nested resources.
        """
        endpoint = self._get_endpoint(parent_id, resource_id)
        self.client.delete(endpoint)

    def custom_action(
        self,
        action: str,
        method: str = "post",
        resource_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        data: Optional[JSONDict] = None,
        params: Optional[JSONDict] = None,
    ) -> Union[T, JSONDict]:
        """
        Perform a custom action on the resource.

        :param action: The name of the custom action.
        :param method: The HTTP method to use. Defaults to "post".
        :param resource_id: Optional resource ID if the action is for a specific resource.
        :param parent_id: ID of the parent resource for nested resources.
        :param data: Optional data to send with the request.
        :param params: Optional query parameters.
        :return: The API response.
        """
        endpoint = self._get_endpoint(parent_id, resource_id, action)

        kwargs = {}
        if params:
            kwargs["params"] = params
        if data:
            kwargs["json"] = data

        response = getattr(self.client, method.lower())(endpoint, **kwargs)
        try:
            return self._convert_to_model(response)
        except ValueError:
            return response

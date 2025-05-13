"""
Module `operations.py`
=====================

This module defines the CRUD operations for API resources.
It provides implementations for list, create, read, update, partial_update, destroy,
and custom_action operations.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from .base import T

if TYPE_CHECKING:
    from .base import Crud

from ..exceptions import APIError, DataValidationError, NetworkError, NotFoundError
from ..models import ApiResponse
from ..types import JSONDict, JSONList, RawResponse

def list_operation(  # Note: self type added below
    self: "Crud", parent_id: Optional[str] = None, params: Optional[JSONDict] = None
) -> Union[JSONList, List[T], ApiResponse]:
    """
    Retrieve a list of resources.

    Args:
        parent_id: Optional ID of the parent resource for nested resources.
        params: Optional query parameters.

    Returns:
        Union[JSONList, List[T], ApiResponse]: List of resources.

    Raises:
        ValueError: If list action is not allowed for this resource.
        NotFoundError: If the parent resource (if applicable) is not found.
        NetworkError: If a network-related error occurs during the request.
        APIError: For other API-related errors (e.g., 4xx/5xx responses).
    """
    ...

# Note: self type added below

def create_operation(
    self: "Crud", data: Union[JSONDict, T], parent_id: Optional[str] = None, params: Optional[JSONDict] = None
) -> Union[T, JSONDict]:
    """
    Create a new resource.

    Args:
        data: The data for the new resource.
        parent_id: Optional ID of the parent resource for nested resources.
        params: Optional query parameters.

    Returns:
        Union[T, JSONDict]: The created resource.

    Raises:
        ValueError: If create action is not allowed for this resource.
        DataValidationError: If the input data fails validation.
        NotFoundError: If the parent resource (if applicable) is not found.
        NetworkError: If a network-related error occurs during the request.
        APIError: For other API-related errors (e.g., 4xx/5xx responses).
    """
    ...

def read_operation(self: "Crud", resource_id: str, parent_id: Optional[str] = None) -> Union[T, JSONDict]:  # Note: self type added below
    """
    Retrieve a specific resource.

    Args:
        resource_id: The ID of the resource to retrieve.
        parent_id: Optional ID of the parent resource for nested resources.

    Returns:
        Union[T, JSONDict]: The retrieved resource.

    Raises:
        ValueError: If read action is not allowed for this resource.
        NotFoundError: If the resource or parent resource (if applicable) is not found.
        NetworkError: If a network-related error occurs during the request.
        APIError: For other API-related errors (e.g., 4xx/5xx responses).
    """
    ...

def update_operation(  # Note: self type added below
    self: "Crud",
    resource_id: Optional[str] = None,
    data: Optional[Union[JSONDict, T]] = None,
    parent_id: Optional[str] = None,
    update_mode: Optional[str] = None,
) -> Union[T, JSONDict]:
    """
    Update a resource.

    Args:
        resource_id: The ID of the resource to update. Can be None for non-standard APIs.
        data: The data to update the resource with.
        parent_id: Optional parent ID if this is a nested resource.
        update_mode: The update mode to use. If None, uses the class's _update_mode.
            Supported modes:
            - "standard": Standard RESTful update (default)
            - "no_resource_id": Update without resource ID in URL (e.g., Tripletex company)

    Returns:
        Union[T, JSONDict]: The updated resource.

    Raises:
        ValueError: If update action is not allowed for this resource.
        DataValidationError: If the input data fails validation.
        NotFoundError: If the resource or parent resource (if applicable) is not found.
        NetworkError: If a network-related error occurs during the request.
        APIError: For other API-related errors (e.g., 4xx/5xx responses).
    """
    ...

def partial_update_operation(  # Note: self type added below
    self: "Crud", resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None
) -> Union[T, JSONDict]:
    """
    Partially update a specific resource.

    Args:
        resource_id: The ID of the resource to update.
        data: The partial updated data for the resource.
        parent_id: Optional ID of the parent resource for nested resources.

    Returns:
        Union[T, JSONDict]: The updated resource.

    Raises:
        ValueError: If partial_update action is not allowed for this resource.
        DataValidationError: If the input data fails validation.
        NotFoundError: If the resource or parent resource (if applicable) is not found.
        NetworkError: If a network-related error occurs during the request.
        APIError: For other API-related errors (e.g., 4xx/5xx responses).
    """
    ...

def destroy_operation(self: "Crud", resource_id: str, parent_id: Optional[str] = None) -> None:
    """
    Delete a specific resource.

    Args:
        resource_id: The ID of the resource to delete.
        parent_id: Optional ID of the parent resource for nested resources.

    Raises:
        ValueError: If destroy action is not allowed for this resource.
        NotFoundError: If the resource or parent resource (if applicable) is not found.
        NetworkError: If a network-related error occurs during the request.
        APIError: For other API-related errors (e.g., 4xx/5xx responses).
    """
    ...

def _prepare_request_body_kwargs(
    self: "Crud",
    data: Optional[Union[JSONDict, T]],
    files: Optional[JSONDict],
    content_type: Optional[str],
) -> Dict[str, Any]:
    """
    Prepare request body keyword arguments based on content type and data.

    Args:
        data: Optional data to send with the request.
        files: Optional dictionary of files to upload (for multipart/form-data requests).
        content_type: Optional content type for the request.

    Returns:
        Dict[str, Any]: Dictionary of keyword arguments for the request body.

    Raises:
        TypeError: If the data type is incompatible with the content type.
        ValueError: If an unsupported content type is provided.
    """
    ...

def custom_action_operation(
    self: "Crud",
    action: str,
    method: str = "post",
    resource_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    data: Optional[Union[JSONDict, T]] = None,
    params: Optional[JSONDict] = None,
    files: Optional[JSONDict] = None,
    content_type: Optional[str] = None,
) -> Union[T, JSONDict, List[JSONDict]]:
    """
    Perform a custom action on the resource.

    Args:
        action: The name of the custom action.
        method: The HTTP method to use. Defaults to "post".
        resource_id: Optional resource ID if the action is for a specific resource.
        parent_id: Optional ID of the parent resource for nested resources.
        data: Optional data to send with the request.
        params: Optional query parameters.
        files: Optional dictionary of files to upload (for multipart/form-data requests).
        content_type: Optional content type for the request. If not provided, defaults to
                     "application/json" unless files are provided (which uses multipart/form-data).
                     Supported values: "application/json", "application/x-www-form-urlencoded".

    Returns:
        Union[T, JSONDict, List[JSONDict]]: The API response.

    Raises:
        TypeError: If the parameters are of incorrect types.
        ValueError: If the HTTP method is invalid, the action is not defined, or an unsupported content_type is provided.
        DataValidationError: If the input data fails validation.
        NotFoundError: If the resource or parent resource (if applicable) is not found.
        NetworkError: If a network-related error occurs during the request.
        APIError: For other API-related errors (e.g., 4xx/5xx responses).
    """
    ...

# Aliases for the Crud class methods
list = list_operation
create = create_operation
read = read_operation
update = update_operation
partial_update = partial_update_operation
destroy = destroy_operation
custom_action = custom_action_operation

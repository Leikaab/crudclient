"""
Module `response_conversion.py`
==============================

This module provides functions for converting API responses to model instances.
It handles the initialization of response strategies, validation of responses,
and conversion of response data to model instances.
"""

import logging
from typing import TYPE_CHECKING, Any, List, Optional, Type, TypeVar, Union

if TYPE_CHECKING:
    from .base import Crud

from pydantic import ValidationError as PydanticValidationError

from ..exceptions import DataValidationError, ResponseParsingError
from ..models import ApiResponse
from ..response_strategies import (
    DefaultResponseModelStrategy,
    PathBasedResponseModelStrategy,
    ResponseModelStrategy,
)
from ..types import JSONDict, JSONList, RawResponse

# Define T type variable
T = TypeVar("T")

def _init_response_strategy(self: "Crud") -> None:
    """
    Initialize the response model strategy.

    This method creates an instance of the appropriate response model strategy
    based on the class configuration. It uses PathBasedResponseModelStrategy if
    _single_item_path or _list_item_path are defined, otherwise it uses
    DefaultResponseModelStrategy.
    """
    ...

def _validate_response(self: "Crud", data: RawResponse) -> Union[JSONDict, JSONList]:
    """
    Validate the API response data.

    Args:
        data: The API response data.

    Returns:
        Union[JSONDict, JSONList]: The validated data.

    Raises:
        ValueError: If the response is None, invalid bytes, or not a dict or list.
        ResponseParsingError: If the response is a string that cannot be parsed as JSON.
    """
    ...

def _convert_to_model(self: "Crud", data: RawResponse) -> Union[T, JSONDict]:
    """
    Convert the API response to the datamodel type.

    This method uses the configured response model strategy to convert the data.
    The strategy handles extracting data from the response and converting it to
    the appropriate model type.

    Args:
        data: The API response data.

    Returns:
        Union[T, JSONDict]: An instance of the datamodel or a dictionary.

    Raises:
        DataValidationError: If the response data fails Pydantic validation.
        ResponseParsingError: If the initial response data (string) cannot be parsed as JSON.
        ValueError: If the response data is invalid (e.g., un-decodable bytes).
    """
    ...

def _convert_to_list_model(self: "Crud", data: JSONList) -> Union[List[T], JSONList]:
    """
    Convert the API response to a list of datamodel types.

    Args:
        data: The API response data.

    Returns:
        Union[List[T], JSONList]: A list of instances of the datamodel or the original list.

    Raises:
        DataValidationError: If list items fail Pydantic validation.
    """
    ...

def _validate_list_return(self: "Crud", data: RawResponse) -> Union[JSONList, List[T], ApiResponse]:
    """
    Validate and convert the list response data.

    This method uses the configured response model strategy to validate and convert
    the list response data. It handles different response formats and extracts list
    data according to the strategy.

    Args:
        data: The API response data.

    Returns:
        Union[JSONList, List[T], ApiResponse]: Validated and converted list data.

    Raises:
        DataValidationError: If the response data fails Pydantic validation during conversion.
        ResponseParsingError: If the initial response data (string) cannot be parsed as JSON.
        ValueError: If the response data is invalid (e.g., un-decodable bytes).
    """
    ...

def _fallback_list_conversion(  # Note: self type added below
    self: "Crud", data: RawResponse
) -> Union[JSONList, List[T], ApiResponse]:  # Note: self added in the line above
    """
    Fallback conversion logic for list responses when the strategy fails.

    This method implements the original behavior for backward compatibility.

    Args:
        data: The validated response data.

    Returns:
        Union[JSONList, List[T], ApiResponse]: Converted list data.

    Raises:
        ValueError: If the response format is unexpected or conversion fails.
    """
    ...

def _dump_model_instance(self: "Crud", model_instance: T, partial: bool) -> JSONDict:
    """
    Dump a Pydantic model instance to a dictionary.

    Handles both Pydantic v1 (dict()) and v2 (model_dump()).
    Falls back to __dict__ if necessary.

    Args:
        model_instance: The model instance to dump.
        partial: Whether to exclude unset fields (for partial updates).

    Returns:
        JSONDict: The dumped dictionary representation of the model.

    Raises:
        TypeError: If the instance cannot be dumped.
    """
    ...

def _validate_and_dump_full_dict(self: "Crud", data_dict: JSONDict) -> JSONDict:
    """
    Validate a dictionary against the full datamodel and dump the result.

    Args:
        data_dict: The dictionary to validate and dump.

    Returns:
        JSONDict: The dumped dictionary after validation.

    Raises:
        DataValidationError: If validation fails.
    """
    ...

def _validate_partial_dict(self: "Crud", data_dict: JSONDict) -> None:
    """
    Validate provided fields in a dictionary against the datamodel for partial updates.

    Ignores 'missing' errors.

    Args:
        data_dict: The dictionary containing partial data.

    Raises:
        DataValidationError: If validation fails for non-missing fields.
    """
    ...

def _dump_dictionary(self: "Crud", data_dict: JSONDict, partial: bool) -> JSONDict:
    """
    Validate and dump a dictionary based on the datamodel.

    For partial updates, validates only provided fields.
    For full updates, validates against the full model and dumps the result.

    Args:
        data_dict: The dictionary to dump.
        partial: Whether this is a partial update.

    Returns:
        JSONDict: The validated and/or dumped dictionary.

    Raises:
        DataValidationError: If validation fails.
    """
    ...

def _dump_data(self: "Crud", data: Optional[Union[JSONDict, T]], partial: bool = False) -> JSONDict:
    """
    Dump the data model to a JSON-serializable dictionary.

    Args:
        data: The data to dump.
        partial: Whether this is a partial update (default: False).

    Returns:
        JSONDict: The dumped data.

    Raises:
        DataValidationError: If the data fails validation.
        TypeError: If the input data is not a dict or model instance.
    """
    ...

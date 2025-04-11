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

from ..exceptions import ModelConversionError, ValidationError
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
        ValueError: If the response is None, a string, bytes, or not a dict or list.
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
        ModelConversionError: If the response data fails conversion.
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
        ModelConversionError: If the response data fails conversion.
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
        ValueError: If the response format is unexpected or conversion fails.
        ModelConversionError: If the response data fails conversion.
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

def _dump_data(self: "Crud", data: Optional[Union[JSONDict, T]], partial: bool = False) -> JSONDict:
    """
    Dump the data model to a JSON-serializable dictionary.

    Args:
        data: The data to dump.
        partial: Whether this is a partial update (default: False).

    Returns:
        JSONDict: The dumped data.

    Raises:
        ValidationError: If the data fails validation.
    """
    ...

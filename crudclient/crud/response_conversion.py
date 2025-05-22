"""
Module `response_conversion.py`
==============================

This module provides functions for converting API responses to model instances.
It handles the initialization of response strategies, validation of responses,
and conversion of response data to model instances.
"""

import json
import logging
from typing import TYPE_CHECKING, List, Optional, Type, TypeVar, Union, cast

if TYPE_CHECKING:
    from .base import Crud

from pydantic import ValidationError as PydanticValidationError

from ..exceptions import CrudClientError, DataValidationError, ResponseParsingError
from ..http.utils import redact_json_body  # Import redaction utility
from ..models import ApiResponse
from ..response_strategies import (
    DefaultResponseModelStrategy,
    PathBasedResponseModelStrategy,
)
from ..types import JSONDict, JSONList, RawResponse

logger = logging.getLogger(__name__)

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
    if self._response_strategy is not None:
        logger.debug(f"Using provided response strategy: {self._response_strategy.__class__.__name__}")
        return

    # If a path-based strategy is needed, use PathBasedResponseModelStrategy
    if hasattr(self, "_single_item_path") or hasattr(self, "_list_item_path"):
        logger.debug("Using PathBasedResponseModelStrategy")
        self._response_strategy = PathBasedResponseModelStrategy(
            datamodel=self._datamodel,
            api_response_model=self._api_response_model,
            single_item_path=getattr(self, "_single_item_path", None),
            list_item_path=getattr(self, "_list_item_path", None),
        )
    else:
        # Otherwise, use the default strategy
        logger.debug("Using DefaultResponseModelStrategy")
        self._response_strategy = DefaultResponseModelStrategy(
            datamodel=self._datamodel,
            api_response_model=self._api_response_model,
            list_return_keys=self._list_return_keys,
        )


def _validate_response(self: "Crud", data: RawResponse) -> Union[JSONDict, JSONList, str]:
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
    if data is None:
        raise ValueError("Response data is None")

    # If the data is a string, try to parse it as JSON
    if isinstance(data, str):
        try:
            parsed_data = json.loads(data)
            return cast(Union[JSONDict, JSONList], parsed_data)
        except json.JSONDecodeError as e:
            # Log and raise ResponseParsingError if JSON decoding fails
            error_msg = f"Failed to decode JSON response: {e}"
            response_snippet = data[:100] + "..." if len(data) > 100 else data
            logger.error("%s - Response snippet: %s", error_msg, response_snippet, exc_info=True)
            # Note: We don't have the original requests.Response object here, passing None
            # Pass original_exception first, response is optional
            raise ResponseParsingError(error_msg, original_exception=e, response=None) from e

    if isinstance(data, bytes):
        # Try to decode bytes to string
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            # If it can't be decoded, raise a specific error
            error_msg = f"Unable to decode binary response data: {data[:100]!r}..."
            logger.error(error_msg)
            # Consider if this should be ResponseParsingError too, but ValueError seems okay for now
            raise ValueError(error_msg)

    if not isinstance(data, (dict, list)):
        raise ValueError(f"Expected dict or list response, got {type(data)}")

    return cast(Union[JSONDict, JSONList], data)


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
    try:
        # Validate the response data
        validated_data = self._validate_response(data)

        # If the data is a list, handle it differently
        if isinstance(validated_data, list):
            # Cast to JSONList to satisfy type checker
            return cast(Union[T, JSONDict], self._convert_to_list_model(cast(JSONList, validated_data)))

        # Use the response strategy to convert the data
        if self._response_strategy:
            return self._response_strategy.convert_single(validated_data)

        # If no strategy is available, return the data as is
        return cast(Union[T, JSONDict], validated_data)

    except PydanticValidationError as e:
        # Catch validation errors during single item conversion (likely within strategy)
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Response data validation failed for model {model_name}"
        # Redact data before logging or raising
        # Use a safe default for validated_data in case it's not defined in this exception context
        safe_data = locals().get("validated_data", data)
        redacted_data = redact_json_body(safe_data) if isinstance(safe_data, (dict, list)) else safe_data
        logger.error(f"{error_msg}: errors={json.dumps(e.errors())}")  # Log structured errors
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
    except Exception as e:
        # Catch unexpected errors during conversion
        logger.error(f"Unexpected error converting response to model: {e}", exc_info=True)
        # Re-raise unexpected errors; specific ones like DataValidationError/ResponseParsingError
        # should have been caught earlier or raised by called methods.
        raise


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
    if not self._datamodel:
        return data

    try:
        return [self._datamodel(**item) for item in data]
    except PydanticValidationError as e:
        # Catch validation errors during list item conversion
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Response list item validation failed for model {model_name}"
        # Redact data before logging or raising
        redacted_data = redact_json_body(data) if isinstance(data, (dict, list)) else data
        logger.error(f"{error_msg}: errors={json.dumps(e.errors())}")  # Log structured errors
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
    except Exception as e:
        # Catch unexpected errors during list conversion
        logger.error(f"Unexpected error converting list response to model: {e}", exc_info=True)
        raise


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
    try:
        # Validate the response data
        validated_data = self._validate_response(data)

        # Use the response strategy to convert the data
        if self._response_strategy:
            return self._response_strategy.convert_list(validated_data)

        # If no strategy is available, use the fallback conversion
        return cast(Union[JSONList, List[T], ApiResponse], self._fallback_list_conversion(validated_data))

    except PydanticValidationError as e:
        # Catch validation errors during list conversion (likely within strategy)
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Response list validation failed for model {model_name}"
        # Redact data before logging or raising
        # Use a safe default for validated_data in case it's not defined in this exception context
        safe_data = locals().get("validated_data", data)
        redacted_data = redact_json_body(safe_data) if isinstance(safe_data, (dict, list)) else safe_data
        logger.error(f"{error_msg}: errors={json.dumps(e.errors())}")  # Log structured errors
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
    except Exception as e:
        logger.error(f"Unexpected error validating list return: {e}", exc_info=True)
        # Re-raise unexpected errors
        raise


def _fallback_list_conversion(self: "Crud", data: RawResponse) -> Union[JSONList, List[T], ApiResponse]:
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
    # If the data is already a list, convert it directly
    if isinstance(data, list):
        return cast(Union[JSONList, List[T], ApiResponse], self._convert_to_list_model(cast(JSONList, data)))

    # If the data is a dict, try to extract the list data
    if isinstance(data, dict):
        # If an API response model is provided, use it
        if self._api_response_model:
            try:
                return self._api_response_model(**data)
            except Exception as e:
                logger.warning(f"Failed to convert to API response model: {e}", exc_info=True)
                # Continue with other conversion methods, maybe log warning?

        # Try to extract list data from known keys
        for key in self._list_return_keys:
            if key in data and isinstance(data[key], list):
                return cast(Union[JSONList, List[T], ApiResponse], self._convert_to_list_model(cast(JSONList, data[key])))

    # If the data is a string, try to handle it
    if isinstance(data, str):
        try:
            parsed_data = json.loads(data)
            if isinstance(parsed_data, list):
                return cast(Union[JSONList, List[T], ApiResponse], self._convert_to_list_model(cast(JSONList, parsed_data)))
            elif isinstance(parsed_data, dict):
                # Try to extract list data from known keys
                for key in self._list_return_keys:
                    if key in parsed_data and isinstance(parsed_data[key], list):
                        return cast(Union[JSONList, List[T], ApiResponse], self._convert_to_list_model(cast(JSONList, parsed_data[key])))
        except json.JSONDecodeError as e:
            # Log the error but don't raise, as this is a fallback path
            logger.warning(f"Could not parse string response as JSON in fallback: {e}", exc_info=True)

    logger.warning(f"Could not extract list data from response using fallback, returning empty list. Response snippet: {str(data)[:200]}")
    return []


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
    if hasattr(model_instance, "model_dump") and callable(getattr(model_instance, "model_dump")):
        return cast(JSONDict, getattr(model_instance, "model_dump")(exclude_unset=partial))
    elif hasattr(model_instance, "dict") and callable(getattr(model_instance, "dict")):  # Fallback for older Pydantic
        logger.warning(f"Using deprecated dict() for dumping model {type(model_instance)}.")
        return cast(JSONDict, getattr(model_instance, "dict")(exclude_unset=partial))
    elif hasattr(model_instance, "__dict__"):  # Generic fallback
        logger.warning(f"Using __dict__ for dumping model instance {type(model_instance)}.")
        return cast(JSONDict, model_instance.__dict__)
    else:
        raise TypeError(f"Cannot dump model instance of type {type(model_instance)}")


def _validate_partial_dict(self: "Crud", data_dict: JSONDict, validation_model: Optional[Type[T]] = None) -> None:
    """
    Validate provided fields in a dictionary against the specified validation model for partial updates.

    Ignores 'missing' errors.

    Args:
        data_dict: The dictionary containing partial data.
        validation_model: The model to validate against. If None, falls back to self._datamodel.

    Raises:
        DataValidationError: If validation fails for non-missing fields.
    """
    # Use provided validation_model or fall back to self._datamodel
    model = validation_model or self._datamodel

    if not model:
        return  # No validation if no model

    try:
        # Attempt validation. We only care about non-'missing' errors here.
        getattr(model, "model_validate")(data_dict)
    except PydanticValidationError as e:
        non_missing_errors = [err for err in e.errors() if err.get("type") != "missing"]
        if non_missing_errors:
            model_name = getattr(model, "__name__", "Unknown")
            error_msg = f"Partial update data validation failed for provided fields in model {model_name}"
            # Redact data before logging or raising
            redacted_data = redact_json_body(data_dict) if isinstance(data_dict, (dict, list)) else data_dict
            logger.warning(
                "%s: %s",  # Avoid logging raw data
                error_msg,
                json.dumps(non_missing_errors, indent=2),
                # str(redacted_data)[:200], # Avoid logging even redacted data snippet here
            )
            raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
        # If only 'missing' errors, we ignore them for partial updates.


def _validate_and_dump_full_dict(self: "Crud", data_dict: JSONDict, validation_model: Optional[Type[T]] = None) -> JSONDict:
    """
    Validate a dictionary against the specified validation model and dump the result.

    Args:
        data_dict: The dictionary to validate and dump.
        validation_model: The model to validate against. If None, falls back to self._datamodel.

    Returns:
        JSONDict: The dumped dictionary after validation.

    Raises:
        DataValidationError: If validation fails.
    """
    # Use provided validation_model or fall back to self._datamodel
    model = validation_model or self._datamodel

    if not model:
        # Return as is if no model
        return data_dict

    try:
        validated_model = getattr(model, "model_validate")(data_dict)
        # Dump the validated model (exclude_unset=False for full dump)
        return self._dump_model_instance(validated_model, partial=False)  # type: ignore[no-any-return]
    except PydanticValidationError as e:
        # Re-raise validation errors for full updates
        model_name = getattr(model, "__name__", "Unknown")
        error_msg = f"Input data validation failed for model {model_name}"
        # Redact data before logging or raising
        redacted_data = redact_json_body(data_dict) if isinstance(data_dict, (dict, list)) else data_dict
        logger.warning(
            "%s: %s",  # Avoid logging raw data
            error_msg,
            json.dumps(e.errors(), indent=2),
            # str(redacted_data)[:200], # Avoid logging even redacted data snippet here
        )
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e


def _dump_dictionary(self: "Crud", data_dict: JSONDict, partial: bool, validation_model: Optional[Type[T]] = None) -> JSONDict:
    """
    Validate and dump a dictionary based on the specified validation model.

    For partial updates, validates only provided fields.
    For full updates, validates against the full model and dumps the result.

    Args:
        data_dict: The dictionary to dump.
        partial: Whether this is a partial update.
        validation_model: The model to validate against. If None, falls back to self._datamodel.

    Returns:
        JSONDict: The validated and/or dumped dictionary.

    Raises:
        DataValidationError: If validation fails.
    """
    if partial:
        self._validate_partial_dict(data_dict, validation_model)
        # For partial updates, return the original dict after validation passes
        return data_dict
    else:
        # For full updates, validate and dump
        return self._validate_and_dump_full_dict(data_dict, validation_model)  # type: ignore[no-any-return]


def _dump_data(self: "Crud", data: Optional[Union[JSONDict, T]], validation_model: Optional[Type[T]] = None, partial: bool = False) -> JSONDict:
    """
    Dump the data model to a JSON-serializable dictionary.

    Args:
        data: The data to dump.
        validation_model: Optional model to use for validation. If None, determines model based on operation type.
        partial: Whether this is a partial update (default: False).

    Returns:
        JSONDict: The dumped data.

    Raises:
        DataValidationError: If the data fails validation.
        TypeError: If the input data is not a dict or model instance.
    """
    if data is None:
        return cast(JSONDict, {})

    # Determine which validation model to use
    if validation_model is None:
        if partial is False and hasattr(self, "_create_model") and self._create_model is not None:
            # For create operations
            validation_model = self._create_model
        elif partial is True and hasattr(self, "_update_model") and self._update_model is not None:
            # For update operations
            validation_model = self._update_model
        else:
            # Fall back to datamodel
            validation_model = self._datamodel

    try:
        # Convert data to dictionary
        if validation_model and (isinstance(data, validation_model) or (hasattr(data, "model_dump") or hasattr(data, "dict"))):
            # Handle model instances
            return cast(JSONDict, self._dump_model_instance(data, partial))
        elif isinstance(data, dict):
            # Handle dictionaries
            data_dict = cast(JSONDict, data)
            return cast(JSONDict, self._dump_dictionary(data_dict, partial, validation_model))
        else:
            # Handle invalid types
            raise TypeError(f"Input data must be a dict or a Pydantic model instance, got {type(data).__name__}")

    except DataValidationError:
        # Re-raise DataValidationErrors raised by helpers
        raise
    except Exception as e:
        # Catch unexpected errors during dumping/validation
        logger.error(f"Unexpected error dumping data: {e}", exc_info=True)
        # Wrap unexpected errors for clarity, though DataValidationError is preferred
        raise CrudClientError(f"Unexpected error during data dumping: {e}") from e

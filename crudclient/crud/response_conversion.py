import json
import logging
from typing import List, Optional, TypeVar, Union, cast

from pydantic import ValidationError as PydanticValidationError

from ..exceptions import ModelConversionError, ValidationError
from ..models import ApiResponse
# Import response strategies directly from their modules to avoid circular imports
from ..response_strategies.default import DefaultResponseModelStrategy
from ..response_strategies.path_based import PathBasedResponseModelStrategy
from ..types import JSONDict, JSONList, RawResponse

# Get a logger for this module
logger = logging.getLogger(__name__)

# Define T type variable
T = TypeVar("T")


def _init_response_strategy(self) -> None:
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


def _validate_response(self, data: RawResponse) -> Union[JSONDict, JSONList, str]:
    if data is None:
        raise ValueError("Response data is None")

    # If the data is a string, try to parse it as JSON
    if isinstance(data, str):
        try:
            parsed_data = json.loads(data)
            return cast(Union[JSONDict, JSONList], parsed_data)
        except json.JSONDecodeError:
            # If it's not valid JSON, return it as is for further processing
            return data

    if isinstance(data, bytes):
        # Try to decode bytes to string
        try:
            return data.decode('utf-8')
        except UnicodeDecodeError:
            # If it can't be decoded, raise an error
            raise ValueError(f"Unable to decode binary data: {data[:100]}...")

    if not isinstance(data, (dict, list)):
        raise ValueError(f"Expected dict or list response, got {type(data)}")

    return cast(Union[JSONDict, JSONList], data)


def _convert_to_model(self, data: RawResponse) -> Union[T, JSONDict]:
    try:
        # Validate the response data
        validated_data = self._validate_response(data)

        # If the data is a list, handle it differently
        if isinstance(validated_data, list):
            return self._convert_to_list_model(validated_data)

        # Use the response strategy to convert the data
        if self._response_strategy:
            return self._response_strategy.convert_single(validated_data)

        # If no strategy is available, return the data as is
        return validated_data

    except Exception as e:
        logger.error(f"Failed to convert response to model: {e}")
        if isinstance(e, ModelConversionError):
            raise
        raise ModelConversionError(
            f"Failed to convert response to model: {e}",
            response=None,
            data=data
        ) from e


def _convert_to_list_model(self, data: JSONList) -> Union[List[T], JSONList]:
    if not self._datamodel:
        return data

    try:
        return [self._datamodel(**item) for item in data]
    except Exception as e:
        logger.error(f"Failed to convert list response to model: {e}")
        raise ModelConversionError(
            f"Failed to convert list response to model: {e}",
            response=None,
            data=data
        ) from e


def _validate_list_return(self, data: RawResponse) -> Union[JSONList, List[T], ApiResponse]:
    try:
        # Validate the response data
        validated_data = self._validate_response(data)

        # Use the response strategy to convert the data
        if self._response_strategy:
            return self._response_strategy.convert_list(validated_data)

        # If no strategy is available, use the fallback conversion
        return self._fallback_list_conversion(validated_data)

    except Exception as e:
        logger.error(f"Failed to validate list return: {e}")
        if isinstance(e, (ValueError, ModelConversionError)):
            raise
        raise ValueError(f"Failed to validate list return: {e}") from e


def _fallback_list_conversion(
    self, data: RawResponse
) -> Union[JSONList, List[T], ApiResponse]:
    # If the data is already a list, convert it directly
    if isinstance(data, list):
        return self._convert_to_list_model(data)

    # If the data is a dict, try to extract the list data
    if isinstance(data, dict):
        # If an API response model is provided, use it
        if self._api_response_model:
            try:
                return self._api_response_model(**data)
            except Exception as e:
                logger.error(f"Failed to convert to API response model: {e}")
                # Continue with other conversion methods

        # Try to extract list data from known keys
        for key in self._list_return_keys:
            if key in data and isinstance(data[key], list):
                return self._convert_to_list_model(data[key])

    # If the data is a string, try to handle it
    if isinstance(data, str):
        try:
            parsed_data = json.loads(data)
            if isinstance(parsed_data, list):
                return self._convert_to_list_model(parsed_data)
            elif isinstance(parsed_data, dict):
                # Try to extract list data from known keys
                for key in self._list_return_keys:
                    if key in parsed_data and isinstance(parsed_data[key], list):
                        return self._convert_to_list_model(parsed_data[key])
        except json.JSONDecodeError:
            # Not valid JSON, can't extract list data
            pass

    # If all else fails, return an empty list
    logger.warning(f"Could not extract list data from response, returning empty list: {data}")
    return []


def _dump_data(self, data: Optional[Union[JSONDict, T]], partial: bool = False) -> JSONDict:
    if data is None:
        return {}

    try:
        # If the data is already a dict, return it
        if isinstance(data, dict):
            return cast(JSONDict, data)

        # If the data is a model instance, dump it to a dict
        if hasattr(data, "model_dump"):
            # For Pydantic v2 models
            dump_method = getattr(data, "model_dump")
            if callable(dump_method):
                return cast(JSONDict, dump_method(exclude_unset=partial))

        # For other model types
        if hasattr(data, "dict"):
            # For Pydantic v1 models
            dict_method = getattr(data, "dict")
            if callable(dict_method):
                return cast(JSONDict, dict_method(exclude_unset=partial))

        # If all else fails, try to convert to a dict
        if hasattr(data, "__dict__"):
            return cast(JSONDict, data.__dict__)

        # For safety, just return an empty dict if we can't convert
        logger.warning(f"Could not convert {type(data)} to dict, returning empty dict")
        return {}

    except Exception as e:
        logger.error(f"Failed to dump data: {e}")
        if isinstance(e, PydanticValidationError):
            raise ValidationError(str(e), data=data) from e
        raise ValidationError(f"Failed to dump data: {e}", data=data) from e

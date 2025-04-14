import json
import logging
from typing import List as TypingList  # Rename List
from typing import Optional, TypeVar, Union, cast

from pydantic import ValidationError as PydanticValidationError

from ..exceptions import CrudClientError, DataValidationError, ResponseParsingError
from ..http.utils import redact_json_body  # Import redaction utility
from ..models import ApiResponse

# Import response strategies directly from their modules to avoid circular imports
from ..response_strategies.default import DefaultResponseModelStrategy
from ..response_strategies.path_based import PathBasedResponseModelStrategy
from ..types import JSONDict, JSONList, RawResponse

logger = logging.getLogger(__name__)

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
            error_msg = f"Unable to decode binary response data: {data[:100]}..."
            logger.error(error_msg)
            # Consider if this should be ResponseParsingError too, but ValueError seems okay for now
            raise ValueError(error_msg)

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

    except PydanticValidationError as e:
        # Catch validation errors during single item conversion (likely within strategy)
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Response data validation failed for model {model_name}"
        # Redact data before logging or raising
        redacted_data = redact_json_body(validated_data) if isinstance(validated_data, (dict, TypingList)) else validated_data
        logger.error(f"{error_msg}: errors={json.dumps(e.errors())}")  # Log structured errors
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
    except Exception as e:
        # Catch unexpected errors during conversion
        logger.error(f"Unexpected error converting response to model: {e}", exc_info=True)
        # Re-raise unexpected errors; specific ones like DataValidationError/ResponseParsingError
        # should have been caught earlier or raised by called methods.
        raise


def _convert_to_list_model(self, data: JSONList) -> Union[TypingList[T], JSONList]:
    if not self._datamodel:
        return data

    try:
        return [self._datamodel(**item) for item in data]
    except PydanticValidationError as e:
        # Catch validation errors during list item conversion
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Response list item validation failed for model {model_name}"
        # Redact data before logging or raising
        redacted_data = redact_json_body(data) if isinstance(data, (dict, TypingList)) else data
        logger.error(f"{error_msg}: errors={json.dumps(e.errors())}")  # Log structured errors
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
    except Exception as e:
        # Catch unexpected errors during list conversion
        logger.error(f"Unexpected error converting list response to model: {e}", exc_info=True)
        raise


def _validate_list_return(self, data: RawResponse) -> Union[JSONList, TypingList[T], ApiResponse]:
    try:
        # Validate the response data
        validated_data = self._validate_response(data)

        # Use the response strategy to convert the data
        if self._response_strategy:
            return self._response_strategy.convert_list(validated_data)

        # If no strategy is available, use the fallback conversion
        return self._fallback_list_conversion(validated_data)

    except PydanticValidationError as e:
        # Catch validation errors during list conversion (likely within strategy)
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Response list validation failed for model {model_name}"
        # Redact data before logging or raising
        redacted_data = redact_json_body(validated_data) if isinstance(validated_data, (dict, TypingList)) else validated_data
        logger.error(f"{error_msg}: errors={json.dumps(e.errors())}")  # Log structured errors
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
    except Exception as e:
        logger.error(f"Unexpected error validating list return: {e}", exc_info=True)
        # Re-raise unexpected errors
        raise


def _fallback_list_conversion(self, data: RawResponse) -> Union[JSONList, TypingList[T], ApiResponse]:
    # If the data is already a list, convert it directly
    if isinstance(data, list):
        return self._convert_to_list_model(data)  # type: ignore[arg-type] # data is list here

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
                return self._convert_to_list_model(data[key])  # type: ignore[arg-type] # data[key] is list here

    # If the data is a string, try to handle it
    if isinstance(data, str):
        try:
            parsed_data = json.loads(data)
            if isinstance(parsed_data, list):
                return self._convert_to_list_model(parsed_data)  # type: ignore[arg-type] # parsed_data is list here
            elif isinstance(parsed_data, dict):
                # Try to extract list data from known keys
                for key in self._list_return_keys:
                    if key in parsed_data and isinstance(parsed_data[key], list):
                        return self._convert_to_list_model(parsed_data[key])  # type: ignore[arg-type] # parsed_data[key] is list here
        except json.JSONDecodeError as e:
            # Log the error but don't raise, as this is a fallback path
            logger.warning(f"Could not parse string response as JSON in fallback: {e}", exc_info=True)

    logger.warning(f"Could not extract list data from response using fallback, returning empty list. Response snippet: {str(data)[:200]}")
    return []


def _dump_model_instance(self, model_instance: T, partial: bool) -> JSONDict:
    if hasattr(model_instance, "model_dump") and callable(model_instance.model_dump):  # type: ignore[attr-defined]
        return cast(JSONDict, model_instance.model_dump(exclude_unset=partial))  # type: ignore[attr-defined]
    elif hasattr(model_instance, "dict") and callable(model_instance.dict):  # type: ignore[attr-defined] # Fallback for older Pydantic
        logger.warning(f"Using deprecated dict() for dumping model {type(model_instance)}.")
        return cast(JSONDict, model_instance.dict(exclude_unset=partial))  # type: ignore[attr-defined]
    elif hasattr(model_instance, "__dict__"):  # Generic fallback
        logger.warning(f"Using __dict__ for dumping model instance {type(model_instance)}.")
        return cast(JSONDict, model_instance.__dict__)
    else:
        raise TypeError(f"Cannot dump model instance of type {type(model_instance)}")


def _validate_partial_dict(self, data_dict: JSONDict) -> None:
    if not self._datamodel:
        return  # No validation if no datamodel

    try:
        # Attempt validation. We only care about non-'missing' errors here.
        self._datamodel.model_validate(data_dict)  # type: ignore[attr-defined]
    except PydanticValidationError as e:
        non_missing_errors = [err for err in e.errors() if err.get("type") != "missing"]
        if non_missing_errors:
            error_msg = f"Partial update data validation failed for provided fields in model {self._datamodel.__name__}"  # type: ignore[attr-defined]
            # Redact data before logging or raising
            redacted_data = redact_json_body(data_dict) if isinstance(data_dict, (dict, TypingList)) else data_dict
            logger.warning(
                "%s: %s",  # Avoid logging raw data
                error_msg,
                json.dumps(non_missing_errors, indent=2),
                # str(redacted_data)[:200], # Avoid logging even redacted data snippet here
            )
            raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e
        # If only 'missing' errors, we ignore them for partial updates.


def _validate_and_dump_full_dict(self, data_dict: JSONDict) -> JSONDict:
    if not self._datamodel:
        return data_dict  # Return as is if no datamodel

    try:
        validated_model = self._datamodel.model_validate(data_dict)  # type: ignore[attr-defined]
        # Dump the validated model (exclude_unset=False for full dump)
        return self._dump_model_instance(validated_model, partial=False)
    except PydanticValidationError as e:
        # Re-raise validation errors for full updates
        model_name = getattr(self._datamodel, "__name__", "Unknown")
        error_msg = f"Input data validation failed for model {model_name}"
        # Redact data before logging or raising
        redacted_data = redact_json_body(data_dict) if isinstance(data_dict, (dict, TypingList)) else data_dict
        logger.warning(
            "%s: %s",  # Avoid logging raw data
            error_msg,
            json.dumps(e.errors(), indent=2),
            # str(redacted_data)[:200], # Avoid logging even redacted data snippet here
        )
        raise DataValidationError(error_msg, data=redacted_data, pydantic_error=e) from e


def _dump_dictionary(self, data_dict: JSONDict, partial: bool) -> JSONDict:
    if partial:
        self._validate_partial_dict(data_dict)
        # For partial updates, return the original dict after validation passes
        return data_dict
    else:
        # For full updates, validate and dump
        return self._validate_and_dump_full_dict(data_dict)


def _dump_data(self, data: Optional[Union[JSONDict, T]], partial: bool = False) -> JSONDict:
    if data is None:
        return {}

    try:
        if self._datamodel and isinstance(data, self._datamodel):
            # 1. Handle Model Instances
            return self._dump_model_instance(data, partial)
        elif isinstance(data, dict):
            # 2. Handle Dictionaries
            return self._dump_dictionary(data, partial)
        else:
            # 3. Handle Invalid Types
            raise TypeError(f"Input data must be a dict or a model instance, got {type(data).__name__}")

    except DataValidationError:
        # Re-raise DataValidationErrors raised by helpers
        raise
    except Exception as e:
        # Catch unexpected errors during dumping/validation
        logger.error(f"Unexpected error dumping data: {e}", exc_info=True)
        # Wrap unexpected errors for clarity, though DataValidationError is preferred
        raise CrudClientError(f"Unexpected error during data dumping: {e}") from e

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
            return data.decode("utf-8")
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
        raise ModelConversionError(f"Failed to convert response to model: {e}", response=None, data=data) from e


def _convert_to_list_model(self, data: JSONList) -> Union[List[T], JSONList]:
    if not self._datamodel:
        return data

    try:
        return [self._datamodel(**item) for item in data]
    except Exception as e:
        logger.error(f"Failed to convert list response to model: {e}")
        raise ModelConversionError(f"Failed to convert list response to model: {e}", response=None, data=data) from e


def _validate_list_return(self, data: RawResponse) -> Union[JSONList, List[T], ApiResponse]:
    try:
        # Validate the response data
        validated_data = self._validate_response(data)

        # Use the response strategy to convert the data
        if self._response_strategy:
            return self._response_strategy.convert_list(validated_data)

        # If no strategy is available, use the fallback conversion
        return self._fallback_list_conversion(validated_data)

    except PydanticValidationError as e:  # Catch Pydantic validation errors during list conversion
        logger.error(f"Failed to convert list response items to model: {e}")
        # Wrap Pydantic error in ModelConversionError as expected by tests
        raise ModelConversionError(f"Failed to convert list response items to model: {e}", data=data) from e  # Pass the original raw data
    except Exception as e:
        logger.error(f"Failed to validate list return: {e}")
        # Re-raise other specific errors or wrap unexpected ones
        if isinstance(e, (ValueError, ModelConversionError)):
            raise
        # Wrap other unexpected errors in a generic ValueError for now
        raise ValueError(f"Unexpected error during list validation: {e}") from e


def _fallback_list_conversion(self, data: RawResponse) -> Union[JSONList, List[T], ApiResponse]:
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


def _dump_data(self, data: Optional[Union[JSONDict, T]], partial: bool = False) -> JSONDict:  # noqa: C901
    if data is None:
        return {}

    try:
        # 1. Handle Model Instances
        if self._datamodel and isinstance(data, self._datamodel):
            # Dump model instance, respecting 'partial' flag
            if hasattr(data, "model_dump") and callable(data.model_dump):
                return cast(JSONDict, data.model_dump(exclude_unset=partial))  # type: ignore[attr-defined]
            # Fallback dumping for older Pydantic or other models
            elif hasattr(data, "dict") and callable(data.dict):
                logger.warning(f"Using dict() for dumping model {type(data)}.")
                return cast(JSONDict, data.dict(exclude_unset=partial))  # type: ignore[attr-defined]
            elif hasattr(data, "__dict__"):
                logger.warning(f"Using __dict__ for dumping model {type(data)}.")
                return cast(JSONDict, data.__dict__)
            else:
                raise TypeError(f"Cannot dump model instance of type {type(data)}")

        # 2. Handle Dictionaries
        elif isinstance(data, dict):
            # For partial updates: Validate field types but return original dict
            if partial:
                if self._datamodel:
                    try:
                        # Attempt validation. This might raise ValidationError if required fields
                        # are missing OR if provided fields have type errors.
                        self._datamodel(**data)
                        # If validation passes (e.g., all required fields were provided,
                        # or model allows partial init), return the original dict.
                        return cast(JSONDict, data)
                    except PydanticValidationError as e:
                        # Check if the *only* errors are related to missing fields.
                        # We want to ignore 'missing' errors for partial updates,
                        # but raise errors for invalid types on provided fields.
                        non_missing_errors = [err for err in e.errors() if err.get("type") != "missing"]
                        if non_missing_errors:
                            # If there are errors other than 'missing' (e.g., type errors),
                            # then the partial data is truly invalid. Raise the error.
                            logger.error(f"Partial update data validation failed for provided fields: {e}")
                            # Raise the custom error, attaching the original Pydantic error
                            raise ValidationError(str(e), data=data, pydantic_error=e) from e
                        else:
                            # If all errors were 'missing', ignore them for partial update
                            # and return the original dictionary.
                            return cast(JSONDict, data)
                else:
                    # No datamodel defined, return dict as is for partial update
                    return cast(JSONDict, data)

            # For create/full update, validate if datamodel exists
            elif self._datamodel:
                # Attempt validation by creating a full model instance
                validated_model = self._datamodel(**data)
                # Dump the validated model (exclude_unset=False for full dump)
                if hasattr(validated_model, "model_dump") and callable(validated_model.model_dump):
                    return cast(JSONDict, validated_model.model_dump(exclude_unset=False))
                # Fallback dumping for validated model
                elif hasattr(validated_model, "dict") and callable(validated_model.dict):
                    logger.warning(f"Using dict() for dumping validated model {type(validated_model)}.")
                    return cast(JSONDict, validated_model.dict(exclude_unset=False))  # type: ignore[call-arg]
                elif hasattr(validated_model, "__dict__"):
                    logger.warning(f"Using __dict__ for dumping validated model {type(validated_model)}.")
                    return cast(JSONDict, validated_model.__dict__)
                else:
                    raise TypeError(f"Cannot dump validated model of type {type(validated_model)}")
            else:
                # No datamodel defined, return dict as is for full update
                return cast(JSONDict, data)

        # 3. Handle Invalid Types
        else:
            raise TypeError(f"Input data must be a dict or a model instance, got {type(data).__name__}")

        # Note: Fallback block below is removed as logic is integrated above.

    except PydanticValidationError as e:  # Catch Pydantic's validation error
        logger.error(f"Input data validation failed: {e}")
        # Re-raise as our custom ValidationError, preserving original details
        raise ValidationError(str(e), data=data, pydantic_error=e) from e
    except Exception as e:
        logger.error(f"Failed to dump data: {e}")
        # General catch-all, re-raise as ValidationError for consistency
        raise ValidationError(f"Failed to dump data: {e}", data=data) from e

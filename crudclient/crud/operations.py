import json
import logging
from typing import Any, Dict
from typing import List as TypingList  # Rename List to avoid conflict
from typing import Optional, Union

from pydantic import ValidationError as PydanticValidationError

from ..exceptions import DataValidationError
from ..http.utils import redact_json_body
from ..models import ApiResponse
from ..types import JSONDict, JSONList
from .base import T

logger = logging.getLogger(__name__)


def list_operation(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None) -> Union[JSONList, TypingList[T], ApiResponse]:
    if "list" not in self.allowed_actions:
        raise ValueError(f"List action not allowed for {self.__class__.__name__}")

    endpoint = self._get_endpoint(parent_args=(parent_id,) if parent_id else None)
    response = self.client.get(endpoint, params=params)
    return self._validate_list_return(response)


def create_operation(self, data: Union[JSONDict, T], parent_id: Optional[str] = None, params: Optional[JSONDict] = None) -> Union[T, JSONDict]:
    if "create" not in self.allowed_actions:
        raise ValueError(f"Create action not allowed for {self.__class__.__name__}")

    try:
        # Validate and convert input data
        converted_data = self._dump_data(data)

        # Make the API request
        endpoint = self._get_endpoint(parent_args=(parent_id,) if parent_id else None)
        response = self.client.post(endpoint, json=converted_data, params=params)

        # Convert the response to a model instance
        return self._convert_to_model(response)

    except PydanticValidationError as e:
        # Redact sensitive data before logging or raising
        redacted_data = redact_json_body(data) if isinstance(data, (dict, TypingList)) else data
        logger.error(
            "Request data validation failed during 'create' for resource '%s'. Errors: %s",
            getattr(self._datamodel, "__name__", "Unknown"),
            json.dumps(e.errors()),  # Keep structured errors, avoid logging raw data here
        )
        raise DataValidationError(
            f"Request data validation failed for {getattr(self._datamodel, '__name__', 'Unknown')}",
            data=redacted_data,  # Pass redacted data
            pydantic_error=e,
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in create operation: {e}", exc_info=True)
        raise


def read_operation(self, resource_id: str, parent_id: Optional[str] = None) -> Union[T, JSONDict]:
    if "read" not in self.allowed_actions:
        raise ValueError(f"Read action not allowed for {self.__class__.__name__}")

    endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
    response = self.client.get(endpoint)
    return self._convert_to_model(response)


def update_operation(
    self,
    resource_id: Optional[str] = None,
    data: Optional[Union[JSONDict, T]] = None,
    parent_id: Optional[str] = None,
    update_mode: Optional[str] = None,
) -> Union[T, JSONDict]:
    if "update" not in self.allowed_actions:
        raise ValueError(f"Update action not allowed for {self.__class__.__name__}")

    # Determine the update mode to use
    effective_mode = update_mode or getattr(self, "_update_mode", "standard")

    try:
        # Validate and convert input data
        converted_data = self._dump_data(data)

        # Make the API request based on the update mode
        if effective_mode == "no_resource_id":
            # For APIs that don't use resource_id in the URL (e.g., Tripletex company)
            endpoint = self._get_endpoint(parent_args=(parent_id,) if parent_id else None)
            # Skip data validation and conversion for non-standard APIs
            # Use the original data directly, similar to the working implementation
            if isinstance(data, dict):
                json_data = data
            else:
                # If it's not a dict, we still need to convert it
                json_data = converted_data
            response = self.client.put(endpoint, json=json_data)
        else:
            # Standard RESTful update
            if resource_id is None:
                raise ValueError("resource_id is required for standard update mode")
            endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
            response = self.client.put(endpoint, json=converted_data)

        # Convert the response to a model instance
        return self._convert_to_model(response)

    except PydanticValidationError as e:
        # Redact sensitive data before logging or raising
        redacted_data = redact_json_body(data) if isinstance(data, (dict, TypingList)) else data
        logger.error(
            "Request data validation failed during 'update' for resource '%s'. Errors: %s",
            getattr(self._datamodel, "__name__", "Unknown"),
            json.dumps(e.errors()),  # Keep structured errors, avoid logging raw data here
        )
        raise DataValidationError(
            f"Request data validation failed for {getattr(self._datamodel, '__name__', 'Unknown')}",
            data=redacted_data,  # Pass redacted data
            pydantic_error=e,
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in update operation: {e}", exc_info=True)
        raise


def partial_update_operation(self, resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]:
    if "partial_update" not in self.allowed_actions:
        raise ValueError(f"Partial update action not allowed for {self.__class__.__name__}")

    try:
        # Validate and convert input data (partial=True)
        converted_data = self._dump_data(data, partial=True)

        # Make the API request
        endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
        response = self.client.patch(endpoint, json=converted_data)

        # Convert the response to a model instance
        return self._convert_to_model(response)

    except PydanticValidationError as e:
        # Redact sensitive data before logging or raising
        redacted_data = redact_json_body(data) if isinstance(data, (dict, TypingList)) else data
        logger.error(
            "Request data validation failed during 'partial_update' for resource '%s'. Errors: %s",
            getattr(self._datamodel, "__name__", "Unknown"),
            json.dumps(e.errors()),  # Keep structured errors, avoid logging raw data here
        )
        raise DataValidationError(
            f"Partial update request data validation failed for {getattr(self._datamodel, '__name__', 'Unknown')}",
            data=redacted_data,  # Pass redacted data
            pydantic_error=e,
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in partial update operation: {e}", exc_info=True)
        raise


def destroy_operation(self, resource_id: str, parent_id: Optional[str] = None) -> None:
    if "destroy" not in self.allowed_actions:
        raise ValueError(f"Destroy action not allowed for {self.__class__.__name__}")

    endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
    self.client.delete(endpoint)


def _prepare_request_body_kwargs(
    self,
    data: Optional[Union[JSONDict, T]],
    files: Optional[JSONDict],
    content_type: Optional[str],
) -> Dict[str, Any]:
    request_body_kwargs = {}

    # a. Multipart/Form-Data (Files)
    if files is not None:
        request_body_kwargs["files"] = files

        # If data is also provided (for additional form fields)
        if data is not None:
            if hasattr(data, "model_dump") and callable(data.model_dump):  # type: ignore[attr-defined]
                request_body_kwargs["data"] = data.model_dump()  # type: ignore[attr-defined]
            elif isinstance(data, dict):
                request_body_kwargs["data"] = data
            else:
                raise TypeError("For multipart/form-data with files, 'data' must be a dict or a Pydantic model")

    # b. Application/x-www-form-urlencoded
    elif content_type == "application/x-www-form-urlencoded":
        if data is not None:
            if hasattr(data, "model_dump") and callable(data.model_dump):  # type: ignore[attr-defined]
                request_body_kwargs["data"] = data.model_dump()  # type: ignore[attr-defined]
            elif isinstance(data, dict):
                request_body_kwargs["data"] = data
            else:
                raise TypeError("For application/x-www-form-urlencoded, 'data' must be a dict or a Pydantic model")

    # c. Application/json (Default)
    elif files is None and (content_type is None or content_type == "application/json"):
        if data is not None:
            if hasattr(data, "model_dump") and callable(data.model_dump):  # type: ignore[attr-defined]
                request_body_kwargs["json"] = data.model_dump()  # type: ignore[attr-defined]
            elif isinstance(data, dict):
                request_body_kwargs["json"] = data
            else:
                raise TypeError("For application/json, 'data' must be a dict or a Pydantic model")
        else:
            # Explicitly set json=None if no data is provided
            request_body_kwargs["json"] = None

    # d. Unsupported Content-Type with Data
    elif data is not None and content_type is not None:
        raise ValueError(f"Unsupported content_type '{content_type}' for provided 'data'")

    return request_body_kwargs


def custom_action_operation(
    self,
    action: str,
    method: str = "post",
    resource_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    data: Optional[Union[JSONDict, T]] = None,
    params: Optional[JSONDict] = None,
    files: Optional[JSONDict] = None,
    content_type: Optional[str] = None,
) -> Union[T, JSONDict, TypingList[JSONDict]]:
    # Runtime type checks for critical parameters
    if not isinstance(action, str):
        raise TypeError(f"Action must be a string, got {type(action).__name__}")

    if method not in ["get", "post", "put", "patch", "delete", "head", "options", "trace"]:
        raise ValueError(f"Invalid HTTP method: {method}")

    if resource_id is not None and not isinstance(resource_id, str):
        raise TypeError(f"Resource ID must be a string or None, got {type(resource_id).__name__}")

    if parent_id is not None and not isinstance(parent_id, str):
        raise TypeError(f"Parent ID must be a string or None, got {type(parent_id).__name__}")

    # Build endpoint arguments: only include non-None resource_id and action
    endpoint_args = [arg for arg in [resource_id, action] if arg is not None]
    endpoint = self._get_endpoint(*endpoint_args, parent_args=(parent_id,) if parent_id else None)

    final_kwargs = {}
    if params:
        final_kwargs["params"] = params

    try:
        # Handle data payload for methods that use a request body
        if method.lower() in ["post", "put", "patch"]:
            request_body_kwargs = self._prepare_request_body_kwargs(data, files, content_type)
            final_kwargs.update(request_body_kwargs)

        # Make the API request
        response = getattr(self.client, method.lower())(endpoint, **final_kwargs)

        # Handle the response
        try:
            # Check if the response is a list type
            if hasattr(response, "__iter__") and not isinstance(response, (dict, str, bytes)):
                return response
            # Attempt to convert the response. Specific validation/parsing errors
            # (DataValidationError, ResponseParsingError) should be raised from
            # _convert_to_model or its delegates if they occur.
            return self._convert_to_model(response)
        except Exception as e:
            # Log unexpected errors during response conversion in custom actions
            logger.error(f"Unexpected error converting custom action response: {e}", exc_info=True)
            # Re-raise the original unexpected exception for higher-level handling
            raise

    except PydanticValidationError as e:
        # Redact sensitive data before logging or raising
        redacted_data = redact_json_body(data) if isinstance(data, (dict, TypingList)) else data
        # Assuming data validation might happen implicitly if data is a dict
        # and needs conversion before sending, although the code tries to dump models directly.
        # Logging here provides visibility if Pydantic validation occurs unexpectedly at this stage.
        logger.error(
            "Request data validation failed during custom action '%s'. Errors: %s",
            action,  # Use the action name for context
            json.dumps(e.errors()),  # Keep structured errors, avoid logging raw data here
        )
        raise DataValidationError(
            "Custom action request data validation failed",
            data=redacted_data,  # Pass redacted data
            pydantic_error=e,
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error in custom_action operation: {e}", exc_info=True)
        raise


# Aliases for the Crud class methods
list = list_operation
create = create_operation
read = read_operation
update = update_operation
partial_update = partial_update_operation
destroy = destroy_operation
custom_action = custom_action_operation

import logging
from typing import List, Optional, Union

from ..exceptions import ModelConversionError, ValidationError
from ..models import ApiResponse
from ..types import JSONDict, JSONList
from .base import T

# Get a logger for this module
logger = logging.getLogger(__name__)

# Import T from base module


def list_operation(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None) -> Union[JSONList, List[T], ApiResponse]:
    if "list" not in self.allowed_actions:
        raise ValueError(f"List action not allowed for {self.__class__.__name__}")

    endpoint = self._get_endpoint(parent_args=(parent_id,) if parent_id else None)
    response = self.client.get(endpoint, params=params)
    return self._validate_list_return(response)


def create_operation(self, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]:
    if "create" not in self.allowed_actions:
        raise ValueError(f"Create action not allowed for {self.__class__.__name__}")

    try:
        # Validate and convert input data
        converted_data = self._dump_data(data)

        # Make the API request
        endpoint = self._get_endpoint(parent_args=(parent_id,) if parent_id else None)
        response = self.client.post(endpoint, json=converted_data)

        # Convert the response to a model instance
        return self._convert_to_model(response)

    except ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle other exceptions
        logger.error(f"Error in create operation: {e}")
        raise


def read_operation(self, resource_id: str, parent_id: Optional[str] = None) -> Union[T, JSONDict]:
    if "read" not in self.allowed_actions:
        raise ValueError(f"Read action not allowed for {self.__class__.__name__}")

    endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
    response = self.client.get(endpoint)
    return self._convert_to_model(response)


def update_operation(self, resource_id: str, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]:
    if "update" not in self.allowed_actions:
        raise ValueError(f"Update action not allowed for {self.__class__.__name__}")

    try:
        # Validate and convert input data
        converted_data = self._dump_data(data)

        # Make the API request
        endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
        response = self.client.put(endpoint, json=converted_data)

        # Convert the response to a model instance
        return self._convert_to_model(response)

    except ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle other exceptions
        logger.error(f"Error in update operation: {e}")
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

    except ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle other exceptions
        logger.error(f"Error in partial update operation: {e}")
        raise


def destroy_operation(self, resource_id: str, parent_id: Optional[str] = None) -> None:
    if "destroy" not in self.allowed_actions:
        raise ValueError(f"Destroy action not allowed for {self.__class__.__name__}")

    endpoint = self._get_endpoint(resource_id, parent_args=(parent_id,) if parent_id else None)
    self.client.delete(endpoint)


def custom_action_operation(
    self,
    action: str,
    method: str = "post",
    resource_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    data: Optional[Union[JSONDict, T]] = None,
    params: Optional[JSONDict] = None,
) -> Union[T, JSONDict, List[JSONDict]]:
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

    kwargs = {}
    if params:
        kwargs["params"] = params

    try:
        # Handle data payload for methods that use a request body
        if method.lower() in ["post", "put", "patch"]:
            if data is not None:
                # If data is a model instance, dump it (assuming it has model_dump)
                # Custom actions might use different models, so don't validate against self._datamodel here.
                if hasattr(data, "model_dump") and callable(data.model_dump):  # type: ignore[attr-defined]
                    kwargs["json"] = data.model_dump()  # type: ignore[attr-defined]
                elif isinstance(data, dict):
                    # Pass dictionaries directly for custom actions
                    kwargs["json"] = data
                else:
                    # Raise error for unsupported data types
                    raise TypeError(f"Unsupported data type for custom action payload: {type(data).__name__}")
            else:
                # Explicitly set json=None if no data is provided
                kwargs["json"] = None

        # Make the API request
        response = getattr(self.client, method.lower())(endpoint, **kwargs)

        # Handle the response
        try:
            # Check if the response is a list type
            if hasattr(response, "__iter__") and not isinstance(response, (dict, str, bytes)):
                return response
            return self._convert_to_model(response)
        except Exception as e:
            logger.error(f"Failed to convert response to model: {e}")
            if isinstance(e, ModelConversionError):
                raise
            raise ModelConversionError(f"Failed to convert response to model: {e}", response=None, data=response) from e

    except ValidationError:
        # Re-raise validation errors
        raise
    except Exception as e:
        # Handle other exceptions
        logger.error(f"Error in custom_action operation: {e}")
        raise


# Aliases for the Crud class methods
list = list_operation
create = create_operation
read = read_operation
update = update_operation
partial_update = partial_update_operation
destroy = destroy_operation
custom_action = custom_action_operation

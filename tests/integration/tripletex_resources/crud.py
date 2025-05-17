from typing import Any, Generic, Optional, Type, TypeVar, Union

from crudclient.crud import Crud
from crudclient.response_strategies import ModelDumpable
from crudclient.types import JSONDict, RawResponse

T = TypeVar("T", bound=ModelDumpable)


class TripletexCrud(Crud[T], Generic[T]):
    """
    Base class for Tripletex CRUD operations.

    This class extends the generic Crud class with Tripletex-specific functionality
    to handle the Tripletex API response format, which returns single items in a
    'value' field and lists in a 'values' field.
    """

    # Override these attributes to allow for different model types
    _create_model: Optional[Type[Any]] = None
    _update_model: Optional[Type[Any]] = None
    _api_response_model: Optional[Type[Any]] = None

    def _convert_to_model(self, data: RawResponse) -> Union[T, JSONDict]:
        """
        Override the default _convert_to_model method to handle the nested response structure.

        Tripletex API returns single items in the 'value' field of the response.
        This method extracts the 'value' field before passing it to the parent class's
        conversion logic.

        Args:
            data: The API response data.

        Returns:
            Union[T, JSONDict]: An instance of the datamodel or a dictionary.

        Raises:
            DataValidationError: If the response data fails validation.
            ValueError: If the response data is invalid or missing the 'value' field.
        """
        # First validate the response data using the parent class's method
        validated_data = self._validate_response(data)

        # If the data is already a model instance, return it
        if self._datamodel is not None and isinstance(validated_data, self._datamodel):
            return validated_data

        # If the data is a dictionary, check for the 'value' field
        if isinstance(validated_data, dict):
            if "value" in validated_data:
                # Extract the 'value' field and pass it to the parent class's conversion logic
                return super()._convert_to_model(validated_data["value"])
            # If no 'value' field, continue with normal processing (for list responses)

        # For all other cases, use the parent class's implementation
        return super()._convert_to_model(validated_data)

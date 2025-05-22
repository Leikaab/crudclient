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
        Convert Tripletex API response to data model.

        Parameters
        ----------
        data : RawResponse
            The raw response data from the Tripletex API.

        Returns
        -------
        Union[T, JSONDict]
            An instance of the datamodel or a dictionary.

        Raises
        ------
        DataValidationError
            If the response data fails validation.
        ValueError
            If the response data is None, invalid, or not a dictionary.
            If the response data is missing the expected structure.

        Notes
        -----
        This method overrides the default _convert_to_model method to handle
        Tripletex's nested response structure. Tripletex API returns single items
        in the 'value' field and lists in the 'values' field of the response.
        """
        # First validate the response data using the parent class's method
        validated_data = self._validate_response(data)

        if validated_data is None:
            raise ValueError("Response data is None or invalid.")

        # If the data is already a model instance, return it
        if self._datamodel is not None and isinstance(validated_data, self._datamodel):
            return validated_data

        if not isinstance(validated_data, dict):
            raise ValueError("Response data is not a dictionary.")

        # For single item responses (value field)
        if "value" in validated_data and validated_data["value"] is not None and self._datamodel is not None:
            value_data = validated_data["value"]
            if isinstance(value_data, dict):
                return self._datamodel(**value_data)
            return value_data

        # For list responses (values field)
        if self._api_response_model is not None:
            try:
                # Try direct instantiation with the response model
                return self._api_response_model(**validated_data)
            except Exception:
                pass

        # Fall back to parent class behavior
        return super()._convert_to_model(validated_data)

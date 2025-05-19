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
        in the 'value' field of the response. This method extracts the 'value' field
        before passing it to the parent class's conversion logic.
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

        cleaned_data = validated_data.get("value", None)
        if isinstance(cleaned_data, (list, dict)):
            # If the subdata is a list or dict, convert it to the model
            return super()._convert_to_model(cleaned_data)

        return super()._convert_to_model(validated_data)

from typing import Any, Dict, Generic, List, TypeVar

from crudclient.crud import Crud
from crudclient.response_strategies import ModelDumpable

T = TypeVar("T", bound=ModelDumpable)


class TripletexCrud(Crud[T], Generic[T]):
    """
    Base class for Tripletex CRUD operations.

    This class extends the generic Crud class with Tripletex-specific functionality.
    """

    def _validate_response(self, response_data: Any) -> Dict[str, Any]:
        """
        Override the default _validate_response method to handle the nested response structure.

        Tripletex API returns data in the 'value' field of the response.
        """
        if isinstance(response_data, dict) and "value" in response_data:
            return response_data["value"]
        return response_data

    def _validate_list_return(self, response_data: dict) -> List[T]:
        """
        Validate and extract the list of items from the response data.

        Tripletex API returns items in the 'values' field of the response.
        """
        if not isinstance(response_data, dict):
            raise ValueError(f"Expected dict response, got {type(response_data)}")

        if "values" not in response_data:
            raise ValueError(f"Expected 'values' in response, got keys: {list(response_data.keys())}")

        values = response_data["values"]
        if not isinstance(values, list):
            raise ValueError(f"Expected list in 'values', got {type(values)}")

        # For simplicity in this example, we'll just return the raw values
        # In a real implementation, you would convert these to model objects
        return values

    def listcreate(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple resources in a single request.

        Args:
            data_list: A list of dictionaries containing the data for each resource to create.

        Returns:
            A list of the created resources.
        """
        endpoint = self._get_endpoint()
        payload = {"values": data_list}
        response = self.client.post(endpoint + "/list", json=payload)

        if isinstance(response, dict) and "values" in response:
            return response["values"]

        return []

    def listupdate(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update multiple resources in a single request.

        Args:
            data_list: A list of dictionaries containing the data for each resource to update.
                       Each dictionary must include an 'id' field.

        Returns:
            A list of the updated resources.
        """
        endpoint = self._get_endpoint()
        payload = {"values": data_list}
        response = self.client.put(endpoint + "/list", json=payload)

        if isinstance(response, dict) and "values" in response:
            return response["values"]

        return []

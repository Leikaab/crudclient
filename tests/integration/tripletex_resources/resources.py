from typing import Any, Dict, List, Union

from crudclient.types import JSONDict

from .crud import TripletexCrud
from .models import Country, CountryResponse, Supplier, SupplierResponse


class TripletexSuppliers(TripletexCrud[Supplier]):
    """
    CRUD operations for Tripletex suppliers.

    Note: We're using None for _datamodel to return dictionaries instead of model objects
    because the Tripletex API has specific requirements for the request format.
    The Supplier model is still used for type hints and documentation.
    """
    _resource_path = "supplier"
    _datamodel = None  # Use None to return dictionaries instead of model objects
    _api_response_model = SupplierResponse
    allowed_actions = ["list", "read", "create", "update", "destroy"]

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a supplier.

        This method overrides the default create method to handle the nested response structure.
        """
        endpoint = self._get_endpoint()
        response = self.client.post(endpoint, json=data)

        if isinstance(response, dict) and "value" in response:
            return response["value"]

        # If response is not a dict or doesn't have 'value', return an empty dict
        if isinstance(response, dict):
            return response

        return {}

    def update(self, resource_id: str | int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a supplier.

        This method overrides the default update method to handle the nested response structure.
        """
        endpoint = f"{self._get_endpoint()}/{resource_id}"
        response = self.client.put(endpoint, json=data)

        if isinstance(response, dict) and "value" in response:
            return response["value"]

        # If response is not a dict or doesn't have 'value', return an empty dict
        if isinstance(response, dict):
            return response

        return {}

    def listcreate(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple suppliers in a single request.

        For Tripletex API, we need to create resources one by one since the batch endpoint
        is returning errors.

        Args:
            data_list: A list of dictionaries containing the data for each resource to create.

        Returns:
            A list of the created resources.
        """
        created_resources = []
        for data in data_list:
            created = self.create(data)
            created_resources.append(created)

        return created_resources

    def listupdate(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update multiple suppliers in a single request.

        For Tripletex API, we need to update resources one by one since the batch endpoint
        is returning errors.

        Args:
            data_list: A list of dictionaries containing the data for each resource to update.
                       Each dictionary must include an 'id' field.

        Returns:
            A list of the updated resources.
        """
        updated_resources = []
        for data in data_list:
            if "id" not in data:
                raise ValueError("Each item in data_list must have an 'id' field")

            resource_id = data["id"]
            updated = self.update(resource_id, data)
            updated_resources.append(updated)

        return updated_resources


class TripletexCountries(TripletexCrud[Country]):
    """
    CRUD operations for Tripletex countries.
    """
    _resource_path = "country"
    _datamodel = Country
    _api_response_model = CountryResponse
    allowed_actions = ["list", "read"]

    def read(self, resource_id: str | int) -> Union[Dict[str, Any], JSONDict]:
        """
        Read a country by ID.

        This method overrides the default read method to handle the nested response structure.
        """
        endpoint = f"{self._get_endpoint()}/{resource_id}"
        response = self.client.get(endpoint)

        # The response has a 'value' field that contains the actual country data
        if isinstance(response, dict) and 'value' in response:
            return response['value']

        # If response is not a dict or doesn't have 'value', return it as is
        if isinstance(response, dict):
            return response

        # Last resort: return an empty dict
        return {}

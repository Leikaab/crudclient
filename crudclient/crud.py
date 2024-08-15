from typing import Any, Dict, Optional, Union

from .client import Client


class Crud:
    """
    Base class for CRUD operations on API resources.
    """

    def __init__(self, client: Client, base_endpoint: str):
        """
        Initialize the CRUD resource.

        :param client: An instance of the API client
        :param base_endpoint: The base endpoint for this resource (e.g., '/users')
        """
        self.client = client
        self.base_endpoint = base_endpoint.strip("/")

    def list(self, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], bytes, str]:
        """
        Retrieve a list of resources.

        :param params: Optional query parameters
        :return: The API response
        """
        return self.client.get(f"/{self.base_endpoint}", params=params)

    def create(self, data: Dict[str, Any]) -> Union[Dict[str, Any], bytes, str]:
        """
        Create a new resource.

        :param data: The data for the new resource
        :return: The API response
        """
        return self.client.post(f"/{self.base_endpoint}", json=data)

    def get(self, resource_id: str) -> Union[Dict[str, Any], bytes, str]:
        """
        Retrieve a specific resource.

        :param resource_id: The ID of the resource to retrieve
        :return: The API response
        """
        return self.client.get(f"/{self.base_endpoint}/{resource_id}")

    def update(self, resource_id: str, data: Dict[str, Any]) -> Union[Dict[str, Any], bytes, str]:
        """
        Update a specific resource.

        :param resource_id: The ID of the resource to update
        :param data: The updated data for the resource
        :return: The API response
        """
        return self.client.put(f"/{self.base_endpoint}/{resource_id}", json=data)

    def partial_update(self, resource_id: str, data: Dict[str, Any]) -> Union[Dict[str, Any], bytes, str]:
        """
        Partially update a specific resource.

        :param resource_id: The ID of the resource to update
        :param data: The partial updated data for the resource
        :return: The API response
        """
        return self.client.patch(f"/{self.base_endpoint}/{resource_id}", json=data)

    def delete(self, resource_id: str) -> Union[Dict[str, Any], bytes, str]:
        """
        Delete a specific resource.

        :param resource_id: The ID of the resource to delete
        :return: The API response
        """
        return self.client.delete(f"/{self.base_endpoint}/{resource_id}")

    def custom_action(
        self,
        action: str,
        method: str = "post",
        resource_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], bytes, str]:
        """
        Perform a custom action on the resource.

        :param action: The name of the custom action
        :param method: The HTTP method to use (default is 'post')
        :param resource_id: Optional resource ID if the action is for a specific resource
        :param data: Optional data to send with the request
        :param params: Optional query parameters
        :return: The API response
        """
        endpoint = f"/{self.base_endpoint}"
        if resource_id:
            endpoint += f"/{resource_id}"
        endpoint += f"/{action}"

        kwargs = {}
        if data:
            kwargs["json"] = data
        if params:
            kwargs["params"] = params

        return getattr(self.client, method.lower())(endpoint, **kwargs)

import os
from typing import Any, Dict, List, Optional

from crudclient.api import API
from crudclient.client import Client, ClientConfig
from crudclient.crud import Crud
from crudclient.types import JSONDict

from .models import DataField, DataFieldsResponse, TemplateType, TemplateTypesResponse, User, UsersResponse


class OneflowConfig(ClientConfig):
    hostname = "https://api.test.oneflow.com"
    version = "v1"
    api_key = os.getenv("ONEFLOW_API_KEY")
    headers: Optional[Dict[str, str]] = {"x-oneflow-user-email": os.getenv("ONEFLOW_USER_EMAIL", "")}
    timeout: Optional[float] = 10.0
    retries: Optional[int] = 3

    def auth(self) -> Dict[str, str]:
        return {
            "x-oneflow-api-token": self.api_key or "",
        }


class UsersCrud(Crud[User]):
    _resource_path = "users"
    _datamodel = User
    _api_response_model = UsersResponse
    allowed_actions = ["list"]


class OneflowTemplateTypes(Crud[TemplateType]):
    _resource_path = "template_types"
    _datamodel = TemplateType
    _api_response_model = TemplateTypesResponse
    _methods: List[str] = ["list", "read", "create"]
    data_fields: "OneflowDataFields | None" = None


class OneflowDataFields(Crud[DataField]):

    _resource_path = "data_fields"
    _datamodel = DataField
    _api_response_model = DataFieldsResponse

    _methods: List[str] = ["update", "destroy"]
    _parent_resource = OneflowTemplateTypes

    def update(self, resource_id: str, data: Dict[str, Any] | DataField, parent_id: str | None = None) -> DataField | JSONDict:
        if parent_id is None:
            raise ValueError("Parent id is required for updating data fields")

        converted_data: JSONDict = self._dump_data(data)

        converted_data["custom_id"] = resource_id
        passable_data = {"data_fields": [converted_data]}
        endpoint = self._get_endpoint(parent_args=(parent_id,))
        response = self.client.put(endpoint, json=passable_data)
        assert isinstance(response, dict)
        for i in response["data_fields"]:
            if i["custom_id"] == converted_data["custom_id"]:
                return DataField.model_validate(i)
        raise ValueError("Invalid return from api")


class OneflowAPI(API):
    client_class = Client

    def _register_endpoints(self):
        assert self.client is not None, "Client is not initialized"

        self.users = UsersCrud(self.client)
        self.template_types = OneflowTemplateTypes(self.client)
        self.template_types.data_fields = OneflowDataFields(self.client, parent=self.template_types)

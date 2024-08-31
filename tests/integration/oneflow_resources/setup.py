import os
from typing import Any, Dict, List, Optional, cast

from crudclient.api import API
from crudclient.client import Client, ClientConfig
from crudclient.crud import Crud
from crudclient.types import JSONDict

from .models import DataField, DataFieldsResponse, TemplateType, TemplateTypesResponse, User, UsersResponse


class OneflowConfig(ClientConfig):
    hostname: str = "https://api.test.oneflow.com"
    version: str = "v1"
    api_key: str = os.getenv("ONEFLOW_API_KEY", "")
    headers: Optional[Dict[str, str]] = {"x-oneflow-user-email": os.getenv("ONEFLOW_USER_EMAIL", "")}
    timeout: Optional[float] = 10.0
    retries: Optional[int] = 3

    def auth(self) -> Dict[str, str]:
        return {
            "x-oneflow-api-token": self.api_key,
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


class OneflowDataFields(Crud[DataField]):

    _resource_path = "data_fields"
    _datamodel = DataField
    _api_response_model = DataFieldsResponse

    _methods: List[str] = ["update", "destroy"]
    _parent = OneflowTemplateTypes

    def update(self, resource_id: str, data: Dict[str, Any], parent_id: str | None = None) -> DataField | JSONDict:
        if parent_id is None:
            raise ValueError("Parent id is required for updating data fields")

        data["custom_id"] = resource_id
        passable_data = {"data_fields": [data]}
        endpoint = self._get_endpoint(parent_args=(parent_id,))
        response = self.client.put(endpoint, json=passable_data)
        response = cast(JSONDict, response)
        for i in response["data_fields"]:
            if i["custom_id"] == data["custom_id"]:
                return DataField.model_validate(i)
        raise ValueError("Invalid return from api")


class OneflowAPI(API):
    client_class = Client

    def _register_endpoints(self):
        self.users = UsersCrud(self.client)
        self.template_types = OneflowTemplateTypes(self.client)
        self.data_fields = OneflowDataFields(self.client)

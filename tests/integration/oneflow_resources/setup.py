import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from crudclient.api import API
from crudclient.auth import ApiKeyAuth
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud import Crud
from crudclient.types import JSONDict

from .models import (
    DataField,
    DataFieldsResponse,
    TemplateType,
    TemplateTypesResponse,
    User,
    UsersResponse,
)

# Load environment variables from .env file
load_dotenv()


class OneflowConfig(ClientConfig):
    hostname = "https://api.test.oneflow.com"
    version = "v1"
    api_key = os.getenv("ONEFLOW_API_KEY")
    headers: Optional[Dict[str, str]] = {"x-oneflow-user-email": os.getenv("ONEFLOW_USER_EMAIL", "")}

    def __init__(self):
        super().__init__()
        if self.api_key:
            self.auth_strategy = ApiKeyAuth(api_key=self.api_key, header_name="x-oneflow-api-token")


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

        converted_data: JSONDict = self._dump_data(data, partial=True)

        converted_data["custom_id"] = resource_id
        passable_data = {"data_fields": [converted_data]}
        # Fix the endpoint construction
        endpoint = f"template_types/{parent_id}/data_fields"
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

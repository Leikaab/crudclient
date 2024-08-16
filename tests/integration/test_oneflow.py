import os
from typing import Dict, Optional

import pytest
from pydantic import BaseModel, Field

from crudclient.api import API
from crudclient.client import Client, ClientConfig
from crudclient.crud import Crud
from crudclient.models import ApiResponse, Link


class User(BaseModel):
    links: Dict[str, Link] = Field(None, alias="_links")
    active: bool
    email: str
    id: int
    is_admin: bool
    name: str
    phone_number: str
    state: str
    title: str


class UsersResponse(ApiResponse[User]):
    pass


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


class OneflowAPI(API):
    client_class = Client

    def _register_endpoints(self):
        self.users = UsersCrud(self.client)


@pytest.fixture
def api():
    config = OneflowConfig()
    return OneflowAPI(client_config=config)


def test_api_configuration(api):
    assert api.client.base_url == "https://api.test.oneflow.com/v1"
    assert api.client.config.api_key == os.getenv("ONEFLOW_API_KEY")
    assert os.getenv("ONEFLOW_API_KEY") != ""
    assert os.getenv("ONEFLOW_USER_EMAIL") != ""
    assert api.client.config.headers == {"x-oneflow-user-email": os.getenv("ONEFLOW_USER_EMAIL")}


def test_list_users(api):
    users = api.users.list()
    assert isinstance(users, UsersResponse)
    assert len(users.data) > 0
    assert isinstance(users.data[0], User)
    assert users.data[0].id is not None

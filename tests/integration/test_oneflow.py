import os
import random

import pytest

from .oneflow_resources.setup import DataField, OneflowAPI, OneflowConfig, TemplateType, TemplateTypesResponse, User, UsersResponse


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


def test_list_template_types(api):
    template_types = api.template_types.list()
    assert isinstance(template_types, TemplateTypesResponse)
    assert len(template_types.data) > 0
    assert isinstance(template_types.data[0], TemplateType)
    assert template_types.data[0].id is not None


def test_read_template_type(api):
    template_type = api.template_types.read(220129)
    assert isinstance(template_type, TemplateType)
    assert template_type.id == 220129
    assert template_type.name == "TestTemplateGroup"
    assert template_type.updated_time is not None


def test_update_data_field(api):
    template_type_id = api.template_types.read(220129)
    rand = random.randint(1, 1000)
    data = {
        "name": "Employee_name",
        "description": "Name of employee",
        "placeholder": "John Workerson",
        "value": "test",
    }
    new_data = data.copy()
    new_data["value"] = f"new value {rand}"
    changed_data_field = api.template_types.data_fields.update(resource_id="employee_name", parent_id=template_type_id.id, data=new_data)
    assert isinstance(changed_data_field, DataField)
    assert changed_data_field.value == f"new value {rand}"

    reverted_data_field = api.template_types.data_fields.update(resource_id="employee_name", parent_id=template_type_id.id, data=data)
    assert isinstance(reverted_data_field, DataField)
    assert reverted_data_field.value == data["value"]

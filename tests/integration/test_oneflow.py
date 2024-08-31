import logging
import os
import random

import pytest

from .oneflow_resources.setup import DataField, OneflowAPI, OneflowConfig, TemplateType, TemplateTypesResponse, User, UsersResponse


def setup_logging():
    # Create the logger for 'crudclient'
    logger = logging.getLogger("crudclient")

    # Set the logger's level to DEBUG to capture all levels of logs
    logger.setLevel(logging.DEBUG)

    # Define a standard formatter for the log messages
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create and configure the FileHandler to log to 'error.log'
    file_handler = logging.FileHandler("/workspace/logs/error.log")
    file_handler.setLevel(logging.INFO)  # Log only INFO level and above to the file
    file_handler.setFormatter(formatter)

    # Add the FileHandler to the logger
    logger.addHandler(file_handler)

    # Optionally, you can also add a StreamHandler to output logs to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)  # Log all levels to the console
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


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
    logger = setup_logging()
    logger.info("Starting test_update_data_field")
    template_type_id = api.template_types.read(220129)
    rand = random.randint(1, 1000)
    data = {
        "custom_id": "employee_name",
        "name": "Employee_name",
        "description": "Name of employee",
        "placeholder": "John Workerson",
        "value": "test",
    }
    new_data = data.copy()
    new_data["value"] = f"new value {rand}"
    changed_data_field = api.data_fields.update(parent_id=template_type_id.id, data=[new_data])
    assert isinstance(changed_data_field, list)
    assert isinstance(changed_data_field[0], DataField)
    assert changed_data_field[0].value == f"new value {rand}"

    reverted_data_field = api.data_fields.update(parent_id=template_type_id.id, data=[data])
    assert isinstance(reverted_data_field, list)
    assert isinstance(reverted_data_field[0], DataField)
    assert reverted_data_field[0].value == [data][0]["value"]
    return reverted_data_field

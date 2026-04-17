"""
Fixtures specific to CRUD tests.
"""

from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel
from pytest_httpserver import HTTPServer

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud.base import Crud, T
from crudclient.types import JSONDict

_T = TypeVar("_T")


class BaseTestModel(BaseModel):
    """Test model for CRUD operations."""

    id: int
    name: str


class BaseTestCrud(Crud[BaseTestModel]):
    """Test CRUD class."""

    _resource_path = "test-resources"
    _datamodel = BaseTestModel

    def _prepare_request_body_kwargs(
        self,
        data: Optional[Union[JSONDict, T]],
        files: Optional[JSONDict],
        content_type: Optional[str],
    ) -> Dict[str, Any]:
        request_body_kwargs = {}

        # a. Multipart/Form-Data (Files)
        if files is not None:
            request_body_kwargs["files"] = files

            # If data is also provided (for additional form fields)
            if data is not None:
                if hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
                    request_body_kwargs["data"] = getattr(data, "model_dump")()
                elif isinstance(data, dict):
                    request_body_kwargs["data"] = data
                else:
                    raise TypeError("For multipart/form-data with files, 'data' must be a dict or a Pydantic model")

        # b. Application/x-www-form-urlencoded
        elif content_type == "application/x-www-form-urlencoded":
            if data is not None:
                if hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
                    request_body_kwargs["data"] = getattr(data, "model_dump")()
                elif isinstance(data, dict):
                    request_body_kwargs["data"] = data
                else:
                    raise TypeError("For application/x-www-form-urlencoded, 'data' must be a dict or a Pydantic model")

        # c. Application/json (Default)
        elif files is None and (content_type is None or content_type == "application/json"):
            if data is not None:
                if hasattr(data, "model_dump") and callable(getattr(data, "model_dump")):
                    request_body_kwargs["json"] = getattr(data, "model_dump")()
                elif isinstance(data, dict):
                    request_body_kwargs["json"] = data
                else:
                    raise TypeError("For application/json, 'data' must be a dict or a Pydantic model")
            else:
                # Explicitly set json=None if no data is provided
                request_body_kwargs["json"] = None  # type: ignore[assignment]

        # d. Unsupported Content-Type with Data
        elif data is not None and content_type is not None:
            raise ValueError(f"Unsupported content_type '{content_type}' for provided 'data'")

        return request_body_kwargs


# Define a dummy Parent Crud class for nesting tests


class ParentCrud(Crud[BaseModel]):  # Using BaseModel as a placeholder
    _resource_path = "parents"
    # No specific datamodel needed if only testing path generation


@pytest.fixture
def mock_client() -> MagicMock:
    """Return a mock Client instance with enhanced parent_id handling."""
    client = MagicMock(spec=Client)

    # Store original method references

    # Create a new mock client
    client = MagicMock(spec=Client)

    # Set up default return values for each method
    client.get.return_value = {"id": 1, "name": "Test Resource"}
    client.post.return_value = {"id": 1, "name": "Created Resource"}
    client.put.return_value = {"id": 1, "name": "Updated Resource"}
    client.patch.return_value = {"id": 1, "name": "Partially Updated Resource"}
    client.delete.return_value = None

    return client


@cast(Callable[..., _T], pytest.fixture)
def base_test_crud(mock_client: MagicMock) -> BaseTestCrud:
    """Return a BaseTestCrud instance with a mock client."""
    return BaseTestCrud(mock_client)


@cast(Callable[..., _T], pytest.fixture)
def http_client(httpserver: HTTPServer) -> Client:
    """Return a Client configured to communicate with the HTTPServer."""
    config = ClientConfig(hostname=f"http://{httpserver.host}:{httpserver.port}")
    return Client(config)


@cast(Callable[..., _T], pytest.fixture)
def base_test_crud_httpserver(http_client: Client) -> BaseTestCrud:
    """Return a BaseTestCrud instance using a real Client against HTTPServer."""
    return BaseTestCrud(http_client)


@pytest.fixture
def parent_crud(mock_client: MagicMock) -> ParentCrud:
    """Fixture for a parent CRUD resource instance."""
    return ParentCrud(mock_client)


@cast(Callable[..., _T], pytest.fixture)
def nested_base_test_crud(mock_client: MagicMock, parent_crud: ParentCrud) -> BaseTestCrud:
    """Fixture for a BaseTestCrud instance nested under ParentCrud."""
    # Instantiate BaseTestCrud with parent_crud as the parent
    return BaseTestCrud(mock_client, parent=parent_crud)

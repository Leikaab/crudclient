"""
Fixtures specific to API tests.
"""

from typing import Any, Dict, Optional, Union

import pytest
from pydantic import BaseModel

from crudclient.api import API
from crudclient.client import Client
from crudclient.crud import Crud
from crudclient.crud.base import T
from crudclient.types import JSONDict


class MockCrud(Crud[BaseModel]):
    _resource_path = "test"
    _datamodel = None

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


class MockAPI(API):
    client_class = Client

    def _register_endpoints(self):
        if self.client is None:
            raise ValueError("Client is required!")
        self.test_resource: Crud = MockCrud(self.client)

    def _register_groups(self):
        """
        Implementation of the abstract method to register ResourceGroup instances.
        This mock implementation doesn't register any groups.
        """


@pytest.fixture
def standard_data():
    """Return standard test data for API tests."""
    full_url = "https://api.example.com/v1/test"
    hostname = "https://api.example.com"
    return {"full_url": full_url, "hostname": hostname}

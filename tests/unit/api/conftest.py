"""
Fixtures specific to API tests.
"""

import pytest
from pydantic import BaseModel

from crudclient.api import API
from crudclient.client import Client
from crudclient.crud import Crud


class MockCrud(Crud[BaseModel]):
    _resource_path = "test"
    _datamodel = None


class MockAPI(API):
    client_class = Client

    def _register_endpoints(self):
        if self.client is None:
            raise ValueError("Client is required!")
        self.test_resource: Crud = MockCrud(self.client)


@pytest.fixture
def standard_data():
    """Return standard test data for API tests."""
    full_url = "https://api.example.com/v1/test"
    hostname = "https://api.example.com"
    return {"full_url": full_url, "hostname": hostname}

"""
Fixtures specific to CRUD tests.
"""

from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from crudclient.client import Client
from crudclient.crud.base import Crud
from crudclient.testing.simple_mock import SimpleMockClient


class TestModel(BaseModel):
    """Test model for CRUD operations."""
    id: int
    name: str


class TestCrud(Crud[TestModel]):
    """Test CRUD class."""
    _resource_path = "test-resources"
    _datamodel = TestModel


@pytest.fixture
def mock_client():
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


@pytest.fixture
def test_crud(mock_client):
    """Return a TestCrud instance with a mock client."""
    return TestCrud(mock_client)


@pytest.fixture
def simple_mock_client():
    """Return a SimpleMockClient instance."""
    return SimpleMockClient()


@pytest.fixture
def test_crud_with_simple_mock(simple_mock_client):
    """Return a TestCrud instance with a SimpleMockClient."""
    return TestCrud(simple_mock_client)

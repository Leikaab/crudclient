"""
Fixtures specific to CRUD tests.
"""

from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from crudclient.client import Client
from crudclient.crud.base import Crud
from crudclient.testing.simple_mock import SimpleMockClient


class BaseTestModel(BaseModel):
    """Test model for CRUD operations."""

    id: int
    name: str


class BaseTestCrud(Crud[BaseTestModel]):
    """Test CRUD class."""

    _resource_path = "test-resources"
    _datamodel = BaseTestModel


# Define a dummy Parent Crud class for nesting tests


class ParentCrud(Crud[BaseModel]):  # Using BaseModel as a placeholder
    _resource_path = "parents"
    # No specific datamodel needed if only testing path generation


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
def base_test_crud(mock_client):
    """Return a BaseTestCrud instance with a mock client."""
    return BaseTestCrud(mock_client)


@pytest.fixture
def simple_mock_client():
    """Return a SimpleMockClient instance."""
    return SimpleMockClient()


@pytest.fixture
def base_test_crud_with_simple_mock(simple_mock_client):
    """Return a BaseTestCrud instance with a SimpleMockClient."""
    return BaseTestCrud(simple_mock_client)


@pytest.fixture
def parent_crud(mock_client):
    """Fixture for a parent CRUD resource instance."""
    return ParentCrud(mock_client)


@pytest.fixture
def nested_base_test_crud(mock_client, parent_crud):
    """Fixture for a BaseTestCrud instance nested under ParentCrud."""
    # Instantiate BaseTestCrud with parent_crud as the parent
    return BaseTestCrud(mock_client, parent=parent_crud)

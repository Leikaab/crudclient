"""
Fixtures specific to CRUD tests.
"""

from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from crudclient.client import Client
from crudclient.crud import Crud


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
    """Return a mock Client instance."""
    return MagicMock(spec=Client)


@pytest.fixture
def test_crud(mock_client):
    """Return a TestCrud instance with a mock client."""
    return TestCrud(mock_client)

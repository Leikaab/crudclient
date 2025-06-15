"""
Unit tests for the ResourceGroup class.

This module contains tests for the ResourceGroup class, focusing on:
1. Initialization and parent-child relationships
2. Behavior as a Crud instance
3. Child registration and path construction
"""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict

from crudclient.client import Client
from crudclient.crud.base import Crud
from crudclient.groups import ResourceGroup


class ResourceTestModel(BaseModel):
    """Test model for ResourceGroup tests."""

    id: int
    name: str

    # Allow extra attributes for validation flexibility in tests
    model_config = ConfigDict(extra="allow")


class ConcreteChildCrud(Crud[ResourceTestModel]):
    """Concrete Crud class for testing as a child endpoint."""

    _resource_path = "child-resources"
    _datamodel = ResourceTestModel


class ConcreteChildGroup(ResourceGroup[ResourceTestModel]):
    """Concrete ResourceGroup class for testing as a child group."""

    _resource_path = "child-group"
    _datamodel = ResourceTestModel

    def _register_child_endpoints(self) -> None:
        """Register a test endpoint."""
        self.nested_resource = ConcreteChildCrud(self.client, parent=self)


class ConcreteResourceGroup(ResourceGroup[ResourceTestModel]):
    """Concrete ResourceGroup class for testing basic functionality."""

    _resource_path = "test-group"
    _datamodel = ResourceTestModel


class ConcreteParentGroup(ResourceGroup[ResourceTestModel]):
    """Concrete ResourceGroup class for testing parent-child relationships."""

    _resource_path = "parent-group"
    _datamodel = ResourceTestModel

    def _register_child_endpoints(self) -> None:
        """Register a test endpoint."""
        self.child_crud = ConcreteChildCrud(self.client, parent=self)

    def _register_child_groups(self) -> None:
        """Register a test group."""
        self.child_group = ConcreteChildGroup(self.client, parent=self)


@pytest.fixture
def mock_client() -> MagicMock:
    """Return a mock Client instance."""
    client = MagicMock(spec=Client)

    # Set up default return values for each method that match what the response strategy expects
    client.get.return_value = {"id": 1, "name": "Test Resource"}
    client.post.return_value = {"id": 1, "name": "Created Resource"}
    client.put.return_value = {"id": 123, "name": "Updated Resource"}
    client.patch.return_value = {"id": 1, "name": "Partially Updated Resource"}
    client.delete.return_value = None

    return client


class TestResourceGroupInitialization:
    """Tests for ResourceGroup initialization."""

    def test_init_calls_super_init(self, mock_client: MagicMock) -> None:
        """Test that ResourceGroup.__init__ calls super().__init__."""
        with patch.object(Crud, "__init__", return_value=None) as mock_super_init:
            ConcreteResourceGroup(mock_client)  # Create instance without assigning to unused variable

            # Assert super().__init__ was called with correct arguments
            mock_super_init.assert_called_once_with(mock_client, None)

    def test_init_sets_client_and_parent(self, mock_client: MagicMock) -> None:
        """Test that ResourceGroup.__init__ sets client and parent attributes."""
        # Create a parent
        parent = ConcreteResourceGroup(mock_client)

        # Create a group with a parent
        group = ConcreteResourceGroup(mock_client, parent=parent)

        # Assert client and parent are set correctly
        assert group.client is mock_client
        assert group.parent is parent

    def test_init_calls_register_methods(self, mock_client: MagicMock) -> None:
        """Test that ResourceGroup.__init__ calls _register_child_endpoints and _register_child_groups."""
        with patch.object(ConcreteResourceGroup, "_register_child_endpoints") as mock_register_endpoints:
            with patch.object(ConcreteResourceGroup, "_register_child_groups") as mock_register_groups:
                ConcreteResourceGroup(mock_client)  # Create instance without assigning to unused variable

                # Assert registration methods were called
                mock_register_endpoints.assert_called_once()
                mock_register_groups.assert_called_once()


class TestResourceGroupAsCrud:
    """Tests for ResourceGroup behavior as a Crud instance."""

    def test_crud_list_operation(self, mock_client: MagicMock) -> None:
        """Test that ResourceGroup can perform list operations as a Crud instance."""
        # Arrange
        group = ConcreteResourceGroup(mock_client)
        # Set up mock response for list operation with the expected structure
        mock_client.get.return_value = [{"id": 1, "name": "Test 1"}, {"id": 2, "name": "Test 2"}]

        # Act
        result = group.list()

        # Assert
        # Check that the client was called with the correct path
        mock_client.get.assert_called_once()
        args, kwargs = mock_client.get.call_args
        assert args[0] == "test-group"
        assert isinstance(result, list)
        assert len(result) == 2

    def test_crud_read_operation(self, mock_client: MagicMock) -> None:
        """Test that ResourceGroup can perform read operations as a Crud instance."""
        # Arrange
        group = ConcreteResourceGroup(mock_client)
        resource_id = "123"
        mock_client.get.return_value = {"id": 123, "name": "Test Resource"}

        # Act
        result = group.read(resource_id=resource_id)

        # Assert
        # Check that the client was called with the correct path
        mock_client.get.assert_called_once()
        args, kwargs = mock_client.get.call_args
        assert args[0] == "test-group/123"
        assert isinstance(result, ResourceTestModel)
        assert result.id == 123
        assert result.name == "Test Resource"

    def test_crud_create_operation(self, mock_client: MagicMock) -> None:
        """Test that ResourceGroup can perform create operations as a Crud instance."""
        # Arrange
        group = ConcreteResourceGroup(mock_client)
        # Include id in the data to avoid validation error
        data = {"id": 1, "name": "New Resource"}
        mock_client.post.return_value = {"id": 1, "name": "New Resource"}

        # Act
        result = group.create(data=data)

        # Assert
        # Check that the client was called with the correct path and payload
        mock_client.post.assert_called_once_with("test-group", json=data, params=None)
        assert isinstance(result, ResourceTestModel)
        assert result.id == 1
        assert result.name == "New Resource"

    def test_crud_update_operation(self, mock_client: MagicMock) -> None:
        """Test that ResourceGroup can perform update operations as a Crud instance."""
        # Arrange
        group = ConcreteResourceGroup(mock_client)
        resource_id = "123"
        # Include id in the data to avoid validation error
        data = {"id": 123, "name": "Updated Resource"}
        mock_client.put.return_value = {"id": 123, "name": "Updated Resource"}

        # Act
        result = group.update(resource_id=resource_id, data=data)

        # Assert
        # Check that the client was called with the correct path
        mock_client.put.assert_called_once()
        args, kwargs = mock_client.put.call_args
        assert args[0] == "test-group/123"
        assert isinstance(result, ResourceTestModel)
        assert result.id == 123
        assert result.name == "Updated Resource"

    def test_crud_destroy_operation(self, mock_client: MagicMock) -> None:
        """Test that ResourceGroup can perform destroy operations as a Crud instance."""
        # Arrange
        group = ConcreteResourceGroup(mock_client)
        resource_id = "123"

        # Act
        result = group.destroy(resource_id=resource_id)

        # Assert
        # Check that the client was called with the correct path
        mock_client.delete.assert_called_once()
        args, kwargs = mock_client.delete.call_args
        assert args[0] == "test-group/123"
        assert result is None


class TestResourceGroupChildRegistration:
    """Tests for ResourceGroup child registration and pathing."""

    def test_child_crud_registration(self, mock_client: MagicMock) -> None:
        """Test that child Crud instances are registered correctly."""
        # Arrange & Act
        parent_group = ConcreteParentGroup(mock_client)

        # Assert
        assert hasattr(parent_group, "child_crud")
        assert isinstance(parent_group.child_crud, ConcreteChildCrud)
        assert parent_group.child_crud.parent is parent_group

    def test_child_group_registration(self, mock_client: MagicMock) -> None:
        """Test that child ResourceGroup instances are registered correctly."""
        # Arrange & Act
        parent_group = ConcreteParentGroup(mock_client)

        # Assert
        assert hasattr(parent_group, "child_group")
        assert isinstance(parent_group.child_group, ConcreteChildGroup)
        assert parent_group.child_group.parent is parent_group

    def test_nested_path_construction(self, mock_client: MagicMock) -> None:
        """Test path construction for nested resources."""
        # Arrange
        parent_group = ConcreteParentGroup(mock_client)

        # Set up mock responses for list operations
        mock_client.get.side_effect = [
            [{"id": 1, "name": "Child Resource"}],  # For child_crud.list()
            [{"id": 2, "name": "Child Group"}],  # For child_group.list()
            [{"id": 3, "name": "Nested Resource"}],  # For nested_resource.list()
        ]

        # Act - Call methods that trigger _get_endpoint
        parent_group.child_crud.list()
        parent_group.child_group.list()
        parent_group.child_group.nested_resource.list()

        # Check that the client was called with the correct paths
        assert mock_client.get.call_count == 3

        # Extract all call arguments
        call_args_list = mock_client.get.call_args_list
        paths = [args[0] for args, _ in call_args_list]

        # Check that the expected paths were called
        assert "parent-group/child-resources" in paths
        assert "parent-group/child-group" in paths
        assert "parent-group/child-group/child-resources" in paths

    def test_deep_nesting_path_construction(self, mock_client: MagicMock) -> None:
        """Test path construction for deeply nested resources."""
        # Arrange - Create a deeper nesting structure
        top_group = ConcreteParentGroup(mock_client)

        # Set up mock response for read operation
        mock_client.get.return_value = {"id": 456, "name": "Nested Resource Item"}

        # Act - Call a method on the most deeply nested resource
        result = top_group.child_group.nested_resource.read(resource_id="456")

        # Assert - Check the result and that the client was called with the correct path
        assert isinstance(result, ResourceTestModel)
        assert result.id == 456
        assert result.name == "Nested Resource Item"

        mock_client.get.assert_called_once()
        args, kwargs = mock_client.get.call_args
        assert args[0] == "parent-group/child-group/child-resources/456"

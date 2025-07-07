"""
Unit tests for endpoint_builder builder module.
"""

from unittest.mock import Mock
from crudclient.utils.endpoint_builder.builder import EndpointBuilder


class TestEndpointBuilder:
    """Test the EndpointBuilder class."""

    def test_init_minimal(self):
        """Test EndpointBuilder initialization with minimal arguments."""
        builder = EndpointBuilder(resource_path="items")
        assert builder.resource_path == "items"
        assert builder.parent_builder is None
        assert builder._endpoint_prefix is None

    def test_init_with_parent(self):
        """Test EndpointBuilder initialization with a parent builder."""
        parent_builder = Mock()
        builder = EndpointBuilder(resource_path="items", parent_builder=parent_builder)
        assert builder.resource_path == "items"
        assert builder.parent_builder == parent_builder
        assert builder._endpoint_prefix is None

    def test_init_with_endpoint_prefix(self):
        """Test EndpointBuilder initialization with endpoint prefix."""
        builder = EndpointBuilder(resource_path="items", endpoint_prefix="/api/v1")
        assert builder.resource_path == "items"
        assert builder.parent_builder is None
        assert builder._endpoint_prefix == "/api/v1"

    def test_build_endpoint_simple(self):
        """Test building a simple endpoint without args."""
        builder = EndpointBuilder(resource_path="items")
        endpoint = builder.build_endpoint()
        assert endpoint == "items"

    def test_build_endpoint_with_id(self):
        """Test building an endpoint with a resource ID."""
        builder = EndpointBuilder(resource_path="items")
        endpoint = builder.build_endpoint(123)
        assert endpoint == "items/123"

    def test_build_endpoint_with_multiple_args(self):
        """Test building an endpoint with multiple arguments."""
        builder = EndpointBuilder(resource_path="items")
        endpoint = builder.build_endpoint(123, "details", "info")
        assert endpoint == "items/123/details/info"

    def test_build_endpoint_with_parent(self):
        """Test building an endpoint with a parent builder."""
        parent_builder = Mock()
        parent_builder.resource_path = "users"
        parent_builder.parent_builder = None
        parent_builder.get_parent_path.return_value = None
        parent_builder.get_prefix_segments.return_value = []
        parent_builder.build_endpoint.return_value = "/users/123"
        parent_builder._get_endpoint_prefix.return_value = None

        child_builder = EndpointBuilder(resource_path="items", parent_builder=parent_builder)
        endpoint = child_builder.build_endpoint(456, parent_args=[123])
        assert endpoint == "users/123/items/456"

    def test_build_endpoint_with_nested_parents(self):
        """Test building an endpoint with nested parent builders."""
        grandparent_builder = Mock()
        grandparent_builder.resource_path = "organizations"
        grandparent_builder.parent_builder = None
        grandparent_builder.get_parent_path.return_value = None
        grandparent_builder.get_prefix_segments.return_value = []
        grandparent_builder.build_endpoint.return_value = "/organizations/1"
        grandparent_builder._get_endpoint_prefix.return_value = None

        parent_builder = Mock()
        parent_builder.resource_path = "users"
        parent_builder.parent_builder = grandparent_builder
        parent_builder.get_parent_path.return_value = "/organizations/1"
        parent_builder.get_prefix_segments.return_value = []
        parent_builder.build_endpoint.return_value = "/organizations/1/users/123"
        parent_builder._get_endpoint_prefix.return_value = None

        child_builder = EndpointBuilder(resource_path="items", parent_builder=parent_builder)
        endpoint = child_builder.build_endpoint(456, parent_args=[123, 1])
        assert endpoint == "organizations/1/users/123/items/456"

    def test_build_endpoint_with_prefix(self):
        """Test building an endpoint with endpoint prefix."""
        builder = EndpointBuilder(resource_path="items", endpoint_prefix="/api/v2")
        endpoint = builder.build_endpoint(123)
        assert endpoint == "api/v2/items/123"

    def test_get_parent_path_no_parent(self):
        """Test get_parent_path with no parent builder."""
        builder = EndpointBuilder(resource_path="items")
        assert builder.get_parent_path() is None

    def test_get_parent_path_with_parent(self):
        """Test get_parent_path with a parent builder."""
        parent_builder = Mock()
        parent_builder.resource_path = "users"
        parent_builder.parent_builder = None
        parent_builder.get_parent_path.return_value = None
        parent_builder.get_prefix_segments.return_value = []
        parent_builder.build_endpoint.return_value = "/users/123"
        parent_builder._get_endpoint_prefix.return_value = None

        child_builder = EndpointBuilder(resource_path="items", parent_builder=parent_builder)
        parent_path = child_builder.get_parent_path([123])
        assert parent_path == "/users/123"

    def test_get_prefix_segments_no_prefix(self):
        """Test get_prefix_segments with no endpoint prefix."""
        builder = EndpointBuilder(resource_path="items")
        segments = builder.get_prefix_segments()
        assert segments == []

    def test_get_prefix_segments_with_prefix(self):
        """Test get_prefix_segments with endpoint prefix."""
        builder = EndpointBuilder(resource_path="items", endpoint_prefix="/api/v1")
        segments = builder.get_prefix_segments()
        assert segments == ["api", "v1"]

    def test_get_prefix_segments_with_empty_prefix(self):
        """Test get_prefix_segments with empty endpoint prefix."""
        builder = EndpointBuilder(resource_path="items", endpoint_prefix="")
        segments = builder.get_prefix_segments()
        assert segments == []

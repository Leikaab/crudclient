"""
Fixtures related to creating various mock clients for testing.
"""

from typing import Any, Callable, Dict, List, Optional, Union

import pytest
from pytest import FixtureRequest

from crudclient.config import ClientConfig
from crudclient.testing.core.client import MockClient
from crudclient.testing.core.http_client import MockHTTPClient  # Added import
from crudclient.testing.response_builder import ResponseBuilder
from crudclient.testing.response_builder.basic import BasicResponseBuilder


@pytest.fixture
def create_mock_client(create_mock_client_config: Callable[..., ClientConfig]) -> Callable[..., MockClient]:
    """
    Factory fixture to create a mock client with enhanced capabilities.

    This fixture provides a factory function that creates a MockClient instance
    with configurable behavior for testing.
    """

    def _factory(
        config: Optional[Union[ClientConfig, Dict[str, Any]]] = None,
        response_patterns: Optional[List[Dict[str, Any]]] = None,
        network_conditions: Optional[Dict[str, Any]] = None,
        rate_limit: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> MockClient:
        # Use provided config or create a default one
        if isinstance(config, ClientConfig):
            client_config = config
        elif isinstance(config, dict):
            client_config = create_mock_client_config(**config)
        else:
            client_config = create_mock_client_config(**kwargs.get("config_options", {}))

        # Ensure hostname is set in the config object itself, even if overridden with None
        # This prevents errors when accessing client.config.base_url later.
        if client_config.hostname is None:
            client_config.hostname = "https://api.example.com"  # Use a sensible default

        # Create the mock HTTP client and the main mock client
        # Provide a default hostname if None
        base_url = client_config.hostname  # Should always have a value now
        http_client = MockHTTPClient(base_url=base_url)
        client = MockClient(http_client=http_client, base_url=base_url)
        client.config = client_config  # Assign the full config

        # Configure response patterns
        if response_patterns:
            for pattern in response_patterns:
                client.with_response_pattern(**pattern)

        # Configure network conditions
        if network_conditions:
            client.with_network_condition(**network_conditions)

        # Configure rate limiting
        if rate_limit:
            client.with_rate_limiter(**rate_limit)

        return client

    return _factory


@pytest.fixture
def mock_client(request: FixtureRequest) -> MockClient:
    """
    Provides a pre-configured mock client for testing.

    This fixture creates a MockClient with default configuration for use in tests.
    """
    config = ClientConfig(hostname="https://api.example.com", version="v1")
    # Provide a default hostname if None (though unlikely here as it's set explicitly)
    base_url = config.hostname or "https://api.example.com"
    http_client = MockHTTPClient(base_url=base_url)
    client = MockClient(http_client=http_client, base_url=base_url)
    client.config = config  # Assign the full config
    return client


@pytest.fixture
def rest_mock_client() -> MockClient:
    """
    Provides a mock client pre-configured for REST API testing.

    This fixture creates a MockClient with REST API patterns for common resources.
    """
    resources = {
        "users": {
            "base_path": "/users",
            "list_response": [{"id": 1, "name": "User 1"}, {"id": 2, "name": "User 2"}],
            "get_response": {"id": 1, "name": "User 1", "email": "user1@example.com"},
            "create_response": {"id": 3, "name": "New User", "created": True},
            "update_response": {"id": 1, "name": "Updated User", "updated": True},
            "delete_response": {"success": True},
        },
        "posts": {
            "base_path": "/posts",
            "list_response": [{"id": 1, "title": "Post 1", "user_id": 1}, {"id": 2, "title": "Post 2", "user_id": 2}],
            "get_response": {"id": 1, "title": "Post 1", "content": "Content here", "user_id": 1},
            "create_response": {"id": 3, "title": "New Post", "created": True},
            "update_response": {"id": 1, "title": "Updated Post", "updated": True},
            "delete_response": {"success": True},
        },
    }

    # Create a default config
    config = ClientConfig(hostname="https://api.example.com", version="v1")
    # Provide a default hostname if None (though unlikely here as it's set explicitly)
    base_url = config.hostname or "https://api.example.com"
    http_client = MockHTTPClient(base_url=base_url)
    client = MockClient(http_client=http_client, base_url=base_url)
    client.config = config  # Assign the full config

    # Configure REST resources
    for resource_name, resource_config in resources.items():
        base_path = resource_config.get("base_path", resource_name)

        # List endpoint
        if "list_response" in resource_config:
            client.with_response_pattern(method="GET", path_pattern=f"{base_path}$", data=resource_config["list_response"])  # type: ignore[arg-type]

        # Get endpoint
        if "get_response" in resource_config:
            client.with_response_pattern(
                method="GET", path_pattern=f"{base_path}/\\d+$", data=resource_config["get_response"]  # type: ignore[arg-type]
            )

        # Create endpoint
        if "create_response" in resource_config:
            client.with_response_pattern(
                method="POST", path_pattern=f"{base_path}$", data=resource_config["create_response"]  # type: ignore[arg-type]
            )

        # Update endpoint
        if "update_response" in resource_config:
            client.with_response_pattern(
                method="PUT", path_pattern=f"{base_path}/\\d+$", data=resource_config["update_response"]  # type: ignore[arg-type]
            )

        # Delete endpoint
        if "delete_response" in resource_config:
            client.with_response_pattern(
                method="DELETE", path_pattern=f"{base_path}/\\d+$", data=resource_config["delete_response"]  # type: ignore[arg-type]
            )

    # Add error responses
    # Validation error
    client.with_response_pattern(
        method="POST",
        path_pattern=r".*",
        data=ResponseBuilder.create_validation_error(  # Extract body from MockResponse
            fields={"name": "Name is required", "email": "Invalid email format"},
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Validation failed",
        ).json(),  # Assuming .json() gets the body dict
        status_code=422,
    )

    # Auth error
    client.with_response_pattern(
        method="GET",
        path_pattern=r".*",
        data=ResponseBuilder.create_auth_error(  # Extract body from MockResponse
            error_type="invalid_token", status_code=401
        ).json(),  # Assuming .json() gets the body dict
        status_code=401,
    )

    # Rate limit error
    client.with_response_pattern(
        method="GET",
        path_pattern=r".*",
        data=ResponseBuilder.create_rate_limit_error(  # Extract body from MockResponse
            limit=100, remaining=0, reset_seconds=60
        ).json(),  # Assuming .json() gets the body dict
        status_code=429,
    )

    return client


@pytest.fixture
def graphql_mock_client() -> MockClient:
    """
    Provides a mock client pre-configured for GraphQL API testing.

    This fixture creates a MockClient with GraphQL API patterns.
    """
    # Create a default config
    config = ClientConfig(hostname="https://api.example.com", version="v1")
    # Provide a default hostname if None (though unlikely here as it's set explicitly)
    base_url = config.hostname or "https://api.example.com"
    http_client = MockHTTPClient(base_url=base_url)
    client = MockClient(http_client=http_client, base_url=base_url)
    client.config = config  # Assign the full config

    # Add GraphQL query patterns
    client.with_response_pattern(
        method="POST",
        path_pattern=r"/graphql$",
        data=BasicResponseBuilder.create_graphql_response(  # Extract body from MockResponse
            data={"users": [{"id": "1", "name": "User 1", "email": "user1@example.com"}, {"id": "2", "name": "User 2", "email": "user2@example.com"}]}
        ).json(),  # Assuming .json() gets the body dict
    )

    client.with_response_pattern(
        method="POST",
        path_pattern=r"/graphql$",
        data=BasicResponseBuilder.create_graphql_response(  # Extract body from MockResponse
            data={
                "user": {
                    "id": "1",
                    "name": "User 1",
                    "email": "user1@example.com",
                    "posts": [{"id": "1", "title": "Post 1"}, {"id": "2", "title": "Post 2"}],
                }
            }
        ).json(),  # Assuming .json() gets the body dict
    )

    client.with_response_pattern(
        method="POST",
        path_pattern=r"/graphql$",
        data=BasicResponseBuilder.create_graphql_response(  # Extract body from MockResponse
            data={"createUser": {"id": "3", "name": "New User", "email": "newuser@example.com"}}
        ).json(),  # Assuming .json() gets the body dict
    )

    # Default response for unmatched GraphQL queries
    client.with_response_pattern(
        method="POST",
        path_pattern=r"/graphql$",
        data=BasicResponseBuilder.create_graphql_response(  # Extract body from MockResponse
            errors=[{"message": "Unknown query", "locations": [{"line": 1, "column": 1}], "path": ["query"]}]
        ).json(),  # Assuming .json() gets the body dict
        status_code=400,
    )

    return client

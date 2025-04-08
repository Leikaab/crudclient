"""
Fixtures specific to unit tests.
"""

import uuid
from typing import Any, Callable, Dict, List, Optional, Type, Union

import pytest
from unittest.mock import MagicMock
import requests_mock

from crudclient.auth.base import AuthStrategy
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import CustomAuth
from crudclient.config import ClientConfig
from crudclient.exceptions import APIError

from tests.unit.mock_client import (
    MockClient, MockResponse, SimpleMockClient,
    APIPatternBuilder, ResponseBuilder, RequestVerifier, ResponseVerifier
)
from tests.unit.mock_client.factory import create_mock_client, create_simple_mock_client

# --- Authentication Strategy Fixtures ---


@pytest.fixture
def bearer_auth_strategy() -> BearerAuth:
    """Provides a BearerAuth strategy instance."""
    return BearerAuth(token="test-bearer-token")


@pytest.fixture
def basic_auth_strategy() -> BasicAuth:
    """Provides a BasicAuth strategy instance."""
    return BasicAuth(username="testuser", password="testpassword")


@pytest.fixture
def custom_auth_strategy() -> CustomAuth:
    """Provides a CustomAuth strategy instance with a header callback."""
    def _get_custom_headers() -> Dict[str, str]:
        return {"X-Custom-Auth": "custom-value", "X-Another-Header": "another-value"}

    return CustomAuth(header_callback=_get_custom_headers)


# --- Client Configuration Factory ---

@pytest.fixture
def create_mock_client_config(bearer_auth_strategy: BearerAuth) -> Callable[..., ClientConfig]:
    """
    Factory fixture to create a mock ClientConfig instance.
    Allows customization for different test scenarios.
    """
    def _factory(
        hostname: str = "https://api.example.com",
        version: str = "v1",
        api_key: Optional[str] = "default-key",  # Retained for potential direct use if needed
        auth_strategy: Optional[AuthStrategy] = None,
        headers: Optional[Dict[str, str]] = None,
        retries: int = 3,
        timeout: int = 10,
        **kwargs: Any
    ) -> ClientConfig:
        config = ClientConfig()
        config.hostname = hostname
        config.version = version
        config.api_key = api_key  # Store it, though auth_strategy is preferred
        config.auth_strategy = auth_strategy if auth_strategy is not None else bearer_auth_strategy  # Default to Bearer
        config.headers = headers if headers is not None else {"User-Agent": "crudclient-test"}
        config.retries = retries
        config.timeout = timeout

        # Allow overriding any other ClientConfig attributes via kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                # Optionally raise an error for unknown kwargs or just ignore
                # raise AttributeError(f"ClientConfig has no attribute '{key}'")
                pass  # Ignoring unknown kwargs for flexibility

        return config
    return _factory


@pytest.fixture
def default_mock_client_config(create_mock_client_config: Callable[..., ClientConfig]) -> ClientConfig:
    """Provides a default mock client configuration instance."""
    return create_mock_client_config()


@pytest.fixture
def requests_mocker():
    """Provide a requests mocker for HTTP request mocking."""
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def create_user_data():
    """Factory fixture to create user test data."""
    """Factory fixture to create user test data with unique IDs."""
    _id_counter = 1

    def _create(id: Optional[int] = None, name: str = "Test User", email: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        nonlocal _id_counter
        user_id = id if id is not None else _id_counter
        user_email = email if email is not None else f"test{user_id}@example.com"
        if id is None:
            _id_counter += 1
        return {
            "id": user_id,
            "name": f"{name} {user_id}",
            "email": user_email,
            "uuid": str(uuid.uuid4()),  # Add a unique identifier
            **kwargs
        }
    return _create


@pytest.fixture
def create_api_response():
    """Factory fixture to create API response data."""
    """
    Factory fixture to create versatile API response data for requests_mock.

    Allows specifying status code, data payload, metadata, links, and error details.
    """
    def _create(
        status_code: int = 200,
        data: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
        links: Optional[Dict[str, str]] = None,
        error: Optional[Dict[str, Any]] = None,
        data_key: str = "data",  # Key under which main data is nested
        headers: Optional[Dict[str, str]] = None,
        raw_content: Optional[bytes] = None,  # For non-JSON responses
        content_type: str = "application/json"  # Default content type
    ) -> Dict[str, Any]:

        response_config: Dict[str, Any] = {
            "status_code": status_code,
            "headers": headers if headers is not None else {"Content-Type": content_type}
        }

        if raw_content is not None:
            response_config["content"] = raw_content
            # Ensure content-type reflects raw content if not JSON
            if "json" not in content_type.lower():
                response_config["headers"]["Content-Type"] = content_type
            return response_config  # Raw content overrides JSON structure

        # Build JSON body if no raw content
        json_body: Dict[str, Any] = {}

        if data is not None:
            json_body[data_key] = data
        if metadata is not None:
            json_body["metadata"] = metadata
        if links is not None:
            json_body["links"] = links
        if error is not None:
            # Ensure error structure doesn't overwrite data if both are somehow provided
            # (though typically only one would be present in a real response)
            if data_key in json_body and "error" == data_key:
                # Avoid key collision if data_key happens to be 'error'
                json_body["_error_details"] = error  # Use a different key
            else:
                json_body["error"] = error

        if json_body:  # Only add json key if there's content
            response_config["json"] = json_body
        elif status_code >= 400 and not error:
            # Add a default error structure for error status codes if none provided
            response_config["json"] = {"error": {"message": "Default error message", "code": f"ERR_{status_code}"}}
        elif status_code < 400 and not data and not metadata and not links:
            # For success codes with no body (e.g., 204 No Content), don't add 'json'
            pass

        return response_config
    return _create


@pytest.fixture
def create_paginated_api_response(create_api_response: Callable[..., Dict[str, Any]]) -> Callable[..., Dict[str, Any]]:
    """Factory fixture specifically for creating paginated API responses."""
    def _create(
        items: list,
        page: int = 1,
        per_page: int = 10,
        total_items: Optional[int] = None,
        total_pages: Optional[int] = None,
        base_url: str = "https://api.example.com/v1/items",
        **kwargs: Any  # Pass other args to create_api_response
    ) -> Dict[str, Any]:
        _total_items = total_items if total_items is not None else len(items) * (total_pages if total_pages else page + 1)  # Estimate if needed
        _total_pages = total_pages if total_pages is not None else (_total_items + per_page - 1) // per_page

        metadata = {
            "pagination": {
                "currentPage": page,
                "perPage": per_page,
                "totalItems": _total_items,
                "totalPages": _total_pages,
            }
        }
        links = {
            "self": f"{base_url}?page={page}&per_page={per_page}",
            "first": f"{base_url}?page=1&per_page={per_page}",
            "last": f"{base_url}?page={_total_pages}&per_page={per_page}",
        }
        if page > 1:
            links["prev"] = f"{base_url}?page={page - 1}&per_page={per_page}"
        if page < _total_pages:
            links["next"] = f"{base_url}?page={page + 1}&per_page={per_page}"

        # Ensure status_code defaults to 200 if not provided in kwargs
        if 'status_code' not in kwargs:
            kwargs['status_code'] = 200

        return create_api_response(data=items, metadata=metadata, links=links, **kwargs)
    return _create


@pytest.fixture
def create_error_api_response(create_api_response: Callable[..., Dict[str, Any]]) -> Callable[..., Dict[str, Any]]:
    """Factory fixture for creating structured error API responses."""
    def _create(
        status_code: int = 400,
        message: str = "Bad Request",
        error_code: Optional[str] = None,
        details: Optional[Any] = None,
        **kwargs: Any  # Pass other args to create_api_response
    ) -> Dict[str, Any]:
        error_payload = {
            "message": message,
            "code": error_code or f"ERR_{status_code}",
        }
        if details is not None:
            error_payload["details"] = details

        # Ensure data_key is not 'error' to avoid conflicts if user passes it
        if 'data_key' in kwargs and kwargs['data_key'] == 'error':
            del kwargs['data_key']

        return create_api_response(status_code=status_code, error=error_payload, **kwargs)
    return _create


@pytest.fixture
def mock_api_error() -> Type[APIError]:
    """Provides the APIError exception class for testing."""
    return APIError


# --- Enhanced Mock Client Fixtures ---
@pytest.fixture
def api_pattern_builder():
    """
    Provides the APIPatternBuilder class for creating API patterns.
    """
    return APIPatternBuilder


@pytest.fixture
def response_builder():
    """
    Provides the ResponseBuilder class for creating complex responses.
    """
    return ResponseBuilder


@pytest.fixture
def request_verifier():
    """
    Provides the RequestVerifier class for verifying API requests.
    """
    return RequestVerifier


@pytest.fixture
def response_verifier():
    """
    Provides the ResponseVerifier class for verifying API responses.
    """
    return ResponseVerifier
    return ResponseVerifier


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
        **kwargs: Any
    ) -> MockClient:
        # Use provided config or create a default one
        client_config = config or create_mock_client_config(**kwargs.get('config_options', {}))

        # Create the mock client
        client = MockClient(client_config)

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
def simple_mock_client(request) -> SimpleMockClient:
    """
    Provides a simple mock client for testing.

    This fixture creates a SimpleMockClient instance for use in tests.
    The SimpleMockClient is a lightweight alternative to MockClient that
    doesn't inherit from the real Client class, making it more reliable
    for testing.
    """
    return SimpleMockClient()


@pytest.fixture
def mock_client(request) -> MockClient:
    """
    Provides a pre-configured mock client for testing.

    This fixture creates a MockClient with default configuration for use in tests.
    """
    config = ClientConfig(hostname="https://api.example.com", version="v1")
    return MockClient(config)


@pytest.fixture
def create_mock_response() -> Callable[..., MockResponse]:
    """
    Factory fixture to create mock responses.

    This fixture provides a factory function that creates MockResponse instances
    with configurable properties for testing.
    """
    def _factory(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        content: Optional[bytes] = None,
        error: Optional[Exception] = None,
    ) -> MockResponse:
        return MockResponse(
            status_code=status_code,
            json_data=json_data,
            text=text,
            headers=headers,
            content=content,
            error=error
        )

    return _factory


@pytest.fixture
def rest_mock_client() -> MockClient:
    """
    Provides a mock client pre-configured for REST API testing.

    This fixture creates a MockClient with REST API patterns for common resources.
    """
    resources = {
        'users': {
            'base_path': '/users',
            'list_response': [
                {'id': 1, 'name': 'User 1'},
                {'id': 2, 'name': 'User 2'}
            ],
            'get_response': {'id': 1, 'name': 'User 1', 'email': 'user1@example.com'},
            'create_response': {'id': 3, 'name': 'New User', 'created': True},
            'update_response': {'id': 1, 'name': 'Updated User', 'updated': True},
            'delete_response': {'success': True}
        },
        'posts': {
            'base_path': '/posts',
            'list_response': [
                {'id': 1, 'title': 'Post 1', 'user_id': 1},
                {'id': 2, 'title': 'Post 2', 'user_id': 2}
            ],
            'get_response': {'id': 1, 'title': 'Post 1', 'content': 'Content here', 'user_id': 1},
            'create_response': {'id': 3, 'title': 'New Post', 'created': True},
            'update_response': {'id': 1, 'title': 'Updated Post', 'updated': True},
            'delete_response': {'success': True}
        }
    }

    # Create a default config
    config = ClientConfig(hostname="https://api.example.com", version="v1")
    client = MockClient(config)

    # Configure REST resources
    for resource_name, resource_config in resources.items():
        base_path = resource_config.get('base_path', resource_name)

        # List endpoint
        if 'list_response' in resource_config:
            client.with_response_pattern(
                method="GET",
                url_pattern=f"{base_path}$",
                response=resource_config['list_response']
            )

        # Get endpoint
        if 'get_response' in resource_config:
            client.with_response_pattern(
                method="GET",
                url_pattern=f"{base_path}/\\d+$",
                response=resource_config['get_response']
            )

        # Create endpoint
        if 'create_response' in resource_config:
            client.with_response_pattern(
                method="POST",
                url_pattern=f"{base_path}$",
                response=resource_config['create_response']
            )

        # Update endpoint
        if 'update_response' in resource_config:
            client.with_response_pattern(
                method="PUT",
                url_pattern=f"{base_path}/\\d+$",
                response=resource_config['update_response']
            )

        # Delete endpoint
        if 'delete_response' in resource_config:
            client.with_response_pattern(
                method="DELETE",
                url_pattern=f"{base_path}/\\d+$",
                response=resource_config['delete_response']
            )

    # Add error responses
    # Validation error
    client.with_response_pattern(
        method="POST",
        url_pattern=r".*",
        response=ResponseBuilder.create_validation_error(
            fields={'name': 'Name is required', 'email': 'Invalid email format'},
            status_code=422,
            error_code="VALIDATION_ERROR",
            message="Validation failed"
        )
    )

    # Auth error
    client.with_response_pattern(
        method="GET",
        url_pattern=r".*",
        response=ResponseBuilder.create_auth_error(
            error_type="invalid_token",
            status_code=401
        )
    )

    # Rate limit error
    client.with_response_pattern(
        method="GET",
        url_pattern=r".*",
        response=ResponseBuilder.create_rate_limit_error(
            limit=100,
            remaining=0,
            reset_seconds=60
        )
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
    client = MockClient(config)

    # Add GraphQL query patterns
    client.with_response_pattern(
        method="POST",
        url_pattern=r"/graphql$",
        json_matcher=lambda json_data: isinstance(json_data, dict)
        and "query" in json_data
        and "GetUsers" in json_data["query"],
        response=ResponseBuilder.create_graphql_response(
            data={
                'users': [
                    {'id': '1', 'name': 'User 1', 'email': 'user1@example.com'},
                    {'id': '2', 'name': 'User 2', 'email': 'user2@example.com'}
                ]
            }
        )
    )

    client.with_response_pattern(
        method="POST",
        url_pattern=r"/graphql$",
        json_matcher=lambda json_data: isinstance(json_data, dict)
        and "query" in json_data
        and "GetUser" in json_data["query"],
        response=ResponseBuilder.create_graphql_response(
            data={
                'user': {
                    'id': '1',
                    'name': 'User 1',
                    'email': 'user1@example.com',
                    'posts': [
                        {'id': '1', 'title': 'Post 1'},
                        {'id': '2', 'title': 'Post 2'}
                    ]
                }
            }
        )
    )

    client.with_response_pattern(
        method="POST",
        url_pattern=r"/graphql$",
        json_matcher=lambda json_data: isinstance(json_data, dict)
        and "mutation" in json_data.get("query", "")
        and "CreateUser" in json_data.get("query", ""),
        response=ResponseBuilder.create_graphql_response(
            data={
                'createUser': {
                    'id': '3',
                    'name': 'New User',
                    'email': 'newuser@example.com'
                }
            }
        )
    )

    # Default response for unmatched GraphQL queries
    client.with_response_pattern(
        method="POST",
        url_pattern=r"/graphql$",
        response=ResponseBuilder.create_graphql_response(
            errors=[{
                'message': 'Unknown query',
                'locations': [{'line': 1, 'column': 1}],
                'path': ['query']
            }]
        )
    )

    return client

"""
Fixtures specific to unit tests.
"""

import uuid
from typing import Any, Callable, Dict, Optional, Type
from unittest.mock import MagicMock  # Add MagicMock import

import pytest
import requests_mock

from crudclient.auth import AuthStrategy, BasicAuth, BearerAuth, CustomAuth
from crudclient.config import ClientConfig
from crudclient.exceptions import APIError
from crudclient.testing.response_builder import ResponseBuilder
from crudclient.testing.response_builder.api_patterns import APIPatternBuilder
from crudclient.testing.response_builder.response import MockResponse
from crudclient.testing.verification import Verifier

# Make fixtures from other files available

# Update import paths to match the actual module structure

# --- Authentication Strategy Fixtures ---


@pytest.fixture
def bearer_auth_strategy() -> BearerAuth:
    """Provides a BearerAuth strategy instance."""
    return BearerAuth(access_token="test-bearer-token")


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
        **kwargs: Any,
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
def valid_config(create_mock_client_config: Callable[..., ClientConfig]) -> ClientConfig:
    """Provides a standard, valid ClientConfig instance."""
    return create_mock_client_config()


@pytest.fixture
def mock_client_config() -> MagicMock:
    """Fixture for a mocked ClientConfig, available to all unit tests."""
    config = MagicMock(spec=ClientConfig)
    config.base_url = "http://test.com"
    config.log_request_body = False
    config.log_response_body = False
    # Configure auth_strategy behavior to prevent TypeError
    config.auth_strategy = MagicMock()
    config.auth_strategy.prepare_request_params.return_value = {}
    # Add other config defaults if needed
    return config


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
        return {"id": user_id, "name": f"{name} {user_id}", "email": user_email, "uuid": str(uuid.uuid4()), **kwargs}  # Add a unique identifier

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
        content_type: str = "application/json",  # Default content type
    ) -> Dict[str, Any]:

        response_config: Dict[str, Any] = {"status_code": status_code, "headers": headers if headers is not None else {"Content-Type": content_type}}

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
        **kwargs: Any,  # Pass other args to create_api_response
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
        if "status_code" not in kwargs:
            kwargs["status_code"] = 200

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
        **kwargs: Any,  # Pass other args to create_api_response
    ) -> Dict[str, Any]:
        error_payload = {
            "message": message,
            "code": error_code or f"ERR_{status_code}",
        }
        if details is not None:
            error_payload["details"] = details

        # Ensure data_key is not 'error' to avoid conflicts if user passes it
        if "data_key" in kwargs and kwargs["data_key"] == "error":
            del kwargs["data_key"]

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
    return Verifier


@pytest.fixture
def response_verifier():
    """
    Provides the ResponseVerifier class for verifying API responses.
    """
    return Verifier


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
            # Removed invalid 'content' and 'error' parameters
        )

    return _factory

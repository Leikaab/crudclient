"""
Testing utilities for the crudclient library.

This module provides a framework for creating test doubles (mocks, stubs, fakes, spies)
for the crudclient library components (Client, API, CRUD, Auth, HTTPClient).
"""

from .auth import (
    ApiKeyAuthMock,
    AuthMockBase,
    AuthVerificationHelpers,
    BasicAuthMock,
    BearerAuthMock,
    CustomAuthMock,
    OAuthMock,
    create_api_key_auth_mock,
    create_basic_auth_mock,
    create_bearer_auth_mock,
    create_custom_auth_mock,
    create_oauth_mock,
)
from .core.client import MockClient
from .core.http_client import MockHTTPClient
from .doubles import DataStore, FakeAPI
from .exceptions import (
    AuthStrategyError,
    CRUDOperationError,
    DataStoreError,
    MockConfigurationError,
    RequestNotConfiguredError,
    ResourceNotFoundError,
    SpyError,
    TestingError,
    VerificationError,
)
from .factory import MockClientFactory
from .response_builder import ResponseBuilder
from .response_builder.api_patterns import APIPatternBuilder
from .response_builder.response import MockResponse
from .simple_mock import SimpleMockClient
from .spy import MethodCall, SpyBase
from .verification import Verifier

class RequestVerifier:
    """Placeholder for RequestVerifier class referenced in tests."""

    ...

class ResponseVerifier:
    """Placeholder for ResponseVerifier class referenced in tests."""

    ...

__all__ = [
    # Main classes
    "MockClient",
    "MockHTTPClient",
    "MockClientFactory",
    "Verifier",
    "FakeAPI",
    "DataStore",
    "MethodCall",
    "SpyBase",
    "MockResponse",
    "SimpleMockClient",
    "APIPatternBuilder",
    "ResponseBuilder",
    "RequestVerifier",
    "ResponseVerifier",
    # Auth mocks
    "ApiKeyAuthMock",
    "AuthMockBase",
    "AuthVerificationHelpers",
    "BasicAuthMock",
    "BearerAuthMock",
    "CustomAuthMock",
    "OAuthMock",
    "create_api_key_auth_mock",
    "create_basic_auth_mock",
    "create_bearer_auth_mock",
    "create_custom_auth_mock",
    "create_oauth_mock",
    # Exceptions
    "TestingError",
    "MockConfigurationError",
    "VerificationError",
    "RequestNotConfiguredError",
    "AuthStrategyError",
    "CRUDOperationError",
    "DataStoreError",
    "ResourceNotFoundError",
    "SpyError",
]

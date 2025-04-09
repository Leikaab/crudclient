"""
Testing utilities for the crudclient library.

This module provides a framework for creating test doubles (mocks, stubs, fakes, spies)
for the crudclient library components (Client, API, CRUD, Auth, HTTPClient).
"""
# Import directly from the module file
from .exceptions import (
    TestingError,
    MockConfigurationError,
    VerificationError,
    RequestNotConfiguredError,
    AuthStrategyError,
    CRUDOperationError,
    DataStoreError,
    ResourceNotFoundError,
    SpyError,
)
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
from .spy import MethodCall, SpyBase
from .doubles import FakeAPI, DataStore
from .verification import Verifier
from .core.http_client import MockHTTPClient
from .core.client import MockClient
from .factory import MockClientFactory  # Import from factory.py file
from .response_builder.response import MockResponse  # Import MockResponse from response_builder
from .simple_mock import SimpleMockClient  # Import SimpleMockClient
from .response_builder.api_patterns import APIPatternBuilder  # Import APIPatternBuilder
from .response_builder import ResponseBuilder  # Import ResponseBuilder

# These classes are referenced in tests but don't seem to exist in the codebase
# Defining placeholder classes to avoid import errors


class RequestVerifier:
    """Placeholder for RequestVerifier class referenced in tests."""
    pass


class ResponseVerifier:
    """Placeholder for ResponseVerifier class referenced in tests."""
    pass


__all__ = [
    # Main classes
    'MockClient',
    'MockHTTPClient',
    'MockClientFactory',
    'Verifier',
    'FakeAPI',
    'DataStore',
    'MethodCall',
    'SpyBase',
    'MockResponse',
    'SimpleMockClient',
    'APIPatternBuilder',
    'ResponseBuilder',
    'RequestVerifier',
    'ResponseVerifier',

    # Auth mocks
    'ApiKeyAuthMock',
    'AuthMockBase',
    'AuthVerificationHelpers',
    'BasicAuthMock',
    'BearerAuthMock',
    'CustomAuthMock',
    'OAuthMock',
    'create_api_key_auth_mock',
    'create_basic_auth_mock',
    'create_bearer_auth_mock',
    'create_custom_auth_mock',
    'create_oauth_mock',

    # Exceptions
    'TestingError',
    'MockConfigurationError',
    'VerificationError',
    'RequestNotConfiguredError',
    'AuthStrategyError',
    'CRUDOperationError',
    'DataStoreError',
    'ResourceNotFoundError',
    'SpyError',
]

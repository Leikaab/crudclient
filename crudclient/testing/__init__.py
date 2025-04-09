"""
Testing utilities for the crudclient library.

This module provides a framework for creating test doubles (mocks, stubs, fakes, spies)
for the crudclient library components (Client, API, CRUD, Auth, HTTPClient).
"""

# from .factory import MockClientFactory  # Import from factory.py file
from .core.client import MockClient
from .core.http_client import MockHTTPClient
from .verification import Verifier
from .doubles import FakeAPI, DataStore
from .spy import MethodCall, SpyBase
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

__all__ = [
    # Main classes
    'MockClient',
    'MockHTTPClient',
    # 'MockClientFactory',
    'Verifier',
    'FakeAPI',
    'DataStore',
    'MethodCall',
    'SpyBase',

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

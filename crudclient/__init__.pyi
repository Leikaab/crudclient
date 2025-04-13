"""
CrudClient Library
================

A flexible and extensible client library for interacting with RESTful APIs.

This library provides a set of classes and utilities for building API clients
that follow the CRUD (Create, Read, Update, Delete) pattern. It includes support
for authentication, error handling, and data validation.

Main Components:
    - API: Base class for creating API clients with CRUD resources.
    - Client: HTTP client for making API requests.
    - ClientConfig: Configuration for the client.
    - Crud: Base class for CRUD operations on API resources.
    - AuthStrategy: Base class for authentication strategies.

Example:
    ```python
    from crudclient import API, ClientConfig
    from crudclient.auth import BearerAuth

    class MyAPI(API):
        def _register_endpoints(self):
            self.users = UsersCrud(self.client)
            self.posts = PostsCrud(self.client)

    # Create a configuration with bearer token authentication
    config = ClientConfig(
        hostname="https://api.example.com",
        auth_strategy=BearerAuth(token="your_token")
    )

    # Initialize the API client
    api = MyAPI(client_config=config)

    # Use the API client
    users = api.users.list()
    ```
"""

from .api import API
from .client import Client
from .config import ClientConfig
from .crud import Crud
from .exceptions import (
    APIError,
    AuthenticationError,
    ClientInitializationError,
    CrudClientError,
    InvalidClientError,
    InvalidResponseError,
    ModelConversionError,
    NotFoundError,
)
from .models import ApiResponse
from .types import JSONDict, JSONList, RawResponse

__all__ = [
    "API",
    "Client",
    "ClientConfig",
    "Crud",
    "APIError",
    "InvalidClientError",
    "ClientInitializationError",
    "CrudClientError",
    "AuthenticationError",
    "NotFoundError",
    "InvalidResponseError",
    "ModelConversionError",
    "ApiResponse",
    "JSONDict",
    "JSONList",
    "RawResponse",
]

__version__: str

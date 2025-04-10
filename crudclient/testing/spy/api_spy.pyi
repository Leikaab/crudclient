"""
API spy implementation for recording and verifying API interactions.

This module provides a spy implementation of the API class that records
all method calls for later verification.
"""

from typing import Any, Optional, Type

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud.base import Crud

from .base import SpyBase


class ApiSpy(API, SpyBase):
    """
    Spy implementation of the API class.

    This class wraps an API instance and records all method calls for later verification.
    It can be used to verify that the expected methods were called with the expected
    arguments during testing.
    """

    client_class: Type[Client]
    delegate: API

    def __init__(
        self,
        client: Optional[Client] = None,
        client_config: Optional[ClientConfig] = None,
        delegate: Optional[API] = None,
        **kwargs: Any
    ):
        """
        Initialize an ApiSpy instance.

        Args:
            client: Optional client instance to use
            client_config: Optional client configuration
            delegate: Optional delegate API to forward calls to
            **kwargs: Additional keyword arguments to pass to the API constructor
        """
        ...

    def _register_endpoints(self) -> None:
        """
        Record and forward a call to _register_endpoints.

        Returns:
            Result from the delegate API

        Raises:
            Any exception raised by the delegate API
        """
        ...

    def register_endpoint(
        self,
        name: str,
        endpoint: str,
        model: Optional[Type[Any]] = None,
        **kwargs: Any
    ) -> Crud:
        """
        Record and forward a call to register_endpoint.

        Args:
            name: Name of the endpoint
            endpoint: API endpoint path
            model: Optional data model for the endpoint
            **kwargs: Additional keyword arguments

        Returns:
            Crud instance for the registered endpoint

        Raises:
            ValueError: If client is not initialized
            Any exception raised by the delegate API
        """
        ...

    def __getattr__(self, name: str) -> Any:
        """
        Record and forward attribute access to the delegate API.

        Args:
            name: Attribute name

        Returns:
            Attribute value from the delegate API

        Raises:
            Any exception raised by the delegate API
        """
        ...

    # Helper methods for verification

    def assert_endpoint_registered(self, name: str) -> None:
        """
        Assert that an endpoint was registered.

        Args:
            name: Name of the endpoint

        Raises:
            AssertionError: If the endpoint was not registered
        """
        ...

    def assert_endpoint_registered_with_model(self, name: str, model: Type[Any]) -> None:
        """
        Assert that an endpoint was registered with a specific model.

        Args:
            name: Name of the endpoint
            model: Expected model class

        Raises:
            AssertionError: If the endpoint was not registered with the specified model
        """
        ...

"""
API spy implementation for verification-focused testing.

This module provides a spy implementation of the API interface that records
all method calls for later verification in tests. It can be used to verify
that specific API methods were called with the expected arguments.
"""

from typing import Any, Optional, Type

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud.base import Crud

from .base import SpyBase


class ApiSpy(API, SpyBase):
    """
    Spy implementation of the API interface.

    This class records all method calls to the API interface for verification
    in tests, while delegating to a real or mock implementation. It can be used
    to verify that specific API methods were called with the expected arguments,
    without affecting the actual behavior of the API.

    Example:
        >>> from crudclient.testing.spy import ApiSpy
        >>> api_spy = ApiSpy()
        >>> api_spy.register_endpoint("users", "/users", User)
        >>> api_spy.assert_endpoint_registered("users")
        >>> api_spy.assert_endpoint_registered_with_model("users", User)
    """

    client_class = Client

    def __init__(
        self,
        client: Optional[Client] = None,
        client_config: Optional[ClientConfig] = None,
        delegate: Optional[API] = None,
        **kwargs: Any
    ):
        """
        Initialize the API spy.

        Args:
            client: Optional client instance to use for API requests.
                If not provided, a new client will be created using the client_config.
            client_config: Optional client configuration to use when creating a new client.
                If not provided, a default configuration will be used.
            delegate: Optional delegate API implementation to forward method calls to.
                If not provided, the parent class implementation will be used.
            **kwargs: Additional arguments to pass to the API constructor.
        """
        # Create a default client_config if none is provided
        if client_config is None:
            client_config = ClientConfig(hostname="https://example.com")

        API.__init__(self, client, client_config, **kwargs)
        SpyBase.__init__(self)

        # Create a delegate API if not provided
        self.delegate = delegate or super()

    def _register_endpoints(self) -> None:
        """
        Record and delegate _register_endpoints method call.

        This method records the call to _register_endpoints and delegates
        to the delegate implementation.

        Returns:
            None
        """
        try:
            result = self.delegate._register_endpoints()
            self._record_call('_register_endpoints', (), {}, result)
            return result
        except Exception as e:
            self._record_call('_register_endpoints', (), {}, exception=e)
            raise

    def register_endpoint(
        self,
        name: str,
        endpoint: str,
        model: Optional[Type[Any]] = None,
        **kwargs: Any
    ) -> Crud:
        """
        Record and delegate register_endpoint method call.

        This method records the call to register_endpoint with the provided
        arguments and delegates to the delegate implementation.

        Args:
            name: Name of the endpoint to register
            endpoint: API endpoint path
            model: Optional model class to use for serialization/deserialization
            **kwargs: Additional arguments to pass to the endpoint constructor

        Returns:
            CRUD interface for the registered endpoint
        """
        try:
            # If delegate is super(), we need to implement register_endpoint ourselves
            if hasattr(self.delegate, 'register_endpoint'):
                result = self.delegate.register_endpoint(name, endpoint, model, **kwargs)
            else:
                # Implement register_endpoint if not available in delegate
                # Create a Crud instance and set it as an attribute
                if self.client is None:
                    raise ValueError("Client must be initialized before registering endpoints")
                result = Crud(self.client)
                result._resource_path = endpoint
                result._datamodel = model
                setattr(self, name, result)
            self._record_call(
                'register_endpoint',
                (name, endpoint),
                {'model': model, **kwargs},
                result
            )
            return result
        except Exception as e:
            self._record_call(
                'register_endpoint',
                (name, endpoint),
                {'model': model, **kwargs},
                exception=e
            )
            raise

    def __getattr__(self, name: str) -> Any:
        """
        Record and delegate attribute access.

        This method records the call to __getattr__ with the provided
        attribute name and delegates to the delegate implementation.

        Args:
            name: Name of the attribute to access

        Returns:
            Attribute value

        Raises:
            AttributeError: If the attribute does not exist
        """
        try:
            result = getattr(self.delegate, name)
            self._record_call('__getattr__', (name,), {}, result)
            return result
        except Exception as e:
            self._record_call('__getattr__', (name,), {}, exception=e)
            raise

    # Helper methods for verification

    def assert_endpoint_registered(self, name: str) -> None:
        """
        Assert that an endpoint was registered.

        This method checks if the register_endpoint method was called
        with the specified endpoint name.

        Args:
            name: Name of the endpoint to check

        Raises:
            AssertionError: If the endpoint was not registered
        """
        for call in self.calls:
            if call.method_name == 'register_endpoint' and call.args and call.args[0] == name:
                return

        raise AssertionError(f"Endpoint {name} was not registered")

    def assert_endpoint_registered_with_model(self, name: str, model: Type[Any]) -> None:
        """
        Assert that an endpoint was registered with a specific model.

        This method checks if the register_endpoint method was called
        with the specified endpoint name and model.

        Args:
            name: Name of the endpoint to check
            model: Expected model class

        Raises:
            AssertionError: If the endpoint was not registered with the specified model
        """
        for call in self.calls:
            if (
                call.method_name == 'register_endpoint'
                and call.args and call.args[0] == name
                and 'model' in call.kwargs and call.kwargs['model'] == model
            ):
                return

        raise AssertionError(f"Endpoint {name} was not registered with model {model.__name__}")

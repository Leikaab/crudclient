"""
API spy implementation for verification-focused testing.
"""

from typing import Any, Dict, List, Optional, Type, Union

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud import Crud

from .base import SpyBase


class ApiSpy(API, SpyBase):
    """
    Spy implementation of the API interface.

    This class records all method calls to the API interface for verification
    in tests, while delegating to a real or mock implementation.
    """

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
            client: Optional client instance
            client_config: Optional client configuration
            delegate: Optional delegate API implementation
            **kwargs: Additional arguments
        """
        API.__init__(self, client, client_config, **kwargs)
        SpyBase.__init__(self)

        # Create a delegate API if not provided
        self.delegate = delegate or super()

    def _register_endpoints(self) -> None:
        """
        Record and delegate _register_endpoints method call.

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

        Args:
            name: Name of the endpoint
            endpoint: API endpoint
            model: Optional model class
            **kwargs: Additional arguments

        Returns:
            CRUD interface
        """
        try:
            result = self.delegate.register_endpoint(name, endpoint, model, **kwargs)
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

        Args:
            name: Name of the attribute

        Returns:
            Attribute value
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

        Args:
            name: Name of the endpoint
        """
        for call in self.calls:
            if call.method_name == 'register_endpoint' and call.args and call.args[0] == name:
                return

        raise AssertionError(f"Endpoint {name} was not registered")

    def assert_endpoint_registered_with_model(self, name: str, model: Type[Any]) -> None:
        """
        Assert that an endpoint was registered with a specific model.

        Args:
            name: Name of the endpoint
            model: Expected model class
        """
        for call in self.calls:
            if (
                call.method_name == 'register_endpoint'
                and call.args and call.args[0] == name
                and 'model' in call.kwargs and call.kwargs['model'] == model
            ):
                return

        raise AssertionError(f"Endpoint {name} was not registered with model {model.__name__}")

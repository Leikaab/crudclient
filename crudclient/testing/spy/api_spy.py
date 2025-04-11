from typing import Any, Optional, Type

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud.base import Crud

from .base import SpyBase


class ApiSpy(API, SpyBase):

    client_class = Client

    def __init__(self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, delegate: Optional[API] = None, **kwargs: Any):
        # Create a default client_config if none is provided
        if client_config is None:
            client_config = ClientConfig(hostname="https://example.com")

        API.__init__(self, client, client_config, **kwargs)
        SpyBase.__init__(self)

        # Create a delegate API if not provided
        self.delegate = delegate or super()

    def _register_endpoints(self) -> None:
        try:
            result = self.delegate._register_endpoints()
            self._record_call("_register_endpoints", (), {}, result)
            return result
        except Exception as e:
            self._record_call("_register_endpoints", (), {}, exception=e)
            raise

    def register_endpoint(self, name: str, endpoint: str, model: Optional[Type[Any]] = None, **kwargs: Any) -> Crud:
        try:
            # If delegate is super(), we need to implement register_endpoint ourselves
            if hasattr(self.delegate, "register_endpoint"):
                result = self.delegate.register_endpoint(name, endpoint, model, **kwargs)  # type: ignore
            else:
                # Implement register_endpoint if not available in delegate
                # Create a Crud instance and set it as an attribute
                if self.client is None:
                    raise ValueError("Client must be initialized before registering endpoints")
                result = Crud(self.client)
                result._resource_path = endpoint
                result._datamodel = model
                setattr(self, name, result)
            self._record_call("register_endpoint", (name, endpoint), {"model": model, **kwargs}, result)
            return result
        except Exception as e:
            self._record_call("register_endpoint", (name, endpoint), {"model": model, **kwargs}, exception=e)
            raise

    def __getattr__(self, name: str) -> Any:
        try:
            result = getattr(self.delegate, name)
            self._record_call("__getattr__", (name,), {}, result)
            return result
        except Exception as e:
            self._record_call("__getattr__", (name,), {}, exception=e)
            raise

    # Helper methods for verification

    def assert_endpoint_registered(self, name: str) -> None:
        for call in self.calls:
            if call.method_name == "register_endpoint" and call.args and call.args[0] == name:
                return

        raise AssertionError(f"Endpoint {name} was not registered")

    def assert_endpoint_registered_with_model(self, name: str, model: Type[Any]) -> None:
        for call in self.calls:
            if (
                call.method_name == "register_endpoint"
                and call.args
                and call.args[0] == name
                and "model" in call.kwargs
                and call.kwargs["model"] == model
            ):
                return

        raise AssertionError(f"Endpoint {name} was not registered with model {model.__name__}")

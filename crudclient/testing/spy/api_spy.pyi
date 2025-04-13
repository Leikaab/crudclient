"""
Concrete Test Spy for the `API` Interface using Enhanced Spying.

This module provides `ApiSpy`, a specific implementation of the **Test Spy
pattern** tailored for the `crudclient.api.API` interface. It utilizes
the `EnhancedSpyBase` and `ClassSpy` mechanisms to record and verify
interactions made with the API component, such as endpoint registration.
"""

from typing import Any, Optional, Type

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud.base import Crud

from ..exceptions import VerificationError
from .enhanced import EnhancedSpyBase

class ApiSpy(EnhancedSpyBase, API):  # Inherits from EnhancedSpyBase and conforms to API interface
    """
    A **Test Spy** specifically for the `crudclient.api.API` interface.

    This class acts as a test double that conforms to the `API` interface but
    also inherits from `EnhancedSpyBase` to record method calls made to it
    (primarily `register_endpoint`). It uses composition internally, wrapping a
    concrete `API` subclass instance and spying on its methods using `ClassSpy`.

    Tests can use the verification methods inherited from `EnhancedSpyBase` or
    the dedicated `Verifier` class (`crudclient.testing.verification.Verifier`)
    to assert how the API was interacted with. Custom verification methods
    specific to API interactions are also provided.
    """

    client_class: Type[Client]  # Keep for API compatibility

    def __init__(self, client: Optional[Client] = None, client_config: Optional[ClientConfig] = None, **kwargs: Any):
        """
        Initialize an ApiSpy instance.

        Args:
            client: Optional client instance to use for the underlying API.
            client_config: Optional client configuration for the underlying API.
            **kwargs: Additional keyword arguments to pass to the API constructor.
        """
        ...
    # --- API Interface Methods (for type checking) ---
    # These methods are implemented via ClassSpy or __getattr__ in the .py file,
    # but are declared here to satisfy the API interface for type checkers.

    def _register_endpoints(self) -> None:
        """Abstract method from API base class."""
        ...

    def register_endpoint(self, name: str, endpoint: str, model: Optional[Type[Any]] = None, **kwargs: Any) -> Crud:
        """
        Spy on an endpoint registration call.

        Args:
            name: Name of the endpoint
            endpoint: API endpoint path
            model: Optional data model for the endpoint
            **kwargs: Additional keyword arguments

        Returns:
            Crud instance (typically mocked or from a wrapped API)
        """
        ...

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to the spy wrapper, base class, or target API.

        Args:
            name: Attribute name

        Returns:
            Attribute value from the appropriate source.

        Raises:
            AttributeError: If the attribute is not found.
        """
        ...
    # --- Custom Verification Methods ---

    def verify_endpoint_registered(self, name: str) -> None:
        """
        Verify that an endpoint with the given name was registered via `register_endpoint`.

        Args:
            name: Name of the endpoint

        Raises:
            VerificationError: If the endpoint was not registered
        """
        ...

    def verify_endpoint_registered_with_model(self, name: str, model: Type[Any]) -> None:
        """
        Verify that an endpoint was registered via `register_endpoint` with a specific model.

        Args:
            name: Name of the endpoint
            model: Expected model class

        Raises:
            VerificationError: If the endpoint was not registered with the specified model
        """
        ...

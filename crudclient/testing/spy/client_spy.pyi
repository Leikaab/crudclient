"""
Concrete Test Spy for the `Client` Interface using Enhanced Spying.

This module provides `ClientSpy`, a specific implementation of the **Test Spy
pattern** tailored for the `crudclient.client.Client` interface. It utilizes
the `EnhancedSpyBase` and `ClassSpy` mechanisms to record and verify
interactions made directly with the client component.
"""

from typing import Any, Dict, Optional, Union

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.types import RawResponseSimple

from ..exceptions import VerificationError
from .enhanced import EnhancedSpyBase

class ClientSpy(EnhancedSpyBase, Client):  # Inherits from EnhancedSpyBase and conforms to Client interface
    """
    A **Test Spy** specifically for the `crudclient.client.Client` interface.

    This class acts as a test double that conforms to the `Client` interface but
    also inherits from `EnhancedSpyBase` to record all method calls made to it
    (e.g., `get`, `post`, `put`). It uses composition internally, wrapping a
    real `Client` instance and spying on its methods using `ClassSpy`.

    Tests can use the verification methods inherited from `EnhancedSpyBase` or
    the dedicated `Verifier` class (`crudclient.testing.verification.Verifier`)
    to assert how the client was interacted with. Custom verification methods
    specific to client interactions are also provided.
    """

    def __init__(self, config: Union[ClientConfig, Dict[str, Any]], **kwargs: Any):
        """
        Initialize a ClientSpy instance.

        Args:
            config: Client configuration for the underlying real client.
            **kwargs: Additional keyword arguments to pass to the Client constructor.
        """
        ...
    # --- Client Interface Methods (for type checking) ---
    # These methods are implemented via __getattr__ and ClassSpy in the .py file,
    # but are declared here to satisfy the Client interface for type checkers.

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        """
        Spy on a GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response (typically mocked or from a wrapped client)
        """
        ...

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Spy on a POST request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            API response (typically mocked or from a wrapped client)
        """
        ...

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Spy on a PUT request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            API response (typically mocked or from a wrapped client)
        """
        ...

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        """
        Spy on a DELETE request.

        Args:
            endpoint: API endpoint
            **kwargs: Additional keyword arguments

        Returns:
            API response (typically mocked or from a wrapped client)
        """
        ...

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Spy on a PATCH request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            API response (typically mocked or from a wrapped client)
        """
        ...
    # --- Custom Verification Methods ---

    def verify_endpoint_called(self, endpoint: str) -> None:
        """
        Verify that an endpoint was called via any HTTP method.

        Args:
            endpoint: API endpoint string

        Raises:
            VerificationError: If the endpoint was not called
        """
        ...

    def verify_endpoint_called_with_method(self, method: str, endpoint: str) -> None:
        """
        Verify that an endpoint was called with a specific HTTP method.

        Args:
            method: HTTP method name (lowercase, e.g., 'get', 'post')
            endpoint: API endpoint string

        Raises:
            VerificationError: If the endpoint was not called with the specified method
        """
        ...

    def verify_json_payload_sent(self, method: str, endpoint: str, expected_json: Any) -> None:
        """
        Verify that a specific JSON payload was sent to an endpoint via a specific method.

        Args:
            method: HTTP method name (lowercase, e.g., 'post', 'put', 'patch')
            endpoint: API endpoint string
            expected_json: The expected JSON payload structure/data

        Raises:
            VerificationError: If the specified JSON payload was not sent to the endpoint
                               with the specified method
        """
        ...
    # --- Magic Methods ---

    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the spy wrapper or base class."""
        ...

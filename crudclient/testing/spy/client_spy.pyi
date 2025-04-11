"""
Client spy implementation for recording and verifying client interactions.

This module provides a spy implementation of the Client class that records
all method calls for later verification.
"""

from typing import Any, Dict, Optional, Union

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.types import RawResponseSimple

from .base import SpyBase

class ClientSpy(Client, SpyBase):
    """
    Spy implementation of the Client class.

    This class wraps a Client instance and records all method calls for later verification.
    It can be used to verify that the expected methods were called with the expected
    arguments during testing.
    """

    delegate: Client

    def __init__(
        self,
        config: Union[ClientConfig, Dict[str, Any]],
        delegate: Optional[Client] = None,
        **kwargs: Any
    ):
        """
        Initialize a ClientSpy instance.

        Args:
            config: Client configuration
            delegate: Optional delegate client to forward calls to
            **kwargs: Additional keyword arguments to pass to the Client constructor
        """
        ...

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> RawResponseSimple:
        """
        Record and forward a GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            API response

        Raises:
            Any exception raised by the delegate client
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
        Record and forward a POST request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            API response

        Raises:
            Any exception raised by the delegate client
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
        Record and forward a PUT request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            API response

        Raises:
            Any exception raised by the delegate client
        """
        ...

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        """
        Record and forward a DELETE request.

        Args:
            endpoint: API endpoint
            **kwargs: Additional keyword arguments

        Returns:
            API response

        Raises:
            Any exception raised by the delegate client
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
        Record and forward a PATCH request.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            API response

        Raises:
            Any exception raised by the delegate client
        """
        ...

    # Helper methods for verification

    def assert_endpoint_called(self, endpoint: str) -> None:
        """
        Assert that an endpoint was called.

        Args:
            endpoint: API endpoint

        Raises:
            AssertionError: If the endpoint was not called
        """
        ...

    def assert_endpoint_called_with_method(self, method: str, endpoint: str) -> None:
        """
        Assert that an endpoint was called with a specific method.

        Args:
            method: HTTP method (get, post, put, delete, patch)
            endpoint: API endpoint

        Raises:
            AssertionError: If the endpoint was not called with the specified method
        """
        ...

    def assert_json_payload_sent(
        self,
        method: str,
        endpoint: str,
        expected_json: Any
    ) -> None:
        """
        Assert that a JSON payload was sent to an endpoint.

        Args:
            method: HTTP method (get, post, put, delete, patch)
            endpoint: API endpoint
            expected_json: Expected JSON payload

        Raises:
            AssertionError: If the JSON payload was not sent to the endpoint
        """
        ...

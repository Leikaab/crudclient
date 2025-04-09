"""
Direct implementation of MockClientFactory.

This module provides a direct implementation of the MockClientFactory class
to avoid import conflicts between the factory.py file and the factory/ directory.
"""

from typing import Any, Optional

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.core.client import MockClient
from crudclient.testing.core.http_client import MockHTTPClient
from crudclient.testing.types import Headers, ResponseData, StatusCode


class MockClientFactory:
    """Factory for creating and configuring mock client instances."""

    @classmethod
    def create(
        cls,
        base_url: str = "https://api.example.com",
        enable_spy: bool = False,
        **kwargs: Any
    ) -> MockClient:
        """
        Create a new mock client instance.

        Args:
            base_url: The base URL for the mock client.
            enable_spy: Whether to enable spying on the mock client.
            **kwargs: Additional keyword arguments to pass to the MockClient constructor.

        Returns:
            A configured MockClient instance.
        """
        ...

    @classmethod
    def from_client_config(
        cls,
        config: ClientConfig,
        enable_spy: bool = False,
        **kwargs: Any
    ) -> MockClient:
        """
        Create a new mock client instance from a ClientConfig.

        Args:
            config: The ClientConfig to use.
            enable_spy: Whether to enable spying on the mock client.
            **kwargs: Additional keyword arguments to pass to the MockClient constructor.

        Returns:
            A configured MockClient instance.
        """
        ...

    @classmethod
    def from_real_client(
        cls,
        client: Client,
        enable_spy: bool = False,
        **kwargs: Any
    ) -> MockClient:
        """
        Create a new mock client instance that mimics a real client.

        Args:
            client: The real client to mimic.
            enable_spy: Whether to enable spying on the mock client.
            **kwargs: Additional keyword arguments to pass to the MockClient constructor.

        Returns:
            A configured MockClient instance.
        """
        ...

    @classmethod
    def configure_success_response(
        cls,
        mock_client: MockClient,
        method: str,
        path: str,
        data: Optional[ResponseData] = None,
        status_code: StatusCode = 200,
        headers: Optional[Headers] = None
    ) -> None:
        """
        Configure a successful response for a specific request.

        Args:
            mock_client: The mock client to configure.
            method: The HTTP method of the request.
            path: The path of the request.
            data: The data to return in the response body.
            status_code: The status code to return.
            headers: The headers to return in the response.
        """
        ...

    @classmethod
    def configure_error_response(
        cls,
        mock_client: MockClient,
        method: str,
        path: str,
        status_code: StatusCode = 400,
        data: Optional[ResponseData] = None,
        headers: Optional[Headers] = None,
        error: Optional[Exception] = None
    ) -> None:
        """
        Configure an error response for a specific request.

        Args:
            mock_client: The mock client to configure.
            method: The HTTP method of the request.
            path: The path of the request.
            status_code: The status code to return.
            data: The data to return in the response body.
            headers: The headers to return in the response.
            error: An exception to raise instead of returning a response.
        """
        ...

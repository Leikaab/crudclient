"""
Factory for creating mock client instances.

This module provides the main factory for creating configured mock client instances
that can be used in tests to simulate the behavior of the crudclient library.
"""

from typing import Any, Dict, Optional, Type, Union

from crudclient.client import Client
from crudclient.config import ClientConfig

from .core.client import MockClient
from .core.http_client import MockHTTPClient
from .exceptions import MockConfigurationError
from .types import Headers, ResponseData, StatusCode
from .auth import (
    create_api_key_auth_mock,
    create_basic_auth_mock,
    create_bearer_auth_mock,
    create_custom_auth_mock,
    create_oauth_mock,
)
from .factory.helpers import _add_error_responses, _configure_auth_mock, _create_api_patterns


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

    @classmethod
    def create_mock_client(
        cls,
        config: Optional[Union[ClientConfig, Dict[str, Any]]] = None,
        **kwargs: Any
    ) -> MockClient:
        """
        Create a pre-configured MockClient instance with advanced configuration options.

        This method provides a comprehensive way to create and configure a mock client
        with various behaviors including authentication, pre-configured response patterns,
        and common error responses.

        Args:
            config: Optional client configuration (ClientConfig object or dict).
            **kwargs: Additional configuration options including:
                - enable_spy: Whether to enable spying on the mock client (default: False).
                - auth_strategy: An already configured authentication strategy instance.
                - auth_type: Type of authentication to mock ('basic', 'bearer', 'apikey', 'custom', 'oauth').
                - auth_config: Dictionary with configuration for the chosen 'auth_type'.
                    See `crudclient.testing.auth` mocks for specific options.
                - api_type: Type of API patterns to pre-configure ('rest', 'graphql', 'oauth').
                - api_resources: (For 'rest' api_type) Dict defining REST resources and their responses.
                    See `crudclient.testing.response_builder.api_patterns.APIPatternBuilder.rest_resource`.
                - graphql_config: (For 'graphql' api_type) Dict defining GraphQL endpoint behavior.
                    See `crudclient.testing.response_builder.api_patterns.APIPatternBuilder.graphql_endpoint`.
                - oauth_config: (For 'oauth' api_type) Dict defining OAuth flow behavior.
                    See `crudclient.testing.response_builder.api_patterns.APIPatternBuilder.oauth_flow`.
                - error_responses: Dict defining common error responses to add ('validation', 'rate_limit', 'auth').
                    See `crudclient.testing.factory.helpers._add_error_responses`.
                - response_patterns: List of raw response pattern dictionaries to configure directly
                    on the underlying `MockHTTPClient`.

        Returns:
            Configured MockClient instance.

        Note:
            Network condition simulation (latency, packet loss, error rate), rate limiting,
            and default responses for unmatched requests are not currently implemented in MockClient.
            Parameters related to these features (`latency_ms`, `packet_loss_percentage`,
            `error_rate_percentage`, `rate_limit`, `rate_window_seconds`, `default_response`)
            are accepted but ignored.
        """
        ...

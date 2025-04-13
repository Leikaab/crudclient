"""
Factory Pattern Implementation for Mock Client Creation.

This module utilizes the **Factory pattern** to provide a centralized and
flexible way to create and configure various mock client instances
(`MockClient`, `SimpleMockClient`) needed for testing different scenarios.
It encapsulates the complex setup logic behind simple creation methods.

Key Components:
- `MockClientFactory`: A class implementing Factory Methods (`create`,
  `from_client_config`, etc.) to produce configured `MockClient` instances.
- `create_simple_mock_client`: A factory function for creating `SimpleMockClient`
  instances.
"""

from typing import Any, Dict, List, Optional, Union

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.auth import (
    ApiKeyAuthMock,
    BasicAuthMock,
    BearerAuthMock,
    CustomAuthMock,
    OAuthMock,
)
from crudclient.testing.core.client import MockClient
from crudclient.testing.simple_mock import SimpleMockClient
from crudclient.testing.types import Headers, ResponseData, StatusCode

# --- Helper Functions ---

def _create_api_patterns(api_type: str, **kwargs: Any) -> List[Dict[str, Any]]:
    """
    Creates API response patterns based on the specified API type.

    Args:
        api_type: The type of API ('rest', 'oauth')
        **kwargs: Additional configuration options specific to the API type

    Returns:
        A list of response pattern dictionaries that can be used with MockClient.configure_response
    """
    ...

def _add_error_responses(client: MockClient, error_configs: Dict[str, Any]) -> None:
    """
    Adds common error response configurations to a MockClient.

    Args:
        client: The MockClient instance to configure
        error_configs: Dictionary containing error configuration options
    """
    ...

def _configure_auth_mock(auth_mock: Union[BasicAuthMock, BearerAuthMock, ApiKeyAuthMock, CustomAuthMock, OAuthMock], config: Dict[str, Any]) -> None:
    """
    Configures advanced behaviors for an authentication mock object.

    Args:
        auth_mock: The authentication mock object to configure
        config: Dictionary containing configuration options
    """
    ...

def _add_error_responses_to_simple_mock(client: SimpleMockClient, error_configs: Dict[str, Any]) -> None:
    """
    Adds common error response configurations to a SimpleMockClient.

    Args:
        client: The SimpleMockClient instance to configure
        error_configs: Dictionary containing error configuration options
    """
    ...

# --- MockClientFactory ---

class MockClientFactory:
    """
    Implements the **Factory Method pattern** for creating `MockClient` instances.

    This factory centralizes the creation logic for `MockClient`, allowing for
    consistent setup and configuration based on different inputs (e.g., base URL,
    `ClientConfig`, existing `Client`). It simplifies the process of obtaining
    a ready-to-use mock client for various testing needs, including those
    requiring specific response configurations or spying capabilities.

    Key Factory Methods:
    - `create`: Creates a basic `MockClient`.
    - `from_client_config`: Creates a `MockClient` based on a `ClientConfig`.
    - `from_real_client`: Creates a `MockClient` mimicking a real `Client`.
    - `create_mock_client`: Creates a `MockClient` with advanced configurations.

    Configuration helper methods (`configure_success_response`,
    `configure_error_response`) are also provided for convenience, although they
    don't strictly follow the Factory pattern themselves.
    """

    @classmethod
    def create(
        cls,
        base_url: str = "https://api.example.com",
        enable_spy: bool = False,
        config: Optional[ClientConfig] = None,
        **kwargs: Any,
    ) -> MockClient:
        """
        Creates a basic MockClient instance.

        Args:
            base_url: The base URL for the mock API.
            enable_spy: If True, enables request spying capabilities.
            config: An optional ClientConfig object to associate with the client.
            **kwargs: Additional keyword arguments passed to the MockClient constructor.

        Returns:
            A configured MockClient instance.
        """
        ...

    @classmethod
    def from_client_config(cls, config: ClientConfig, enable_spy: bool = False, **kwargs: Any) -> MockClient:
        """
        Creates a MockClient instance based on a ClientConfig object.

        Args:
            config: The ClientConfig object to use for configuration.
            enable_spy: If True, enables request spying capabilities.
            **kwargs: Additional keyword arguments passed to the MockClient constructor.

        Returns:
            A MockClient instance configured according to the ClientConfig.
        """
        ...

    @classmethod
    def from_real_client(cls, client: Client, enable_spy: bool = False, **kwargs: Any) -> MockClient:
        """
        Creates a MockClient instance based on an existing real Client object.

        Args:
            client: The real Client object to mimic.
            enable_spy: If True, enables request spying capabilities.
            **kwargs: Additional keyword arguments passed to the MockClient constructor.

        Returns:
            A MockClient instance configured similarly to the real Client.
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
        headers: Optional[Headers] = None,
    ) -> None:
        """
        Configures a successful response for a specific request pattern on the MockClient.

        Args:
            mock_client: The MockClient instance to configure.
            method: The HTTP method (e.g., "GET", "POST").
            path: The URL path pattern (regex).
            data: The response data (JSON serializable).
            status_code: The HTTP status code (default: 200).
            headers: Optional response headers.
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
        error: Optional[Exception] = None,
    ) -> None:
        """
        Configures an error response or raises an exception for a specific request pattern.

        Args:
            mock_client: The MockClient instance to configure.
            method: The HTTP method (e.g., "GET", "POST").
            path: The URL path pattern (regex).
            status_code: The HTTP status code for the error response (default: 400).
            data: The error response data (JSON serializable).
            headers: Optional response headers.
            error: An optional Exception instance to raise when the request matches.
                   If provided, status_code, data, and headers are ignored.
        """
        ...

    @classmethod
    def create_mock_client(cls, config: Optional[Union[ClientConfig, Dict[str, Any]]] = None, **kwargs: Any) -> MockClient:
        """
        Creates and configures a MockClient with advanced options like authentication,
        API patterns, and error responses.

        Args:
            config: A ClientConfig object or a dictionary to initialize ClientConfig.
                    If None, a default config is used.
            **kwargs: Additional configuration options:
                auth_strategy: An AuthStrategyBase instance. Overrides auth_type/auth_config.
                auth_type: Type of authentication ('basic', 'bearer', 'apikey', 'custom', 'oauth').
                auth_config: Dictionary with specific configuration for the chosen auth_type.
                enable_spy: Boolean to enable request spying (default: False).
                api_type: Type of API ('rest', 'oauth') to pre-configure patterns for.
                api_resources: Dictionary defining REST resources (used if api_type='rest').
                oauth_config: Dictionary defining OAuth flow patterns (used if api_type='oauth').
                error_responses: Dictionary defining common error responses ('validation', 'rate_limit', 'auth').
                response_patterns: A list of dictionaries, each defining a response pattern
                                   (passed directly to mock_client.configure_response).
                Other kwargs are passed to the underlying MockClient constructor.

        Returns:
            A fully configured MockClient instance.
        """
        ...

# --- SimpleMockClient Creation ---

def create_simple_mock_client(**kwargs: Any) -> SimpleMockClient:
    """
    Acts as a **Simple Factory** for creating `SimpleMockClient` instances.

    This function provides a straightforward way to instantiate and configure
    a `SimpleMockClient`, hiding the underlying setup details. It allows
    pre-configuration of response patterns and error handling based on common
    API types or specific definitions.

    Args:
        **kwargs: Configuration options:
            default_response: The default response dictionary for unmatched requests.
            api_type: Type of API ('rest', 'oauth') to pre-configure patterns for.
            api_resources: Dictionary defining REST resources (used if api_type='rest').
            oauth_config: Dictionary defining OAuth flow patterns (used if api_type='oauth').
            error_responses: Dictionary defining common error responses ('validation', 'rate_limit', 'auth').
            response_patterns: A list of dictionaries, each defining a response pattern
                               (passed directly to client.with_response_pattern).

    Returns:
        A configured SimpleMockClient instance.
    """
    ...

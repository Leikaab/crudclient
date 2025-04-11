
from typing import Any, Dict, Optional, Union

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.factory.helpers import _add_error_responses, _configure_auth_mock, _create_api_patterns  # Use absolute import

from .auth import create_api_key_auth_mock, create_basic_auth_mock, create_bearer_auth_mock, create_custom_auth_mock, create_oauth_mock
from .core.client import MockClient
from .core.http_client import MockHTTPClient
from .types import Headers, ResponseData, StatusCode


class MockClientFactory:

    @classmethod
    def create(
        cls,
        base_url: str = "https://api.example.com",
        enable_spy: bool = False,
        **kwargs: Any
    ) -> MockClient:
        # Create a mock HTTP client
        http_client = MockHTTPClient(base_url=base_url)

        # Create a mock client with the mock HTTP client
        mock_client = MockClient(
            http_client=http_client,
            enable_spy=enable_spy,
            **kwargs
        )

        return mock_client

    @classmethod
    def from_client_config(
        cls,
        config: ClientConfig,
        enable_spy: bool = False,
        **kwargs: Any
    ) -> MockClient:
        # Extract the base URL from the config
        base_url = config.hostname or "https://api.example.com"

        # Create a mock client with the base URL
        mock_client = cls.create(
            base_url=base_url,
            enable_spy=enable_spy,
            **kwargs
        )

        # Configure the mock client with the auth strategy from the config
        if config.auth_strategy is not None:
            mock_client.set_auth_strategy(config.auth_strategy)

        return mock_client

    @classmethod
    def from_real_client(
        cls,
        client: Client,
        enable_spy: bool = False,
        **kwargs: Any
    ) -> MockClient:
        # Extract the config from the real client
        config = client.config

        # Create a mock client from the config
        mock_client = cls.from_client_config(
            config=config,
            enable_spy=enable_spy,
            **kwargs
        )

        return mock_client

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
        mock_client.configure_response(
            method=method,
            path=path,
            status_code=status_code,
            data=data,
            headers=headers
        )

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
        if error is not None:
            mock_client.configure_response(
                method=method,
                path=path,
                error=error
            )
        else:
            mock_client.configure_response(
                method=method,
                path=path,
                status_code=status_code,
                data=data,
                headers=headers
            )

    @classmethod
    def create_mock_client(
        cls,
        config: Optional[Union[ClientConfig, Dict[str, Any]]] = None,
        **kwargs: Any
    ) -> MockClient:
        # Ensure we have a valid config
        if config is None:
            config = ClientConfig(hostname="https://api.example.com", version="v1")
        elif isinstance(config, dict):
            config = ClientConfig(**config)

        # Configure authentication if specified
        if 'auth_strategy' in kwargs:
            # Use the provided auth strategy directly
            config.auth_strategy = kwargs['auth_strategy']
        elif 'auth_type' in kwargs:
            # Create an auth strategy based on the type
            auth_type = kwargs['auth_type'].lower()
            auth_config = kwargs.get('auth_config', {})

            if auth_type == 'basic':
                auth_mock = create_basic_auth_mock(
                    username=auth_config.get('username', 'user'),
                    password=auth_config.get('password', 'pass')
                )

                # Apply any auth behavior configurations
                _configure_auth_mock(auth_mock, auth_config)
                config.auth_strategy = auth_mock.get_auth_strategy()

            elif auth_type == 'bearer':
                auth_mock = create_bearer_auth_mock(
                    token=auth_config.get('token', 'valid_token')
                )

                # Apply any auth behavior configurations
                _configure_auth_mock(auth_mock, auth_config)
                config.auth_strategy = auth_mock.get_auth_strategy()

            elif auth_type == 'apikey':
                header_name = auth_config.get('header_name')
                param_name = auth_config.get('param_name')

                if header_name:
                    auth_mock = create_api_key_auth_mock(
                        api_key=auth_config.get('api_key', 'valid_api_key'),
                        header_name=header_name
                    )
                elif param_name:
                    auth_mock = create_api_key_auth_mock(
                        api_key=auth_config.get('api_key', 'valid_api_key'),
                        header_name=None,
                        param_name=param_name
                    )
                else:
                    # Default to header auth
                    auth_mock = create_api_key_auth_mock(
                        api_key=auth_config.get('api_key', 'valid_api_key')
                    )

                # Apply any auth behavior configurations
                _configure_auth_mock(auth_mock, auth_config)
                config.auth_strategy = auth_mock.get_auth_strategy()

            elif auth_type == 'custom':
                header_callback = auth_config.get('header_callback')
                param_callback = auth_config.get('param_callback')

                auth_mock = create_custom_auth_mock(
                    header_callback=header_callback,
                    param_callback=param_callback
                )

                # Apply any auth behavior configurations
                _configure_auth_mock(auth_mock, auth_config)
                config.auth_strategy = auth_mock.get_auth_strategy()

            elif auth_type == 'oauth':
                auth_mock = create_oauth_mock(
                    client_id=auth_config.get('client_id', 'client_id'),
                    client_secret=auth_config.get('client_secret', 'client_secret'),
                    token_url=auth_config.get('token_url', 'https://example.com/oauth/token'),
                    authorize_url=auth_config.get('authorize_url'),
                    grant_type=auth_config.get('grant_type', 'authorization_code'),
                    scope=auth_config.get('scope', 'read write'),
                    access_token=auth_config.get('access_token'),
                    refresh_token=auth_config.get('refresh_token')
                )

                # Apply any auth behavior configurations
                _configure_auth_mock(auth_mock, auth_config)
                config.auth_strategy = auth_mock.get_auth_strategy()

        # Extract enable_spy from kwargs
        enable_spy = kwargs.pop('enable_spy', False)

        # Create the mock client
        mock_client = cls.create(
            base_url=config.hostname or "https://api.example.com",
            enable_spy=enable_spy,
            **kwargs
        )

        # Configure the mock client with the auth strategy from the config
        if config.auth_strategy is not None:
            mock_client.set_auth_strategy(config.auth_strategy)

        # Note: Network conditions, rate limiting, and default response configuration
        # are not currently supported in the MockClient implementation.
        # These features may be added in future versions.

        # The following parameters are accepted but not currently used:
        # - latency_ms: Simulated network latency in milliseconds
        # - packet_loss_percentage: Percentage of requests that will be dropped
        # - error_rate_percentage: Percentage of requests that will raise errors
        # - rate_limit: Maximum number of requests allowed in the rate window
        # - rate_window_seconds: Time window for rate limiting in seconds
        # - default_response: Default response for unmatched requests

        # Add API-specific patterns based on api_type
        api_type = kwargs.get('api_type')
        if api_type:
            patterns = _create_api_patterns(api_type, **kwargs)
            for pattern in patterns:
                mock_client.configure_response(**pattern)

        # Add common error responses if specified
        if 'error_responses' in kwargs:
            _add_error_responses(mock_client, kwargs['error_responses'])

        # Add response patterns if specified
        patterns = kwargs.get('response_patterns', [])
        for pattern in patterns:
            mock_client.configure_response(**pattern)

        return mock_client

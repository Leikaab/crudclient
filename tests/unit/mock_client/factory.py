"""
Factory functions for creating mock clients.

This module provides factory functions for creating pre-configured mock clients
with various behaviors and response patterns.
"""

from typing import Any, Dict, List, Optional, Union, Callable, Type

from crudclient.auth.base import AuthStrategy
from crudclient.config import ClientConfig

from .client import MockClient
from .simple_mock import SimpleMockClient
from .response import MockResponse
from .api_patterns import APIPatternBuilder
from .response_builder import ResponseBuilder
from .auth import (
    BasicAuthMock, BearerAuthMock, ApiKeyAuthMock, CustomAuthMock,
    create_basic_auth_mock, create_bearer_auth_mock,
    create_api_key_auth_mock, create_custom_auth_mock,
    AuthVerificationHelpers
)


def create_mock_client(
    config: Optional[Union[ClientConfig, Dict[str, Any]]] = None,
    **kwargs: Any
) -> MockClient:
    """
    Create a pre-configured MockClient instance.

    Args:
        config: Optional client configuration
        **kwargs: Additional configuration options including:
            - latency_ms: Simulated network latency in milliseconds
            - packet_loss_percentage: Percentage of requests that will be dropped
            - error_rate_percentage: Percentage of requests that will raise errors
            - rate_limit: Maximum number of requests allowed in the rate window
            - rate_window_seconds: Time window for rate limiting in seconds
            - response_patterns: List of response patterns to configure
            - default_response: Default response for unmatched requests
            - api_type: Type of API to mock (rest, graphql, etc.)
            - api_resources: Resources to mock for REST APIs
            - error_responses: Pre-configured error responses to include
            - auth_strategy: Authentication strategy to use
            - auth_type: Type of authentication to mock (basic, bearer, apikey, custom)
            - auth_config: Configuration for the authentication strategy

    Returns:
        Configured MockClient instance
    """
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

    client = MockClient(config)

    # Apply network conditions if specified
    if 'latency_ms' in kwargs or 'packet_loss_percentage' in kwargs or 'error_rate_percentage' in kwargs:
        client.with_network_condition(
            latency_ms=kwargs.get('latency_ms', 0),
            packet_loss_percentage=kwargs.get('packet_loss_percentage', 0.0),
            error_rate_percentage=kwargs.get('error_rate_percentage', 0.0)
        )

    # Apply rate limiting if specified
    if 'rate_limit' in kwargs or 'rate_window_seconds' in kwargs:
        client.with_rate_limiter(
            limit=kwargs.get('rate_limit', 60),
            window_seconds=kwargs.get('rate_window_seconds', 60)
        )

    # Set default response if specified
    if 'default_response' in kwargs:
        client.with_default_response(kwargs['default_response'])

    # Add API-specific patterns based on api_type
    api_type = kwargs.get('api_type')
    if api_type:
        patterns = _create_api_patterns(api_type, **kwargs)
        for pattern in patterns:
            client.with_response_pattern(**pattern)

    # Add common error responses if specified
    if 'error_responses' in kwargs:
        _add_error_responses(client, kwargs['error_responses'])

    # Add response patterns if specified
    patterns = kwargs.get('response_patterns', [])
    for pattern in patterns:
        client.with_response_pattern(**pattern)

    return client


def create_simple_mock_client(**kwargs: Any) -> SimpleMockClient:
    """
    Create a pre-configured SimpleMockClient instance.

    Args:
        **kwargs: Configuration options including:
            - response_patterns: List of response patterns to configure
            - default_response: Default response for unmatched requests
            - api_type: Type of API to mock (rest, graphql, etc.)
            - api_resources: Resources to mock for REST APIs
            - error_responses: Pre-configured error responses to include
            - auth_strategy: Authentication strategy to use
            - auth_type: Type of authentication to mock (basic, bearer, apikey, custom)
            - auth_config: Configuration for the authentication strategy

    Returns:
        Configured SimpleMockClient instance
    """
    client = SimpleMockClient()

    # Set default response if specified
    if 'default_response' in kwargs:
        client.with_default_response(kwargs['default_response'])

    # Add API-specific patterns based on api_type
    api_type = kwargs.get('api_type')
    if api_type:
        patterns = _create_api_patterns(api_type, **kwargs)
        for pattern in patterns:
            client.with_response_pattern(**pattern)

    # Add common error responses if specified
    if 'error_responses' in kwargs:
        _add_error_responses(client, kwargs['error_responses'])

    # Add response patterns if specified
    patterns = kwargs.get('response_patterns', [])
    for pattern in patterns:
        client.with_response_pattern(**pattern)

    return client


def _create_api_patterns(api_type: str, **kwargs: Any) -> List[Dict[str, Any]]:
    """
    Create response patterns for a specific API type.

    Args:
        api_type: Type of API to mock (rest, graphql, etc.)
        **kwargs: Additional configuration options

    Returns:
        List of response patterns
    """
    patterns = []

    if api_type.lower() == 'rest':
        # Create patterns for REST resources
        resources = kwargs.get('api_resources', {})
        for resource_name, resource_config in resources.items():
            resource_patterns = APIPatternBuilder.rest_resource(
                base_path=resource_config.get('base_path', resource_name),
                resource_id_pattern=resource_config.get('id_pattern', r'\d+'),
                list_response=resource_config.get('list_response'),
                get_response=resource_config.get('get_response'),
                create_response=resource_config.get('create_response'),
                update_response=resource_config.get('update_response'),
                delete_response=resource_config.get('delete_response')
            )
            patterns.extend(resource_patterns)

    elif api_type.lower() == 'graphql':
        # Create patterns for GraphQL endpoint
        graphql_config = kwargs.get('graphql_config', {})
        graphql_patterns = APIPatternBuilder.graphql_endpoint(
            url_pattern=graphql_config.get('url_pattern', r'/graphql$'),
            query_matchers=graphql_config.get('query_matchers'),
            default_response=graphql_config.get('default_response')
        )
        patterns.extend(graphql_patterns)

    elif api_type.lower() == 'oauth':
        # Create patterns for OAuth flow
        oauth_config = kwargs.get('oauth_config', {})
        oauth_patterns = APIPatternBuilder.oauth_flow(
            token_url_pattern=oauth_config.get('token_url_pattern', r'/oauth/token$'),
            success_response=oauth_config.get('success_response'),
            error_response=oauth_config.get('error_response'),
            valid_credentials=oauth_config.get('valid_credentials')
        )
        patterns.extend(oauth_patterns)

    return patterns


def _add_error_responses(
    client: Union[MockClient, SimpleMockClient],
    error_configs: Dict[str, Any]
) -> None:
    """
    Add common error responses to a mock client.

    Args:
        client: Mock client instance
        error_configs: Error response configurations
    """
    # Add validation error response
    if 'validation' in error_configs:
        config = error_configs['validation']
        client.with_response_pattern(
            method=config.get('method', 'POST'),
            url_pattern=config.get('url_pattern', r'.*'),
            response=ResponseBuilder.create_validation_error(
                fields=config.get('fields', {'field': 'Invalid value'}),
                status_code=config.get('status_code', 422),
                error_code=config.get('error_code', 'VALIDATION_ERROR'),
                message=config.get('message', 'Validation failed')
            ),
            **config.get('matchers', {})
        )

    # Add rate limit error response
    if 'rate_limit' in error_configs:
        config = error_configs['rate_limit']
        client.with_response_pattern(
            method=config.get('method', 'GET'),
            url_pattern=config.get('url_pattern', r'.*'),
            response=ResponseBuilder.create_rate_limit_error(
                limit=config.get('limit', 100),
                remaining=config.get('remaining', 0),
                reset_seconds=config.get('reset_seconds', 60)
            ),
            **config.get('matchers', {})
        )

    # Add authentication error response
    if 'auth' in error_configs:
        config = error_configs['auth']
        client.with_response_pattern(
            method=config.get('method', 'GET'),
            url_pattern=config.get('url_pattern', r'.*'),
            response=ResponseBuilder.create_auth_error(
                error_type=config.get('error_type', 'invalid_token'),
                status_code=config.get('status_code', 401)
            ),
            **config.get('matchers', {})
        )


def _configure_auth_mock(auth_mock: Union[BasicAuthMock, BearerAuthMock, ApiKeyAuthMock, CustomAuthMock], config: Dict[str, Any]) -> None:
    """
    Configure an authentication mock with behavior settings.

    Args:
        auth_mock: The authentication mock to configure
        config: Configuration options
    """
    # Configure failure behavior
    if config.get('should_fail', False):
        auth_mock.with_failure(
            failure_type=config.get('failure_type', 'invalid_token'),
            status_code=config.get('status_code', 401),
            message=config.get('message', 'Authentication failed')
        )

    # Configure token expiration
    if 'expires_in_seconds' in config:
        auth_mock.with_token_expiration(expires_in_seconds=config['expires_in_seconds'])

    # Configure expired token
    if config.get('token_expired', False):
        auth_mock.with_expired_token()

    # Configure refresh token
    if 'refresh_token' in config:
        auth_mock.with_refresh_token(
            refresh_token=config['refresh_token'],
            max_refresh_attempts=config.get('max_refresh_attempts', 3)
        )

    # Configure expired refresh token
    if config.get('refresh_token_expired', False):
        auth_mock.with_expired_refresh_token()

    # Configure MFA
    if config.get('mfa_required', False):
        auth_mock.with_mfa_required(verified=config.get('mfa_verified', False))

    # Configure failure after X requests
    if 'fail_after_requests' in config:
        auth_mock.fail_after(request_count=config['fail_after_requests'])

    # Configure custom headers
    custom_headers = config.get('custom_headers', {})
    for name, value in custom_headers.items():
        auth_mock.with_custom_header(name, value)

    # Configure custom params
    custom_params = config.get('custom_params', {})
    for name, value in custom_params.items():
        auth_mock.with_custom_param(name, value)

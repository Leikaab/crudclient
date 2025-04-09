"""
Factory function for creating simple mock clients.

This module provides a factory function for creating pre-configured simple mock clients
that can be used for testing API interactions without the complexity of real HTTP clients.
The factory function supports various configuration options including response patterns,
error responses, and API-specific behaviors.
"""

from typing import Any, Dict

from crudclient.testing.factory.helpers import _create_api_patterns
from crudclient.testing.simple_mock import SimpleMockClient


def create_simple_mock_client(**kwargs: Any) -> SimpleMockClient:
    """
    Create a pre-configured SimpleMockClient instance for testing API interactions.

    This factory function creates and configures a SimpleMockClient with various
    response patterns, error behaviors, and API-specific configurations. It provides
    a convenient way to set up mock clients for testing without having to manually
    configure each aspect of the client's behavior.

    Args:
        **kwargs: Configuration options including:
            - response_patterns: List of response patterns to configure the client with.
              Each pattern should be a dictionary with keys for method, path, status_code, etc.
            - default_response: Default response for unmatched requests. This will be returned
              when no specific pattern matches the incoming request.
            - api_type: Type of API to mock (rest, graphql, oauth). This determines the
              pattern generation strategy.
            - api_resources: Resources to mock for REST APIs. Should be a dictionary mapping
              resource names to their configuration.
            - error_responses: Pre-configured error responses to include (validation errors,
              rate limiting, authentication failures, etc.)
            - auth_strategy: Authentication strategy to use with the mock client.
            - auth_type: Type of authentication to mock (basic, bearer, apikey, custom, oauth).
            - auth_config: Configuration for the authentication strategy.

    Returns:
        SimpleMockClient: A fully configured SimpleMockClient instance ready for use in tests.

    Examples:
        Basic usage with default response:

        >>> client = create_simple_mock_client(
        ...     default_response={"status": "ok"}
        ... )

        Configuring a REST API with resources:

        >>> client = create_simple_mock_client(
        ...     api_type="rest",
        ...     api_resources={
        ...         "users": {
        ...             "list_response": {"data": [{"id": 1, "name": "User 1"}]},
        ...             "get_response": {"id": 1, "name": "User 1"}
        ...         }
        ...     }
        ... )

        Adding error responses:

        >>> client = create_simple_mock_client(
        ...     error_responses={
        ...         "validation": {"status_code": 422},
        ...         "rate_limit": {"limit": 100, "remaining": 0}
        ...     }
        ... )
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
        _add_error_responses_to_simple_mock(client, kwargs['error_responses'])

    # Add response patterns if specified
    patterns = kwargs.get('response_patterns', [])
    for pattern in patterns:
        client.with_response_pattern(**pattern)

    return client


def _add_error_responses_to_simple_mock(
    client: SimpleMockClient,
    error_configs: Dict[str, Any]
) -> None:
    """
    Add common error responses to a SimpleMockClient.

    This function configures a SimpleMockClient with common error responses based on
    the provided configuration. It supports validation errors, rate limit errors,
    and authentication errors.

    Args:
        client: SimpleMockClient instance to configure
        error_configs: Error response configurations including:
            - validation: Configuration for validation error responses
            - rate_limit: Configuration for rate limit error responses
            - auth: Configuration for authentication error responses
    """
    # Add validation error response
    if 'validation' in error_configs:
        config = error_configs['validation']
        # Create validation error data
        validation_error_data = {
            "error": {
                "code": config.get('error_code', 'VALIDATION_ERROR'),
                "message": config.get('message', 'Validation failed'),
                "fields": config.get('fields', {'field': 'Invalid value'})
            }
        }

        client.with_response_pattern(
            method=config.get('method', 'POST'),
            url_pattern=config.get('url_pattern', r'.*'),
            response={
                "status_code": config.get('status_code', 422),
                "json_data": validation_error_data,
                "headers": {"Content-Type": "application/json"}
            }
        )

    # Add rate limit error response
    if 'rate_limit' in error_configs:
        config = error_configs['rate_limit']
        # Create rate limit error data
        rate_limit_data = {
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded. Please try again later."
            }
        }

        rate_limit_headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(config.get('limit', 100)),
            "X-RateLimit-Remaining": str(config.get('remaining', 0)),
            "X-RateLimit-Reset": str(config.get('reset_seconds', 60))
        }

        client.with_response_pattern(
            method=config.get('method', 'GET'),
            url_pattern=config.get('url_pattern', r'.*'),
            response={
                "status_code": 429,
                "json_data": rate_limit_data,
                "headers": rate_limit_headers
            }
        )

    # Add authentication error response
    if 'auth' in error_configs:
        config = error_configs['auth']
        # Create auth error data
        error_type = config.get('error_type', 'invalid_token')

        error_messages = {
            "invalid_token": "The access token is invalid or has expired",
            "invalid_credentials": "Invalid username or password",
            "missing_credentials": "Authentication credentials were not provided",
            "insufficient_scope": "The access token does not have the required scope",
            "mfa_required": "Multi-factor authentication is required"
        }

        message = error_messages.get(error_type, "Authentication failed")

        auth_error_data = {
            "error": {
                "code": error_type.upper(),
                "message": message
            }
        }

        auth_headers = {
            "Content-Type": "application/json",
            "WWW-Authenticate": f'Bearer error="{error_type}", error_description="{message}"'
        }

        client.with_response_pattern(
            method=config.get('method', 'GET'),
            url_pattern=config.get('url_pattern', r'.*'),
            response={
                "status_code": config.get('status_code', 401),
                "json_data": auth_error_data,
                "headers": auth_headers
            }
        )

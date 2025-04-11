"""
Helper functions for creating and configuring mock clients.

This module provides helper functions for configuring mock clients with various
response patterns, error behaviors, and authentication strategies.
"""

from typing import Any, Dict, List, Union

from crudclient.testing.auth import ApiKeyAuthMock, BasicAuthMock, BearerAuthMock, CustomAuthMock, OAuthMock
from crudclient.testing.core.client import MockClient
from crudclient.testing.response_builder.api_patterns import APIPatternBuilder

def _create_api_patterns(api_type: str, **kwargs: Any) -> List[Dict[str, Any]]:
    """
    Create response patterns for a specific API type.

    This function generates response patterns based on the specified API type and
    configuration options. It supports REST, GraphQL, and OAuth API types.

    Args:
        api_type: Type of API to mock (rest, graphql, oauth)
        **kwargs: Additional configuration options including:
            - api_resources: Dict of resources to configure for REST APIs
            - graphql_config: Configuration for GraphQL endpoints
            - oauth_config: Configuration for OAuth flows

    Returns:
        List of response patterns that can be used to configure a mock client
    """
    ...


def _add_error_responses(
    client: MockClient,
    error_configs: Dict[str, Any]
) -> None:
    """
    Add common error responses to a mock client.

    This function configures a mock client with common error responses based on
    the provided configuration. It supports validation errors, rate limit errors,
    and authentication errors.

    Args:
        client: Mock client instance to configure
        error_configs: Error response configurations including:
            - validation: Configuration for validation error responses
            - rate_limit: Configuration for rate limit error responses
            - auth: Configuration for authentication error responses
    """
    ...


def _configure_auth_mock(
    auth_mock: Union[BasicAuthMock, BearerAuthMock, ApiKeyAuthMock, CustomAuthMock, OAuthMock],
    config: Dict[str, Any]
) -> None:
    """
    Configure an authentication mock with behavior settings.

    This function configures an authentication mock with various behavior settings
    such as failure conditions, token expiration, and custom headers/parameters.

    Args:
        auth_mock: The authentication mock to configure
        config: Configuration options including:
            - should_fail: Whether the authentication should fail
            - failure_type: Type of failure (e.g., 'invalid_token')
            - status_code: HTTP status code for failure responses
            - message: Error message for failure responses
            - expires_in_seconds: Token expiration time in seconds
            - token_expired: Whether the token is already expired
            - refresh_token: Refresh token to use
            - refresh_token_expired: Whether the refresh token is expired
            - mfa_required: Whether MFA is required
            - mfa_verified: Whether MFA is verified
            - fail_after_requests: Number of requests after which to fail
            - custom_headers: Custom headers to include in requests
            - custom_params: Custom parameters to include in requests
    """
    ...

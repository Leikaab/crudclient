# crudclient/testing/factory.py

from typing import Any, Dict, List, Optional, Union

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.testing.auth import (
    ApiKeyAuthMock,
    BasicAuthMock,
    BearerAuthMock,
    CustomAuthMock,
    OAuthMock,
    create_api_key_auth_mock,
    create_basic_auth_mock,
    create_bearer_auth_mock,
    create_custom_auth_mock,
    create_oauth_mock,
)
from crudclient.testing.core.client import MockClient
from crudclient.testing.core.http_client import MockHTTPClient
from crudclient.testing.response_builder.api_patterns import APIPatternBuilder
from crudclient.testing.simple_mock import SimpleMockClient
from crudclient.testing.types import Headers, ResponseData, StatusCode

# --- Helper Functions (from factory/helpers.py) ---


def _create_api_patterns(api_type: str, **kwargs: Any) -> List[Dict[str, Any]]:
    patterns = []

    if api_type.lower() == "rest":
        # Create patterns for REST resources
        resources = kwargs.get("api_resources", {})
        for resource_name, resource_config in resources.items():
            resource_patterns = APIPatternBuilder.rest_resource(
                base_path=resource_config.get("base_path", resource_name),
                resource_id_pattern=resource_config.get("id_pattern", r"\d+"),
                list_response=resource_config.get("list_response"),
                get_response=resource_config.get("get_response"),
                create_response=resource_config.get("create_response"),
                update_response=resource_config.get("update_response"),
                delete_response=resource_config.get("delete_response"),
                search_response=resource_config.get("search_response"),
                filter_response=resource_config.get("filter_response"),
                patch_response=resource_config.get("patch_response"),
            )
            patterns.extend(resource_patterns)

            # Add batch operations if configured
            if resource_config.get("batch_operations"):
                batch_config = resource_config.get("batch_operations", {})
                batch_patterns = APIPatternBuilder.batch_operations(
                    base_path=resource_config.get("base_path", resource_name),
                    batch_create_response=batch_config.get("create_response"),
                    batch_update_response=batch_config.get("update_response"),
                    batch_delete_response=batch_config.get("delete_response"),
                )
                patterns.extend(batch_patterns)

            # Add nested resources if configured
            nested_resources = resource_config.get("nested_resources", {})
            for nested_name, nested_config in nested_resources.items():
                nested_patterns = APIPatternBuilder.nested_resource(
                    parent_path=resource_config.get("base_path", resource_name),
                    child_path=nested_config.get("base_path", nested_name),
                    parent_id_pattern=resource_config.get("id_pattern", r"\d+"),
                    child_id_pattern=nested_config.get("id_pattern", r"\d+"),
                    list_response=nested_config.get("list_response"),
                    get_response=nested_config.get("get_response"),
                    create_response=nested_config.get("create_response"),
                    update_response=nested_config.get("update_response"),
                    delete_response=nested_config.get("delete_response"),
                )
                patterns.extend(nested_patterns)

    # Removed GraphQL section as requested

    elif api_type.lower() == "oauth":
        # Create patterns for OAuth flow
        oauth_config = kwargs.get("oauth_config", {})
        oauth_patterns = APIPatternBuilder.oauth_flow(
            token_url_pattern=oauth_config.get("token_url_pattern", r"/oauth/token$"),
            success_response=oauth_config.get("success_response"),
            error_response=oauth_config.get("error_response"),
            valid_credentials=oauth_config.get("valid_credentials"),
        )
        patterns.extend(oauth_patterns)

    return patterns


def _add_error_responses(client: MockClient, error_configs: Dict[str, Any]) -> None:
    # Add validation error response
    if "validation" in error_configs:
        config = error_configs["validation"]
        validation_error_data = {
            "error": {
                "code": config.get("error_code", "VALIDATION_ERROR"),
                "message": config.get("message", "Validation failed"),
                "fields": config.get("fields", {"field": "Invalid value"}),
            }
        }
        client.configure_response(
            method=config.get("method", "POST"),
            path=config.get("url_pattern", r".*"),
            status_code=config.get("status_code", 422),
            data=validation_error_data,
            headers={"Content-Type": "application/json"},
        )

    # Add rate limit error response
    if "rate_limit" in error_configs:
        config = error_configs["rate_limit"]
        rate_limit_data = {"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Rate limit exceeded. Please try again later."}}
        rate_limit_headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(config.get("limit", 100)),
            "X-RateLimit-Remaining": str(config.get("remaining", 0)),
            "X-RateLimit-Reset": str(config.get("reset_seconds", 60)),
        }
        client.configure_response(
            method=config.get("method", "GET"),
            path=config.get("url_pattern", r".*"),
            status_code=429,
            data=rate_limit_data,
            headers=rate_limit_headers,
        )

    # Add authentication error response
    if "auth" in error_configs:
        config = error_configs["auth"]
        error_type = config.get("error_type", "invalid_token")
        error_messages = {
            "invalid_token": "The access token is invalid or has expired",
            "invalid_credentials": "Invalid username or password",
            "missing_credentials": "Authentication credentials were not provided",
            "insufficient_scope": "The access token does not have the required scope",
            "mfa_required": "Multi-factor authentication is required",
        }
        message = error_messages.get(error_type, "Authentication failed")
        auth_error_data = {"error": {"code": error_type.upper(), "message": message}}
        auth_headers = {"Content-Type": "application/json", "WWW-Authenticate": f'Bearer error="{error_type}", error_description="{message}"'}
        client.configure_response(
            method=config.get("method", "GET"),
            path=config.get("url_pattern", r".*"),
            status_code=config.get("status_code", 401),
            data=auth_error_data,
            headers=auth_headers,
        )


def _configure_auth_mock(auth_mock: Union[BasicAuthMock, BearerAuthMock, ApiKeyAuthMock, CustomAuthMock, OAuthMock], config: Dict[str, Any]) -> None:
    # Configure failure behavior
    if config.get("should_fail", False):
        auth_mock.with_failure(
            failure_type=config.get("failure_type", "invalid_token"),
            status_code=config.get("status_code", 401),
            message=config.get("message", "Authentication failed"),
        )

    # Configure token expiration
    if "expires_in_seconds" in config:
        auth_mock.with_token_expiration(expires_in_seconds=config["expires_in_seconds"])

    # Configure expired token
    if config.get("token_expired", False):
        auth_mock.with_expired_token()

    # Configure refresh token
    if "refresh_token" in config:
        auth_mock.with_refresh_token(refresh_token=config["refresh_token"])

    # Configure expired refresh token
    if config.get("refresh_token_expired", False):
        auth_mock.with_expired_refresh_token()

    # Configure MFA
    if config.get("mfa_required", False):
        auth_mock.with_mfa_required(verified=config.get("mfa_verified", False))

    # Configure failure after X requests
    if "fail_after_requests" in config:
        auth_mock.fail_after(request_count=config["fail_after_requests"])

    # Configure custom headers
    custom_headers = config.get("custom_headers", {})
    for name, value in custom_headers.items():
        auth_mock.with_custom_header(name, value)

    # Configure custom params
    custom_params = config.get("custom_params", {})
    for name, value in custom_params.items():
        auth_mock.with_custom_param(name, value)


# --- Helper Function (from factory/simple_mock.py) ---


def _add_error_responses_to_simple_mock(client: SimpleMockClient, error_configs: Dict[str, Any]) -> None:
    # Add validation error response
    if "validation" in error_configs:
        config = error_configs["validation"]
        validation_error_data = {
            "error": {
                "code": config.get("error_code", "VALIDATION_ERROR"),
                "message": config.get("message", "Validation failed"),
                "fields": config.get("fields", {"field": "Invalid value"}),
            }
        }
        client.with_response_pattern(
            method=config.get("method", "POST"),
            url_pattern=config.get("url_pattern", r".*"),
            response={
                "status_code": config.get("status_code", 422),
                "json_data": validation_error_data,
                "headers": {"Content-Type": "application/json"},
            },
        )

    # Add rate limit error response
    if "rate_limit" in error_configs:
        config = error_configs["rate_limit"]
        rate_limit_data = {"error": {"code": "RATE_LIMIT_EXCEEDED", "message": "Rate limit exceeded. Please try again later."}}
        rate_limit_headers = {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": str(config.get("limit", 100)),
            "X-RateLimit-Remaining": str(config.get("remaining", 0)),
            "X-RateLimit-Reset": str(config.get("reset_seconds", 60)),
        }
        client.with_response_pattern(
            method=config.get("method", "GET"),
            url_pattern=config.get("url_pattern", r".*"),
            response={"status_code": 429, "json_data": rate_limit_data, "headers": rate_limit_headers},
        )

    # Add authentication error response
    if "auth" in error_configs:
        config = error_configs["auth"]
        error_type = config.get("error_type", "invalid_token")
        error_messages = {
            "invalid_token": "The access token is invalid or has expired",
            "invalid_credentials": "Invalid username or password",
            "missing_credentials": "Authentication credentials were not provided",
            "insufficient_scope": "The access token does not have the required scope",
            "mfa_required": "Multi-factor authentication is required",
        }
        message = error_messages.get(error_type, "Authentication failed")
        auth_error_data = {"error": {"code": error_type.upper(), "message": message}}
        auth_headers = {"Content-Type": "application/json", "WWW-Authenticate": f'Bearer error="{error_type}", error_description="{message}"'}
        client.with_response_pattern(
            method=config.get("method", "GET"),
            url_pattern=config.get("url_pattern", r".*"),
            response={"status_code": config.get("status_code", 401), "json_data": auth_error_data, "headers": auth_headers},
        )


# --- MockClientFactory (from client_factory.py) ---


class MockClientFactory:
    @classmethod
    def create(
        cls,
        base_url: str = "https://api.example.com",
        enable_spy: bool = False,
        config: Optional[ClientConfig] = None,
        **kwargs: Any,
    ) -> MockClient:
        http_client = MockHTTPClient(base_url=base_url)
        mock_client = MockClient(http_client=http_client, config=config, enable_spy=enable_spy, **kwargs)
        return mock_client

    @classmethod
    def from_client_config(cls, config: ClientConfig, enable_spy: bool = False, **kwargs: Any) -> MockClient:
        base_url = config.hostname or "https://api.example.com"
        mock_client = cls.create(base_url=base_url, enable_spy=enable_spy, config=config, **kwargs)  # Pass config here
        if config.auth_strategy is not None:
            mock_client.set_auth_strategy(config.auth_strategy)
        return mock_client

    @classmethod
    def from_real_client(cls, client: Client, enable_spy: bool = False, **kwargs: Any) -> MockClient:
        config = client.config
        mock_client = cls.from_client_config(config=config, enable_spy=enable_spy, **kwargs)
        return mock_client

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
        mock_client.configure_response(method=method, path=path, status_code=status_code, data=data, headers=headers)

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
        if error is not None:
            mock_client.configure_response(method=method, path=path, error=error)
        else:
            mock_client.configure_response(method=method, path=path, status_code=status_code, data=data, headers=headers)

    @classmethod
    def create_mock_client(cls, config: Optional[Union[ClientConfig, Dict[str, Any]]] = None, **kwargs: Any) -> MockClient:
        # Ensure we have a valid config
        if config is None:
            config = ClientConfig(hostname="https://api.example.com", version="v1")
        elif isinstance(config, dict):
            config = ClientConfig(**config)

        # Configure authentication if specified
        if "auth_strategy" in kwargs:
            config.auth_strategy = kwargs["auth_strategy"]
        elif "auth_type" in kwargs:
            auth_type = kwargs["auth_type"].lower()
            auth_config = kwargs.get("auth_config", {})
            auth_mock: Optional[Union[BasicAuthMock, BearerAuthMock, ApiKeyAuthMock, CustomAuthMock, OAuthMock]] = None

            if auth_type == "basic":
                auth_mock = create_basic_auth_mock(username=auth_config.get("username", "user"), password=auth_config.get("password", "pass"))
            elif auth_type == "bearer":
                auth_mock = create_bearer_auth_mock(token=auth_config.get("token", "valid_token"))
            elif auth_type == "apikey":
                header_name = auth_config.get("header_name")
                param_name = auth_config.get("param_name")
                if header_name:
                    auth_mock = create_api_key_auth_mock(api_key=auth_config.get("api_key", "valid_api_key"), header_name=header_name)
                elif param_name:
                    auth_mock = create_api_key_auth_mock(api_key=auth_config.get("api_key", "valid_api_key"), header_name=None, param_name=param_name)
                else:
                    auth_mock = create_api_key_auth_mock(api_key=auth_config.get("api_key", "valid_api_key"))  # Default to header
            elif auth_type == "custom":
                auth_mock = create_custom_auth_mock(
                    header_callback=auth_config.get("header_callback"), param_callback=auth_config.get("param_callback")
                )
            elif auth_type == "oauth":
                auth_mock = create_oauth_mock(
                    client_id=auth_config.get("client_id", "client_id"),
                    client_secret=auth_config.get("client_secret", "client_secret"),
                    token_url=auth_config.get("token_url", "https://example.com/oauth/token"),
                    authorize_url=auth_config.get("authorize_url"),
                    grant_type=auth_config.get("grant_type", "authorization_code"),
                    scope=auth_config.get("scope", "read write"),
                    access_token=auth_config.get("access_token"),
                    refresh_token=auth_config.get("refresh_token"),
                )

            if auth_mock:
                _configure_auth_mock(auth_mock, auth_config)  # Use local helper
                config.auth_strategy = auth_mock.get_auth_strategy()

        # Extract enable_spy from kwargs
        enable_spy = kwargs.pop("enable_spy", False)

        # Create the mock client, passing the finalized config object
        # Filter out factory-specific kwargs before passing to MockClient constructor
        factory_kwargs = {
            "auth_type",
            "auth_config",
            "api_type",
            "api_resources",
            "graphql_config",
            "oauth_config",
            "error_responses",
            "response_patterns",
        }
        client_kwargs = {k: v for k, v in kwargs.items() if k not in factory_kwargs}

        mock_client = cls.create(
            base_url=config.hostname or "https://api.example.com",
            enable_spy=enable_spy,
            config=config,
            **client_kwargs,  # Pass filtered kwargs
        )

        # Configure the mock client with the auth strategy from the config
        if config.auth_strategy is not None:
            mock_client.set_auth_strategy(config.auth_strategy)

        # Add API-specific patterns based on api_type
        api_type = kwargs.get("api_type")
        if api_type:
            patterns = _create_api_patterns(api_type, **kwargs)  # Use local helper
            for pattern in patterns:
                mock_client.configure_response(**pattern)

        # Add common error responses if specified
        if "error_responses" in kwargs:
            _add_error_responses(mock_client, kwargs["error_responses"])  # Use local helper

        # Add response patterns if specified
        patterns = kwargs.get("response_patterns", [])
        for pattern in patterns:
            mock_client.configure_response(**pattern)

        return mock_client


# --- SimpleMockClient Creation (from factory/simple_mock.py) ---


def create_simple_mock_client(**kwargs: Any) -> SimpleMockClient:
    client = SimpleMockClient()

    # Set default response if specified
    if "default_response" in kwargs:
        client.with_default_response(kwargs["default_response"])

    # Add API-specific patterns based on api_type
    api_type = kwargs.get("api_type")
    if api_type:
        patterns = _create_api_patterns(api_type, **kwargs)  # Use local helper
        for pattern in patterns:
            # Adapt pattern for SimpleMockClient's with_response_pattern
            response_dict = {
                "status_code": pattern.get("status_code", 200),
                "json_data": pattern.get("data"),
                "headers": pattern.get("headers"),
                "text_data": pattern.get("text"),  # Assuming text might be used
                "error": pattern.get("error"),
            }
            # Filter out None values
            response_dict = {k: v for k, v in response_dict.items() if v is not None}

            # Ensure method and url_pattern are strings, providing defaults if None
            method = pattern.get("method", "GET") or "GET"
            url_pattern = pattern.get("path", r".*") or r".*"
            client.with_response_pattern(
                method=method,
                url_pattern=url_pattern,  # Use 'path' from MockClient pattern as 'url_pattern'
                response=response_dict,
            )

    # Add common error responses if specified
    if "error_responses" in kwargs:
        _add_error_responses_to_simple_mock(client, kwargs["error_responses"])  # Use local helper

    # Add response patterns if specified
    patterns = kwargs.get("response_patterns", [])
    for pattern in patterns:
        # Adapt pattern for SimpleMockClient's with_response_pattern
        response_dict = {
            "status_code": pattern.get("status_code", 200),
            "json_data": pattern.get("data"),
            "headers": pattern.get("headers"),
            "text_data": pattern.get("text"),
            "error": pattern.get("error"),
        }
        # Filter out None values
        response_dict = {k: v for k, v in response_dict.items() if v is not None}

        # Ensure method and url_pattern are strings, providing defaults if None
        method = pattern.get("method", "GET") or "GET"
        url_pattern = pattern.get("path", r".*") or r".*"
        client.with_response_pattern(
            method=method,
            url_pattern=url_pattern,  # Use 'path' from MockClient pattern as 'url_pattern'
            response=response_dict,
        )

    return client

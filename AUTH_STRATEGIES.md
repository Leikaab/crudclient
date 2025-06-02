# Authentication Strategies in CrudClient

This document explains the authentication strategy pattern implemented in CrudClient and how to use it effectively.

## Overview

CrudClient uses the Strategy Pattern for authentication, allowing different authentication mechanisms to be easily interchangeable. This approach provides several benefits:

1. **Flexibility**: Easily switch between different authentication methods without changing client code
2. **Extensibility**: Add new authentication strategies without modifying existing code
3. **Separation of Concerns**: Authentication logic is isolated from the rest of the client
4. **Testability**: Authentication strategies can be tested independently

## Migration Notice

**As of version 0.8.0**, all authentication strategies have been migrated to use the [apiconfig](https://github.com/apiconfig/apiconfig) library. This provides enhanced features like token validation, expiration handling, and stricter input validation.

### Breaking Changes
- `BearerAuth` now uses `access_token=` parameter instead of `token=`
- Empty credentials now raise `AuthStrategyError` instead of being silently accepted
- Custom header names are no longer supported in `BearerAuth` (use `CustomAuth` instead)
- `ApiKeyAuth` now validates that the API key is not empty

## Available Authentication Strategies

CrudClient provides several built-in authentication strategies (re-exported from apiconfig):

### BearerAuth

Used for Bearer token authentication, commonly used in OAuth 2.0 and JWT-based APIs.

```python
from crudclient.auth import BearerAuth
from crudclient import ClientConfig, Client

# Create a bearer token authentication strategy
auth_strategy = BearerAuth(access_token="your_access_token")

# Use it in your client configuration
config = ClientConfig(
    hostname="https://api.example.com",
    auth=auth_strategy
)
client = Client(config)
```

### BasicAuth

Used for HTTP Basic Authentication.

```python
from crudclient.auth import BasicAuth
from crudclient import ClientConfig, Client

# Create a basic authentication strategy
auth_strategy = BasicAuth(username="your_username", password="your_password")

# Use it in your client configuration
config = ClientConfig(
    hostname="https://api.example.com",
    auth=auth_strategy
)
client = Client(config)
```

### ApiKeyAuth

Used for API key authentication, either in headers or query parameters.

```python
from crudclient.auth import ApiKeyAuth
from crudclient import ClientConfig, Client

# Create an API key authentication strategy (in header)
auth_strategy = ApiKeyAuth(
    api_key="your_api_key",
    header_name="X-API-Key"
)

# Or as a query parameter
auth_strategy = ApiKeyAuth(
    api_key="your_api_key",
    param_name="api_key"  # Will be sent as ?api_key=your_api_key
)

# Use it in your client configuration
config = ClientConfig(
    hostname="https://api.example.com",
    auth=auth_strategy
)
client = Client(config)
```

### CustomAuth

Used for custom authentication mechanisms or when you need dynamic authentication logic.

```python
from crudclient.auth import CustomAuth
from crudclient import ClientConfig, Client

# Create a custom authentication strategy with a callback
def apply_custom_auth(request):
    # This could fetch tokens from a cache, generate signatures, etc.
    request.headers["Authorization"] = "Custom your_dynamic_token"
    request.params["session"] = "your_session_id"
    return request

auth_strategy = CustomAuth(apply_auth=apply_custom_auth)

# Use it in your client configuration
config = ClientConfig(
    hostname="https://api.example.com",
    auth=auth_strategy
)
client = Client(config)
```

## Backward Compatibility

For backward compatibility, CrudClient provides a factory function to create authentication strategies from the old-style configuration:

```python
from crudclient.auth import create_auth_strategy
from crudclient import ClientConfig, Client

# Old style
config = ClientConfig(
    hostname="https://api.example.com",
    api_key="your_token",
    auth_type="bearer"  # or "basic" or "none"
)

# New style (equivalent)
auth_strategy = create_auth_strategy("bearer", "your_token")  # Uses access_token internally
config = ClientConfig(
    hostname="https://api.example.com",
    auth=auth_strategy
)
```

## Creating Custom Authentication Strategies

You can create your own authentication strategies by implementing the `AuthStrategy` abstract base class:

```python
from crudclient.auth import AuthStrategy

class MyCustomAuth(AuthStrategy):
    def __init__(self, token: str, additional_param: str):
        self.token = token
        self.additional_param = additional_param

    def apply_auth(self, request):
        """Apply authentication to the request."""
        request.headers["Authorization"] = f"MyCustom {self.token}"
        request.headers["X-Additional"] = self.additional_param
        return request
```

**Note**: For detailed information on implementing custom strategies, refer to the [apiconfig documentation](https://github.com/apiconfig/apiconfig).

## Error Handling

The new authentication strategies provide better error handling with `AuthStrategyError`:

```python
from crudclient.auth import BearerAuth, BasicAuth, AuthStrategyError

try:
    # This will raise an error for empty tokens
    auth = BearerAuth(access_token="")
except AuthStrategyError as e:
    print(f"Authentication error: {e}")

try:
    # This will raise an error for empty credentials
    auth = BasicAuth(username="", password="secret")
except AuthStrategyError as e:
    print(f"Authentication error: {e}")
```

## Best Practices

1. **Choose the Right Strategy**: Select the authentication strategy that best matches your API's requirements.
2. **Keep Tokens Secure**: Never hardcode tokens or credentials in your code. Use environment variables or secure storage.
3. **Handle Validation Errors**: Always catch `AuthStrategyError` when creating auth strategies with user input.
4. **Token Refresh**: For APIs that require token refresh, use the `CustomAuth` strategy with a callback that handles token refresh logic.
5. **Testing**: When writing tests, you can easily mock authentication strategies or create test-specific implementations.
6. **Migration**: When upgrading from v0.7.x, update `BearerAuth(token=...)` to `BearerAuth(access_token=...)` and handle the new validation errors.

## Migration from v0.7.x

For a complete migration guide, see [CHANGELOG.md](CHANGELOG.md) and the [auth migration documentation](apiconfig_auth_migration/README.md).
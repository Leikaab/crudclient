# `crudclient.auth`

This module provides authentication strategies for the `crudclient`. It defines a base abstract class `AuthStrategy` and several concrete implementations for common authentication schemes.

## Core Concept: `AuthStrategy`

The foundation of this module is the abstract base class `AuthStrategy` (defined in `base.py`). Any authentication mechanism must inherit from this class and implement the following methods:

*   `prepare_request_headers() -> Dict[str, str]`: Returns a dictionary of HTTP headers to be added to the outgoing request.
*   `prepare_request_params() -> Dict[str, str]`: Returns a dictionary of query parameters to be added to the outgoing request URL.

## Available Strategies

The following concrete authentication strategies are provided:

### 1. `BasicAuth`

(Defined in `basic.py`)

Implements HTTP Basic Authentication.

*   **Initialization:** `BasicAuth(username: str, password: str)`
*   **Behavior:** Adds an `Authorization` header with the value `Basic <base64-encoded username:password>`. Does not add any query parameters.

```python
# Example (Conceptual - Assumes client accepts an AuthStrategy)
from crudclient.auth import BasicAuth
# from crudclient import CrudClient # Assuming client import

auth = BasicAuth(username="myuser", password="mypassword")
# client = CrudClient(base_url="...", auth=auth)
```

### 2. `BearerAuth`

(Defined in `bearer.py`)

Implements Bearer Token Authentication.

*   **Initialization:** `BearerAuth(token: str)`
*   **Behavior:** Adds an `Authorization` header with the value `Bearer <token>`. Does not add any query parameters.

```python
# Example (Conceptual - Assumes client accepts an AuthStrategy)
from crudclient.auth import BearerAuth
# from crudclient import CrudClient # Assuming client import

auth = BearerAuth(token="your-secret-token")
# client = CrudClient(base_url="...", auth=auth)
```

### 3. `ApiKeyAuth`

(Defined in `custom.py`)

Implements authentication using an API key sent either via a request header or a query parameter.

*   **Initialization:** `ApiKeyAuth(api_key: str, header_name: Optional[str] = None, param_name: Optional[str] = None)`
    *   Exactly one of `header_name` or `param_name` must be provided.
*   **Behavior:**
    *   If `header_name` is provided, adds a header `{header_name: api_key}`.
    *   If `param_name` is provided, adds a query parameter `{param_name: api_key}`.

```python
# Example: API Key in Header (Conceptual)
from crudclient.auth.custom import ApiKeyAuth # Note: Import from .custom
# from crudclient import CrudClient # Assuming client import

auth_header = ApiKeyAuth(api_key="secret-key", header_name="X-API-Key")
# client_header = CrudClient(base_url="...", auth=auth_header)

# Example: API Key in Query Parameter (Conceptual)
auth_param = ApiKeyAuth(api_key="secret-key", param_name="apiKey")
# client_param = CrudClient(base_url="...", auth=auth_param)
```

### 4. `CustomAuth`

(Defined in `custom.py`)

Provides a flexible way to implement custom authentication logic using callbacks.

*   **Initialization:** `CustomAuth(header_callback: Optional[Callable[[], Dict[str, str]]] = None, param_callback: Optional[Callable[[], Dict[str, str]]] = None)`
    *   At least one callback (`header_callback` or `param_callback`) must be provided.
*   **Behavior:**
    *   Calls `header_callback()` (if provided) to get custom headers. The callback must return a dictionary.
    *   Calls `param_callback()` (if provided) to get custom query parameters. The callback must return a dictionary.

```python
# Example (Conceptual - Assumes client accepts an AuthStrategy)
from crudclient.auth.custom import CustomAuth # Note: Import from .custom
# from crudclient import CrudClient # Assuming client import
import time

def get_expiring_token_header():
    # Logic to fetch or generate a token
    token = f"token-{int(time.time())}"
    return {"X-Custom-Token": token}

auth = CustomAuth(header_callback=get_expiring_token_header)
# client = CrudClient(base_url="...", auth=auth)
```

## Factory Function: `create_auth_strategy`

(Defined in `__init__.py`)

A helper function is available directly from `crudclient.auth` to create common authentication strategies based on string identifiers.

*   **Signature:** `create_auth_strategy(auth_type: str, token=None) -> Optional[AuthStrategy]`
*   **Behavior:**
    *   `auth_type="none"` or `token=None`: Returns `None` (no authentication).
    *   `auth_type="bearer"`: Returns `BearerAuth(token)`. Assumes `token` is a string.
    *   `auth_type="basic"`:
        *   If `token` is a `tuple` `(username, password)`, returns `BasicAuth(username, password)`.
        *   If `token` is a `str` (username), returns `BasicAuth(username, "")`.
        *   Raises `TypeError` for other `token` types.
    *   Any other `auth_type` string: Defaults to returning `BearerAuth(token)`. (Note: This factory does not currently create `ApiKeyAuth` or `CustomAuth` instances).

```python
from crudclient.auth import create_auth_strategy

# No auth
auth_none = create_auth_strategy("none")

# Bearer auth
auth_bearer = create_auth_strategy("bearer", "my-bearer-token")

# Basic auth
auth_basic_tuple = create_auth_strategy("basic", ("user", "pass"))
auth_basic_str = create_auth_strategy("basic", "user_only")

# Unknown type defaults to Bearer
auth_unknown = create_auth_strategy("some_other_type", "some-token")
# auth_unknown is equivalent to BearerAuth("some-token")
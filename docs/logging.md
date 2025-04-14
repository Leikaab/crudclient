# Enhanced Logging and Error Handling in `crudclient`

The `crudclient` library incorporates comprehensive logging using Python's standard `logging` module and provides a structured exception hierarchy. This gives developers valuable insights into the client's behavior, aiding in debugging, monitoring, and robust error handling when interacting with APIs.

## Default Behavior: `NullHandler` and `WARNING` Level

By default, `crudclient` logging is configured for safety and minimal interference with consuming applications:

*   **Default Handler:** It attaches a `logging.NullHandler` to its root logger (`'crudclient'`). This means **no log output will be produced by `crudclient` unless you explicitly configure a handler** in your application.
*   **Default Level:** The root logger `'crudclient'` is set to `logging.WARNING`. Even if you add a handler, only messages with severity `WARNING`, `ERROR`, or `CRITICAL` will be processed by default.

## Why Configure Logging?

Because `crudclient` uses a `NullHandler` by default, you **must** configure the Python `logging` system in your application to actually see or capture log messages from the library. This involves:

1.  **Adding a Handler:** Specify *where* to send log messages (e.g., console, file).
2.  **Setting the Level:** Specify the minimum severity level you want to see (e.g., `INFO`, `DEBUG`).

## Configuring Logging

Here are common ways to configure logging for `crudclient`:

**1. Basic Configuration (Quick Setup)**

Use `logging.basicConfig` for simple scripts or initial debugging. Call this early in your application startup.

```python
import logging
import crudclient # Or your SDK built on crudclient

# Configure basic logging to see INFO level messages and above from ALL loggers
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# To see DEBUG messages (very verbose, includes request/response bodies if enabled):
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Now, when you use crudclient or your SDK, logs will appear
# client = crudclient.Client(...)
# ... operations ...
```

**2. Direct Logger Configuration (More Control)**

Configure the `'crudclient'` logger (or its children) directly for fine-grained control.

```python
import logging
import sys
import crudclient

# 1. Get the desired logger
logger = logging.getLogger('crudclient') # Or 'crudclient.http', 'crudclient.auth', etc.
logger.setLevel(logging.DEBUG) # Set desired level

# 2. Create a handler (e.g., StreamHandler to output to console)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG) # Process DEBUG and above if logger allows

# 3. Create a formatter (optional)
formatter = logging.Formatter('CRUDCLIENT: %(levelname)s [%(name)s] %(message)s')
handler.setFormatter(formatter)

# 4. Add the handler to the logger
logger.addHandler(handler)

# Optional: Prevent propagation if root logger is already configured
# logger.propagate = False

# Now, logs will appear via this handler
# client = crudclient.Client(...)
# ... operations ...
```

**3. Client Configuration Flags for Body Logging**

Within the `ClientConfig`, you can control whether request and response bodies are included in `DEBUG` level logs:

*   `log_request_body` (bool, default `False`): If `True`, includes the request body in `DEBUG` logs.
*   `log_response_body` (bool, default `False`): If `True`, includes the response body in `DEBUG` logs.

```python
from crudclient import Client, ClientConfig

config = ClientConfig(
    base_url="https://api.example.com",
    log_request_body=True,  # Enable request body logging at DEBUG level
    log_response_body=True  # Enable response body logging at DEBUG level
)
client = Client(config=config)

# Ensure logging is configured to DEBUG level to see these bodies
# logging.getLogger('crudclient.http').setLevel(logging.DEBUG)
# ... add handler ...
```

Remember that enabling body logging can expose sensitive data (see "Data Redaction and Sensitivity").

## Logger Hierarchy

`crudclient` uses hierarchical logger names based on the module structure:

*   `crudclient`: Root logger for the library.
*   `crudclient.client`: Main `Client` class logs.
*   `crudclient.config`: Configuration loading logs.
*   `crudclient.http`: General HTTP operations.
    *   `crudclient.http.client`: Specific HTTP client interactions.
    *   `crudclient.http.retry`: Request retry logic.
    *   `crudclient.http.request`: Request preparation.
    *   `crudclient.http.response`: Response processing.
*   `crudclient.auth`: General authentication.
    *   `crudclient.auth.basic`: Basic Authentication.
    *   `crudclient.auth.bearer`: Bearer Token Authentication.
    *   `crudclient.auth.custom`: Custom Authentication strategies.
*   `crudclient.crud`: Generic CRUD operations.
    *   `crudclient.crud.endpoint`: Endpoint interactions.
    *   `crudclient.crud.validation`: Request/response data validation.

Configuring a parent logger (e.g., `crudclient.http`) affects its children unless they are configured more specifically.

## What is Logged?

### HTTP Lifecycle Logging (`crudclient.http.*`)

*   **`DEBUG`:** Extremely detailed logs about the request/response cycle.
    *   Outgoing request: Method, URL, headers (redacted), query parameters. Request body (bytes, redacted) included if `log_request_body=True`.
    *   Incoming response: Status code, reason phrase, headers (redacted). Response body (bytes, redacted) included if `log_response_body=True`.
    *   Details about retry attempts before they happen.
*   **`INFO`:** Higher-level information about HTTP interactions.
    *   Summary log after a request completes (or fails after retries): Method, URL, final status code, duration.
    *   Retry attempts being made: Attempt number, delay, reason (status code or exception), method, URL.

### Error Handling and Exceptions (`crudclient.exceptions`)

`crudclient` uses a custom exception hierarchy, rooted in `CrudClientError`. Errors are typically logged just before an exception is raised.

*   **Exception Hierarchy:**
    *   `CrudClientError`: Base class for all library-specific errors.
    *   `ConfigurationError`: Errors during client configuration.
    *   `NetworkError`: Issues connecting to the server or during data transmission (e.g., timeouts, connection errors). Often wraps `httpx` exceptions. Logged at `ERROR` level.
    *   `APIError`: Base class for errors originating from the API response (HTTP status >= 400). Logged at `WARNING` (4xx) or `ERROR` (5xx) level.
        *   Contains `request` (`httpx.Request`) and `response` (`httpx.Response`) attributes for context.
        *   `AuthenticationError`: Specifically for 401/403 errors. Logged at `WARNING` level.
        *   `ClientError`: Other 4xx errors (e.g., 400 Bad Request, 404 Not Found). Logged at `WARNING` level.
        *   `ServerError`: 5xx errors. Logged at `ERROR` level.
    *   `DataValidationError`: Errors during request/response Pydantic model validation. Logged at `ERROR` level. Contains validation error details (redacted).
    *   `ResponseHandlingError`: Errors during the processing of a successful response (e.g., issues with custom response strategies). Logged at `ERROR` level.

*   **Logging Pattern:** Errors like network issues, 5xx server errors, or validation failures are typically logged at the `ERROR` level before the corresponding exception is raised. Client-side errors (4xx) are logged at the `WARNING` level before raising `APIError` or its subclasses.

*   **Handling Exceptions:** You can catch specific exceptions to handle different error conditions gracefully.

    ```python
    from crudclient import Client
    from crudclient.exceptions import APIError, NetworkError, DataValidationError, AuthenticationError

    client = Client(base_url="https://api.example.com")

    try:
        # Example: Fetch a resource that might not exist or require auth
        resource = client.crud("items").read("item_id_123")
    except AuthenticationError as e:
        logging.error(f"Authentication failed: {e.response.status_code}")
        # Handle token refresh or prompt user for credentials
    except APIError as e:
        # Handle other API errors (e.g., 404 Not Found, 400 Bad Request, 5xx Server Error)
        logging.error(f"API Error: Status={e.response.status_code}, Body={e.response.text}")
        # Implement specific logic based on status code or response body
    except DataValidationError as e:
        logging.error(f"Response data validation failed: {e}")
        # Handle unexpected response structure
    except NetworkError as e:
        logging.error(f"Network error occurred: {e}")
        # Handle connection issues, maybe retry later
    except Exception as e:
        logging.exception("An unexpected error occurred") # Catch-all
    ```

### Authentication Logging (`crudclient.auth.*`)

*   **`DEBUG`:** Logs which authentication strategy is being applied to a request and details about token acquisition/refresh attempts.
*   **`INFO`:** Logs successful token refresh operations.
*   **`ERROR`:** Logs failures during token acquisition or refresh.
*   **Note:** Sensitive credentials (passwords, full tokens, API keys) are **never** logged.

### Data Validation Logging (`crudclient.crud.validation`)

*   **`ERROR`:** Logs Pydantic `ValidationError` when validating outgoing request data or incoming response data against defined models.
    *   The log message includes the model name and structured error details.
    *   Sensitive data within the validation error context is automatically redacted.

## Data Redaction and Sensitivity

`crudclient` automatically attempts to redact sensitive information in logs and exceptions to prevent accidental exposure:

*   **HTTP Headers:** Values for common sensitive headers (e.g., `Authorization`, `Set-Cookie`, `X-Api-Key`) are replaced with `[REDACTED]`.
*   **Request/Response Bodies:** If body logging is enabled (`DEBUG` level with `log_request_body=True` or `log_response_body=True`), the logged bodies are scanned for keys matching common sensitive patterns (e.g., `password`, `token`, `secret`, `apiKey`), and their values are redacted. Bodies are also truncated if they exceed a certain length.
*   **Validation Errors:** Data included in `DataValidationError` logs and exceptions is also subject to redaction based on sensitive key names.

**Important Considerations:**

*   **Verbosity:** `DEBUG` level logging is extremely verbose. Enable it only when necessary for detailed debugging.
*   **Sensitivity:** Despite redaction efforts, be cautious when enabling `DEBUG` logging (especially body logging) in production or when sharing logs. Sensitive information might still be present if it doesn't match standard patterns. Always review logs before sharing.
*   **Performance:** Excessive logging (especially `DEBUG` level with large bodies) can have a minor performance impact. Configure levels appropriately for your environment.

By leveraging `crudclient`'s logging and structured exceptions, you can build more observable and resilient applications. Remember to configure logging according to your application's needs and handle potential exceptions gracefully.
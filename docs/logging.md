# Enhanced Logging in `crudclient`

The `crudclient` library incorporates comprehensive logging using Python's standard `logging` module. This provides developers using the library (especially when building SDKs) with valuable insights into the client's behavior, aiding in debugging and understanding interactions with APIs.

## Why Use Logging?

*   **Debugging:** Trace HTTP requests and responses, identify authentication issues, pinpoint data validation errors, and understand retry logic.
*   **Visibility:** Gain a clearer picture of how `crudclient` interacts with the target API under the hood.

## Enabling Logging

By default, `crudclient` logging is **disabled**. It attaches a `logging.NullHandler` to its root logger (`'crudclient'`). This ensures that `crudclient` won't produce log output unless explicitly configured by the consuming application.

To see logs from `crudclient`, you need to configure the Python `logging` system in your application. Here are a few common ways:

**1. Basic Configuration (Quick Setup)**

Use `logging.basicConfig` at the start of your application. This is often sufficient for simple scripts or initial debugging.

```python
import logging
import crudclient # Or your SDK built on crudclient

# Configure basic logging to see INFO level messages and above
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# To see DEBUG messages (very verbose):
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Now, when you use crudclient or your SDK, logs will appear
# client = crudclient.Client(...)
# ... operations ...
```

**2. Advanced Configuration (More Control)**

For more control over formatting and output destinations (e.g., files, specific streams), configure the `'crudclient'` logger directly.

```python
import logging
import sys
import crudclient # Or your SDK built on crudclient

# Get the crudclient logger
logger = logging.getLogger('crudclient')
logger.setLevel(logging.DEBUG) # Set the desired level for the logger

# Create a handler (e.g., StreamHandler to output to stderr)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.DEBUG) # Set the desired level for the handler

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Prevent logs from propagating to the root logger if basicConfig was also used
# logger.propagate = False

# Now, when you use crudclient or your SDK, logs will appear based on this config
# client = crudclient.Client(...)
# ... operations ...
```

## What is Logged?

`crudclient` logs information across different categories and severity levels:

*   **`DEBUG`:**
    *   **HTTP Lifecycle:** Detailed information about each request and response, including method, URL, headers, and raw request/response bodies (bytes). Very verbose.
    *   **Authentication:** Logs which authentication handler is being applied to a request.
    *   **Configuration:** Logs successful loading of configuration details.

*   **`INFO`:**
    *   **HTTP Retries:** Logs when a request is being retried, including the attempt number, the reason (status code or exception), method, and URL.
    *   **Configuration:** Logs the start of the configuration loading process.

*   **`WARNING`:**
    *   **Authentication:** Logs HTTP 401 (Unauthorized) and 403 (Forbidden) responses.
    *   **Data Validation:** Logs Pydantic `ValidationError` when validating outgoing request data or incoming response data against defined models. Includes the model name and error details.
    *   **Error Handling:** Logs non-authentication related HTTP 4xx client errors (e.g., 400 Bad Request, 404 Not Found). Includes method, URL, and status code.

*   **`ERROR`:**
    *   **Error Handling:** Logs network-level exceptions (e.g., connection errors, timeouts) and HTTP 5xx server errors. Includes method, URL, and status code or exception details.
    *   **Configuration:** Logs Pydantic `ValidationError` encountered during the validation of client configuration.

## Important Considerations

*   **Verbosity:** `DEBUG` level logging is extremely verbose, especially the logging of request/response bodies and headers.
*   **Sensitivity:** Be cautious when enabling `DEBUG` logging in production environments or when sharing logs. Request/response bodies and headers might contain sensitive information (e.g., API keys, personal data, proprietary information). Review and sanitize logs appropriately if necessary.
*   **Performance:** While generally efficient, excessive logging (especially writing large amounts of `DEBUG` data to slow destinations) can have a minor performance impact. Configure levels appropriately for your environment.

By leveraging `crudclient`'s logging, you can significantly improve your development and debugging workflow when interacting with APIs. Remember to configure it according to your application's needs.
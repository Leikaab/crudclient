# `crudclient.testing.simple_mock`

This module provides a lightweight mock client, `SimpleMockClient`, designed for testing applications that use `crudclient` to interact with HTTP APIs. It focuses on defining expected request patterns, returning predefined responses, recording interactions, and providing assertion helpers to verify that the correct requests were made.

## Core Component: `SimpleMockClient`

The primary class is `SimpleMockClient`. You instantiate it directly:

```python
from crudclient.testing.simple_mock import SimpleMockClient

mock_client = SimpleMockClient()
```

## Configuring Responses

You configure the mock client to respond to specific requests using pattern matching.

### `with_response_pattern`

This method defines how the mock client should respond to a request matching a specific pattern.

```python
mock_client.with_response_pattern(
    method="GET",
    url_pattern=r"/api/items/\d+$",
    response={"id": 123, "name": "Test Item"},
    params={"include_details": "true"}, # Optional: Match query parameters
    headers={"X-Custom-Header": "value"}, # Optional: Match request headers
    max_calls=1 # Optional: Limit how many times this pattern can match
)
```

*   **`method`**: The uppercase HTTP method (e.g., "GET", "POST").
*   **`url_pattern`**: A regular expression string to match against the request URL.
*   **`response`**: The response to return if the pattern matches. This can be:
    *   A dictionary (will be returned as JSON with status 200).
    *   A string (will be returned as text with status 200).
    *   A `MockResponse` object (allows specifying status code, headers, etc.).
    *   A callable that accepts the request keyword arguments (`**kwargs`) and returns a `MockResponse`.
*   **Optional Matchers**: You can provide dictionaries for `params`, `data`, `json`, or `headers` to require exact key-value matches in the incoming request for the pattern to apply.
*   **`max_calls`**: Optionally limit the number of times this specific pattern can be successfully matched. Defaults to infinity.

Patterns are checked in the order they are added. The first matching pattern (considering method, URL, optional matchers, and `max_calls`) is used.

### `with_default_response`

If no configured pattern matches an incoming request, a default response is returned. By default, this is a 404 Not Found JSON response. You can override this:

```python
from crudclient.testing.response_builder.response import MockResponse

mock_client.with_default_response(MockResponse(status_code=500, text="Default error"))
# Or with a dictionary/string
mock_client.with_default_response({"error": "Fallback response"})
```

## Simulating API Interaction

Use the `SimpleMockClient` instance in your tests where you would normally use a real `crudclient` instance. It provides standard HTTP methods:

```python
# In your test:
response_body = mock_client.get("/api/items/123", params={"include_details": "true"})
# response_body will be '{"id": 123, "name": "Test Item"}' based on the pattern above
```

Supported methods: `get`, `post`, `put`, `delete`, `patch`. These methods return the response body as a string.

## Verifying Requests

The mock client records every request made to it in the `request_history` attribute. This is a list of `RequestRecord` objects, each containing details about the request (method, url, params, data, json, headers) and the `MockResponse` that was returned.

You can use assertion methods to verify interactions:

### `assert_request_count`

Checks the number of requests matching optional filters.

```python
# Assert exactly one POST request was made to any URL starting with /api/users
mock_client.assert_request_count(1, method="POST", url_pattern=r"^/api/users")

# Assert two requests were made in total
mock_client.assert_request_count(2)
```

### `assert_request_sequence`

Checks if a specific sequence of requests occurred.

```python
mock_client.assert_request_sequence([
    {"method": "POST", "url_pattern": r"/api/users$"},
    {"method": "GET", "url_pattern": r"/api/users/\d+$"},
])
```
This checks if a POST to `/api/users` was followed *at some point* by a GET to `/api/users/<id>`. Use `strict=True` to enforce that the history matches the sequence exactly.

### `assert_request_params`

Checks if requests matching optional filters contain specific query parameters.

```python
# Assert that at least one GET request to /api/items had the 'page' param set to '2'
mock_client.assert_request_params({"page": "2"}, method="GET", url_pattern=r"/api/items")

# Assert that *all* GET requests to /api/items had 'page' set to '2'
mock_client.assert_request_params({"page": "2"}, method="GET", url_pattern=r"/api/items", match_all=True)

# Assert using a validator function
mock_client.assert_request_params({"user_id": lambda x: isinstance(x, str) and len(x) > 0})
```

## Example Usage

```python
import pytest
from crudclient.testing.simple_mock import SimpleMockClient
from crudclient.testing.response_builder.response import MockResponse

def process_user_data(client, user_id):
    # Function under test
    user_details = client.get(f"/api/users/{user_id}", params={"fields": "name,email"})
    client.post("/api/logs", json={"message": f"Processed user {user_id}"})
    return user_details

def test_process_user_data():
    mock_client = SimpleMockClient()

    # Configure responses
    mock_client.with_response_pattern(
        method="GET",
        url_pattern=r"/api/users/123",
        response={"name": "Alice", "email": "alice@example.com"},
        params={"fields": "name,email"} # Require specific params
    )
    mock_client.with_response_pattern(
        method="POST",
        url_pattern=r"/api/logs",
        response=MockResponse(status_code=201) # Respond with 201 Created
    )

    # Call the function under test
    result = process_user_data(mock_client, 123)

    # Assertions
    assert result == '{"name": "Alice", "email": "alice@example.com"}'

    mock_client.assert_request_count(2) # Check total requests
    mock_client.assert_request_sequence([
        {"method": "GET", "url_pattern": r"/api/users/123"},
        {"method": "POST", "url_pattern": r"/api/logs"},
    ])
    mock_client.assert_request_params(
        {"fields": "name,email"},
        method="GET",
        url_pattern=r"/api/users/123"
    )
    # Check JSON payload of the POST request
    post_request = mock_client.request_history[1] # Get the second request record
    assert post_request.method == "POST"
    assert post_request.json == {"message": "Processed user 123"}
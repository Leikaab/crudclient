# crudclient.testing

The `crudclient.testing` module provides a comprehensive testing framework for applications using the `crudclient` library. It offers a variety of test doubles (mocks, stubs, fakes, spies) that can be used to simulate the behavior of the crudclient components in tests.

## Key Components

### Core Test Doubles

- **MockClient (`core.client.MockClient`)**: A mock implementation of the `crudclient.Client` interface. Ideal for testing components that interact with the `Client` class. It allows configuring responses and verifying calls made *to* the client instance itself. It typically requires a separate mock (like `unittest.mock.MagicMock` or `MockHTTPClient`) for the underlying HTTP layer if needed.
- **MockHTTPClient (`core.http_client.MockHTTPClient`)**: A mock implementation of the low-level HTTP client interface (e.g., replacing `requests.Session`). Useful for testing components that directly use the HTTP client or for providing the HTTP layer mock *to* `MockClient`. It focuses on simulating HTTP responses (status codes, data, headers, errors) for specific URL paths and methods.
### Factory

- **MockClientFactory**: A factory for creating and configuring mock client instances.

### Verification

- **Verifier**: Utilities for verifying interactions with mock objects.

### Advanced Doubles (`doubles/`)

- **FakeAPI (`doubles.fake_api.FakeAPI`)**: A sophisticated fake implementation of the `crudclient.API` class, backed by an in-memory `DataStore`. Simulates API behavior, including CRUD operations, relationships, validation, and more. Excellent for integration-style tests without needing a live backend.
- **DataStore (`doubles.data_store.DataStore`)**: An in-memory data store used by `FakeAPI`. Supports collections, relationships, filtering, sorting, validation, soft deletes, and more. Can potentially be used independently for specific data-centric testing needs.
- **StubClient (`doubles.stubs_client.StubClient`)**: A simpler stub implementation of the `crudclient.Client`. Returns predefined responses based on request patterns (method/URL regex). Can simulate network latency and errors. Useful for scenarios where you need basic, predictable client behavior without complex state or interaction verification. Records request history for basic checks.
- **Other Stubs (`doubles/stubs*.py`)**: Basic stubs for other layers like `API` and `CRUD`, providing minimal, non-functional stand-ins.
## Usage Examples

### Basic Mock Client

```python
from crudclient.testing import MockClientFactory

# Create a mock client
mock_client = MockClientFactory.create(base_url="https://api.example.com")

# Configure a response
mock_client.configure_response(
    method="GET",
    path="/users/123",
    status_code=200,
    data={"id": "123", "name": "Test User"}
)

# Use the mock client
response = mock_client.get("/users/123")
assert response.status_code == 200
assert response.json() == {"id": "123", "name": "Test User"}

# Verify the underlying HTTP client mock was called (if MockClient was given one)
# Example: mock_http_layer.request.assert_called_once_with(...)
```

### Using the FakeAPI

```python
from crudclient.testing import FakeAPI
from crudclient.testing.doubles import RelationshipType

# Create a fake API
api = FakeAPI()

# Register endpoints
api.register_endpoint("users", "/users")
api.register_endpoint("posts", "/posts")

# Define relationships
api.define_relationship(
    source_collection="users",
    target_collection="posts",
    relationship_type=RelationshipType.ONE_TO_MANY
)

# Add validation rules
api.add_validation_rule(
    field="email",
    validator_func=lambda x: isinstance(x, str) and "@" in x,
    error_message="Invalid email format",
    collection="users"
)

# Use the API
user = api.users.create({"name": "Test User", "email": "test@example.com"})
post = api.posts.create({"title": "Test Post", "users_id": user["id"]})

# Get user with related posts
user_with_posts = api.users.get(user["id"], include_related=["posts"])
assert len(user_with_posts["posts"]) > 0
```

### Using the StubClient

```python
from crudclient.testing.doubles import StubClient
from crudclient.config import ClientConfig

# Configure the stub
config = ClientConfig(hostname="https://stub.example.com")
stub_client = StubClient(config)

# Add specific responses (using regex patterns)
stub_client.add_response("^GET:/users/\d+$", {"id": 1, "name": "Stub User"})
stub_client.add_response("^POST:/users$", {"id": 2, "name": "New Stub User"})
stub_client.set_default_response({"message": "Default stub response"})
stub_client.set_latency(50) # Simulate 50ms latency

# Use the stub client
user = stub_client.get("/users/1")
assert user["name"] == "Stub User"

new_user = stub_client.post("/users", json_payload={"name": "New Stub User"})
assert new_user["id"] == 2

# Check request history
history = stub_client.get_request_history()
assert len(history) == 2
assert history[0]["method"] == "GET"
```

### Verifying Interactions (with MockClient)

The `MockClient` (often created via `MockClientFactory`) can be used with the `Verifier` for interaction testing.

```python
from crudclient.testing import MockClientFactory, Verifier

# Create a mock client
# Note: For verification, MockClient often uses a MagicMock internally
# or you might provide one for the http_client argument.
mock_client = MockClientFactory.create()

# Configure a response (using MockHTTPClient style)
mock_client.configure_response(
    method="GET",
    path="/users/123",
    status_code=200,
    data={"id": "123", "name": "Test User"}
)

# Use the mock client in your code under test
# e.g., service_that_uses_client.fetch_user("123")
mock_client.get("/users/123") # Simulating the call made by the service

# Verify the interaction on the MockClient instance
Verifier.verify_called_with(mock_client, "get", path="/users/123")

# If you need to verify calls to the underlying HTTP layer mock:
# Verifier.verify_called_with(mock_client.http_client, "request", method="GET", path="/users/123")
```

## Module Structure

The `crudclient.testing` module is organized into the following submodules:

- **core**: Core mock implementations (`MockClient`, `MockHTTPClient`) replacing primary client interfaces.
- **auth**: Mock implementations and helpers for various authentication strategies (Basic, Bearer, API Key, OAuth, etc.).
- **crud**: Mock implementations related to CRUD endpoint operations.
- **doubles**: Advanced, stateful test doubles (`FakeAPI`, `DataStore`) and simpler stubs (`StubClient`).
- **spy**: Components for recording and verifying interactions (used by `Verifier` and potentially `MockClient`).
- **helpers**: General utility functions and classes useful across different tests (e.g., rate limiting simulation, partial response generation).
- **response_builder**: Utilities for constructing complex mock HTTP responses, often used with `MockHTTPClient` or `StubClient`.

## Design Principles

The testing framework is designed with the following principles in mind:

1. **Modularity**: Each component is designed to be used independently or in combination with others.
2. **Flexibility**: The framework supports a wide range of testing scenarios, from simple mocks to sophisticated fakes.
3. **Ease of use**: The API is designed to be intuitive and easy to use.
4. **Realism**: The fake implementations aim to simulate the behavior of real components as closely as possible.
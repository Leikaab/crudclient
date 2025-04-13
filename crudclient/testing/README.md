# crudclient.testing

The `crudclient.testing` module provides a comprehensive testing framework for applications using the `crudclient` library. It offers a variety of test doubles (mocks, stubs, fakes, spies) that can be used to simulate the behavior of the crudclient components in tests.

## Key Components

### Core Test Doubles

- **MockClient (`core.client.MockClient`)**: A mock implementation of the `crudclient.Client` interface. Ideal for testing components that interact with the `Client` class. It allows configuring responses and verifying calls made *to* the client instance itself. It typically requires a separate mock (like `unittest.mock.MagicMock` or `MockHTTPClient`) for the underlying HTTP layer if needed.
- **MockHTTPClient (`core.http_client.MockHTTPClient`)**: A mock implementation of the low-level HTTP client interface (e.g., replacing `requests.Session`). Useful for testing components that directly use the HTTP client or for providing the HTTP layer mock *to* `MockClient`. It focuses on simulating HTTP responses (status codes, data, headers, errors) for specific URL paths and methods.
### Factory

- **MockClientFactory**: A factory for creating and configuring mock client instances.

### Verification

- **Verifier (`verification.Verifier`)**: Implements the Verifier pattern using static methods to assert interactions (calls, arguments, counts) with test doubles (spies, mocks). Raises `VerificationError` on failure.
- **Verification Helpers (`spy.verification_helpers`, `auth.verification`)**: Provide more specific verification functions tailored for `EnhancedSpyBase` objects (e.g., call sequence, timing) or authentication details (headers, tokens, errors). Typically raise `AssertionError`.

### Advanced Doubles (`doubles/`)

- **FakeAPI (`doubles.fake_api.FakeAPI`)**: A sophisticated **fake** implementation of `crudclient.API`. Operates entirely in memory, backed by an internal `DataStore` instance (`fake_api.database`). Simulates API behavior by registering endpoints (`register_endpoint`) which map to `DataStore` collections. Ideal for integration tests requiring realistic API interaction without external dependencies. Supports model conversion.
- **DataStore (`doubles.data_store.DataStore`)**: An in-memory simulation of a relational database, used by `FakeAPI` or standalone. Supports named collections (tables), relationships (foreign keys with integrity checks), validation rules, unique constraints, advanced filtering/sorting, pagination, soft deletes (`_deleted` flag), optimistic locking (`_version` field), and automatic timestamps (`_created_at`, `_updated_at`).
- **StubClient (`doubles.stubs_client.StubClient`)**: A simpler stub implementation of the `crudclient.Client`. Returns predefined responses based on request patterns (method/URL regex). Can simulate network latency and errors. Useful for scenarios where you need basic, predictable client behavior without complex state or interaction verification. Records request history for basic checks.
- **Other Stubs (`doubles/stubs*.py`)**: Basic stubs for other layers like `API` and `CRUD`, providing minimal, non-functional stand-ins.
## Usage Examples

### Basic Mock Client

```python
from crudclient.testing import MockClientFactory, Verifier

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

# Verify the call to the mock client instance
Verifier.verify_called_with(mock_client, "get", path="/users/123")
```

### Using the FakeAPI

```python
from crudclient.testing import FakeAPI
# Assume UserModel and PostModel are defined Pydantic models
# from crudclient.models import BaseModel
# class UserModel(BaseModel): id: int; name: str; email: str
# class PostModel(BaseModel): id: int; title: str; user_id: int

# Create a fake API (creates an internal DataStore)
api = FakeAPI()

# Register endpoints, linking attribute names to DataStore collections and models
users_crud = api.register_endpoint("users", "/users", model=UserModel)
posts_crud = api.register_endpoint("posts", "/posts", collection="post_data", model=PostModel) # Use custom collection name

# Define relationships (using DataStore collection names)
# A user has many posts (posts.user_id -> users.id)
api.define_relationship(
    source_collection="post_data", # Collection with the foreign key
    source_field="user_id",        # The foreign key field
    target_collection="users",     # The referenced collection
    target_field="id",             # The primary key in the target
    relationship_type="many_to_one" # many posts to one user
)

# Add validation rules to the DataStore via FakeAPI
api.add_validation_rule(
    field="email",
    validator_func=lambda x: isinstance(x, str) and "@" in x,
    error_message="Invalid email format",
    collection="users" # Apply only to the 'users' collection
)
api.add_unique_constraint(fields="email", collection="users")

# Use the API via registered attributes (users_crud === api.users)
user_data = {"id": 1, "name": "Test User", "email": "test@example.com"}
created_user = api.users.create(user_data) # Returns UserModel instance
assert created_user.id == 1

post_data = {"id": 101, "title": "Test Post", "user_id": created_user.id}
created_post = api.posts.create(post_data) # Returns PostModel instance
assert created_post.id == 101

# Get user (DataStore handles relationship embedding if defined)
# Note: include_related uses the *source* collection name ('post_data')
retrieved_user = api.users.get(created_user.id, include_related=["post_data"])
# The related posts might be under a key like 'post_data' or derived from the relationship
# assert len(retrieved_user.post_data) == 1 # Exact key depends on implementation detail

# List users with filters (passed to DataStore)
active_users = api.users.list(filters={"is_active": True}) # Assuming default is_active=True in model

# Access underlying DataStore for setup/assertions if needed
assert api.database.get("users", 1)["name"] == "Test User"
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
- **auth**: Mock implementations and verification helpers (`AuthVerificationHelpers`) for various authentication strategies.
- **crud**: Mock implementations related to CRUD endpoint operations.
- **doubles**: Advanced, stateful test doubles (`FakeAPI`, `DataStore`) and simpler stubs (`StubClient`).
- **spy**: Components for recording interactions (`EnhancedSpyBase`) and specific verification helpers (`spy.verification_helpers`).
- **verification**: General interaction verification utilities (`Verifier`).
- **helpers**: General utility functions and classes useful across different tests.
- **response_builder**: Utilities for constructing complex mock HTTP responses.

## Design Principles

The testing framework is designed with the following principles in mind:

1. **Modularity**: Each component is designed to be used independently or in combination with others.
2. **Flexibility**: The framework supports a wide range of testing scenarios, from simple mocks to sophisticated fakes.
3. **Ease of use**: The API is designed to be intuitive and easy to use.
4. **Realism**: The fake implementations aim to simulate the behavior of real components as closely as possible.
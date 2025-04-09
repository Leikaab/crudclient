# crudclient.testing

The `crudclient.testing` module provides a comprehensive testing framework for applications using the `crudclient` library. It offers a variety of test doubles (mocks, stubs, fakes, spies) that can be used to simulate the behavior of the crudclient components in tests.

## Key Components

### Core Mocks

- **MockClient**: A mock implementation of the `crudclient.Client` class.
- **MockHTTPClient**: A mock implementation of the HTTP client used by the `crudclient.Client`.

### Factory

- **MockClientFactory**: A factory for creating and configuring mock client instances.

### Verification

- **Verifier**: Utilities for verifying interactions with mock objects.

### Doubles

- **FakeAPI**: A sophisticated fake implementation of the `crudclient.API` class with an in-memory database.
- **DataStore**: An in-memory data store with support for relationships, filtering, sorting, and more.

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
```

### Verifying Interactions

```python
from crudclient.testing import MockClientFactory, Verifier

# Create a mock client with spy enabled
mock_client = MockClientFactory.create(enable_spy=True)

# Configure a response
mock_client.configure_response(
    method="GET",
    path="/users/123",
    status_code=200,
    data={"id": "123", "name": "Test User"}
)

# Use the mock client
mock_client.get("/users/123")

# Verify the interaction
Verifier.verify_called_with(mock_client, "get", "/users/123")
```

## Module Structure

The `crudclient.testing` module is organized into the following submodules:

- **core**: Core mock implementations of the client and HTTP client.
- **auth**: Mock implementations of authentication strategies.
- **crud**: Mock implementations of CRUD operations.
- **doubles**: Advanced test doubles like FakeAPI and DataStore.
- **spy**: Components for recording and verifying interactions.
- **helpers**: Utility functions and classes for tests.
- **response_builder**: Utilities for constructing mock responses.

## Design Principles

The testing framework is designed with the following principles in mind:

1. **Modularity**: Each component is designed to be used independently or in combination with others.
2. **Flexibility**: The framework supports a wide range of testing scenarios, from simple mocks to sophisticated fakes.
3. **Ease of use**: The API is designed to be intuitive and easy to use.
4. **Realism**: The fake implementations aim to simulate the behavior of real components as closely as possible.
# Downstream Testing Strategies for crudclient

This document provides guidance on testing strategies for applications that depend on the crudclient library. It explains common testing challenges, recommends best practices, and provides concrete examples to help you write effective tests for your crudclient-based code.

## Table of Contents

1. [Introduction](#introduction)
2. [Testing Approaches](#testing-approaches)
3. [Test Organization and Structure](#test-organization-and-structure)
4. [Mocking Strategies](#mocking-strategies)
5. [Test Utilities and Patterns](#test-utilities-and-patterns)
6. [Best Practices for Testable Design](#best-practices-for-testable-design)
7. [Code Examples](#code-examples)
8. [Common Testing Scenarios](#common-testing-scenarios)
9. [Future Considerations](#future-considerations)

## Introduction

### What is Downstream Testing?

Downstream testing refers to testing code that depends on a library or framework - in this case, the crudclient library. When your application uses crudclient to interact with external APIs, you need strategies to test your application code effectively without being hindered by the external dependencies.

### Why is it Important?

Testing code that depends on crudclient presents several challenges:

1. **External Dependencies**: Your tests might depend on external APIs that are slow, unreliable, or have usage limits.
2. **Authentication Complexity**: crudclient supports various authentication strategies that need to be properly mocked or configured in tests.
3. **Response Handling**: The library has sophisticated response handling with different strategies that need to be considered in tests.
4. **Error Scenarios**: Testing error handling is critical but can be difficult to simulate with real APIs.
5. **Type Safety**: The library uses Pydantic models for type safety, which need to be properly integrated into test fixtures.

Effective testing strategies help you overcome these challenges, ensuring your application is reliable and maintainable.

## Testing Approaches

### Unit Testing with Mocks

Unit testing focuses on testing individual components in isolation. When testing code that depends on crudclient, you'll often need to mock the crudclient components to isolate your code from external dependencies.

**Benefits:**
- Fast execution
- No external dependencies
- Ability to test edge cases and error scenarios
- Focused on specific functionality

**Example:**
```python
def test_user_service_get_user(mocker):
    # Mock the crudclient API
    mock_api = mocker.Mock()
    mock_api.users.read.return_value = User(id=1, name="Test User")

    # Initialize the service with the mock
    user_service = UserService(api=mock_api)

    # Test the service method
    user = user_service.get_user(1)

    # Verify the result
    assert user.id == 1
    assert user.name == "Test User"

    # Verify the API was called correctly
    mock_api.users.read.assert_called_once_with("1")
```

### Integration Testing with Real APIs

Integration testing verifies that your code works correctly with the actual crudclient library and external APIs. These tests are valuable for ensuring end-to-end functionality but require careful management.

**Benefits:**
- Tests the actual integration with external APIs
- Verifies that your code works with the real crudclient implementation
- Catches issues that might not be apparent in unit tests

**Considerations:**
- Use a test environment for the external API if possible
- Implement proper test data setup and cleanup
- Consider rate limiting and API usage costs
- Use VCR-like libraries to record and replay API responses

**Example:**
```python
def test_user_service_integration():
    # Initialize the API with test configuration
    config = TestConfig(hostname="https://api.test.example.com")
    api = MyAPI(client_config=config)

    # Initialize the service with the real API
    user_service = UserService(api=api)

    # Test the service method
    user = user_service.get_user(1)

    # Verify the result
    assert user.id == 1
    assert user.name is not None
```

### Test Doubles (Stubs, Fakes)

Test doubles are objects that replace real components in tests. They can be more sophisticated than simple mocks, providing realistic behavior without external dependencies.

**Types of Test Doubles:**
- **Stubs**: Provide canned answers to calls made during the test
- **Fakes**: Have working implementations but use simplified versions of the real component
- **Mocks**: Pre-programmed with expectations about calls they're expected to receive
- **Spies**: Record calls made to them for later verification

**Example of a Fake API Client:**
```python
class FakeUsersCrud:
    def __init__(self):
        self.users = {
            "1": User(id=1, name="Test User")
        }

    def read(self, user_id):
        if user_id not in self.users:
            raise NotFoundError(f"User {user_id} not found")
        return self.users[user_id]

    def list(self):
        return list(self.users.values())

class FakeAPI:
    def __init__(self):
        self.users = FakeUsersCrud()

# In your test
def test_user_service_with_fake():
    user_service = UserService(api=FakeAPI())
    user = user_service.get_user(1)
    assert user.id == 1
    assert user.name == "Test User"
```

## Test Organization and Structure

### Breaking Down Large Test Files

Large test files can become difficult to maintain and understand. Breaking them down into smaller, focused files improves organization and readability.

**Recommendations:**
- Create separate test files for different components or features
- Group related tests together
- Keep test files small and focused on specific functionality
- Use descriptive file names that indicate what's being tested

**Example Directory Structure:**
```
tests/
├── unit/
│   ├── services/
│   │   ├── test_user_service.py
│   │   ├── test_order_service.py
│   │   └── test_product_service.py
│   └── models/
│       ├── test_user_model.py
│       ├── test_order_model.py
│       └── test_product_model.py
└── integration/
    ├── test_user_api.py
    ├── test_order_api.py
    └── test_product_api.py
```

### Creating Shared Test Fixtures and Utilities

Shared fixtures and utilities help keep your tests DRY (Don't Repeat Yourself) and consistent.

**Recommendations:**
- Create fixtures for common test data
- Implement utility functions for repetitive test operations
- Use conftest.py files to share fixtures across multiple test files
- Document fixtures and utilities clearly

**Example conftest.py:**
```python
import pytest
from unittest.mock import Mock

from crudclient.client import Client
from crudclient.config import ClientConfig
from myapp.models import User

@pytest.fixture
def mock_client():
    """Return a mock Client instance."""
    return Mock(spec=Client)

@pytest.fixture
def test_config():
    """Return a test configuration."""
    return ClientConfig(
        hostname="https://api.test.example.com",
        api_key="test_key"
    )

@pytest.fixture
def test_user():
    """Return a test user."""
    return User(id=1, name="Test User", email="test@example.com")
```

### Implementing Consistent Patterns

Consistent patterns for test setup and teardown make tests easier to understand and maintain.

**Recommendations:**
- Use the Arrange-Act-Assert (AAA) pattern for test structure
- Implement consistent setup and teardown procedures
- Use descriptive test names that indicate what's being tested
- Follow a consistent style for assertions and verifications

**Example AAA Pattern:**
```python
def test_user_service_get_user():
    # Arrange
    mock_api = Mock()
    mock_api.users.read.return_value = User(id=1, name="Test User")
    user_service = UserService(api=mock_api)

    # Act
    user = user_service.get_user(1)

    # Assert
    assert user.id == 1
    assert user.name == "Test User"
    mock_api.users.read.assert_called_once_with("1")
```

## Mocking Strategies

### Mocking the Client Class

The `Client` class is responsible for making HTTP requests to the API. Mocking it allows you to control the responses without making actual HTTP requests.

**Example:**
```python
def test_with_mock_client(mocker):
    # Create a mock client
    mock_client = mocker.Mock(spec=Client)

    # Configure the mock to return specific responses
    mock_client.get.return_value = {"id": 1, "name": "Test User"}

    # Use the mock client in your code
    crud = UsersCrud(mock_client)
    user = crud.read("1")

    # Verify the client was called correctly
    mock_client.get.assert_called_once_with("users/1")

    # Verify the result
    assert user.id == 1
    assert user.name == "Test User"
```

### Mocking the API Class

The `API` class is the high-level interface that users interact with. Mocking it allows you to control the behavior of all CRUD operations.

**Example:**
```python
def test_with_mock_api(mocker):
    # Create a mock API
    mock_api = mocker.Mock()

    # Configure the mock to return specific responses
    mock_api.users.read.return_value = User(id=1, name="Test User")
    mock_api.users.list.return_value = [User(id=1, name="Test User")]

    # Use the mock API in your code
    user_service = UserService(api=mock_api)
    user = user_service.get_user(1)

    # Verify the API was called correctly
    mock_api.users.read.assert_called_once_with("1")

    # Verify the result
    assert user.id == 1
    assert user.name == "Test User"
```

### Mocking CRUD Operations

You can mock individual CRUD operations to control their behavior in tests.

**Example:**
```python
def test_with_mock_crud(mocker):
    # Create a mock CRUD instance
    mock_crud = mocker.Mock()

    # Configure the mock to return specific responses
    mock_crud.read.return_value = User(id=1, name="Test User")
    mock_crud.list.return_value = [User(id=1, name="Test User")]

    # Create a mock API that returns the mock CRUD
    mock_api = mocker.Mock()
    mock_api.users = mock_crud

    # Use the mock API in your code
    user_service = UserService(api=mock_api)
    user = user_service.get_user(1)

    # Verify the CRUD operation was called correctly
    mock_crud.read.assert_called_once_with("1")

    # Verify the result
    assert user.id == 1
    assert user.name == "Test User"
```

## Test Utilities and Patterns

### Factory Functions for Test Data

Factory functions help create test data consistently and efficiently.

**Example:**
```python
def create_test_user(id=1, name="Test User", email="test@example.com", **kwargs):
    """Create a test user with default values that can be overridden."""
    data = {
        "id": id,
        "name": name,
        "email": email,
        **kwargs
    }
    return User(**data)

# In your test
def test_user_service():
    user = create_test_user(name="Custom Name")
    assert user.name == "Custom Name"
```

### Mock Response Generators

Mock response generators create realistic API responses for testing.

**Example:**
```python
def generate_user_response(id=1, name="Test User", email="test@example.com", **kwargs):
    """Generate a mock user response."""
    return {
        "id": id,
        "name": name,
        "email": email,
        **kwargs
    }

# In your test
def test_with_mock_response(mocker):
    mock_client = mocker.Mock()
    mock_client.get.return_value = generate_user_response()

    crud = UsersCrud(mock_client)
    user = crud.read("1")

    assert user.id == 1
    assert user.name == "Test User"
```

## Best Practices for Testable Design

### Designing for Testability

Designing your code with testing in mind makes it easier to write effective tests.

**Recommendations:**
- Use dependency injection to make dependencies replaceable in tests
- Keep classes and functions focused on a single responsibility
- Avoid global state and singletons
- Make side effects explicit and controllable

**Example of Testable Design:**
```python
# Hard to test
class UserServiceHard:
    def __init__(self):
        config = ClientConfig(hostname="https://api.example.com")
        self.api = MyAPI(client_config=config)

    def get_user(self, user_id):
        return self.api.users.read(str(user_id))

# Easy to test
class UserServiceEasy:
    def __init__(self, api):
        self.api = api

    def get_user(self, user_id):
        return self.api.users.read(str(user_id))
```

### Separation of Concerns

Separating concerns makes your code more modular and easier to test.

**Recommendations:**
- Separate business logic from API interaction
- Create service layers that encapsulate API calls
- Use repositories or data access objects to abstract data retrieval
- Implement clear boundaries between components

### Error Handling Testing

Testing error handling ensures your code behaves correctly in exceptional situations.

**Example:**
```python
def test_user_service_error_handling(mocker):
    # Mock the API to raise an exception
    mock_api = mocker.Mock()
    mock_api.users.read.side_effect = NotFoundError("User not found")

    # Test the service
    user_service = UserService(api=mock_api)

    # Verify that the exception is handled appropriately
    with pytest.raises(UserNotFoundError):
        user_service.get_user(1)

    # Verify the API was called correctly
    mock_api.users.read.assert_called_once_with("1")
```

## Common Testing Scenarios

### Testing CRUD Operations

CRUD operations are the core functionality of crudclient. Testing them thoroughly ensures your application works correctly with the API.

**Example Testing Create Operation:**
```python
def test_create_user(mocker):
    # Mock the API
    mock_api = mocker.Mock()
    mock_api.users.create.return_value = User(id=1, name="New User", email="new@example.com")

    # Test the service
    user_service = UserService(api=mock_api)
    user_data = {"name": "New User", "email": "new@example.com"}
    user = user_service.create_user(user_data)

    # Verify the API was called correctly
    mock_api.users.create.assert_called_once_with(user_data)

    # Verify the result
    assert user.id == 1
    assert user.name == "New User"
    assert user.email == "new@example.com"
```

### Testing Authentication

Authentication is a critical aspect of API interactions. Testing it ensures your application can authenticate correctly with the API.

**Example Testing Bearer Authentication:**
```python
def test_bearer_auth(mocker):
    # Mock the auth strategy
    mock_auth = mocker.Mock()

    # Configure the mock config with the mock auth
    mock_config = mocker.Mock()
    mock_config.auth = mock_auth

    # Create a client with the mock config
    client = Client(mock_config)

    # Use the client in your code
    client.get("users/1")

    # Verify the auth strategy was used
    mock_auth.apply_auth.assert_called_once()
```

## Future Considerations

### Testing with Asyncio/Async Code

When crudclient adds support for async operations, you'll need strategies for testing async code that depends on the library.

**Considerations for Future Async Testing:**
- Use pytest-asyncio for testing async code
- Create async mock objects and fixtures
- Test async error handling
- Ensure proper cleanup of async resources

### Providing Mock Objects and Factories

To simplify testing for users of your library, consider providing mock objects and factories that they can import directly.

**Example of a Mock API Factory:**
```python
# In your library's test utilities module
def create_mock_api(mocker, **kwargs):
    """Create a mock API with pre-configured responses."""
    mock_api = mocker.Mock()

    # Configure default responses
    mock_users = mocker.Mock()
    mock_users.read.return_value = User(id=1, name="Test User")
    mock_users.list.return_value = [User(id=1, name="Test User")]

    # Attach mock CRUD instances to the mock API
    mock_api.users = mock_users

    return mock_api

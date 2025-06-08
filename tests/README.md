# Testing Guidelines for CRUDClient

## Table of Contents
- [Test Structure and Documentation](#test-structure-and-documentation)
- [Test Organization](#test-organization)
- [Best Practices for Writing Effective Tests](#best-practices-for-writing-effective-tests)
- [Using Fixtures](#using-fixtures)
- [Mocking and Test Isolation](#mocking-and-test-isolation)
- [Running Tests](#running-tests)
- [Coverage](#coverage)

This document provides comprehensive guidelines for creating, organizing, and documenting tests for the CRUDClient library.

## Test Structure and Documentation

### The GIVEN-WHEN-THEN Pattern

All tests should follow the GIVEN-WHEN-THEN pattern, which provides a clear structure for test cases:

* **GIVEN** - What are the initial conditions for the test? This includes any setup, fixtures, or preconditions.
* **WHEN** - What is occurring that needs to be tested? This is the action or behavior being tested.
* **THEN** - What is the expected response or outcome? This includes all assertions and verifications.

#### Example:

```python
def test_bearer_auth_failure(self, bearer_auth_client, mock_request):
    """Test handling of Bearer Authentication failures."""
    # GIVEN
    url = f"{bearer_auth_client.base_url}/users"
    mock_request.get(
        url,
        status_code=401,
        json={"error": "Unauthorized", "message": "Invalid token"}
    )

    # WHEN
    with pytest.raises(AuthenticationError) as excinfo:
        bearer_auth_client.get("/users")

    # THEN
    # Check that the exception contains the error details
    assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
    assert "Invalid token" in str(excinfo.value)

    # Check that the Authorization header was set correctly
    request = mock_request.request_history[0]
    assert "Authorization" in request.headers
    assert request.headers["Authorization"] == "Bearer valid_token"
```

In this example:
- **GIVEN**: We set up a mock request that will return a 401 error
- **WHEN**: We make a request with the bearer_auth_client that should trigger the error
- **THEN**: We verify that the correct exception is raised with the expected details, and that the authorization header was correctly set

### Test Docstrings

Each test function should have a clear docstring that explains:

1. What functionality is being tested
2. Any special conditions or edge cases being tested
3. The expected outcome

Example:
```python
def test_token_refresh_on_401(self, refreshable_token_client, mock_request):
    """
    Test token refresh behavior when receiving a 401 Unauthorized response.

    Verifies that when a 401 response with 'Token expired' message is received,
    the client properly raises an AuthenticationError with the appropriate details.
    """
```

## Test Organization

### Directory Structure

Tests are organized into the following structure:

- `tests/` - Root directory for all tests
  - `unit/` - Unit tests that test individual components in isolation
    - `auth/` - Tests for authentication functionality
    - `client/` - Tests for client functionality
    - `crud/` - Tests for CRUD operations
    - `http/` - Tests for HTTP functionality
  - `integration/` - Tests that verify multiple components working together

### Test Classes and Methods

- Group related tests into test classes
- Name test classes with a `Test` prefix (e.g., `TestAuthFailures`)
- Name test methods with a `test_` prefix followed by a descriptive name
- Organize test methods logically within the class, typically from simple to complex scenarios

## Best Practices for Writing Effective Tests

1. **Test one thing per test**: Each test should verify a single behavior or functionality.

2. **Keep tests independent**: Tests should not depend on the state from other tests.

3. **Use descriptive names**: Test names should clearly indicate what is being tested.

4. **Minimize test setup**: Keep the setup code as minimal as possible to make tests easier to understand.

5. **Use appropriate assertions**: Use specific assertions that provide clear error messages.

6. **Test edge cases**: Include tests for boundary conditions, error cases, and edge scenarios.

7. **Avoid test logic**: Tests should be straightforward without complex conditional logic.

8. **Use fixtures for common setup**: Extract common setup code into fixtures.

9. **Clean up after tests**: Ensure tests clean up any resources they create.

10. **Test both positive and negative scenarios**: Verify both successful operations and error handling.

## Using Fixtures

The project provides several fixtures in the `conftest.py` files to simplify test setup.

### Global Fixtures (tests/conftest.py)

- `base_url`: Returns a base URL for API tests
- `mock_response_factory`: Factory for creating mock response objects
- `api_response_type`: Parametrized fixture for different API response content types
- `temp_file`: Provides a temporary file path
- `manage_env_vars`: Provides functions to safely set/unset environment variables
- `timer`: Context manager for measuring execution time

#### Example Usage:

```python
def test_with_mock_response(mock_response_factory):
    # Create a mock response with custom attributes
    mock_resp = mock_response_factory(
        status_code=201,
        json_data={'id': 123},
        headers={"Content-Type": "application/json"}
    )

    # Use the mock response in your test
    assert mock_resp.status_code == 201
    assert mock_resp.json() == {'id': 123}
```

```python
def test_with_env_vars(manage_env_vars):
    # Unpack the fixture
    set_var, del_var = manage_env_vars

    # Set environment variables for the test
    set_var('API_KEY', 'test-key')

    # Test code that uses environment variables
    # ...

    # Optionally, explicitly delete variables
    del_var('API_KEY')
```

### Unit Test Fixtures (tests/unit/conftest.py)

- Authentication strategy fixtures: `bearer_auth_strategy`, `basic_auth_strategy`, `custom_auth_strategy`
- Client configuration fixtures: `create_mock_client_config`, `default_mock_client_config`
- HTTP mocking: `requests_mocker`
- Test data factories: `create_user_data`, `create_api_response`, `create_paginated_api_response`, `create_error_api_response`

#### Example Usage:

```python
def test_client_initialization(create_mock_client_config):
    # Create a custom client config
    config = create_mock_client_config(
        hostname="https://custom-api.example.com",
        version="v2",
        retries=5
    )

    # Use the config in your test
    client = Client(config)
    assert client.base_url == "https://custom-api.example.com/v2"
```

```python
def test_paginated_response(create_paginated_api_response, requests_mocker):
    # Create mock paginated data
    items = [{"id": i, "name": f"Item {i}"} for i in range(1, 6)]
    response = create_paginated_api_response(
        items=items,
        page=1,
        per_page=5,
        total_items=20,
        total_pages=4
    )

    # Mock the API request
    requests_mocker.get("https://api.example.com/v1/items", **response)

    # Test code that makes the request
    # ...
```

## Mocking and Test Isolation

### Mocking External Dependencies

1. **Use `requests_mock` for HTTP requests**:
   ```python
   def test_api_call(requests_mocker):
       requests_mocker.get(
           "https://api.example.com/users",
           json={"data": [{"id": 1, "name": "User 1"}]}
       )
       # Test code that makes HTTP requests
   ```

2. **Use `unittest.mock` for other dependencies**:
   ```python
   def test_with_mocked_dependency(mocker):
       mock_function = mocker.patch("module.function")
       mock_function.return_value = "mocked result"
       # Test code that uses the mocked function
   ```

3. **Use the `mock_response_factory` for complex response mocking**:
   ```python
   def test_with_complex_response(mock_response_factory):
       mock_resp = mock_response_factory(
           status_code=200,
           json_data={"result": "success"},
           headers={"X-Rate-Limit": "100"}
       )
       # Use mock_resp in your test
   ```

### Test Isolation Guidelines

1. **Reset mocks between tests**: Ensure mocks are reset between tests to prevent test interdependence.

2. **Use fresh fixtures**: Use function-scoped fixtures by default to ensure a clean state for each test.

3. **Avoid global state**: Don't rely on global variables or state that could be modified by other tests.

4. **Clean up resources**: Use teardown code or fixture finalizers to clean up any resources created during tests.

5. **Use appropriate scopes for fixtures**: Use the appropriate scope (`function`, `class`, `module`, or `session`) based on the fixture's purpose and performance considerations.

## Running Tests

### Basic Commands

* `poetry run pytest` - Run all tests
* `poetry run pytest tests/unit` - Run all unit tests
* `poetry run pytest tests/unit/test_todos.py` - Run tests in a specific file
* `poetry run pytest tests/unit/test_todos.py::test_new_todo` - Run a specific test
* `poetry run pytest -v` - Run tests with verbose output
* `poetry run pytest --last-failed` - Rerun only the last failed tests
* `poetry run pytest --setup-show` - Show when fixtures are called relative to test functions

### Running Tests with Different Configurations

1. **Parallel execution**:
   ```
   poetry run pytest -n auto  # Use all available CPU cores
   poetry run pytest -n 4     # Use 4 CPU cores
   ```

2. **Run tests marked with specific markers**:
   ```
   poetry run pytest -m "no_parallel"  # Run tests marked with no_parallel
   ```

3. **Generate coverage reports**:
   ```
   poetry run pytest --cov=crudclient  # Basic coverage
   poetry run pytest --cov=crudclient --cov-report=html  # HTML report
   poetry run pytest --cov=crudclient --cov-report=xml   # XML report
   ```

4. **Run tests with specific verbosity**:
   ```
   poetry run pytest -v   # Verbose
   poetry run pytest -vv  # More verbose
   poetry run pytest -q   # Quiet
   ```

5. **Filter tests by name**:
   ```
   poetry run pytest -k "auth"  # Run tests with 'auth' in the name
   ```

6. **Stop on first failure**:
   ```
   poetry run pytest -x  # Stop after first failure
   ```

7. **Show extra test summary**:
   ```
   poetry run pytest -ra  # Show extra test summary info for all except passed tests
   ```

## Coverage

The project uses [coverage.py](https://coverage.readthedocs.io/) and [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) for measuring test coverage.

### Coverage Configuration

The `.coveragerc` file defines the coverage configuration:

- Source directory: `crudclient`
- Branch coverage is enabled
- Certain files and patterns are excluded from coverage
- HTML reports are generated in the `coverage_html_report` directory

### Running Coverage

```bash
# Run tests with coverage
poetry run pytest --cov=crudclient

# Generate HTML report
poetry run pytest --cov=crudclient --cov-report=html

# Generate XML report (for CI tools)
poetry run pytest --cov=crudclient --cov-report=xml
```

### Viewing Coverage Reports

After generating an HTML report, open `coverage_html_report/index.html` in a web browser to view the detailed coverage report.
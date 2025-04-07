# Test Suite Refactoring Plan

This document outlines the steps required to refactor the existing test suite to fully align with the recommendations in `downstream_testing.md`. The plan addresses unit test restructuring, fixture modularity, test pattern implementation, parallel execution configuration, and integration test structure.

## 1. Unit Test Restructuring

The current unit tests are organized in a flat structure within the `tests/unit/` directory. To better mirror the `crudclient` source code structure, we will reorganize them into subdirectories that match the package structure.

### Current Structure

```
tests/unit/
├── __init__.py
├── test_api.py
├── test_auth_failures.py
├── test_auth_strategies.py
├── test_client_auth.py
├── test_client_data.py
├── test_client_error_handling.py
├── test_client.py
├── test_config.py
├── test_error_handler.py
├── test_http_client.py
├── test_malformed_responses.py
├── test_response_strategies.py
├── test_retry_handler.py
└── http_client_errors/
    ├── __init__.py
    ├── conftest.py
    ├── test_client_errors.py
    ├── test_malformed_responses.py
    ├── test_network_errors.py
    ├── test_retry_behavior.py
    └── test_server_errors.py
```

### Target Structure

```
tests/unit/
├── __init__.py
├── conftest.py  # Unit test-level fixtures
├── client/
│   ├── __init__.py
│   ├── conftest.py  # Client-specific fixtures
│   ├── test_client_base.py  # Renamed from test_client.py
│   ├── test_client_auth.py
│   ├── test_client_data.py
│   └── test_client_error_handling.py
├── crud/
│   ├── __init__.py
│   ├── conftest.py  # CRUD-specific fixtures
│   ├── test_crud_base.py
│   ├── test_crud_operations.py
│   └── test_response_conversion.py
├── auth/
│   ├── __init__.py
│   ├── conftest.py  # Auth-specific fixtures
│   ├── test_auth_base.py
│   ├── test_auth_bearer.py
│   ├── test_auth_custom.py
│   ├── test_auth_failures.py
│   └── test_auth_strategies.py
├── http/
│   ├── __init__.py
│   ├── conftest.py  # HTTP-specific fixtures
│   ├── test_http_client.py
│   ├── test_retry_handler.py
│   ├── test_error_handler.py
│   └── errors/  # Renamed from http_client_errors
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_client_errors.py
│       ├── test_malformed_responses.py
│       ├── test_network_errors.py
│       ├── test_retry_behavior.py
│       └── test_server_errors.py
├── response_strategies/
│   ├── __init__.py
│   ├── conftest.py  # Response strategies-specific fixtures
│   ├── test_default_strategy.py
│   └── test_path_based_strategy.py
└── api/
    ├── __init__.py
    ├── conftest.py  # API-specific fixtures
    └── test_api.py
```

### File Movement Plan

1. Create the new directory structure
2. Move existing test files to their appropriate locations:
   - `test_api.py` → `tests/unit/api/test_api.py`
   - `test_auth_failures.py` → `tests/unit/auth/test_auth_failures.py`
   - `test_auth_strategies.py` → `tests/unit/auth/test_auth_strategies.py`
   - `test_client_auth.py` → `tests/unit/client/test_client_auth.py`
   - `test_client_data.py` → `tests/unit/client/test_client_data.py`
   - `test_client_error_handling.py` → `tests/unit/client/test_client_error_handling.py`
   - `test_client.py` → `tests/unit/client/test_client_base.py`
   - `test_config.py` → `tests/unit/test_config.py` (remains at root level as it's a core component)
   - `test_error_handler.py` → `tests/unit/http/test_error_handler.py`
   - `test_http_client.py` → `tests/unit/http/test_http_client.py`
   - `test_malformed_responses.py` → `tests/unit/http/errors/test_malformed_responses.py`
   - `test_response_strategies.py` → `tests/unit/response_strategies/test_response_strategies.py` (may be split into multiple files)
   - `test_retry_handler.py` → `tests/unit/http/test_retry_handler.py`
   - Move all files in `http_client_errors/` to `tests/unit/http/errors/`

3. Update imports in test files to reflect the new structure
4. Create `__init__.py` files in each new directory

## 2. Fixture Modularity

Currently, fixtures are defined within individual test files, with only one `conftest.py` file in the `http_client_errors` directory. We will implement a hierarchical fixture organization using `conftest.py` files at different levels.

### Fixture Organization Strategy

#### Global Fixtures (`tests/conftest.py`)

Global fixtures that are used across both unit and integration tests:

- Base configuration fixtures
- Logging fixtures
- Common utility functions
- Session-scoped fixtures for expensive operations

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for API tests."""
    return "https://api.example.com"

@pytest.fixture
def mock_response():
    """Create a mock response object with common attributes."""
    mock = Mock()
    mock.status_code = 200
    mock.json.return_value = {"status": "success"}
    return mock
```

#### Unit Test Fixtures (`tests/unit/conftest.py`)

Fixtures specific to unit tests:

- Mock client configurations
- Mock API responses
- Common test data for unit tests

```python
# tests/unit/conftest.py
import pytest
from unittest.mock import Mock, patch
import requests_mock

from crudclient.config import ClientConfig

@pytest.fixture
def mock_client_config():
    """Return a mock client configuration."""
    return ClientConfig(hostname="https://api.example.com")

@pytest.fixture
def requests_mocker():
    """Provide a requests mocker for HTTP request mocking."""
    with requests_mock.Mocker() as m:
        yield m
```

#### Integration Test Fixtures (`tests/integration/conftest.py`)

Fixtures specific to integration tests:

- Real API configurations
- Test data setup and cleanup
- Service-specific configurations

```python
# tests/integration/conftest.py
import pytest
from crudclient.config import ClientConfig

@pytest.fixture(scope="session")
def integration_config():
    """Return a configuration for integration tests."""
    return ClientConfig(
        hostname="https://jsonplaceholder.typicode.com",
        timeout=10
    )
```

#### Module-Specific Fixtures

Each module will have its own `conftest.py` with fixtures specific to that module:

- `tests/unit/client/conftest.py`: Client-specific fixtures
- `tests/unit/crud/conftest.py`: CRUD-specific fixtures
- `tests/unit/auth/conftest.py`: Auth-specific fixtures
- `tests/unit/http/conftest.py`: HTTP-specific fixtures
- `tests/unit/response_strategies/conftest.py`: Response strategies-specific fixtures
- `tests/integration/<service_name>/conftest.py`: Service-specific fixtures

Example for client module:

```python
# tests/unit/client/conftest.py
import pytest
from unittest.mock import Mock

from crudclient.client import Client
from crudclient.config import ClientConfig

@pytest.fixture
def mock_client():
    """Return a mock Client instance."""
    return Mock(spec=Client)

@pytest.fixture
def real_test_client(mock_client_config):
    """Return a real Client instance with test configuration."""
    return Client(mock_client_config)
```

## 3. Test Pattern Implementation

We will mandate the consistent use of the Arrange-Act-Assert (AAA) pattern in all tests and specify preferred mocking strategies.

### Arrange-Act-Assert Pattern

All tests should follow the AAA pattern:

1. **Arrange**: Set up the test data, fixtures, and conditions
2. **Act**: Execute the code being tested
3. **Assert**: Verify the results

Example implementation:

```python
def test_client_get_request(mock_client_config, requests_mocker):
    # Arrange
    client = Client(mock_client_config)
    requests_mocker.get(
        "https://api.example.com/users/1",
        json={"id": 1, "name": "Test User"}
    )
    
    # Act
    response = client.get("users/1")
    
    # Assert
    assert response == {"id": 1, "name": "Test User"}
```

### Mocking Strategies

#### Preferred Approach: Dependency Injection with `mocker`

Use the `mocker` fixture from `pytest-mock` to create mock objects and inject them into the classes under test:

```python
def test_api_with_mock_client(mocker):
    # Create a mock client
    mock_client = mocker.Mock(spec=Client)
    mock_client.get.return_value = {"id": 1, "name": "Test User"}
    
    # Inject the mock client into the API
    api = API(client=mock_client)
    
    # Use the API with the mock client
    result = api.users.read("1")
    
    # Verify the client was called correctly
    mock_client.get.assert_called_once_with("users/1")
    assert result == {"id": 1, "name": "Test User"}
```

#### Test Data Factories

Create factory functions for generating test data:

```python
# tests/unit/conftest.py
@pytest.fixture
def create_user_data():
    """Factory fixture to create user test data."""
    def _create(id=1, name="Test User", email="test@example.com", **kwargs):
        return {
            "id": id,
            "name": name,
            "email": email,
            **kwargs
        }
    return _create
```

#### Mock Response Generators

Create generators for mock API responses:

```python
# tests/unit/conftest.py
@pytest.fixture
def create_api_response():
    """Factory fixture to create API response data."""
    def _create(status_code=200, data=None, error=None):
        response = {
            "status_code": status_code,
            "headers": {"Content-Type": "application/json"}
        }
        
        if data is not None:
            response["json"] = {"data": data}
        
        if error is not None:
            response["json"] = {"error": error}
            
        return response
    return _create
```

## 4. Parallel Execution Configuration

We will set up `pytest-xdist` for parallel test execution to improve test performance.

### Setup Steps

1. Add `pytest-xdist` to development dependencies in `pyproject.toml`:

```toml
[tool.poetry.group.dev.dependencies]
pytest-xdist = "^3.5.0"
```

2. Configure `pytest.ini` for parallel execution:

```ini
[pytest]
testpaths =
    crudclient/*/tests
    tests/

# Set verbosity level and enable parallel execution
addopts = -ra -q -n auto

# Specify patterns for test file discovery
python_files = test_*.py
```

3. Create a custom scheduler in the root `conftest.py` to handle tests marked with `no_parallel`:

```python
# tests/conftest.py
def pytest_xdist_make_scheduler(config, log):
    from xdist.scheduler import LoadScheduling
    
    class CustomScheduling(LoadScheduling):
        def _split_scope(self, nodeid):
            if "no_parallel" in nodeid:
                # Run tests marked with no_parallel on the first worker only
                return "no_parallel"
            return super()._split_scope(nodeid)
    
    return CustomScheduling(config, log)
```

4. Mark integration tests that modify external resources with `@pytest.mark.no_parallel`:

```python
@pytest.mark.no_parallel
def test_create_resource(api):
    # Test implementation that modifies external resources
    pass
```

## 5. Integration Test Structure

The current integration test structure (`tests/integration/<service_name>/`) is appropriate and aligns with the document's principles. We will maintain this structure but ensure that:

1. Each service directory has its own `conftest.py` with service-specific fixtures
2. Tests follow the AAA pattern
3. Tests that modify external resources are marked with `@pytest.mark.no_parallel`
4. Test data setup and cleanup is properly handled

Example structure:

```
tests/integration/
├── __init__.py
├── conftest.py  # Common integration test fixtures
├── jsonplaceholder/
│   ├── __init__.py
│   ├── conftest.py  # JSONPlaceholder-specific fixtures
│   ├── test_posts.py
│   └── test_users.py
├── tripletex/
│   ├── __init__.py
│   ├── conftest.py  # Tripletex-specific fixtures
│   ├── test_auth.py
│   ├── test_countries.py
│   └── test_suppliers.py
└── fiken/
    ├── __init__.py
    ├── conftest.py  # Fiken-specific fixtures
    ├── test_companies.py
    └── test_invoices.py
```

## 6. Verification

After completing the refactoring, we will run all tests in parallel to ensure the refactoring is successful:

```bash
poetry run pytest -n auto
```

This will verify that:

1. All tests pass after the refactoring
2. Tests can run in parallel without conflicts
3. Tests marked with `@pytest.mark.no_parallel` run sequentially

## Implementation Steps

1. **Preparation**:
   - Back up the current test suite
   - Create a new branch for the refactoring

2. **Unit Test Restructuring**:
   - Create the new directory structure
   - Move test files to their appropriate locations
   - Update imports in test files

3. **Fixture Modularity**:
   - Create `conftest.py` files at each level
   - Move fixtures from test files to appropriate `conftest.py` files
   - Update test files to use the fixtures from `conftest.py`

4. **Test Pattern Implementation**:
   - Refactor tests to follow the AAA pattern
   - Implement consistent mocking strategies
   - Create test data factories and mock response generators

5. **Parallel Execution Configuration**:
   - Add `pytest-xdist` to development dependencies
   - Configure `pytest.ini` for parallel execution
   - Create a custom scheduler in the root `conftest.py`
   - Mark tests that modify external resources with `@pytest.mark.no_parallel`

6. **Integration Test Structure**:
   - Create `conftest.py` files for each service
   - Ensure tests follow the AAA pattern
   - Mark tests that modify external resources with `@pytest.mark.no_parallel`

7. **Verification**:
   - Run all tests in parallel to ensure the refactoring is successful
   - Fix any issues that arise

## Conclusion

This refactoring plan will align the test suite with the recommendations in `downstream_testing.md`, resulting in a more maintainable, efficient, and effective test suite. The restructured tests will be easier to understand, maintain, and extend, and will provide better test coverage for the crudclient library.
# Test Migration Guide

[← Back to Main README](./README.md)

## Overview
Guidelines for updating tests during the apiconfig authentication migration.

## Test Categories

### Unit Tests
- Test individual functions/classes in isolation
- All dependencies mocked
- Focus: Single component behavior

### Component Tests
- Test interaction between crudclient modules
- External dependencies mocked
- Focus: Internal integration

### Integration Tests
- Test against real external systems
- No mocking of external services
- Focus: End-to-end functionality

## Test Migration Strategy

### Tests to Delete
Remove unit tests that verify apiconfig's internal behavior:
- Basic auth header encoding
- Bearer token formatting
- Empty credential handling (when not testing crudclient's response)
- Parameter validation logic

### Tests to Keep
Preserve tests that verify crudclient's behavior:
- Error propagation from auth failures
- Client integration with auth strategies
- Request/response flow with authentication
- API-specific authentication scenarios

## Test File Changes

### Before Migration
```
tests/unit/auth/strategies/
├── test_basic_auth.py      # DELETE
├── test_bearer_auth.py     # DELETE
├── test_api_key_auth.py    # DELETE
└── test_custom_auth.py     # DELETE

tests/unit/auth/
├── test_basic_failures.py  # KEEP & UPDATE
├── test_bearer_failures.py # KEEP & UPDATE
└── test_custom_failures.py # KEEP & UPDATE
```

### After Migration
```
tests/unit/auth/
├── test_basic_failures.py
├── test_bearer_failures.py
└── test_custom_failures.py
```

## Examples of Tests to Delete

### Unit Tests Testing apiconfig Internals

From `tests/unit/auth/strategies/test_basic_auth.py`:
```python
# DELETE - Tests apiconfig's base64 encoding:
def test_prepare_request_headers(self):
    auth = BasicAuth(username="user", password="pass")
    headers = auth.prepare_request_headers()
    expected_token = base64.b64encode(b"user:pass").decode("ascii")
    assert headers == {"Authorization": f"Basic {expected_token}"}
```

From `tests/unit/auth/strategies/test_bearer_auth.py`:
```python
# DELETE - Tests apiconfig's header formatting:
def test_prepare_request_headers(self):
    auth = BearerAuth(token="test_token")
    headers = auth.prepare_request_headers()
    assert headers == {"Authorization": "Bearer test_token"}
```

## Examples of Tests to Keep

### Component Tests

From `tests/unit/auth/test_basic_failures.py`:
```python
# KEEP - Tests crudclient's error handling:
@pytest.mark.asyncio
async def test_auth_basic_failure_empty_creds(
    mock_client_auth_response_factory, mock_network_client
):
    """Test that empty credentials are properly handled"""
    # Tests how crudclient handles auth errors
```

From `tests/unit/client/test_client_auth.py`:
```python
# KEEP - Tests client integration:
def test_client_uses_bearer_auth_strategy(testing_api_url):
    """Test that the client properly integrates with auth strategies"""
    auth_strategy = BearerAuth(access_token="test_token")  # Updated parameter
    api_client = APIClient(
        base_url=testing_api_url,
        auth_strategy=auth_strategy
    )
    # Tests that auth is properly applied to requests
```

## Common Test Updates

### 1. Update BearerAuth Parameter

**Before**:
```python
auth = BearerAuth(token="test_token")
```

**After**:
```python
auth = BearerAuth(access_token="test_token")
```

### 2. Update Exception Types

**Before**:
```python
with pytest.raises(TypeError):
    auth = CustomAuth(apply_auth="not a function")
```

**After**:
```python
with pytest.raises(AuthStrategyError):
    auth = CustomAuth(apply_auth="not a function")
```

### 3. Handle New Validation

**Before** (test passes):
```python
auth = BasicAuth(username="", password="")  # No error
```

**After** (update test):
```python
with pytest.raises(AuthStrategyError, match="Username cannot be empty"):
    auth = BasicAuth(username="", password="pass")
```

## Integration Test Example

From `tests/integration/fiken_resources/setup.py`:
```python
# Update parameter name:
# Before:
self.auth_strategy = BearerAuth(token=self.api_key)

# After:
self.auth_strategy = BearerAuth(access_token=self.api_key)
```

## Test Migration Checklist

- [ ] Delete `tests/unit/auth/strategies/` directory
- [ ] Update all `token=` to `access_token=`
- [ ] Update exception types from `TypeError` to `AuthStrategyError`
- [ ] Add validation tests for empty credentials
- [ ] Update import paths to single `auth` module
- [ ] Run full test suite to verify
- [ ] Update test documentation

## Key Principle

**Test Ownership**: Test how crudclient uses auth strategies, not how auth strategies work internally. Delegate internal auth strategy testing to apiconfig.
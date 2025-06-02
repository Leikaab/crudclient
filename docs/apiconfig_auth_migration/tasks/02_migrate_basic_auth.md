# Task 2: Migrate BasicAuth Only

[← Back to Incremental Implementation Plan](../05_incremental_implementation_plan.md)

## Objective
Migrate only the `BasicAuth` class to use `apiconfig` implementation while keeping other auth classes unchanged.

## Prerequisites
- Task 1 completed successfully
- All tests passing after BearerAuth migration

## Implementation Steps

### Step 2.1: Update imports in `__init__.py`
**File**: `/workspace/crudclient/auth/__init__.py`

Replace the BasicAuth import:
```python
# FROM:
from .basic import BasicAuth

# TO:
from apiconfig.auth.strategies.basic import BasicAuth
```

### Step 2.2: Delete the old BasicAuth file
```bash
rm /workspace/crudclient/auth/basic.py
```

### Step 2.3: Run BasicAuth-specific tests
```bash
# Unit tests for BasicAuth
pytest tests/unit/auth/strategies/test_basic.py -xvs

# Component tests that use BasicAuth
pytest tests/unit/auth/test_basic_failures.py -xvs
pytest tests/unit/client/test_client_auth.py::test_basic_auth -xvs
```

### Step 2.4: Fix test failures

#### Handle empty credential validation
Old behavior allowed empty username/password, new behavior raises `AuthStrategyError`.

Update tests expecting empty credentials:
```python
# OLD:
auth = BasicAuth(username="", password="pass")
# No exception

# NEW:
with pytest.raises(AuthStrategyError, match="Username cannot be empty"):
    auth = BasicAuth(username="", password="pass")

with pytest.raises(AuthStrategyError, match="Password cannot be empty"):
    auth = BasicAuth(username="user", password="")
```

#### Update any integration test setups
Check integration test setup files that might use BasicAuth:
- `tests/integration/fiken_resources/setup.py`
- `tests/integration/oneflow_resources/setup.py`

### Step 2.5: Verify all tests pass
```bash
# Run all auth-related tests
pytest tests/unit/auth/ -xvs
pytest tests/unit/client/test_client_auth.py -xvs

# Run integration tests to ensure no regression
pytest tests/integration/ -xvs
```

## Success Criteria
- ✅ BasicAuth imported from apiconfig
- ✅ Old basic.py file deleted
- ✅ All BasicAuth tests updated and passing
- ✅ BearerAuth still working (from Task 1)
- ✅ No regression in integration tests

## Rollback Plan
If issues arise:
1. Restore the import in `__init__.py`
2. Restore the `basic.py` file from git
3. Revert test changes

## Time Estimate
20 minutes (faster than Task 1 since pattern is established)

## Notes
- BasicAuth is simpler than BearerAuth (no parameter name changes)
- Main change is validation of empty credentials
- Integration tests should continue working if they use valid credentials

[← Previous: Task 1](./01_migrate_bearer_auth.md) | [Continue to Task 3: Migrate ApiKeyAuth →](./03_migrate_api_key_auth.md)
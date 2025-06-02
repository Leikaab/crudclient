# Task 1: Migrate BearerAuth Only

[← Back to Incremental Implementation Plan](../05_incremental_implementation_plan.md)

## Objective
Migrate only the `BearerAuth` class to use `apiconfig` implementation while keeping all other auth classes unchanged.

## Prerequisites
- All existing tests passing
- Understanding of breaking change: `token=` → `access_token=`

## Implementation Steps

### Step 1.1: Update imports in `__init__.py`
**File**: `/workspace/crudclient/auth/__init__.py`

Replace the BearerAuth import:
```python
# FROM:
from .bearer import BearerAuth

# TO:
from apiconfig.auth.strategies.bearer import BearerAuth
```

### Step 1.2: Delete the old BearerAuth file
```bash
rm /workspace/crudclient/auth/bearer.py
```

### Step 1.3: Run BearerAuth-specific tests
```bash
# Unit tests for BearerAuth
pytest tests/unit/auth/strategies/test_bearer.py -xvs

# Component tests that use BearerAuth
pytest tests/unit/auth/test_bearer_failures.py -xvs
pytest tests/unit/client/test_client_auth.py::test_bearer_auth -xvs
```

### Step 1.4: Fix test failures

#### Update parameter name in tests
Search for `BearerAuth(token=` and replace with `BearerAuth(access_token=`:

**Files to update**:
- `tests/unit/auth/strategies/test_bearer.py`
- `tests/unit/auth/test_bearer_failures.py`
- `tests/unit/client/test_client_auth.py`
- Any integration test setup files using BearerAuth

#### Handle empty token validation
Old behavior allowed empty tokens, new behavior raises `AuthStrategyError`.

Update tests expecting empty tokens to assert the exception:
```python
# OLD:
auth = BearerAuth(token="")
# No exception

# NEW:
with pytest.raises(AuthStrategyError, match="Access token cannot be empty"):
    auth = BearerAuth(access_token="")
```

### Step 1.5: Verify all tests pass
```bash
# Run all auth-related tests
pytest tests/unit/auth/ -xvs
pytest tests/unit/client/test_client_auth.py -xvs

# Run integration tests to ensure no regression
pytest tests/integration/ -xvs
```

## Success Criteria
- ✅ BearerAuth imported from apiconfig
- ✅ Old bearer.py file deleted
- ✅ All BearerAuth tests updated and passing
- ✅ No regression in integration tests
- ✅ Other auth strategies still work unchanged

## Rollback Plan
If issues arise:
1. Restore the import in `__init__.py`
2. Restore the `bearer.py` file from git
3. Revert test changes

## Time Estimate
30 minutes

## Notes
- This is the first auth migration, so take time to understand the pattern
- The `header_name` parameter is no longer supported (always uses "Authorization")
- Token expiration and refresh are now available but not required for basic usage

[Continue to Task 2: Migrate BasicAuth →](./02_migrate_basic_auth.md)
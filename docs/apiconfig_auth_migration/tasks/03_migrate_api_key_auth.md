# Task 3: Migrate ApiKeyAuth Only

[← Back to Incremental Implementation Plan](../05_incremental_implementation_plan.md)

## Objective
Migrate only the `ApiKeyAuth` class to use `apiconfig` implementation while keeping CustomAuth unchanged in the same file.

## Prerequisites
- Tasks 1-2 completed successfully
- All tests passing after BasicAuth migration

## Implementation Steps

### Step 3.1: Update imports in `__init__.py`
**File**: `/workspace/crudclient/auth/__init__.py`

Replace the ApiKeyAuth import:
```python
# FROM:
from .custom import ApiKeyAuth, CustomAuth

# TO:
from apiconfig.auth.strategies.api_key import ApiKeyAuth
from .custom import CustomAuth  # Keep CustomAuth for now
```

### Step 3.2: Remove ApiKeyAuth from custom.py
**File**: `/workspace/crudclient/auth/custom.py`

Remove the ApiKeyAuth class definition but keep CustomAuth:
- Delete the ApiKeyAuth class (approximately lines will vary)
- Keep all imports that CustomAuth needs
- Remove any imports only used by ApiKeyAuth

### Step 3.3: Run ApiKeyAuth-specific tests
```bash
# Unit tests for ApiKeyAuth
pytest tests/unit/auth/strategies/test_api_key.py -xvs

# Component tests that might use ApiKeyAuth
pytest tests/unit/auth/test_custom_failures.py -xvs
pytest tests/unit/client/test_client_auth.py -xvs -k "api_key"
```

### Step 3.4: Fix test failures

#### Handle stricter validation
The apiconfig version validates more strictly:

```python
# OLD: Allowed empty API key
auth = ApiKeyAuth(api_key="", location="header", key_name="X-API-Key")

# NEW: Raises exception
with pytest.raises(AuthStrategyError, match="API key cannot be empty"):
    auth = ApiKeyAuth(api_key="", location="header", key_name="X-API-Key")
```

#### Update location validation
```python
# OLD: Silent failure or default behavior
auth = ApiKeyAuth(api_key="key", location="invalid", key_name="X-API-Key")

# NEW: Raises exception
with pytest.raises(AuthStrategyError, match="Invalid location"):
    auth = ApiKeyAuth(api_key="key", location="invalid", key_name="X-API-Key")
```

### Step 3.5: Verify all tests pass
```bash
# Run all auth-related tests
pytest tests/unit/auth/ -xvs
pytest tests/unit/client/test_client_auth.py -xvs

# Specifically verify CustomAuth still works
pytest tests/unit/auth/strategies/test_custom.py -xvs
```

## Success Criteria
- ✅ ApiKeyAuth imported from apiconfig
- ✅ CustomAuth still in custom.py and working
- ✅ All ApiKeyAuth tests updated and passing
- ✅ Previous migrations (BearerAuth, BasicAuth) still working
- ✅ No regression in other tests

## Rollback Plan
If issues arise:
1. Restore the import in `__init__.py`
2. Restore the ApiKeyAuth class in `custom.py`
3. Revert test changes

## Time Estimate
25 minutes

## Notes
- This is trickier because ApiKeyAuth and CustomAuth are in the same file
- Be careful not to break CustomAuth while removing ApiKeyAuth
- The apiconfig version has stricter validation for location parameter
- Valid locations are "header" and "query" only

[← Previous: Task 2](./02_migrate_basic_auth.md) | [Continue to Task 4: Migrate CustomAuth →](./04_migrate_custom_auth.md)
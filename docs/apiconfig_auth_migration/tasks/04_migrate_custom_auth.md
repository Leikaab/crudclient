# Task 4: Migrate CustomAuth Only

[← Back to Incremental Implementation Plan](../05_incremental_implementation_plan.md)

## Objective
Migrate the `CustomAuth` class to use `apiconfig` implementation, completing the migration of all auth strategies.

## Prerequisites
- Tasks 1-3 completed successfully
- All tests passing after ApiKeyAuth migration

## Implementation Steps

### Step 4.1: Update imports in `__init__.py`
**File**: `/workspace/crudclient/auth/__init__.py`

Replace the CustomAuth import:
```python
# FROM:
from .custom import CustomAuth

# TO:
from apiconfig.auth.strategies.custom import CustomAuth
```

### Step 4.2: Delete the custom.py file
```bash
# Now that both ApiKeyAuth and CustomAuth are migrated
rm /workspace/crudclient/auth/custom.py
```

### Step 4.3: Run CustomAuth-specific tests
```bash
# Unit tests for CustomAuth
pytest tests/unit/auth/strategies/test_custom.py -xvs

# Component tests that use CustomAuth
pytest tests/unit/auth/test_custom_failures.py -xvs
pytest tests/unit/client/test_client_auth.py -xvs -k "custom"
```

### Step 4.4: Fix test failures

#### Exception type changes
```python
# OLD: Raises TypeError for invalid callbacks
with pytest.raises(TypeError):
    auth = CustomAuth(apply_auth="not a callable")

# NEW: Raises AuthStrategyError
with pytest.raises(AuthStrategyError, match="apply_auth must be callable"):
    auth = CustomAuth(apply_auth="not a callable")
```

#### Handle new validation
The apiconfig version validates that callbacks are actually callable:
```python
# Update tests that expect TypeError to expect AuthStrategyError
# Search for: pytest.raises(TypeError
# In files: tests/unit/auth/strategies/test_custom.py
#          tests/unit/auth/test_custom_failures.py
```

### Step 4.5: Verify all tests pass
```bash
# Run all auth-related tests
pytest tests/unit/auth/ -xvs
pytest tests/unit/client/test_client_auth.py -xvs

# Verify all strategies work
pytest tests/unit/auth/strategies/ -xvs
```

## Success Criteria
- ✅ CustomAuth imported from apiconfig
- ✅ custom.py file deleted
- ✅ All CustomAuth tests updated and passing
- ✅ All auth strategies now using apiconfig
- ✅ No regression in any tests

## Rollback Plan
If issues arise:
1. Restore the import in `__init__.py`
2. Restore the `custom.py` file from git
3. Revert test changes

## Time Estimate
20 minutes

## Notes
- CustomAuth is the most flexible auth strategy
- Main changes are exception types (TypeError → AuthStrategyError)
- The refresh_auth and is_expired callbacks now have better validation
- All concrete auth strategies are now migrated!

[← Previous: Task 3](./03_migrate_api_key_auth.md) | [Continue to Task 5: Migrate Base Classes →](./05_migrate_base_classes.md)
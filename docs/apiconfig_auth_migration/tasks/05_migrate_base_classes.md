# Task 5: Migrate Base Classes

[← Back to Incremental Implementation Plan](../05_incremental_implementation_plan.md)

## Objective
Update base class imports and remove the old base.py file, as all concrete strategies now use apiconfig.

## Prerequisites
- Tasks 1-4 completed successfully
- All auth strategies migrated to apiconfig

## Implementation Steps

### Step 5.1: Update AuthStrategy import in `__init__.py`
**File**: `/workspace/crudclient/auth/__init__.py`

Add the base class import:
```python
# FROM:
from .base import AuthStrategy

# TO:
from apiconfig.auth.base import AuthStrategy
```

### Step 5.2: Update AuthStrategyError import
Also add the exception import:
```python
# Add this import:
from apiconfig.exceptions.auth import AuthStrategyError
```

### Step 5.3: Delete the base.py file
```bash
rm /workspace/crudclient/auth/base.py
```

### Step 5.4: Check for any direct base class usage
Search for any code that might be importing from the old location:
```bash
# Search for direct imports of base.py
grep -r "from crudclient.auth.base import" tests/
grep -r "from crudclient.auth.base import" crudclient/

# Search for AuthStrategy usage
grep -r "AuthStrategy" tests/unit/auth/
```

### Step 5.5: Update any found imports
If any tests import AuthStrategy directly, update them:
```python
# FROM:
from crudclient.auth.base import AuthStrategy

# TO:
from crudclient.auth import AuthStrategy
```

### Step 5.6: Run tests to verify
```bash
# Run all auth tests
pytest tests/unit/auth/ -xvs

# Run client tests
pytest tests/unit/client/test_client_auth.py -xvs
```

## Success Criteria
- ✅ AuthStrategy imported from apiconfig
- ✅ AuthStrategyError available from auth module
- ✅ base.py file deleted
- ✅ All tests still passing
- ✅ No direct imports of old base module

## Rollback Plan
If issues arise:
1. Restore the import in `__init__.py`
2. Restore the `base.py` file from git
3. Revert any import updates

## Time Estimate
15 minutes

## Notes
- This is mostly cleanup since strategies are already migrated
- AuthStrategy is mainly used for type hints
- AuthStrategyError might be used in tests
- After this task, the auth module structure is ready for consolidation

[← Previous: Task 4](./04_migrate_custom_auth.md) | [Continue to Task 6: Consolidate to auth.py →](./06_consolidate_auth_module.md)
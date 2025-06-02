# Task 6: Consolidate to Single auth.py File

[← Back to Incremental Implementation Plan](../05_incremental_implementation_plan.md)

## Objective
Replace the entire auth module directory with a single `auth.py` file, simplifying the project structure.

## Prerequisites
- Tasks 1-5 completed successfully
- All imports already pointing to apiconfig

## Implementation Steps

### Step 6.1: Create the new auth.py file
**File**: `/workspace/crudclient/auth.py`

Create with all the re-exports:
```python
"""
Authentication strategies for crudclient.

This module re-exports authentication functionality from apiconfig,
providing a clean interface for authentication in API clients.
"""

# Base classes
from apiconfig.auth.base import AuthStrategy
from apiconfig.exceptions.auth import AuthStrategyError

# Concrete strategies
from apiconfig.auth.strategies.basic import BasicAuth
from apiconfig.auth.strategies.bearer import BearerAuth
from apiconfig.auth.strategies.api_key import ApiKeyAuth
from apiconfig.auth.strategies.custom import CustomAuth

__all__ = [
    # Base classes
    "AuthStrategy",
    "AuthStrategyError",
    # Concrete strategies
    "BasicAuth",
    "BearerAuth",
    "ApiKeyAuth",
    "CustomAuth",
]
```

### Step 6.2: Update all imports to use new location
Search and replace across the codebase:

```bash
# Find all imports from auth module
grep -r "from crudclient.auth import" . --include="*.py"
grep -r "import crudclient.auth" . --include="*.py"
```

The imports should remain the same since we're maintaining the same interface.

### Step 6.3: Delete the auth module directory
```bash
# Remove the entire directory
rm -rf /workspace/crudclient/auth/
```

### Step 6.4: Run all tests
```bash
# Full test suite to ensure nothing broke
pytest tests/unit/auth/ -xvs
pytest tests/unit/client/test_client_auth.py -xvs
pytest tests/unit/http/ -xvs
pytest tests/integration/ -xvs
```

### Step 6.5: Verify imports work correctly
```python
# Quick verification script
python -c "
from crudclient.auth import BasicAuth, BearerAuth, ApiKeyAuth, CustomAuth, AuthStrategy, AuthStrategyError
print('All imports successful!')
"
```

## Success Criteria
- ✅ Single auth.py file created with all exports
- ✅ Auth module directory deleted
- ✅ All tests still passing
- ✅ No import errors anywhere
- ✅ Clean, simple structure

## Rollback Plan
If issues arise:
1. Delete the new `auth.py` file
2. Restore the `auth/` directory from git
3. All imports should work again

## Time Estimate
15 minutes

## Notes
- This is a structural change only - no functionality changes
- Imports remain the same from user perspective
- Massive simplification: 6 files → 1 file
- Makes it obvious that auth is just re-exporting from apiconfig

[← Previous: Task 5](./05_migrate_base_classes.md) | [Continue to Task 7: Delete Redundant Tests →](./07_delete_redundant_tests.md)
# Task 7: Delete Redundant Unit Tests

[← Back to Incremental Implementation Plan](../05_incremental_implementation_plan.md)

## Objective
Remove unit tests that are now just testing apiconfig's functionality, keeping only tests that verify crudclient's integration.

## Prerequisites
- Tasks 1-6 completed successfully
- All tests currently passing

## Implementation Steps

### Step 7.1: Delete pure unit tests for auth strategies
These tests are now redundant as they test apiconfig's code:

```bash
# Delete unit tests that just test auth strategy internals
rm tests/unit/auth/strategies/test_basic.py
rm tests/unit/auth/strategies/test_bearer.py
rm tests/unit/auth/strategies/test_api_key.py
rm tests/unit/auth/strategies/test_custom.py
```

### Step 7.2: Keep component tests
These tests verify crudclient's usage of auth strategies and should be kept:

**Keep these files**:
- `tests/unit/auth/test_basic_failures.py` - Tests error handling
- `tests/unit/auth/test_bearer_failures.py` - Tests error handling
- `tests/unit/auth/test_custom_failures.py` - Tests error handling
- `tests/unit/client/test_client_auth.py` - Tests client integration

### Step 7.3: Clean up the strategies directory
```bash
# Remove the now-empty strategies directory
rmdir tests/unit/auth/strategies/
```

### Step 7.4: Update test documentation
If there's a test README, update it to reflect the new structure:
- Unit tests for auth strategies are delegated to apiconfig
- Component tests verify integration with crudclient
- Integration tests verify real API usage

### Step 7.5: Run remaining tests
```bash
# Verify remaining tests still pass
pytest tests/unit/auth/ -xvs
pytest tests/unit/client/test_client_auth.py -xvs
pytest tests/integration/ -xvs

# Get test count for documentation
pytest tests/unit/auth/ --collect-only | grep "test session starts" -A 1
```

## Success Criteria
- ✅ Redundant unit tests deleted
- ✅ Component tests still passing
- ✅ Integration tests still passing
- ✅ Cleaner test structure
- ✅ Reduced maintenance burden

## Rollback Plan
If tests are needed:
1. Restore deleted test files from git
2. Tests should pass again immediately

## Time Estimate
20 minutes

## Notes
- This follows the principle: "Don't test the framework"
- We're trusting apiconfig to test its own code
- We only test our usage and integration
- This removes ~200+ lines of test code
- Makes it clear what crudclient is responsible for

## Test Structure After Cleanup
```
tests/unit/auth/
├── test_basic_failures.py    # Component test - KEEP
├── test_bearer_failures.py   # Component test - KEEP
└── test_custom_failures.py   # Component test - KEEP
```

[← Previous: Task 6](./06_consolidate_auth_module.md) | [Continue to Task 8: Update Documentation →](./08_update_documentation.md)
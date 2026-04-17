# Verifier Pattern Fix Plan

## Issue Summary

The test `test_client_retries_on_403_if_configured` in `tests/unit/client/test_client_error_handling.py` is failing with a `VerificationError` because:

1. The `translate_mock_calls_for_verifier` function calls were commented out (lines 240, 244)
2. The `Verifier` calls that depend on them are still active (lines 241, 245)
3. The `Verifier` expects objects with a `calls` attribute, but standard Mock objects don't have this

## Immediate Fix

### Option 1: Restore the translate_mock_calls_for_verifier functionality

```python
# Add import at the top of the file
from tests.unit.helpers import translate_mock_calls_for_verifier

# In the test method, restore the calls with type ignores:
# Line 240-241
translate_mock_calls_for_verifier(client.config.handle_403_retry)  # type: ignore[arg-type]
Verifier.verify_called_once_with(client.config.handle_403_retry, "", client)

# Line 244-245
translate_mock_calls_for_verifier(client.http_client.session_manager.refresh_auth)  # type: ignore[arg-type]
Verifier.verify_call_count(client.http_client.session_manager.refresh_auth, "", 1)
```

### Option 2: Use Mock's built-in assertion methods (Recommended for future)

```python
# Replace Verifier calls with Mock's built-in methods:
# Instead of lines 240-241:
client.config.handle_403_retry.assert_called_once_with(client)

# Instead of lines 244-245:
assert client.http_client.session_manager.refresh_auth.call_count == 1
```

## Long-term Recommendation: Replace Custom Verifier Pattern

### Why the Verifier Pattern is Overengineering

1. **Unnecessary Abstraction**: `unittest.mock` already provides comprehensive assertion methods
2. **Maintenance Burden**: Requires extra translation layer (`translate_mock_calls_for_verifier`)
3. **Type Compatibility Issues**: Causes typing problems that require workarounds
4. **No Clear Advantage**: Standard Mock methods are well-documented and widely understood

### Migration Plan

#### Phase 1: Document the Pattern (Immediate)
Add documentation to `crudclient/testing/verification.py`:

```python
"""
Verifier Pattern Implementation for Test Assertions on Spies/Mocks.

**DEPRECATION NOTICE**: This custom Verifier pattern is being considered for deprecation
in favor of unittest.mock's built-in assertion methods. New tests should prefer using
Mock's built-in methods like assert_called_once_with(), assert_called_with(), etc.

Reasons for deprecation:
1. unittest.mock already provides comprehensive assertion methods
2. The translation layer (translate_mock_calls_for_verifier) adds unnecessary complexity
3. Type compatibility issues require frequent workarounds
4. Standard Mock methods are better documented and more widely understood

This pattern should only be used for custom spy objects that implement the SpyTarget
protocol. For standard Mock objects, use Mock's built-in assertion methods.
"""
```

#### Phase 2: Fix Current Test (Immediate)
1. Import `translate_mock_calls_for_verifier` in the failing test file
2. Add type ignores to handle the type incompatibility
3. Add a comment explaining the temporary nature of this fix

#### Phase 3: Gradual Migration (Future)
1. Identify all uses of Verifier with standard Mock objects
2. Create a migration guide showing how to convert Verifier calls to Mock assertions
3. Update tests gradually, prioritizing:
   - Tests that are frequently modified
   - Tests that have type errors
   - New tests (use Mock methods from the start)

### Example Migration Mappings

| Verifier Method | Mock Equivalent |
|----------------|-----------------|
| `Verifier.verify_called_once_with(mock, "method", arg1, arg2)` | `mock.method.assert_called_once_with(arg1, arg2)` |
| `Verifier.verify_called_with(mock, "method", arg1)` | `mock.method.assert_called_with(arg1)` |
| `Verifier.verify_not_called(mock, "method")` | `mock.method.assert_not_called()` |
| `Verifier.verify_call_count(mock, "method", 3)` | `assert mock.method.call_count == 3` |
| `Verifier.verify_any_call(mock, "method", arg1)` | `mock.method.assert_any_call(arg1)` |

## Implementation Steps

1. **Immediate Fix** (for the current test failure):
   - Add the missing import
   - Restore the `translate_mock_calls_for_verifier` calls with type ignores
   - Add a TODO comment about future migration

2. **Documentation Update**:
   - Add deprecation notice to `crudclient/testing/verification.py`
   - Document the migration plan in the project documentation

3. **Future Migration**:
   - Create a tracking issue for the migration
   - Update contribution guidelines to prefer Mock's built-in methods
   - Gradually migrate existing tests

## Code Changes Needed

```python
# tests/unit/client/test_client_error_handling.py

# Add import at line 24 (after other imports)
from tests.unit.helpers import translate_mock_calls_for_verifier

# Update test method (lines 239-245)
# TODO: Consider migrating to Mock's built-in assertion methods
# See verifier_pattern_fix_plan.md for migration details
translate_mock_calls_for_verifier(client.config.handle_403_retry)  # type: ignore[arg-type]
Verifier.verify_called_once_with(client.config.handle_403_retry, "", client)

translate_mock_calls_for_verifier(client.http_client.session_manager.refresh_auth)  # type: ignore[arg-type]
Verifier.verify_call_count(client.http_client.session_manager.refresh_auth, "", 1)
```

This approach provides a quality fix that:
- Resolves the immediate test failure
- Maintains existing functionality
- Documents the technical debt
- Provides a clear migration path
- Avoids quick hacks or workarounds
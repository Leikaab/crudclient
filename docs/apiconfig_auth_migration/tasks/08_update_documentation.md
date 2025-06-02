# Task 8: Update Documentation

[← Back to Incremental Implementation Plan](../05_incremental_implementation_plan.md)

## Objective
Update all documentation to reflect the new auth structure and migration.

## Prerequisites
- Tasks 1-7 completed successfully
- Auth migration functionally complete

## Implementation Steps

### Step 8.1: Update main README.md
**File**: `/workspace/README.md`

Update the authentication section to reflect:
- Auth strategies now come from apiconfig
- Simpler import structure
- New capabilities (token refresh, validation)

### Step 8.2: Create/Update CHANGELOG
**File**: `/workspace/CHANGELOG.md` (or similar)

Add entry for this migration:
```markdown
## [0.8.0] - 2025-XX-XX
### Changed
- Migrated all authentication strategies to use apiconfig library
- Consolidated auth module from 6 files to single auth.py file
- Breaking: `BearerAuth` now uses `access_token=` instead of `token=`
- Breaking: Empty credentials now raise `AuthStrategyError`
- Breaking: Custom header names no longer supported in BearerAuth

### Added
- Token expiration and refresh support in BearerAuth
- Stricter validation for all auth strategies
- `AuthStrategyError` for auth-specific exceptions

### Removed
- Redundant auth strategy implementations (now delegated to apiconfig)
- ~285 lines of duplicated code
```

### Step 8.3: Update auth examples
Search for auth examples in docs:
```bash
# Find documentation files with auth examples
find . -name "*.md" -type f | xargs grep -l "BasicAuth\|BearerAuth\|ApiKeyAuth\|CustomAuth"
```

Update any examples to show:
- New import location (if showing imports)
- `access_token=` for BearerAuth
- Proper error handling with `AuthStrategyError`

### Step 8.4: Delete old auth README
```bash
# Remove the old auth module README if it exists
rm -f /workspace/crudclient/auth/README.md
```

### Step 8.5: Add migration note to auth.py
Ensure the module docstring in `/workspace/crudclient/auth.py` explains:
- This module re-exports from apiconfig
- See apiconfig docs for detailed auth documentation
- Migration happened in v0.8.0

### Step 8.6: Update any API documentation
If using automated API docs (Sphinx, etc.):
- Regenerate docs
- Verify auth strategies appear correctly
- Check cross-references work

## Success Criteria
- ✅ Main documentation updated
- ✅ CHANGELOG reflects breaking changes
- ✅ Examples use new patterns
- ✅ No references to old auth module structure
- ✅ Clear migration path documented

## Rollback Plan
Documentation changes can be reverted via git if needed.

## Time Estimate
30 minutes

## Notes
- Be thorough - outdated docs cause confusion
- Emphasize the benefits: simpler, more features, better validation
- Make breaking changes very clear
- Consider adding a migration guide for users

## Documentation Checklist
- [ ] README.md updated
- [ ] CHANGELOG.md updated
- [ ] Example code updated
- [ ] API docs regenerated
- [ ] Migration guide created (optional)
- [ ] Old auth/README.md deleted

[← Previous: Task 7](./07_delete_redundant_tests.md) | [Continue to Task 9: Final Review →](./09_final_review.md)
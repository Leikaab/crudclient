# ApiConfig Auth Migration Plan

## Overview
Migration of crudclient authentication module to use apiconfig library implementations.

## Goals

- Remove ~315 lines of redundant authentication code
- Consolidate 6 files into single `auth.py`
- Delegate authentication logic to apiconfig library
- Add token expiration and refresh capabilities
- Maintain backward compatibility where possible

## Documentation Index

### Planning Documents
1. [Technical Migration Details](./01_auth_strategy_migration.md) - Architecture changes and code mapping
2. [Breaking Changes](./02_breaking_changes.md) - API changes and migration paths
3. [Test Migration Guide](./03_test_migration_guide.md) - Test updates and deletions
4. [Implementation Approaches](./04_implementation_checklist.md) - Comparison of migration strategies
5. [Incremental Implementation Plan](./05_incremental_implementation_plan.md) - **Recommended approach**
6. [Migration Summary](./06_migration_summary.md) - Document overview

### Implementation Tasks
Detailed task instructions in [`tasks/`](./tasks/) directory

## Migration Strategy

### Recommended Approach
Incremental migration - one authentication strategy at a time with tests passing after each step.

### Benefits
- Continuous integration capability
- Easy rollback if issues arise
- Clear progress tracking
- Reduced risk

## Current vs Target Architecture

### Current Structure
```
crudclient/auth/
├── __init__.py
├── base.py      (42 lines)
├── basic.py     (65 lines)
├── bearer.py    (61 lines)
├── custom.py    (147 lines)
└── README.md
Total: ~315 lines across 6 files
```

### Target Structure
```
crudclient/auth.py  (30 lines)
```

### Impact
- 90% code reduction (285 lines removed)
- Simplified module structure
- Delegated maintenance to apiconfig

## Breaking Changes

1. Import path consolidation: `crudclient.auth.basic` → `crudclient.auth`
2. `BearerAuth` parameter: `token=` → `access_token=`
3. Empty credentials validation enforced
4. Custom header names removed from BearerAuth
5. Exception type changes: TypeError → AuthStrategyError

Full details in [Breaking Changes Documentation](./02_breaking_changes.md).

## Implementation Timeline

Estimated 3-4 hours total:
- Tasks 1-4: Auth strategy migrations (2 hours)
- Tasks 5-6: Structure consolidation (30 minutes)
- Tasks 7-8: Test cleanup and documentation (1 hour)
- Task 9: Final verification (15 minutes)

## Next Steps

1. Review migration documentation
2. Obtain approval
3. Execute [Incremental Implementation Plan](./05_incremental_implementation_plan.md)
4. Verify tests at each step
5. Update project documentation

## Additional Resources

Visual diagrams are included throughout the documentation to illustrate architecture changes, process flows, and migration progression.
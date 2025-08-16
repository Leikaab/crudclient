# Endpoint Builder Refactoring Plan

## Overview
Extract endpoint generation logic from the monolithic `Crud` class into a reusable `EndpointBuilder` class within a new `crudclient/utils/endpoint_builder/` package. The goal is to create modular, testable, and reusable endpoint construction logic that can eventually be moved to the `apiconfig` package.

## Architecture

### Module Structure
```
crudclient/utils/endpoint_builder/
├── __init__.py          # Package initialization with exports
├── builder.py           # Main EndpointBuilder class
├── validators.py        # Path validation functions
├── path_utils.py        # Path joining utilities
└── segments.py          # Resource segment building logic
```

### Key Classes and Functions

#### `EndpointBuilder` (builder.py)
Main class that orchestrates endpoint construction:
- `__init__(resource_path, parent=None, endpoint_prefix=None)`
- `build_endpoint(*args, parent_args=None) -> str`
- `_get_parent_path(parent_args) -> str`
- `_get_prefix_segments() -> list[str]`

#### Validation Functions (validators.py)
- `validate_path_segments(*args) -> None` - Validates path segment types and values

#### Path Utilities (path_utils.py)
- `join_path_segments(*args) -> str` - Safely joins path segments

#### Segment Building (segments.py)
- `build_resource_segments(resource_path, *args) -> list[str]` - Builds resource path segments

## Implementation Phases

### Phase 1: Create the endpoint_builder package ✅ COMPLETE
- [x] Create directory structure
- [x] Implement `validators.py` with `validate_path_segments`
- [x] Implement `path_utils.py` with `join_path_segments`
- [x] Implement `segments.py` with `build_resource_segments`
- [x] Implement `builder.py` with `EndpointBuilder` class
- [x] Create `__init__.py` with proper exports

### Phase 2: Integrate with Crud class ✅ COMPLETE
- [x] Add `EndpointBuilder` instance to `Crud` class
- [x] Create adapter methods that delegate to `EndpointBuilder`
- [x] Ensure backward compatibility with existing code

### Phase 3: Testing & Validation ✅ COMPLETE
- [x] Create comprehensive unit tests for each module
- [x] Verify all existing tests pass
- [x] Add integration tests for complex scenarios
- [x] Modularize test suite into separate files per module

### Phase 4: Fix Integration Test Failures 🚧 IN PROGRESS
See detailed fix plan in [`endpoint_builder_fixes_plan.md`](./endpoint_builder_fixes_plan.md)

Key issues to address:
1. Overly strict validation (empty strings)
2. Missing dynamic prefix support
3. Architectural improvements needed
4. Deprecation warnings for adapter methods

### Phase 5: Future Migration to `apiconfig`
- [ ] Move the `endpoint_builder` package to `apiconfig`
- [ ] Update imports throughout the codebase
- [ ] Deprecate old methods in `Crud` class

## Technical Decisions

1. **Pure Functions**: Most functions are pure for easier testing
2. **Type Safety**: Comprehensive type hints throughout
3. **Separation of Concerns**: Each module has a single responsibility
4. **Backward Compatibility**: Existing `Crud` API remains unchanged

## Migration Strategy

1. The `Crud` class will use `EndpointBuilder` internally
2. All existing public methods remain available
3. No breaking changes to the API
4. Future deprecation warnings can be added when ready

## Testing Strategy

1. Unit tests for each module in `endpoint_builder`
2. Integration tests to ensure `Crud` class behavior unchanged
3. Edge case testing for path construction
4. Performance benchmarks to ensure no regression

## Notes

- The `_resource_path` property in `Crud` is used directly (not as a method)
- Path joining does not add leading slashes to maintain compatibility
- Empty path segments are filtered out during joining
- Parent paths take precedence over prefix segments

## Current Status: Phase 3 COMPLETE, Phase 4 IN PROGRESS ✅

All unit tests passing (122/122):
- 72 CRUD tests - Full backward compatibility maintained
- 50 endpoint_builder tests - Complete coverage of new functionality

### Integration Test Failures - Root Cause Analysis

After running the full test suite, 3 integration tests failed. Detailed analysis and fixes are documented in [`endpoint_builder_fixes_plan.md`](./endpoint_builder_fixes_plan.md).

#### Summary of Issues:
1. **Overly strict validation**: New validation rejects empty strings used in existing code
2. **Missing dynamic prefix support**: `EndpointBuilder` doesn't call Crud's `_endpoint_prefix()` method
3. **Architectural issues**: Need declarative style and better prefix handling

#### Next Steps:
Implement the fixes outlined in the fixes plan document to resolve all integration test failures while improving the overall architecture.
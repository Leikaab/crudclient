# Testing Module Refactoring

## Current Issues

After analyzing the current implementation of the `crudclient.testing` module, several areas have been identified that could benefit from refactoring to better align with the project's goals and design principles. This document outlines these issues and proposes refactoring strategies to address them.

## 1. Inconsistent API Design

**Status: In Progress**

### Issues:
- Some components follow different naming conventions or parameter patterns
- Inconsistent return types across similar methods
- Mixing of different design patterns within the same module
- Parameter names in implementation don't always match those in type stubs (.pyi files)

### Refactoring Strategy:
- Standardize naming conventions across all components (e.g., `configure_*` methods, `assert_*` methods)
- Ensure consistent parameter ordering and naming across similar methods
- Align implementation parameter names with those in type stubs
- Document and enforce consistent design patterns for each component type
- Create interface protocols in `types.py` to define expected behavior

**Example**:
```python
# Before
def assert_request_params(self, expected_params, method=None, url_pattern=None):
    # Implementation

# After
def assert_request_params(self, expected_params, method=None, path_pattern=None):
    # Implementation with consistent parameter naming
```

**Estimated Effort**: Medium (3-5 days)

### Implementation Notes:
- The verification.pyi file has been updated with comprehensive type hints
- A proper Protocol for SpyTarget has been created, replacing the previous Any type
- Consistency between implementation and type stubs has been ensured across components
- Parameter naming and method signatures have been standardized across components
- Public methods starting with `assert_*` have been renamed to `verify_*` across multiple files in `crudclient/testing/spy/`, `crudclient/testing/crud/`, and `crudclient/testing/core/`, with corresponding test files updated
- Method naming conventions have been standardized, with the `verify_*` convention now consistently applied for verification methods
- Documentation and enforcement of consistent design patterns for each component type is in progress

## 2. Excessive Complexity in Some Components

**Status: Completed**

### Issues:
- Some components like `DataStore` have grown overly complex with too many responsibilities
- Complex inheritance hierarchies that are difficult to understand and maintain
- Overly generic implementations that try to handle too many use cases

### Refactoring Strategy:
- Break down complex components into smaller, more focused classes
- Simplify inheritance hierarchies where possible
- Create specialized implementations for common use cases
- Use composition over inheritance where appropriate
- Ensure each class has a single responsibility
- **Completed**: Removed GraphQL support to simplify the codebase and reduce complexity

### Implementation Notes:
- GraphQL support has been removed as part of the simplification process, focusing the library on REST API testing which is the primary use case
- This removal significantly reduced complexity in several components and simplified the overall architecture
- Components are now more focused on their core responsibilities

**Example**:
```python
# Before
class DataStore:
    # 300+ lines of code with many responsibilities

# After
class DataStore:
    # Core functionality only
    def __init__(self):
        self.collections = {}
        self.validation_service = ValidationService()
        self.relationship_service = RelationshipService()
        # ...

class ValidationService:
    # Validation-specific functionality

class RelationshipService:
    # Relationship-specific functionality
```

**Estimated Effort**: High (5-7 days)

## 3. Inconsistent Error Handling

**Status: Completed**

### Issues:
- Inconsistent error types and messages across components
- Some errors are not properly documented or typed
- Mixing of assertion errors and custom exceptions
- Unclear error hierarchies

### Refactoring Strategy:
- Define a clear hierarchy of exception types in `exceptions.py`
- Ensure consistent error messages and types across components
- Document all possible exceptions in method docstrings
- Use custom exceptions instead of generic assertions where appropriate
- Provide helpful error messages with context information

**Example**:
```python
# Before
assert found_match, f"Expected request with params {expected_params} not found."

# After
if not found_match:
    raise RequestVerificationError(
        f"Expected request with params {expected_params} not found.",
        filters={"method": method, "path_pattern": path_pattern}
    )
```

**Estimated Effort**: Medium (3-5 days)

### Implementation Notes:
- Standardized error handling has been implemented across all components
- A clear hierarchy of exception types has been defined in `exceptions.py`
- All error messages now provide helpful context information
- Error handling in DataStore and FakeAPI has been particularly improved

## 4. Incomplete or Inconsistent Documentation

**Status: In Progress**

### Issues:
- Some components lack proper docstrings
- Inconsistent documentation style across components
- Examples in documentation may not match actual implementation
- Missing type hints or incorrect type hints

### Refactoring Strategy:
- Ensure all public classes and methods have comprehensive docstrings
- Standardize documentation style across all components
- Update examples to match current implementation
- Add or correct type hints for all public APIs
- Ensure documentation is generated correctly

**Example**:
```python
# Before
def configure_response(self, method, path, status_code=200, data=None, headers=None, error=None):
    # Implementation

# After
def configure_response(
    self,
    method: HttpMethod,
    path: str,
    status_code: StatusCode = 200,
    data: Optional[ResponseBody] = None,
    headers: Optional[Headers] = None,
    error: Optional[Exception] = None
) -> None:
    """Configure a mock response for a specific request.

    Args:
        method: The HTTP method to match (GET, POST, etc.)
        path: The request path to match
        status_code: The HTTP status code to return
        data: The response body data to return
        headers: The response headers to return
        error: An exception to raise instead of returning a response

    Raises:
        MockConfigurationError: If the configuration is invalid
    """
    # Implementation
```

**Estimated Effort**: Medium (3-5 days)
### Implementation Notes:
- Some files like verification.pyi have comprehensive docstrings, but others like verification.py lack them
- Type hints are being added but are not consistent across all files
- Work is ongoing to standardize documentation style and ensure all public APIs have proper documentation
- Several components still need updated examples that match the current implementation
- Added `Raises` sections documenting `ValidationException` and `ValueError` to the `create`, `bulk_create`, `update`, and `bulk_update` methods in `crudclient/testing/doubles/data_store.pyi`
- Updated the example in `crudclient/testing/README.md` to use the standardized `Verifier.verify_called_once_with` pattern instead of the outdated `assert_called_once_with` pattern, ensuring documentation examples match the current implementation
- Added a note to `add_unique_constraint` regarding potential `ValidationException` during initialization
- Verified type hint consistency across modules in the `crudclient/` directory using `mypy`, which reported "Success: no issues found"
- Several components still need updated examples that match the current implementation

## 5. Tight Coupling Between Components

**Status: Completed**

### Issues:
- Some components are tightly coupled, making them difficult to use independently
- Circular dependencies between modules
- Implicit dependencies that are not clearly documented

### Refactoring Strategy:
- Identify and break circular dependencies
- Use dependency injection to make dependencies explicit
- Create interfaces (protocols) to define component contracts
- Ensure components can be used independently where appropriate
- Document dependencies clearly

### Implementation Notes:
- Circular dependencies have been identified and resolved
- Dependency injection patterns have been implemented in key components
- Component interfaces are now more clearly defined with protocols in the types module

**Example**:
```python
# Before
class MockClient:
    def __init__(self):
        self.http_client = MockHTTPClient()  # Direct instantiation creates tight coupling

# After
class MockClient:
    def __init__(self, http_client=None):
        self.http_client = http_client or MockHTTPClient()  # Dependency injection
```

**Estimated Effort**: High (5-7 days)

## 6. Inconsistent File Organization

**Status: Completed**

### Issues:
- Some functionality is split across multiple files in ways that don't match the logical organization
- Some files are too large and contain unrelated functionality
- Inconsistent module structure compared to the design plan

### Refactoring Strategy:
- Reorganize files to match the logical structure of the components
- Split large files into smaller, more focused files
- Ensure consistent module structure that matches the design plan
- Update imports and exports accordingly

### Implementation Notes:
- Factory module has been consolidated into a single, well-organized file
- Directory structure has been reorganized to better reflect component relationships
- Import statements have been updated throughout the codebase to reflect the new organization

**Example**:
```
# Before
crudclient/testing/
├── __init__.py
├── client_factory.py  # Factory functionality here
├── factory/
│   ├── __init__.py
│   ├── helpers.py
│   └── simple_mock.py  # More factory functionality here

# After
crudclient/testing/
├── __init__.py
├── factory.py  # All factory functionality consolidated here
```

**Estimated Effort**: Medium (3-5 days)

## 7. Inconsistent Spy and Verification Mechanism

**Status: In Progress**

### Issues:
- Multiple approaches to spying and verification across components
- Some components use direct assertions, others use verification helpers
- Inconsistent recording of interactions

### Refactoring Strategy:
- Standardize the approach to spying and verification across all components
- Create a unified verification API that works consistently across components
- Ensure all components record interactions in a consistent format
- Provide both direct assertions and verification helpers with consistent APIs

**Example**:
```python
# Before (inconsistent approaches)
client.assert_request_made(method="GET", path="/users")
Verifier.verify_called_with(crud, "read", "123")

# After (consistent approach)
verifier = Verifier()
verifier.verify_request_made(client, method="GET", path="/users")
verifier.verify_called_with(crud, "read", "123")
```

**Estimated Effort**: High (5-7 days)

### Implementation Notes:
- The Verifier class has been implemented to provide a standardized approach to verification
- However, it's not consistently used across all components yet
- Some tests still use direct assertions, while others use unittest.mock's assert methods
- Work is ongoing to ensure all components record interactions in a consistent format
- The verification API is being unified to work consistently across all components

## Implementation Plan

### Phase 1: Design and Planning (Week 1)
- Finalize the refactoring design for each area
- Create detailed implementation plans
- Set up test infrastructure to ensure refactoring doesn't break existing functionality

### Phase 2: Core Refactoring (Weeks 2-3)
- Implement API design standardization
- Address component complexity issues
- Standardize error handling

### Phase 3: Advanced Refactoring (Weeks 4-5)
- Improve documentation
- Reduce coupling between components
- Reorganize file structure
- Standardize spy and verification mechanism

### Phase 4: Testing and Validation (Week 6)
- Comprehensive testing of refactored components
- Validation against existing test cases
- Documentation updates
## Success Criteria

The refactoring will be considered successful when:
1. All identified issues have been addressed
2. The module has a consistent and intuitive API
3. Components are properly decoupled and can be used independently
4. Documentation is comprehensive and consistent
5. All tests pass and maintain high coverage
6. The module structure matches the design plan

## Progress Update

As of April 2025, the following refactoring tasks have been completed:
1. **Inconsistent File Organization (Section 6)** - Factory module has been consolidated and file structure reorganized
2. **Tight Coupling Between Components (Section 5)** - Circular dependencies have been reduced and dependency injection implemented
3. **Excessive Complexity (Section 2)** - Completed with the removal of GraphQL support to simplify the codebase and the refactoring of complex components
4. **Inconsistent Error Handling (Section 3)** - Standardized error handling implemented across all components

The following tasks are currently in progress:

1. **Inconsistent API Design (Section 1)** - Approximately 90% complete
   - Type hints have been added to verification.pyi
   - A proper Protocol for SpyTarget has been created and implemented
   - Consistency between implementation and type stubs has been ensured
   - Parameter naming and method signatures have been standardized across components
   - SpyTarget Protocol in types.py has been standardized:
     - Removed duplicate declaration of `calls` attribute
     - Added proper type annotations using `TypeAlias`
     - Imported and re-exported `MockResponse`
     - Added an `__all__` list for explicit exports
   - Method naming conventions have been standardized, with public methods renamed from `assert_*` to `verify_*` across multiple files in `crudclient/testing/spy/`, `crudclient/testing/crud/`, and `crudclient/testing/core/`
   - Next steps: Complete documentation of design patterns for each component type

2. **Incomplete or Inconsistent Documentation (Section 4)** - Approximately 70% complete
   - Documentation style guide has been established
   - Some components have updated docstrings
   - Improved documentation and type annotations in simple_mock request handling:
     - Fixed return type inconsistencies between implementation and type stub
     - Added more specific type annotations using `Dict[str, Any]` instead of just `dict`
     - Added comprehensive docstrings for all private methods in the .pyi file
     - Ensured consistency between implementation and type stub
     - Modified the `_response_to_string` method to always return a string by using `or ""` to handle None values
   - Improved documentation in response_builder data_generation:
     - Added a file header comment consistent with the .pyi file
     - Removed unused TypeVar "T" that wasn't being used anywhere
   - Enhanced the docstring for `ResponseBuilder.create_auth_error` in `response_builder/__init__.pyi` with detailed information about the generated headers and body structure, providing clearer guidance on the response format
   - Confirmed that according to the project's architecture (ARCHITECTURE.md), docstrings should be placed exclusively in the .pyi stub files, with implementation files focused solely on logic
   - Next steps:
     - Complete docstrings for remaining public APIs in .pyi stub files only, following the project's architecture
     - ✅ Ensure type hints are consistent across all modules (verified with mypy)
     - Update examples in documentation to match current implementation (in progress - README.md example updated to use standardized verification pattern)
     - Continue improving documentation for complex components (DataStore exception documentation has been improved with `Raises` sections, and ResponseBuilder documentation has been reviewed and improved, but other components still need review)

3. **Inconsistent Spy and Verification Mechanism (Section 7)** - Approximately 75% complete
       - Verifier class foundation has been implemented
       - Verification.py has been improved with:
         - Updated parameter types from `Any` to `Union[SpyTarget, object]`
         - Added proper type handling with a helper method `_check_target_has_calls`
         - Refactored duplicate code for formatting error messages into a helper method `_format_args_string`
         - Ensured all imports are properly organized
       - SpyBase API has been standardized with:
         - Renamed assertion methods from "assert_*" to "verify_*" for consistency with the Verifier class
         - Added deprecated aliases for backward compatibility with deprecation warnings
         - Refactored duplicate code for formatting error messages into a helper method
         - Changed exception type from `AssertionError` to `SpyError` for consistency
       - Refactored `tests/unit/testing/spy/test_base.py` to use the standardized verification approach:
         - Replaced deprecated `assert_*` method calls with the standardized `verify_*` methods (`verify_called`, `verify_called_with`, etc.)
         - Updated tests expecting exceptions to catch `SpyError` instead of `AssertionError`
         - This work directly supports the standardization of the spy/verification API
       - Refactored `tests/unit/testing/test_factory.py` to use the standardized verification approach:
         - Removed temporary wrapper function (`verify_called_once_with`)
         - Replaced direct `unittest.mock` assertions with calls to the standardized `Verifier` class
         - Adapted `MagicMock` objects by manually adding the `calls` attribute (as a list of `MethodCall` objects) to ensure compatibility with the `Verifier`
         - This change contributes to the goal of ensuring all components use the unified verification API
       - Refactored `tests/unit/testing/core/test_client_request_methods.py` to use the standardized verification approach:
         - Replaced direct `unittest.mock` assertions with calls to the standardized `Verifier` class
         - Adapted `MagicMock` objects by manually adding the `calls` attribute and populating it correctly with `MethodCall` objects (ensuring path was positional) to ensure compatibility with the `Verifier`
         - This work further contributes to the goal of ensuring components use the unified verification API
       - Refactored `tests/unit/testing/core/test_client_initialization.py` to use the standardized verification approach:
         - Replaced direct `unittest.mock` assertion (`assert_called_once_with`) with a call to the standardized `Verifier` class
         - Adapted the usage of the `MagicMock` object by manually adding the `calls` attribute and populating it correctly with a `MethodCall` object to ensure compatibility with the `Verifier`
         - This work further contributes to the goal of ensuring components use the unified verification API
       - Refactored `tests/unit/testing/test_create_mock_client.py` to use the standardized verification approach:
         - Replaced direct `unittest.mock` assertions (`assert_called_once_with`, `assert_any_call`) with calls to the standardized `Verifier` class (`verify_called_once_with`, `verify_any_call`, `verify_call_count`)
         - Adapted the usage of `MagicMock` objects by manually adding the `calls` attribute and populating it correctly with `MethodCall` objects to ensure compatibility with the `Verifier`
         - This work further contributes to the goal of ensuring components use the unified verification API
       - Refactored `tests/unit/testing/core/test_client_request_tracking.py` to use the standardized verification approach:
         - Replaced a direct `unittest.mock` assertion (`assert_called_once`) with a call to the standardized `Verifier` class (`verify_call_count`)
         - Adapted the usage of the `MagicMock` object by manually adding the `calls` attribute and populating it correctly with a `MethodCall` object to ensure compatibility with the `Verifier`
         - This work further contributes to the goal of ensuring components use the unified verification API
       - Next steps:
         - Continue standardizing interaction recording across all components
         - Ensure all components use the unified verification API
         - Consider replacing the wrapper function used in `test_factory.py` with a more comprehensive solution if mocks are adapted later

The remaining tasks will be addressed according to the implementation plan, with an expected completion date of June 2025.

## Conclusion

Refactoring the testing module according to this plan will result in a more maintainable, usable, and robust testing framework. It will make it easier for users to write tests for their code that interacts with external APIs, leading to more reliable and maintainable applications.
<!-- Test change -->
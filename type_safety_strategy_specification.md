# Type Safety Strategy Specification for CrudClient Library

## 1. Introduction

This document outlines the comprehensive type safety strategy for the `crudclient` library. The strategy aims to ensure type correctness both statically and at runtime, while maintaining a balance between safety and performance.

### 1.1 Goals

- Ensure type correctness throughout the library
- Provide clear type interfaces for library users
- Minimize runtime overhead while maintaining safety
- Facilitate early detection of type errors during development
- Support gradual typing adoption for both library maintainers and users

### 1.2 Strategy Overview

The type safety strategy consists of three complementary approaches:

1. **Comprehensive Static Typing**: Leverage Python's type annotation system with mypy and detailed `.pyi` stub files
2. **Pydantic Validation**: Use Pydantic for validating data at API boundaries
3. **Targeted Runtime Checks**: Apply selective runtime type checking only where critical

## 2. Comprehensive Static Typing

### 2.1 Approach

Static typing will be the primary mechanism for ensuring type safety in the codebase. This approach catches type errors at development time without runtime overhead.

### 2.2 Implementation Guidelines

#### 2.2.1 Type Annotations

- All public functions and methods must have complete type annotations
- All class attributes must be annotated
- Use generic types where appropriate to maintain type information across operations
- Prefer more specific types over `Any` where possible
- Use `Union` types to represent values that could be of multiple types
- Use `Optional` for values that could be `None`
- Use `TypeVar` for generic type parameters

#### 2.2.2 Stub Files (`.pyi`)

- Maintain comprehensive `.pyi` stub files for all modules
- Stub files should include detailed docstrings explaining the purpose and usage of each function, class, and method
- Use `overload` decorators in stub files to provide more precise type information for functions with multiple signatures

#### 2.2.3 Mypy Configuration

- Enable strict mypy checks progressively
- Update `mypy.ini` to include stricter checks:
  ```ini
  [mypy]
  python_version = 3.8
  warn_return_any = True
  warn_unused_configs = True
  disallow_untyped_defs = True
  disallow_incomplete_defs = True
  check_untyped_defs = True
  disallow_untyped_decorators = True
  no_implicit_optional = True
  strict_optional = True
  warn_redundant_casts = True
  warn_unused_ignores = True
  warn_no_return = True
  warn_unreachable = True
  ```

### 2.3 Files to Modify

- All `.py` files in the codebase to ensure complete type annotations
- All `.pyi` stub files to ensure they accurately reflect the implementation
- `mypy.ini` to enable stricter type checking

### 2.4 Examples

#### Example 1: Type Annotations in Functions

```python
# Before
def create(self, data, parent_id=None):
    endpoint = self._get_endpoint(parent_id)
    converted_data = self._dump_data(data)
    response = self.client.post(endpoint, json=converted_data)
    return self._convert_to_model(response)

# After
def create(self, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]:
    endpoint = self._get_endpoint(parent_id)
    converted_data: JSONDict = self._dump_data(data)
    response = self.client.post(endpoint, json=converted_data)
    return self._convert_to_model(response)
```

#### Example 2: Using `overload` in Stub Files

```python
# In client.pyi
@overload
def _request(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None,
             handle_response: Literal[True] = True, **kwargs: Any) -> RawResponseSimple: ...

@overload
def _request(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None,
             handle_response: Literal[False] = False, **kwargs: Any) -> requests.Response: ...
```

## 3. Pydantic Validation

### 3.1 Approach

Pydantic will be used to validate data at API boundaries, particularly for data entering and leaving the `Crud` layer. This provides runtime validation with clear error messages while maintaining good performance.

### 3.2 Implementation Guidelines

#### 3.2.1 Model Definition

- Define Pydantic models for all data structures used in API requests and responses
- Use Pydantic's validation features to enforce constraints on data
- Leverage Pydantic's automatic type conversion where appropriate
- Use Pydantic's `Field` class for additional validation rules

#### 3.2.2 Integration with Crud Layer

- Ensure all data entering the `Crud` layer is validated using Pydantic models
- Validate all data returned from API calls before converting to model instances
- Use Pydantic's error handling to provide clear error messages for validation failures

#### 3.2.3 Response Model Strategies

- Enhance the existing response model strategies to leverage Pydantic validation
- Ensure consistent error handling for validation failures

### 3.3 Files to Modify

- `crudclient/models.py`: Enhance existing models and add new ones as needed
- `crudclient/crud.py`: Update methods to use Pydantic validation
- `crudclient/types.py`: Update type definitions to work with Pydantic

### 3.4 Examples

#### Example 1: Enhanced Pydantic Model

```python
# In models.py
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, HttpUrl, validator

T = TypeVar("T")

class Link(BaseModel):
    href: Optional[HttpUrl] = None

    @validator('href')
    def validate_href(cls, v):
        if v is None:
            return v
        # Additional validation logic if needed
        return v

class PaginationLinks(BaseModel):
    next: Optional[Link] = None
    previous: Optional[Link] = None
    self: Link

class ApiResponse(BaseModel, Generic[T]):
    links: PaginationLinks = Field(..., alias="_links")
    count: int
    data: List[T]

    @validator('count')
    def validate_count(cls, v):
        if v < 0:
            raise ValueError("Count cannot be negative")
        return v
```

#### Example 2: Crud Method with Pydantic Validation

```python
# In crud.py
def create(self, data: Union[JSONDict, T], parent_id: Optional[str] = None) -> Union[T, JSONDict]:
    """
    Create a new resource.

    :param data: The data for the new resource.
    :param parent_id: ID of the parent resource for nested resources.
    :return: The created resource.
    :raises ValidationError: If the data fails validation.
    """
    endpoint = self._get_endpoint(parent_id)

    # Validate input data using Pydantic
    if not isinstance(data, dict) and self._datamodel:
        # Already a model instance, ensure it's the correct type
        if not isinstance(data, self._datamodel):
            raise TypeError(f"Data must be an instance of {self._datamodel}, dict, or None")
    elif self._datamodel:
        # Convert dict to model instance for validation
        try:
            data = self._datamodel(**data)
        except Exception as e:
            from .exceptions import ValidationError
            raise ValidationError(f"Failed to validate input data: {e}", data) from e

    converted_data: JSONDict = self._dump_data(data)
    response = self.client.post(endpoint, json=converted_data)

    # Validate response data
    try:
        return self._convert_to_model(response)
    except Exception as e:
        from .exceptions import ModelConversionError
        raise ModelConversionError(f"Failed to convert response to model: {e}", response) from e
```

## 4. Targeted Runtime Checks

### 4.1 Approach

While static typing and Pydantic validation cover most type safety needs, targeted runtime checks will be used in critical areas where type errors would be particularly problematic or where static typing is insufficient.

### 4.2 Implementation Guidelines

#### 4.2.1 When to Use Runtime Checks

- Use runtime checks at public API boundaries where incorrect types would lead to confusing errors
- Apply runtime checks in critical internal logic where type errors could cause data corruption
- Use runtime checks where static typing cannot fully express the constraints

#### 4.2.2 How to Implement Runtime Checks

- Use `isinstance()` checks for simple type verification
- Provide clear error messages that explain the expected types
- Avoid excessive runtime checks that could impact performance
- Consider using Python's `typing.cast()` to help static type checkers without runtime overhead

### 4.3 Files to Modify

- `crudclient/crud.py`: Add targeted runtime checks in critical methods
- `crudclient/client.py`: Add runtime checks at API boundaries
- `crudclient/http/*.py`: Add checks in HTTP handling code where needed

### 4.4 Examples

#### Example 1: Runtime Check in Public API Method

```python
# In crud.py
def custom_action(
    self,
    action: str,
    method: HttpMethodString = "post",
    resource_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    data: Optional[Union[JSONDict, T]] = None,
    params: Optional[JSONDict] = None,
) -> Union[T, JSONDict, List[JSONDict]]:
    """
    Perform a custom action on the resource.

    :param action: The name of the custom action.
    :param method: The HTTP method to use. Defaults to "post".
    :param resource_id: Optional resource ID if the action is for a specific resource.
    :param parent_id: ID of the parent resource for nested resources.
    :param data: Optional data to send with the request.
    :param params: Optional query parameters.
    :return: The API response.
    :raises TypeError: If the parameters are of incorrect types.
    """
    # Runtime type checks for critical parameters
    if not isinstance(action, str):
        raise TypeError(f"Action must be a string, got {type(action).__name__}")

    if method not in ["get", "post", "put", "patch", "delete", "head", "options", "trace"]:
        raise ValueError(f"Invalid HTTP method: {method}")

    if resource_id is not None and not isinstance(resource_id, str):
        raise TypeError(f"Resource ID must be a string or None, got {type(resource_id).__name__}")

    if parent_id is not None and not isinstance(parent_id, str):
        raise TypeError(f"Parent ID must be a string or None, got {type(parent_id).__name__}")

    # Continue with the method implementation
    endpoint = self._get_endpoint(parent_id, resource_id, action)

    kwargs = {}
    if params:
        kwargs["params"] = params
    if data:
        converted_data: JSONDict = self._dump_data(data)
        kwargs["json"] = converted_data

    response = getattr(self.client, method.lower())(endpoint, **kwargs)
    try:
        if isinstance(response, list):
            return response
        return self._convert_to_model(response)
    except Exception as e:
        logger.error(f"Failed to convert response to model: {e}")
        from .exceptions import ModelConversionError
        if isinstance(e, ModelConversionError):
            raise e
        raise ModelConversionError(f"Failed to convert response to model: {e}", None) from e
```

#### Example 2: Runtime Check in Internal Method

```python
# In crud.py
def _dump_data(self, data: Optional[Union[JSONDict, T]]) -> JSONDict:
    """
    Dump the data model to a JSON-serializable dictionary.

    :param data: The data to dump.
    :return: The dumped data.
    :raises ValueError: If the data is not a dict, None, or an instance of the datamodel.
    :raises TypeError: If the data is not of the expected type.
    """
    if data is None:
        return {}

    if isinstance(data, dict):
        return data

    # Critical runtime checks
    if self._datamodel is None:
        raise ValueError("If Data is not a dict or None, _datamodel must be set")

    if not isinstance(data, self._datamodel):
        raise TypeError(f"Data must be an instance of {self._datamodel}, dict, or None")

    if not hasattr(data, "model_dump"):
        raise ValueError(f"{self._datamodel} must have a model_dump method")

    return data.model_dump()
```

## 5. Integration and Testing

### 5.1 Integration Strategy

The three approaches (static typing, Pydantic validation, and targeted runtime checks) should be integrated in a way that provides multiple layers of protection:

1. Static typing catches errors during development
2. Pydantic validation ensures data correctness at API boundaries
3. Targeted runtime checks provide additional safety in critical areas

### 5.2 Testing Guidelines

- Add unit tests specifically for type validation
- Test edge cases where type errors might occur
- Ensure error messages are clear and helpful
- Test with mypy to verify static type correctness
- Test Pydantic validation with both valid and invalid data

### 5.3 Example Test Cases

```python
# Test static typing with mypy
def test_static_typing():
    # This test is run by CI/CD pipeline with mypy
    pass

# Test Pydantic validation
def test_pydantic_validation():
    # Test with valid data
    valid_data = {"name": "Test", "age": 30}
    model = UserModel(**valid_data)
    assert model.name == "Test"
    assert model.age == 30

    # Test with invalid data
    invalid_data = {"name": "Test", "age": "thirty"}
    with pytest.raises(ValidationError):
        UserModel(**invalid_data)

# Test runtime checks
def test_runtime_checks():
    crud = UsersCrud(client)

    # Test with valid data
    valid_result = crud.create({"name": "Test", "age": 30})
    assert valid_result.name == "Test"

    # Test with invalid data
    with pytest.raises(TypeError):
        crud.create(123)  # Not a dict or model instance
```

## 6. Implementation Plan

### 6.1 Phase 1: Static Typing Enhancement

1. Update all `.py` files with complete type annotations
2. Enhance `.pyi` stub files with detailed type information
3. Update `mypy.ini` with stricter checks
4. Run mypy to identify and fix type errors

### 6.2 Phase 2: Pydantic Integration

1. Enhance existing Pydantic models in `models.py`
2. Update `crud.py` to use Pydantic validation
3. Implement error handling for validation failures
4. Test with various data scenarios

### 6.3 Phase 3: Targeted Runtime Checks

1. Identify critical areas that need runtime checks
2. Implement runtime checks with clear error messages
3. Test edge cases to ensure checks are effective
4. Optimize performance where needed

## 7. Conclusion

This type safety strategy provides a comprehensive approach to ensuring type correctness in the `crudclient` library. By combining static typing, Pydantic validation, and targeted runtime checks, the library can achieve a high level of type safety while maintaining good performance and usability.

The strategy is designed to be implemented incrementally, allowing for gradual adoption and continuous improvement of the library's type safety.
# Endpoint Builder Fixes and Improvements Plan

## Overview
This document outlines the necessary fixes and improvements to address integration test failures and architectural issues with the EndpointBuilder implementation.

## Issues Identified

### 1. Architectural Issues

#### 1.1 FikenCrud Should Use Custom EndpointBuilder
**Current Problem**: FikenCrud overrides `_endpoint_prefix()` in Crud class
**Solution**: Create `FikenEndpointBuilder(EndpointBuilder)` to handle custom endpoint logic

```python
# Instead of:
class FikenCrud(Crud[T]):
    def _endpoint_prefix(self) -> tuple[str | None] | list[str | None]:
        return ["companies", self._company_slug]

# Should be:
class FikenEndpointBuilder(EndpointBuilder):
    _endpoint_prefix = ["companies"]  # Declarative style

    def __init__(self, company_slug: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self._company_slug = company_slug

    def get_prefix_segments(self) -> List[str]:
        # Custom logic here
        if self._company_slug:
            return ["companies", self._company_slug]
        return []

class FikenCrud(Crud[T]):
    endpoint_builder_class = FikenEndpointBuilder  # Declarative reference
```

#### 1.2 EndpointBuilder Design Flaws
**Problems**:
- Uses init setters instead of declarative DRF-style class attributes
- `_get_endpoint_prefix()` logic prevents parent+child prefix combinations
- No way to control prefix override vs addition behavior

**Solutions**:

```python
class EndpointBuilder:
    # Declarative style attributes (like DRF)
    resource_path: Optional[str] = None
    endpoint_prefix: Optional[Union[str, List[str]]] = None
    prefix_mode: str = "override"  # "override" or "append"

    def get_prefix_segments(self) -> List[str]:
        """Get prefix segments with proper parent handling."""
        segments = []

        # Get parent prefix if exists and mode is append
        if self.parent_builder and self.prefix_mode == "append":
            segments.extend(self.parent_builder.get_prefix_segments())

        # Add own prefix
        if self.endpoint_prefix:
            if isinstance(self.endpoint_prefix, str):
                segments.append(self.endpoint_prefix)
            else:
                segments.extend(self.endpoint_prefix)

        # If override mode and no own prefix, use parent's
        elif self.parent_builder and self.prefix_mode == "override":
            segments.extend(self.parent_builder.get_prefix_segments())

        return segments
```

### 2. Integration Test Failures

#### 2.1 Empty String Validation Issue
**Problem**: `validate_path_segments` rejects empty strings, breaking existing patterns
**Solution**: Modify validation to allow empty strings

```python
def validate_path_segments(*args: PathArgs) -> None:
    """
    Validate path segments - allow empty strings for backward compatibility.
    """
    for arg in args:
        # Allow None (will be filtered later) and empty strings
        if arg is None:
            continue  # None is allowed, will be filtered in join

        if not isinstance(arg, (str, int)):
            raise TypeError(
                f"Path segment must be string or integer, got {type(arg).__name__}"
            )

        # Only check dangerous characters, not empty strings
        if isinstance(arg, str) and (".." in arg or arg.startswith("/") or arg.endswith("/")):
            raise ValueError("Path segment contains potentially dangerous characters")
```

#### 2.2 Dynamic Prefix Support
**Problem**: Adapter method doesn't call Crud instance's `_endpoint_prefix()` method
**Solution**: Modify adapter to properly bridge the gap

```python
def _get_prefix_segments(self: "Crud[Any]") -> List[str]:
    """
    Adapter method that bridges Crud's _endpoint_prefix() to EndpointBuilder.

    .. deprecated:: 1.0
        This method is deprecated. Use EndpointBuilder directly.
    """
    import warnings
    warnings.warn(
        "_get_prefix_segments is deprecated. Use EndpointBuilder directly.",
        DeprecationWarning,
        stacklevel=2
    )

    # Get prefix from Crud's method (can be overridden by subclasses)
    prefix = self._endpoint_prefix()

    if isinstance(prefix, tuple):
        # Filter None values and convert to strings
        return [str(p) for p in prefix if p is not None]
    elif isinstance(prefix, list):
        # Filter None values and convert to strings
        return [str(p) for p in prefix if p is not None]
    else:
        return []
```

### 3. Deprecation Warnings for Adapter Methods

All adapter methods in `Crud` should include deprecation warnings:

```python
def _get_endpoint(self: "Crud[Any]", *args: Any, parent_args: Optional[Any] = None) -> str:
    """
    Adapter method for backward compatibility.

    .. deprecated:: 1.0
        This method is deprecated. Use EndpointBuilder.build_endpoint() directly.
    """
    import warnings
    warnings.warn(
        "_get_endpoint is deprecated. Use EndpointBuilder.build_endpoint() directly.",
        DeprecationWarning,
        stacklevel=2
    )
    return self._endpoint_builder.build_endpoint(*args, parent_args=parent_args)
```

## Implementation Steps

### Step 1: Fix EndpointBuilder Architecture
1. Refactor EndpointBuilder to use declarative class attributes
2. Implement proper prefix handling with override/append modes
3. Add support for custom endpoint builder classes in Crud

### Step 2: Fix Validation
1. Modify `validate_path_segments` to allow empty strings
2. Update related tests

### Step 3: Fix Dynamic Prefix Support
1. Update `_get_prefix_segments` adapter to call Crud's `_endpoint_prefix()`
2. Ensure EndpointBuilder can be properly configured with dynamic prefixes

### Step 4: Add Deprecation Warnings
1. Add warnings to all adapter methods
2. Update documentation with migration guide

### Step 5: Refactor Fiken Integration
1. Create FikenEndpointBuilder class
2. Update FikenCrud to use the custom builder
3. Test the refactored implementation

## Benefits
1. Clean separation of concerns
2. Extensible architecture for custom endpoint logic
3. Backward compatibility with deprecation path
4. Fixes all integration test failures
5. Follows library design patterns (declarative style)

## Migration Guide for Users

### Before (Override Crud methods):
```python
class CustomCrud(Crud):
    def _endpoint_prefix(self):
        return ["custom", "prefix"]
```

### After (Use custom EndpointBuilder):
```python
class CustomEndpointBuilder(EndpointBuilder):
    endpoint_prefix = ["custom", "prefix"]

class CustomCrud(Crud):
    endpoint_builder_class = CustomEndpointBuilder
# EndpointBuilder Declarative Design

## Core Design Principles

### 1. Fully Declarative Style (DRF-like)

```python
class Crud:
    # Class-level declaration - overrideable by subclasses
    endpoint_builder_class = EndpointBuilder

    # No more _init_endpoint_builder() method
    # No more instance creation in __init__

    @property
    def _endpoint_builder(self):
        """Lazy initialization of endpoint builder using declared class."""
        if not hasattr(self, '_endpoint_builder_instance'):
            # Use the class-level declaration
            builder_class = self.endpoint_builder_class

            # Parent builder if exists
            parent_builder = None
            if self.parent and hasattr(self.parent, '_endpoint_builder'):
                parent_builder = self.parent._endpoint_builder

            # Create instance from declared class
            self._endpoint_builder_instance = builder_class(parent_builder=parent_builder)

        return self._endpoint_builder_instance
```

### 2. Custom EndpointBuilder Classes

```python
class EndpointBuilder:
    """Base endpoint builder with declarative attributes."""

    # Declarative class attributes (like DRF serializers)
    resource_path: Optional[str] = None
    endpoint_prefix: Optional[Union[str, List[str]]] = None
    prefix_mode: str = "override"  # "override" or "append"

    def __init__(self, parent_builder: Optional['EndpointBuilder'] = None):
        # Only store parent reference
        self.parent_builder = parent_builder

        # Copy class attributes to instance
        self.resource_path = self.__class__.resource_path
        self.endpoint_prefix = self.__class__.endpoint_prefix
        self.prefix_mode = self.__class__.prefix_mode


class FikenEndpointBuilder(EndpointBuilder):
    """Custom builder for Fiken API with company slug prefix."""

    # Declarative configuration
    endpoint_prefix = ["companies"]  # Base prefix
    prefix_mode = "override"

    def get_prefix_segments(self, crud_instance=None) -> List[str]:
        """Get prefix with dynamic company slug."""
        segments = ["companies"]

        # Add company slug if available
        if crud_instance and hasattr(crud_instance, 'company_slug'):
            segments.append(crud_instance.company_slug)

        return segments


class FikenCrud(Crud[T]):
    """Base class for Fiken resources."""

    # Declarative endpoint builder
    endpoint_builder_class = FikenEndpointBuilder

    def __init__(self, client: Client, company_slug: str):
        self.company_slug = company_slug
        super().__init__(client)
```

### 3. Resource Path Declaration

Instead of passing resource_path through init, use class inheritance:

```python
class UserEndpointBuilder(EndpointBuilder):
    resource_path = "users"


class PostEndpointBuilder(EndpointBuilder):
    resource_path = "posts"


class CommentEndpointBuilder(EndpointBuilder):
    resource_path = "comments"
    prefix_mode = "append"  # Append to parent's prefix


# Usage in Crud classes
class UserCrud(Crud[User]):
    endpoint_builder_class = UserEndpointBuilder
    _resource_path = "users"  # Keep for backward compatibility


class PostCrud(Crud[Post]):
    endpoint_builder_class = PostEndpointBuilder
    _resource_path = "posts"
```

## Empty String / Idless Read Design Issue

### Problem Statement

- `FikenUser.read()` overrides to allow GET without resource ID
- Currently uses `custom_action(action="", method="get")`
- Empty string validation is blocking this pattern

### Design Options

1. **Option A: Explicit `read_single()` method**
   ```python
   class Crud:
       def read_single(self, **kwargs) -> T:
           """Read single resource without ID (for special endpoints)."""
           return self.custom_action(action="", method="get", **kwargs)
   ```

2. **Option B: Allow `None` as special case**
   ```python
   class Crud:
       def read(self, resource_id: Optional[Union[str, int]] = None, **kwargs) -> T:
           if resource_id is None:
               # Special case - read without ID
               return self.custom_action(action="", method="get", **kwargs)
           # Normal read with ID
   ```

3. **Option C: Sentinel value**
   ```python
   class Crud:
       NO_ID = object()  # Sentinel

       def read(self, resource_id: Union[str, int, object] = None, **kwargs) -> T:
           if resource_id is self.NO_ID:
               # Read without ID
               return self.custom_action(action="", method="get", **kwargs)
   ```

4. **Option D: Keep using `custom_action` explicitly**
   - Most explicit and clear
   - No ambiguity about intent
   - Already works with proper validation

### Recommendation

**Option D** is recommended because:
- It's explicit about the non-standard behavior
- No risk of accidental empty/None passes
- Already implemented and working
- Clear intent in the code

For validation, we should:
- Keep strict validation for normal path segments
- Allow empty action in `custom_action` method specifically
- Document this pattern for special GET endpoints

## Migration Plan

### Phase 1: Update EndpointBuilder to be fully declarative
1. Remove `__init__` parameters for resource_path and endpoint_prefix
2. Add class-level attributes
3. Update initialization to copy class attributes

### Phase 2: Update Crud to use declarative pattern
1. Add `endpoint_builder_class` attribute
2. Replace `_init_endpoint_builder()` with lazy property
3. Remove instance creation from `__init__`

### Phase 3: Create custom EndpointBuilder classes
1. Create `FikenEndpointBuilder` with company slug handling
2. Update `FikenCrud` to use it declaratively
3. Remove `_endpoint_prefix()` override

### Phase 4: Add deprecation warnings
1. Mark all adapter methods with deprecation warnings
2. Guide users to use EndpointBuilder directly

### Phase 5: Handle special cases
1. Document the `custom_action(action="", method="get")` pattern
2. Ensure validation allows this specific use case
3. Add tests for idless read patterns

## Benefits of This Approach

1. **True declarative style** - No hidden instance logic
2. **Easily overrideable** - Just set a different class attribute
3. **Clear inheritance** - Custom builders extend base functionality
4. **No breaking changes** - Existing code continues to work
5. **Better separation** - Endpoint logic fully separated from Crud
6. **Type safe** - Class attributes provide better type hints
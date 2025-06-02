# Breaking Changes

[← Back to Main README](./README.md)

## Overview
API changes introduced by the apiconfig authentication migration.

## Summary of Breaking Changes

1. **Import Path Consolidation**
   - Module structure replaced with single file
   - Submodule imports no longer supported

2. **Parameter Changes**
   - BearerAuth: `token` → `access_token`
   - Custom header names removed from BearerAuth

3. **Validation Changes**
   - Empty credentials now raise AuthStrategyError
   - Whitespace-only values rejected
   - Stricter parameter validation

4. **Exception Changes**
   - TypeError → AuthStrategyError for validation errors
   - New specific error messages

## Import Path Changes

### Before
```python
from crudclient.auth.base import AuthStrategy
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import CustomAuth, ApiKeyAuth
```

### After
```python
from crudclient.auth import AuthStrategy, BasicAuth, BearerAuth, CustomAuth, ApiKeyAuth
```

## BasicAuth Changes

### 1. Empty Credential Validation

**Before**: Empty username/password silently accepted
```python
auth = BasicAuth(username="", password="")  # No error
```

**After**: Raises `AuthStrategyError`
```python
auth = BasicAuth(username="", password="")
# AuthStrategyError: Username cannot be empty or whitespace
```

**Migration**: Validate credentials before instantiation or handle the exception.

### 2. Whitespace Validation

**Before**: Whitespace-only values accepted
```python
auth = BasicAuth(username="   ", password="pass")  # No error
```

**After**: Raises `AuthStrategyError`
```python
auth = BasicAuth(username="   ", password="pass")
# AuthStrategyError: Username cannot be empty or whitespace
```

## BearerAuth Changes

### 1. Parameter Rename

**Before**:
```python
auth = BearerAuth(token="abc123")
```

**After**:
```python
auth = BearerAuth(access_token="abc123")
```

**Migration**: Update all `token=` to `access_token=`

### 2. Custom Headers Removed

**Before**: Custom header names supported
```python
auth = BearerAuth(token="abc123", header_name="X-Custom-Token")
```

**After**: Always uses "Authorization" header
```python
auth = BearerAuth(access_token="abc123")
# Creates: Authorization: Bearer abc123
```

**Migration**: Remove `header_name` parameter. Use `CustomAuth` for custom headers.

### 3. Empty Token Validation

**Before**: Empty tokens accepted
```python
auth = BearerAuth(token="")  # No error
```

**After**: Raises `AuthStrategyError`
```python
auth = BearerAuth(access_token="")
# AuthStrategyError: Access token cannot be empty
```

## ApiKeyAuth Changes

### 1. Empty API Key Validation

**Before**: Empty API keys accepted
```python
auth = ApiKeyAuth(api_key="", location="header", key_name="X-API-Key")  # No error
```

**After**: Raises `AuthStrategyError`
```python
auth = ApiKeyAuth(api_key="", location="header", key_name="X-API-Key")
# AuthStrategyError: API key cannot be empty
```

### 2. Location Validation

**Before**: Any location string accepted
```python
auth = ApiKeyAuth(api_key="key", location="custom", key_name="X-API-Key")  # No error
```

**After**: Only "header" or "query" allowed
```python
auth = ApiKeyAuth(api_key="key", location="custom", key_name="X-API-Key")
# AuthStrategyError: Invalid location 'custom'. Must be 'header' or 'query'
```

## CustomAuth Changes

### Exception Type Change

**Before**: Invalid callbacks raise `TypeError`
```python
try:
    auth = CustomAuth(apply_auth="not a function")
except TypeError:
    # Handle error
```

**After**: Raises `AuthStrategyError`
```python
try:
    auth = CustomAuth(apply_auth="not a function")
except AuthStrategyError:
    # Handle error
```

**Migration**: Update exception handlers to catch `AuthStrategyError`

## Migration Checklist

1. **Update imports** - Remove submodule references
2. **Update BearerAuth** - Change `token=` to `access_token=`
3. **Remove custom headers** - Use default or switch to CustomAuth
4. **Handle validation errors** - Catch AuthStrategyError for empty values
5. **Update exception handling** - Replace TypeError with AuthStrategyError

## Summary Table

| Component | Old Behavior | New Behavior | Action Required |
|-----------|--------------|--------------|-----------------|
| Import paths | Module structure | Single file | Update imports |
| Empty credentials | Allowed | Rejected | Add validation |
| BearerAuth param | `token=` | `access_token=` | Find/replace |
| Custom headers | Supported | Not supported | Use CustomAuth |
| Invalid callbacks | TypeError | AuthStrategyError | Update handlers |
| API key validation | None | Required | Ensure valid keys |

## Risk Assessment

- **Low Risk**: Import path changes (automated find/replace)
- **Medium Risk**: Parameter name changes (search and replace)
- **High Risk**: Exception handling changes (runtime errors if missed)
- **Critical**: Empty credential validation (may break existing code)
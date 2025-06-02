# Technical Migration Details

[← Back to Main README](./README.md)

## Overview
Technical specifications for migrating crudclient authentication to apiconfig library.

## Architecture Changes

### Current Structure
```
crudclient/auth/
├── __init__.py      # Module exports
├── base.py          # AuthStrategy base class (42 lines)
├── basic.py         # BasicAuth implementation (65 lines)
├── bearer.py        # BearerAuth implementation (61 lines)
├── custom.py        # CustomAuth + ApiKeyAuth (147 lines)
└── README.md        # Module documentation
Total: ~315 lines across 6 files
```

### Target Structure
```
crudclient/auth.py   # Re-exports from apiconfig (30 lines)
```

### Architecture Comparison

Current: Internal implementations with inheritance hierarchy
Target: Single file re-exporting apiconfig functionality

Benefits:
- 90% code reduction (285 lines removed)
- Delegate maintenance to apiconfig
- Access to apiconfig's token management features
- Simplified debugging and maintenance

## Implementation Details

### Step 1: Module Removal
Remove the existing auth module directory:
```bash
rm -rf crudclient/auth/
```

This removes:
- `__init__.py` - Module exports
- `base.py` - AuthStrategy base class
- `basic.py` - BasicAuth implementation
- `bearer.py` - BearerAuth implementation
- `custom.py` - CustomAuth and ApiKeyAuth implementations
- `README.md` - Module documentation

### Step 2: Create Consolidated File
Create new `crudclient/auth.py`:

```python
"""Authentication strategies re-exported from apiconfig.

This module delegates all authentication functionality to apiconfig.
See migration notes for breaking changes from previous versions.
"""

# Base classes
from apiconfig.auth.base import AuthStrategy
from apiconfig.exceptions.auth import AuthStrategyError

# Concrete strategies
from apiconfig.auth.strategies.basic import BasicAuth
from apiconfig.auth.strategies.bearer import BearerAuth
from apiconfig.auth.strategies.custom import CustomAuth
from apiconfig.auth.strategies.api_key import ApiKeyAuth

__all__ = [
    "AuthStrategy",
    "AuthStrategyError",
    "BasicAuth",
    "BearerAuth",
    "CustomAuth",
    "ApiKeyAuth",
]
```

## Import Path Updates

### Before
```python
from crudclient.auth.basic import BasicAuth
from crudclient.auth.bearer import BearerAuth
from crudclient.auth.custom import CustomAuth, ApiKeyAuth
from crudclient.auth.base import AuthStrategy
```

### After
```python
from crudclient.auth import BasicAuth
from crudclient.auth import BearerAuth
from crudclient.auth import CustomAuth, ApiKeyAuth
from crudclient.auth import AuthStrategy
```

## Benefits Summary

1. **Code Reduction**: 315 → 30 lines (90% reduction)
2. **Maintenance**: Delegated to apiconfig library
3. **Features**: Access to token refresh and validation
4. **Structure**: Simplified single-file module

## Feature Comparison

### BasicAuth
| Feature | crudclient (old) | apiconfig (new) |
|---------|------------------|-----------------|
| Empty username | Allowed | Raises AuthStrategyError |
| Empty password | Allowed | Raises AuthStrategyError |
| Whitespace validation | None | Enforced |

### BearerAuth
| Feature | crudclient (old) | apiconfig (new) |
|---------|------------------|-----------------|
| Parameter name | `token` | `access_token` |
| Custom headers | Supported | Not supported |
| Token refresh | Not supported | Supported |
| Expiry checking | Not supported | Supported |

### ApiKeyAuth
| Feature | crudclient (old) | apiconfig (new) |
|---------|------------------|-----------------|
| Empty API key | Allowed | Raises AuthStrategyError |
| Location validation | None | Must be "header" or "query" |

### CustomAuth
| Feature | crudclient (old) | apiconfig (new) |
|---------|------------------|-----------------|
| Invalid callbacks | TypeError | AuthStrategyError |
| Refresh support | Not supported | Supported |

## Migration Summary

- **Code**: 315 lines → 30 lines (90% reduction)
- **Files**: 6 files → 1 file
- **Maintenance**: Self-maintained → Delegated to apiconfig
- **Testing**: Full unit test coverage → Integration tests only
- **API Changes**: Minor parameter and validation changes
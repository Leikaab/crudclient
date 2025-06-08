# ResourceGroup Feature

This document describes the `ResourceGroup` feature in the `crudclient` library, which enables typed, hierarchical nesting of API resources.

## Overview

The `ResourceGroup` class is a powerful feature that allows SDK developers to organize related API resources under a common path segment. It serves a dual purpose:

1. **CRUD Operations**: As a subclass of `Crud`, a `ResourceGroup` can perform CRUD operations on its own path segment.
2. **Resource Container**: It acts as a container for child resources (both `Crud` instances and nested `ResourceGroup` instances).

This approach provides several benefits:

- **Improved Type Hinting and Autocompletion**: Enables full type support for nested resource structures, making IDEs and tools like MyPy more effective.
- **Better Code Organization**: Creates a hierarchical structure that mirrors the API's organization, making the SDK codebase cleaner and more maintainable.
- **Namespace Management**: Logically groups related resources, reducing clutter in the main `API` class.

## ResourceGroup Basics

### Inheritance from Crud

`ResourceGroup` inherits from `Crud`, which means it can perform standard CRUD operations on its own path segment. This allows a resource group to not only contain child resources but also to have its own operations.

```python
class ResourceGroup(Crud, ABC):
    """
    Base class for grouping related CRUD resources and other ResourceGroups
    under a common path segment. A ResourceGroup can also have its own
    CRUD operations for its base path, inherited from Crud.
    """
```

### Key Attributes

Like any `Crud` subclass, a `ResourceGroup` can define:

- `_resource_path`: The base path for the resource group in the API
- `_datamodel`: The data model class for the resource group
- `_api_response_model`: Custom API response model, if any
- `allowed_actions`: List of allowed methods for this resource group

### Registration Methods

`ResourceGroup` defines two key methods for registering child resources:

1. `_register_child_endpoints()`: For registering child `Crud` resources
2. `_register_child_groups()`: For registering nested `ResourceGroup` instances

These methods are called during initialization and should be overridden by subclasses to define the resource hierarchy.

## Defining ResourceGroup Subclasses

### Basic Structure

To create a `ResourceGroup` subclass, you need to:

1. Define the class attributes (`_resource_path`, `_datamodel`, etc.)
2. Override the registration methods as needed

```python
from crudclient.groups import ResourceGroup
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

class UserResponse(ApiResponse[User]):
    pass

class UserGroup(ResourceGroup):
    _resource_path = "users"
    _datamodel = User
    _api_response_model = UserResponse
    allowed_actions = ["list", "read"]  # This group can perform list and read operations

    def _register_child_endpoints(self) -> None:
        self.posts = UserPostsCrud(self.client, parent=self)
        self.albums = UserAlbumsCrud(self.client, parent=self)
```

### Setting Resource Path

The `_resource_path` attribute defines the path segment for this resource group. For nested groups, this path is relative to the parent:

```python
class LedgerGroup(ResourceGroup):
    _resource_path = "ledger"  # Results in /ledger

class VoucherGroup(ResourceGroup):
    _resource_path = "voucher"  # When nested under LedgerGroup, results in /ledger/voucher
```

### Configuring CRUD Operations

A `ResourceGroup` can have its own CRUD operations by setting the appropriate attributes:

```python
class LedgerGroup(ResourceGroup):
    _resource_path = "ledger"
    _datamodel = Ledger
    _api_response_model = LedgerResponse
    allowed_actions = ["list", "read"]  # This group can perform list and read operations
```

The `allowed_actions` list controls which CRUD operations are available on the group itself. If a method is not in this list, it won't be available on the instance.

## Implementing Registration Methods

### Registering Child Endpoints

Override `_register_child_endpoints()` to register `Crud` resources as direct attributes of the `ResourceGroup`:

```python
def _register_child_endpoints(self) -> None:
    """
    Register child Crud resources for user-related endpoints.
    """
    self.posts = UserPostsCrud(self.client, parent=self)
    self.albums = UserAlbumsCrud(self.client, parent=self)
    self.todos = UserTodosCrud(self.client, parent=self)
```

### Registering Child Groups

Override `_register_child_groups()` to register nested `ResourceGroup` instances:

```python
def _register_child_groups(self) -> None:
    """
    Register nested ResourceGroup instances.
    """
    self.voucher = VoucherGroup(self.client, parent=self)
```

### The Importance of parent=self

When registering child resources or groups, always pass `parent=self` to establish the parent-child relationship. This is crucial for correct path construction:

```python
self.voucher = VoucherGroup(self.client, parent=self)
```

This ensures that when operations are performed on the child resource, the full path is correctly constructed (e.g., `/ledger/voucher`).

## ResourceGroup Types

### ResourceGroups with Direct CRUD Operations

A `ResourceGroup` can have its own CRUD operations on its path segment:

```python
class LedgerGroup(ResourceGroup):
    _resource_path = "ledger"
    _datamodel = Ledger
    _api_response_model = LedgerResponse
    allowed_actions = ["list", "read"]  # This group can perform list and read operations

    def _register_child_endpoints(self) -> None:
        self.accounts = AccountsCrud(self.client, parent=self)
```

With this configuration, you can perform operations directly on the group:

```python
# Get a list of ledgers
ledger_response = api.ledger.list()
ledgers = ledger_response.values
# ``list`` returns the full API response when a response model is defined.
# Use the ``values`` or ``data`` attribute to access the list itself.

# Get a specific ledger
ledger = api.ledger.read(resource_id=123)

# Access a child resource
accounts = api.ledger.accounts.list()
```

### Purely Organizational ResourceGroups

A `ResourceGroup` can also be purely organizational, with no direct CRUD operations:

```python
class VoucherGroup(ResourceGroup):
    _resource_path = "voucher"
    allowed_actions = []  # No direct CRUD operations

    def _register_child_endpoints(self) -> None:
        self.historical = HistoricalVoucherCrud(self.client, parent=self)
```

In this case, the group serves only as a container for child resources:

```python
# This would raise an AttributeError since list is not in allowed_actions
# api.ledger.voucher.list()

# Access a child resource
historical_vouchers = api.ledger.voucher.historical.list()
```

## Integration with API Class

### Registering Top-Level ResourceGroups

The `API` base class includes an abstract method `_register_groups()` that must be implemented by subclasses to register top-level `ResourceGroup` instances:

```python
class MyAPI(API):
    client_class = MyClient

    def _register_endpoints(self) -> None:
        self.countries = CountriesCrud(self.client)

    def _register_groups(self) -> None:
        self.ledger = LedgerGroup(self.client, parent=None)
```

For top-level groups, pass `parent=None` to indicate that they are not nested under another resource.

### Usage Example

Here's a complete example showing how to use `ResourceGroup` in an API client:

```python
from crudclient.api import API
from crudclient.client import Client
from crudclient.crud import Crud
from crudclient.groups import ResourceGroup
from pydantic import BaseModel

# Define models
class User(BaseModel):
    id: int
    name: str
    email: str

class Post(BaseModel):
    id: int
    userId: int
    title: str
    body: str

# Define CRUD resources
class UserPostsCrud(Crud):
    _resource_path = "posts"
    _datamodel = Post
    allowed_actions = ["list", "read"]

# Define resource groups
class UserGroup(ResourceGroup):
    _resource_path = "users"
    _datamodel = User
    allowed_actions = ["list", "read"]

    def _register_child_endpoints(self) -> None:
        self.posts = UserPostsCrud(self.client, parent=self)

# Define API
class MyAPI(API):
    client_class = Client

    def _register_endpoints(self) -> None:
        # Register top-level CRUD resources
        pass

    def _register_groups(self) -> None:
        # Register top-level resource groups
        self.users = UserGroup(self.client, parent=None)

# Usage
api = MyAPI(client_config=config)
user_response = api.users.list()  # GET /users
users = user_response.values
# The ``ApiResponse`` wrapper includes additional metadata; access ``values`` or
# ``data`` for the actual items.
user = api.users.read(resource_id=1)  # GET /users/1
user_posts = api.users.posts.list(parent_id=1)  # GET /users/1/posts
```

## Considerations

### Namespace Management

Be careful with attribute naming to avoid collisions:

- Attribute names used for child resources should not conflict with standard `Crud` methods or other attributes.
- If a custom action conceptually mirrors a standard CRUD operation, use a distinctive name (e.g., `create_with_options()` instead of `create()`).

### Allowed Actions Behavior

The `allowed_actions` list controls which CRUD operations are available on a `ResourceGroup`:

- Methods corresponding to operations not listed in `allowed_actions` will not be available.
- For purely organizational groups, set `allowed_actions = []` to disable all direct CRUD operations.

### Path Construction

The path for a nested resource is constructed by combining the paths of all its ancestors:

1. For a top-level `ResourceGroup` with `parent=None`, the path is simply its `_resource_path`.
2. For a nested `ResourceGroup` or `Crud` with a parent, the path is the parent's path plus its own `_resource_path`.

This hierarchical path construction is handled automatically by the `Crud._get_endpoint()` method.
## Further Reading

- [Design Proposal](design_proposal_resource_groups.md)
- [Implementation Plan](implementation_plan_resource_groups.md)

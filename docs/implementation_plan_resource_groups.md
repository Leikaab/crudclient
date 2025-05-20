# Implementation Plan: ResourceGroup Feature

This document outlines the detailed steps required to implement the `ResourceGroup` feature in the `crudclient` library, as defined in `docs/design_proposal_resource_groups.md`.

## 1. Prerequisites and Goals Review

*   **Goal:** Implement the `ResourceGroup` class to enable typed, hierarchical nesting of API resources, improving type hinting and code organization for SDK developers.
*   **Key Design Document:** All implementation details should align with [`docs/design_proposal_resource_groups.md`](docs/design_proposal_resource_groups.md).
*   **Branching Strategy (Assumed):** Implementation should occur on a new feature branch (e.g., `feature/resource-groups`).

## 2. Core Component Implementation

### 2.1. Create `ResourceGroup` Base Class

*   **File:** `crudclient/groups.py` (New file)
*   **Class Definition:**
    ```python
    # crudclient/groups.py
    from typing import Optional, Type, Any, List
    from abc import ABC # Required if ResourceGroup itself has abstract methods not from Crud
    # from abc import abstractmethod # Uncomment if making _register_child_... abstract

    # Assuming these are the correct relative paths based on crudclient structure
    from .client import Client
    from .crud.base import Crud
    # from pydantic import BaseModel # Import if BaseModel is used in type hints here

    class ResourceGroup(Crud, ABC): # Inherits from Crud. Add ABC if its own methods are abstract.
        """
        Base class for grouping related CRUD resources and other ResourceGroups
        under a common path segment. A ResourceGroup can also have its own
        CRUD operations for its base path, inherited from Crud.
        """

        # Class variables like _resource_path, _datamodel, allowed_actions are inherited from Crud.
        # Subclasses of ResourceGroup will define these to configure the ResourceGroup's
        # own CRUD behavior for its specific path segment.

        def __init__(self, client: Client, parent: Optional[Crud] = None):
            """
            Initializes the ResourceGroup.

            Args:
                client: The API client instance.
                parent: The parent Crud instance (could be another ResourceGroup,
                        or None for top-level ResourceGroups instantiated directly by the API class).
            """
            super().__init__(client, parent) # Initialize Crud capabilities for this ResourceGroup

            # Call methods to register nested items.
            # These methods will be implemented by subclasses of ResourceGroup.
            self._register_child_endpoints()
            self._register_child_groups()

        # Option: Define with default 'pass' implementation (more flexible)
        def _register_child_endpoints(self) -> None:
            """
            Subclasses should override this method to register child Crud resources.
            These resources will become direct attributes of the ResourceGroup instance.
            Example in a subclass: self.accounts = AccountsCrud(self.client, parent=self)
            """
            pass

        # Option: Define with default 'pass' implementation
        def _register_child_groups(self) -> None:
            """
            Subclasses should override this method to register nested ResourceGroup instances.
            These groups will become direct attributes of the ResourceGroup instance.
            Example in a subclass: self.vouchers = VoucherGroup(self.client, parent=self)
            """
            pass

    # Example of how an SDK developer might use it (for illustrative purposes):
    #
    # from pydantic import BaseModel
    #
    # class MyChildCrud(Crud):
    #     _resource_path = "child_items"
    #     # ... other Crud configurations ...
    #
    # class MyInnerGroup(ResourceGroup):
    #     _resource_path = "inner_group"
    #     # ... Crud configurations for "/parent_group/inner_group" ...
    #
    #     def _register_child_endpoints(self):
    #         self.items = MyChildCrud(self.client, parent=self)
    #
    # class MyParentGroup(ResourceGroup):
    #     _resource_path = "parent_group"
    #     # ... Crud configurations for "/parent_group" ...
    #
    #     def _register_child_groups(self):
    #         self.inner = MyInnerGroup(self.client, parent=self)
    ```
*   **Key Decisions & Implementation Notes:**
    *   **Abstract vs. Default Implementation for Registration Methods:** The current preference is for `_register_child_endpoints` and `_register_child_groups` to have default `pass` implementations. This means `ResourceGroup` does not strictly need to inherit from `ABC` unless `Crud` itself does and `ResourceGroup` adds new abstract methods. If `Crud` is not an `ABC`, then `ResourceGroup` doesn't need to be either, for these methods. Confirm `Crud`'s ABC status.
    *   **Imports:** Verify and use correct relative imports for `Client` and `Crud`.
    *   **Docstrings:** Ensure clear and comprehensive docstrings for the class and methods, explaining its dual role (as a `Crud` endpoint and as a container). Adhere to NumPy docstring format.

### 2.2. Modify `API` Base Class

*   **File:** `crudclient/api.py`
*   **Modifications:**
    1.  Ensure `ABC` and `abstractmethod` are imported from `abc`.
    2.  Add the new abstract method to the `API` class definition (which already inherits from `ABC`):
        ```python
        # In class API(ABC):
        # ... (after _register_endpoints definition)

        @abstractmethod
        def _register_groups(self) -> None:
            """
            Abstract method for subclasses to register top-level ResourceGroup instances.
            These groups will become direct attributes of the API instance.
            Example in a subclass: self.ledger = LedgerGroup(self.client, parent=None)
            """
            pass
        ```
    3.  Update `API.__init__` to call `self._register_groups()`:
        ```python
        # In API.__init__ method:
        # ... (ensure self.client is initialized)
        # self._register_endpoints() # This call already exists
        self._register_groups()   # Add this call after client init and endpoint registration
        ```

## 3. Testing

### 3.1. Unit Tests for `ResourceGroup`

*   **File:** `tests/unit/test_groups.py` (New file)
*   **Test Cases:**
    *   **Initialization:**
        *   Verify `ResourceGroup.__init__` correctly calls `super().__init__(client, parent)`.
        *   Verify `self.client` and `self.parent` are set as expected.
        *   Mock `_register_child_endpoints` and `_register_child_groups` and verify they are called during `__init__`.
    *   **Behavior as a `Crud` Instance:**
        *   Create a simple `ConcreteResourceGroup(ResourceGroup)` subclass.
        *   Set `_resource_path`, `_datamodel`, `allowed_actions` on `ConcreteResourceGroup`.
        *   Mock the `client` passed to `ConcreteResourceGroup`.
        *   Call standard CRUD methods (e.g., `group.read(resource_id="123")`, `group.list()`) on an instance of `ConcreteResourceGroup`.
        *   Verify that the mocked `client` receives calls with correctly constructed URLs (reflecting the group's `_resource_path` and `parent` if provided) and parameters.
    *   **Child Registration and Pathing:**
        *   Define `ConcreteParentGroup(ResourceGroup)` that registers a `ConcreteChildCrud(Crud)` in `_register_child_endpoints` and a `ConcreteChildGroup(ResourceGroup)` in `_register_child_groups`.
        *   Instantiate `ConcreteParentGroup(client, parent=None)`.
        *   Verify `parent_group.child_crud.parent` is `parent_group`.
        *   Verify `parent_group.child_group.parent` is `parent_group`.
        *   Test path construction for `parent_group.child_crud` and `parent_group.child_group` (e.g., by calling a method on them that would trigger `_get_endpoint`).

### 3.2. Unit Tests for `API` Class Modifications

*   **File:** `tests/unit/api/test_api.py` (Existing file, add new tests)
*   **Test Cases:**
    *   Verify `API.__init__` calls the new `_register_groups` method (e.g., using a mock).
    *   Create a simple `ConcreteAPI(API)` that implements `_register_endpoints` and `_register_groups`.
    *   In `_register_groups`, instantiate a mockable `ResourceGroup` subclass.
    *   Verify the `ResourceGroup` instance is correctly initialized (client passed, `parent=None`).
    *   Verify the group is accessible as an attribute on the `ConcreteAPI` instance.

### 3.3. Integration Tests (Against Live APIs)

*   **Objective:** To validate the `ResourceGroup` feature against live APIs, demonstrating its real-world applicability, correct path construction for nested resources, and proper handling of CRUD operations through the group hierarchy. This will be done in two stages: an initial validation with a simple public API, followed by a more complex validation against the Tripletex API.

#### 3.3.1. Stage 1: Initial Validation with JSONPlaceholder API

*   **Target API:** JSONPlaceholder (`https://jsonplaceholder.typicode.com/`).
*   **Rationale:** Public, no authentication, simple nestable resources. Good for initial structural validation.
*   **Files to Modify/Create (within `tests/integration/jsonplaceholder_resources/` and `tests/integration/test_jsonplaceholder.py`):**
    *   **`groups.py` (New File):**
        *   Define `UserGroup(ResourceGroup)` with `_resource_path = "users"`.
            *   This group will handle operations directly on `/users` (e.g., listing all users, getting a specific user by ID).
            *   It will implement `_register_child_endpoints` to register `UserPostsCrud`, `UserAlbumsCrud`, `UserTodosCrud`.
    *   **`resources.py` (Modify Existing):**
        *   Adapt/Create `Crud` subclasses: `UserPostsCrud(Crud)` (path "posts"), `UserAlbumsCrud(Crud)` (path "albums"), `UserTodosCrud(Crud)` (path "todos"). These will take `parent=UserGroup_instance` in their constructor.
    *   **`api.py` (Modify Existing or New):**
        *   Refactor/Create `JSONPlaceholderAPI(API)`.
        *   Implement `_register_groups` to instantiate `UserGroup` (e.g., `self.users = UserGroup(self.client, parent=None)`).
        *   Any non-user-nested top-level resources (e.g., `/posts` directly if desired) would remain in `_register_endpoints`.
    *   **`models.py` (Modify Existing):**
        *   Ensure Pydantic models for User, Post, Album, Todo are accurate.
    *   **`test_jsonplaceholder.py` (Modify Existing):**
        *   Update test cases to use the new `ResourceGroup`-based API structure for user-related endpoints. Examples:
            *   `api.users.list()` (List all users - operation on `UserGroup`).
            *   `api.users.read(resource_id=1)` (Get user 1 - operation on `UserGroup`).
            *   `api.users.posts.list(parent_id=1)` (List posts for user 1 - `UserPostsCrud` under `UserGroup`. Note: `parent_id` here refers to the `userId` needed by the `/users/{userId}/posts` path, which `UserPostsCrud` would handle in its `_get_endpoint` or operation methods).
            *   Similar tests for `api.users.albums.list(parent_id=1)` and `api.users.todos.list(parent_id=1)`.
*   **Success Criteria for Stage 1:** Tests pass against the live JSONPlaceholder API, demonstrating basic nesting, path construction, and operation delegation with `ResourceGroup`.

#### 3.3.2. Stage 2: Advanced Validation with Tripletex API

*   **Target API:** Tripletex.
*   **Rationale:** Complex, stateful, authenticated API that was an original motivation for the `ResourceGroup` feature. Provides a robust test of its capabilities in a real-world scenario.
*   **Focus Area for Refactoring:** Identify a specific, deeply nested part of the Tripletex API (e.g., `ledger` and its sub-resources like `voucher`, `voucher.historical`, or `bank.reconciliation.entry`).
*   **Files to Modify/Create (within `tests/integration/tripletex_resources/` and relevant test files like `tests/integration/test_tripletex.py`):**
    *   **`groups.py` (New or Augment Existing):**
        *   Define `LedgerGroup(ResourceGroup)` with `_resource_path = "ledger"`.
            *   Configure its own CRUD capabilities for `/ledger` if applicable.
            *   In `_register_child_groups`, register `VoucherGroup(ResourceGroup)`.
            *   In `_register_child_endpoints`, register other direct ledger children (e.g., `AccountingPeriodCrud(TripletexCrud)`).
        *   Define `VoucherGroup(ResourceGroup)` with `_resource_path = "voucher"`.
            *   Registered under `LedgerGroup`.
            *   In `_register_child_endpoints`, register `HistoricalVoucherCrud(TripletexCrud)`, `OpeningBalanceCrud(TripletexCrud)`, etc.
    *   **`resources.py` (Modify Existing):**
        *   Adapt existing `TripletexCrud` subclasses for ledger, voucher, etc., to:
            *   Accept a `parent` argument in their `__init__` (if they override it, otherwise `Crud` base handles it).
            *   Have their `_resource_path` be relative to their parent group (e.g., `HistoricalVoucherCrud` would have `_resource_path = "historical"`).
    *   **`api.py` (Modify `TripletexAPI` in `tests/integration/tripletex_resources/client.py`):**
        *   In `_register_groups`, instantiate `LedgerGroup` (e.g., `self.ledger = LedgerGroup(self.client, parent=None)`).
        *   Remove any old-style manual attribute assignments for ledger sub-endpoints that are now managed by the `LedgerGroup` and its children.
    *   **Relevant Test Files (e.g., `test_tripletex.py`, or a new `test_tripletex_ledger_nested.py`):**
        *   Write new test cases or refactor existing ones to specifically target operations through the new `ResourceGroup` hierarchy for the chosen Tripletex nested resources. Examples:
            *   `api.ledger.read(...)` (If `LedgerGroup` supports read on `/ledger`).
            *   `api.ledger.voucher.list(...)` (If `VoucherGroup` supports list on `/ledger/voucher`).
            *   `api.ledger.voucher.historical.create(...)`.
        *   Verify correct path construction, authentication, request data, and response parsing for these nested operations against the live Tripletex test API.
*   **Environment Variables/Authentication:** Ensure tests correctly utilize existing Tripletex test credentials and authentication mechanisms.
*   **Success Criteria for Stage 2:** Complex nested operations using `ResourceGroup`s work correctly against the live Tripletex test API. The refactored Tripletex SDK structure within the tests is clearer and more maintainable.

## 4. Documentation Updates

*   Refer to the "Documentation Plan" section in [`docs/design_proposal_resource_groups.md`](docs/design_proposal_resource_groups.md).
*   **Tasks:**
    1.  Create a new documentation page for `ResourceGroup` (e.g., `docs/resource_groups.md`).
        *   Explain purpose, benefits, inheritance from `Crud`.
        *   Detail how to define `ResourceGroup` subclasses: setting `_resource_path`, `_datamodel`, `allowed_actions` for the group's own operations.
        *   Explain and provide examples for implementing `_register_child_endpoints` and `_register_child_groups`, emphasizing `parent=self`.
        *   Include examples of `ResourceGroup`s with direct CRUD ops and purely organizational ones.
    2.  Update `API` class documentation (docstrings in `crudclient/api.py`, and any related `.md` files like `docs/api.md` if it exists).
        *   Document the new `_register_groups` abstract method and its purpose.
        *   Update API usage examples to include `ResourceGroup` registration.
    3.  Update general `crudclient` usage guides or `README.md` to introduce `ResourceGroup` as a key feature for structuring complex SDKs, with a concise example.
    4.  Incorporate relevant points from the "Considerations for `ResourceGroup(Crud)` Implementation" section of `docs/design_proposal_resource_groups.md` into the new/updated documentation (e.g., namespace management, `allowed_actions` behavior).

## 5. Code Style and Quality

*   **Adherence to Project Standards:** All new and modified code must strictly adhere to the project's established code style and quality standards, primarily enforced via pre-commit hooks.
*   **Formatting (via Pre-commit):**
    *   Code formatting will be enforced using **Black** with the project's configuration (line length 150, target version py310, as specified in `pyproject.toml`).
    *   Imports will be sorted using **isort** with the "black" profile (as specified in `pyproject.toml` and `.pre-commit-config.yaml`).
    *   Unused imports and variables will be removed by **autoflake** (as specified in `.pre-commit-config.yaml`).
    *   Trailing whitespace will be removed (as specified in `.pre-commit-config.yaml`).
*   **Linting and Static Analysis (via Pre-commit and Project Dependencies):** Code will be checked against the following tools:
    *   **Flake8** (enforced by pre-commit).
    *   **MyPy** for static type checking (enforced by pre-commit). New code in `crudclient/` (e.g., `crudclient/groups.py`) must adhere to the stricter type checking rules defined in `mypy.ini` (including `disallow_untyped_defs`, `disallow_incomplete_defs`, `no_implicit_optional`, `strict_optional`, etc.). The Pydantic MyPy plugin is enabled.
    *   **Pylint** (listed as a dev dependency in `pyproject.toml`; ensure checks pass).
    *   **Bandit** (listed as a dev dependency in `pyproject.toml`; ensure checks pass for security analysis).
    *   **pycodestyle** (often integrated with Flake8).
    *   **pydocstyle** (listed as a dev dependency in `pyproject.toml`; for docstring conventions).
*   **Custom Checks (via Pre-commit):**
    *   Adherence to file length limits (e.g., `check-file-length` script as specified in `.pre-commit-config.yaml`).
*   **Pre-commit Hooks:** All configured pre-commit hooks (as defined in `.pre-commit-config.yaml`) must pass before code is committed.
*   **Testing via Hooks:**
    *   `pytest` will be run on changed files as a pre-commit hook.
    *   `pytest --cov` will be run as a pre-push hook.
*   **Type Hinting:** Provide comprehensive and accurate type hinting for all new and modified classes and methods, ensuring MyPy checks pass under the project's configuration.
*   **Docstrings:** Write clear, concise, and accurate docstrings for all public classes, methods, and new modules.
    *   **Style Convention:** The project aims to standardize on **NumPy docstring format**. New code for the `ResourceGroup` feature should adhere to this convention.
    *   **Guidance for Implementing Agent:** Refer to the NumPy docstring guide (e.g., [https://numpydoc.readthedocs.io/en/latest/format.html](https://numpydoc.readthedocs.io/en/latest/format.html)) for detailed formatting of Parameters, Returns, Attributes, Examples, etc. Ensure new docstrings are written in this style from the outset. `pydocstyle` (a dev dependency) will be used to enforce this.

---
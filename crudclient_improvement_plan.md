# CrudClient Improvement Plan

This plan integrates suggestions, code analysis findings, and existing improvement items into a cohesive strategy for the `crudclient` library.

**Phase 1: Core Refactoring & Foundational Improvements**

1.  **Refactor Client & Authentication Logic:** ✅
    *   **Goal:** Decouple authentication logic, improve modularity, and make it easier for users to add custom authentication methods.
    *   **Action:** Implement the **Strategy Pattern** for authentication. ✅
        *   Define a base `AuthStrategy` protocol/abstract class in `crudclient/auth/base.py`. ✅
        *   Implement concrete strategies: `BearerAuth(AuthStrategy)`, `BasicAuth(AuthStrategy)`, etc., in `crudclient/auth/`. ✅
        *   Refactor `ClientConfig` to accept an `AuthStrategy` instance instead of handling auth logic directly. ✅
        *   Refactor `Client._request` (or a dedicated method called by it) to use the configured `AuthStrategy` to prepare the request. ✅
    *   **Action:** Restructure the `crudclient` directory: ✅
        ```
        crudclient/
            __init__.py
            client.py      # Core Client, _request logic
            config.py      # ClientConfig (now simpler, holds AuthStrategy)
            crud.py
            api.py
            models.py
            exceptions.py
            types.py
            auth/          # Authentication strategies
                __init__.py
                base.py        # Base AuthStrategy protocol/ABC
                bearer.py      # Bearer token implementation
                basic.py       # Basic auth implementation
                custom.py      # Custom auth implementation
        ```
    *   **Diagram (Illustrative):**
        ```mermaid
        graph TD
            subgraph Client Configuration
                Config[ClientConfig] -- holds --> AuthStrat[AuthStrategy]
            end

            subgraph Authentication Strategies
                AuthStrat -- implements --> BaseAuth(AuthStrategy Base)
                BaseAuth <|-- BearerAuth
                BaseAuth <|-- BasicAuth
                BaseAuth <|-- CustomAuth
            end

            subgraph Client Execution
                Client -- uses --> Config
                Client -- prepares request using --> AuthStrat
            end
        ```

2.  **Enhance Error Handling & Logging:** ✅
    *   **Goal:** Provide better debugging information and more specific error types.
    *   **Action:** Implement enhanced request/response logging in `Client._request` at DEBUG level. ✅
    *   **Action:** Define `CrudClientError(APIError)` and potentially more specific errors (`AuthenticationError`, `NotFoundError`, `InvalidResponseError`, `ModelConversionError`) in `exceptions.py`. ✅
    *   **Action:** Refactor `Client._handle_error_response` to raise `CrudClientError`, embedding the original `requests.HTTPError` and the raw `requests.Response`. ✅
    *   **Action:** Refactor `Crud.custom_action`'s `try/except ValueError` to log details and raise a specific `ModelConversionError` instead of returning the raw response. ✅

3.  **Address Core Robustness Issues:** ✅
    *   **Goal:** Fix potential bugs and improve reliability.
    *   **Action:** Improve URL construction in `Client._request` while maintaining backward compatibility. ✅
        * Note: We decided against using `urllib.parse.urljoin` to maintain backward compatibility with existing tests and integrations.
    *   **Action:** Use `startswith()` or a proper MIME parser for Content-Type checking in `Client._handle_response`. ✅
    *   **Action:** Replace runtime `assert` checks in `Crud.__init__` and `Crud._dump_data` with explicit `isinstance` checks raising `TypeError` or `ValueError`. ✅
    *   **Action:** Ensure `API._initialize_client` is called *before* `_register_endpoints` during initialization. ✅

**Phase 2: Type Safety & API Refinements**

4.  **Define Type Safety Strategy:**
    *   **Goal:** Ensure type correctness both statically and, where critical, at runtime.
    *   **Action:** Remove `crudclient/runtime_type_checkers.py` and its usages.
    *   **Action:** Rely primarily on:
        *   **Comprehensive Static Typing:** Continue using `mypy` and detailed `.pyi` stubs. Enable stricter `mypy` checks progressively.
        *   **Pydantic Validation:** Leverage Pydantic's validation for data entering/leaving the `Crud` layer via API interactions.
        *   **Targeted Runtime Checks:** Use explicit `isinstance` checks in critical internal logic or public API entry points where type errors are likely and detrimental.
    *   **Action (Evaluation):** Evaluate `typeguard` as an *optional* dependency or configuration for users who need stricter runtime guarantees.

5.  **Refine API/CRUD Layer:**
    *   **Goal:** Improve flexibility, readability, and maintainability of the `Crud` and `API` layers.
    *   **Action:** Design and implement a more flexible strategy for Pydantic response model handling in `Crud`.
    *   **Action:** Refactor complex `Crud` methods (`_get_endpoint`, `_validate_list_return`) for clarity, potentially using helper methods.
    *   **Action:** Consider refactoring `Client._prepare_data` to return headers/data instead of modifying session state directly.
    *   **Action:** Use `typing.overload` for `Client._request` to provide more precise return types based on parameters.
    *   **Action:** Evaluate `RoleBasedModel` - decide if it belongs in the core `models.py` or should be moved to examples/documentation.
    *   **Action:** Evaluate `ClientConfig.__add__` - consider replacing with a more explicit `merge_configs` function if the operator overloading is deemed unclear or inefficient.

**Phase 3: Testing, Documentation & Polish**

6.  **Enhance Testing:**
    *   **Goal:** Increase confidence in the library's correctness and robustness.
    *   **Action:** Use specific Pydantic models in integration tests.
    *   **Action:** Add more tests for error conditions (4xx, 5xx, network errors, malformed responses).
    *   **Action:** Investigate downstream testing strategies.

7.  **Update Documentation & Stubs:** ✅
    *   **Goal:** Ensure documentation and type information are accurate and reflect the changes.
    *   **Action:** Update `ARCHITECTURE.md`, `CONTRIBUTING.md`, `README.md` as needed to reflect the new structure, patterns (Strategy), and decisions. ✅
    *   **Action:** Ensure all public API docstrings are comprehensive and located *only* in `.pyi` files. ✅
        *   Created `.pyi` files for exceptions module ✅
        *   Created `.pyi` files for auth module ✅
        *   Created `.pyi` files for api, crud, models, types, runtime_type_checkers, __init__ module ✅
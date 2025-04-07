# CrudClient Improvement Plan

This plan integrates suggestions, code analysis findings, and existing improvement items into a cohesive strategy for the `crudclient` library.

**Phase 1: Core Refactoring & Foundational Improvements** ✅

Summary of what we did: Core Refactoring & Stability Upgrades

Modular Authentication: Introduced a pluggable auth system using the Strategy Pattern. AuthStrategy interface implemented via BearerAuth, BasicAuth, etc., and injected via ClientConfig.

Project Restructure: Cleaned up crudclient/ layout for better separation of concerns, especially for auth logic.

Improved Error Handling: Added specific error types, structured exceptions, and debug-level request/response logging.

Robustness Fixes: Patched edge cases in URL building, Content-Type parsing, and type safety. Reordered internal init sequence for consistency.


**Phase 2: Type Safety & API Refinements**

1.  **Refactor Client into Smaller Modules with Better Decoupling:** ✅
    *   **Goal:** Improve modularity, testability, and maintainability of the client code by breaking it down into smaller, focused components.
    *   **Action:** Implement a modular architecture with clear separation of concerns: ✅
        *   **Core HTTP Client Module** (`crudclient/http/client.py`): Focused solely on making HTTP requests. ✅
            * Responsible for the basic HTTP operations (GET, POST, PUT, etc.)
            * Delegates to specialized components for other concerns
        *   **Request Preparation Module** (`crudclient/http/request.py`): Handles request formatting and content-type setting. ✅
            * Extracts `_prepare_data` method into a dedicated `RequestFormatter` class
            * Provides methods for different content types (JSON, form data, multipart)
        *   **Response Handling Module** (`crudclient/http/response.py`): Processes and validates responses. ✅
            * Extracts `_handle_response` method into a dedicated `ResponseHandler` class
            * Provides content-type specific response parsing
        *   **Retry Module** (`crudclient/http/retry.py`): Manages retry policies and backoff strategies. ✅
            * Implements various retry strategies (fixed, exponential backoff)
            * Extracts `_maybe_retry_after_403` into a more general retry mechanism
            * Supports custom retry conditions and callbacks
        *   **Error Handling Module** (`crudclient/http/errors.py`): Centralizes error processing logic. ✅
            * Extracts `_handle_error_response` into a dedicated `ErrorHandler` class
            * Maps HTTP status codes to appropriate exceptions
        *   **Session Management Module** (`crudclient/http/session.py`): Manages HTTP sessions and their lifecycle. ✅
            * Handles session creation, configuration, and cleanup
            * Configures adapters, timeouts, and other session parameters
    *   **Action:** Refactor the main `Client` class to use these components: ✅
        ```python
        class Client:
            def __init__(self, config: ClientConfig) -> None:
                self.config = config
                self.session_manager = SessionManager(config)
                self.request_formatter = RequestFormatter()
                self.response_handler = ResponseHandler()
                self.error_handler = ErrorHandler()
                self.retry_handler = RetryHandler(config)

            def _request(self, method, endpoint, **kwargs):
                # Simplified request flow using the specialized components
                session = self.session_manager.get_session()
                prepared_request = self.request_formatter.prepare(method, endpoint, **kwargs)

                response = self.retry_handler.execute(
                    lambda: session.request(**prepared_request)
                )

                if not response.ok:
                    self.error_handler.handle(response)

                return self.response_handler.process(response)
        ```
    *   **Diagram (Illustrative):**
        ```mermaid
        graph TD
            subgraph Client Architecture
                Client --> SessionManager
                Client --> RequestFormatter
                Client --> ResponseHandler
                Client --> ErrorHandler
                Client --> RetryHandler

                SessionManager --> AuthStrategy
                RetryHandler --> RetryStrategy
            end

            subgraph External Components
                Crud --> Client
                API --> Client
            end
        ```

2.  **Define Type Safety Strategy:** ✅
    *   **Goal:** Ensure type correctness both statically and, where critical, at runtime.
    *   **Action:** Remove `crudclient/runtime_type_checkers.py` and its usages. ✅
    *   **Action:** Rely primarily on: ✅
        *   **Comprehensive Static Typing:** Continue using `mypy` and detailed `.pyi` stubs. Enable stricter `mypy` checks progressively. ✅
        *   **Pydantic Validation:** Leverage Pydantic's validation for data entering/leaving the `Crud` layer via API interactions. ✅
        *   **Targeted Runtime Checks:** Use explicit `isinstance` checks in critical internal logic or public API entry points where type errors are likely and detrimental. ✅
    *   **Summary:** The type safety strategy has been defined and documented in `type_safety_strategy_specification.md`. The approach relies on a combination of comprehensive static typing (`mypy`, `.pyi` stubs), Pydantic validation for API boundaries, and targeted runtime checks for critical paths, replacing the previous runtime-heavy approach. The initial action item of removing `runtime_type_checkers.py` was also completed.

3.  **Refine API/CRUD Layer:**
    *   **Goal:** Improve flexibility, readability, and maintainability of the `Crud` and `API` layers.
    *   **Action:** Design and implement a more flexible strategy for Pydantic response model handling in `Crud`.
    *   **Action:** Refactor complex `Crud` methods (`_get_endpoint`, `_validate_list_return`) for clarity, potentially using helper methods.
    *   **Action:** Consider refactoring `Client._prepare_data` to return headers/data instead of modifying session state directly.
    *   **Action:** Use `typing.overload` for `Client._request` to provide more precise return types based on parameters.
    *   **Action:** Evaluate `RoleBasedModel` - decide if it belongs in the core `models.py` or should be moved to examples/documentation.
    *   **Action:** Evaluate `ClientConfig.__add__` - consider replacing with a more explicit `merge_configs` function if the operator overloading is deemed unclear or inefficient.

**Phase 3: Testing, Documentation & Polish**


4.  **Enhance Testing:**
    *   **Goal:** Increase confidence in the library's correctness and robustness.
    *   **Action:** Use specific Pydantic models in integration tests.
    *   **Action:** Add more tests for error conditions (4xx, 5xx, network errors, malformed responses).
    *   **Action:** Investigate downstream testing strategies.

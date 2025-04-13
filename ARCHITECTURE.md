# CrudClient Architecture and Design Principles

This document outlines the architectural philosophy, design decisions, and conventions used in the `crudclient` project. It aims to guide contributors and maintainers in understanding the structure and rationale behind the codebase.

## Core Goal

The primary goal of `crudclient` is to provide a **flexible, reusable, and robust base library** for creating Python clients that interact with RESTful APIs, with a strong focus on simplifying common CRUD (Create, Read, Update, Delete) operations.

## Key Architectural Principles

1.  **Modularity and Separation of Concerns:**
    *   The library is divided into distinct components with clear responsibilities:
        *   `config.py` (`ClientConfig`): Handles client configuration (URL, timeouts, retries) and holds the authentication strategy.
        *   `auth/` (Authentication Strategies): Implements the Strategy Pattern for authentication, with different strategies for various authentication methods.
        *   `client.py` (`Client`): The high-level client orchestrator, applying configuration (auth, retries) and delegating actual HTTP communication to the `http/` layer.
        *   `http/` (HTTP Layer): Contains components (`client.py`, `request.py`, `response.py`, `errors.py`, `retry.py`, `session.py`) responsible for raw HTTP communication, request/response object handling, HTTP-specific error management, retry logic, and session management (e.g., using `requests`).
        *   `crud/` (CRUD Abstraction): Contains components (`base.py`, `endpoint.py`, `operations.py`, `response_conversion.py`) providing abstractions for defining and executing CRUD operations on API endpoints, including URL construction and Pydantic model conversion.
        *   `response_strategies/`: Provides different strategies (e.g., `DefaultResponseStrategy`, `PathBasedResponseStrategy`) for parsing and extracting relevant data from diverse API response structures.
        *   `api.py` (`API`): Acts as an entry point, composing the `Client` and registering `Crud` resource endpoints.
        *   `models.py`: Defines base Pydantic models for common API patterns (like `ApiResponse`).
        *   `exceptions.py`: Defines custom exceptions specific to the `crudclient` library's logic.
        *   `testing/`: Contains a comprehensive testing framework with various test doubles (mocks, fakes, stubs, spies) to facilitate testing applications built with `crudclient`.
    *   This separation makes the library easier to understand, test, and maintain.

2.  **Extensibility:**
    *   The core classes (`ClientConfig`, `Crud`, `API`) are designed to be subclassed by users to adapt the client to specific API requirements (e.g., custom authentication flows, unique endpoint structures, specific response models).

3.  **Convention over Configuration (where sensible):**
    *   The library provides sensible defaults (e.g., for retries, timeouts, common CRUD method names) but allows easy overrides through configuration or subclassing.

## Design Decisions and Conventions

1.  **Type Hinting Strategy:**
    *   **Emphasis on Static Typing:** We strive for comprehensive type hinting to improve code correctness and maintainability, leveraging Python's typing features.
    *   **`.pyi` Stub Files:** Type hints for the public API and detailed docstrings are only located in `.pyi` stub files (`client.pyi`, `config.pyi`, etc.).
        *   **Rationale:** This provides excellent type information and documentation for library *consumers* (e.g., via IDE autocompletion and type checkers) without cluttering the implementation (`.py`) files, keeping the core logic cleaner for *maintainers*.
    *   **Mypy:** Static type checking is enforced using `mypy`. Configuration is in `mypy.ini`. (Note: Stricter checks may be enabled post-alpha).

2.  **Code Style and Formatting:**
    *   **PEP 8:** We follow PEP 8 guidelines, particularly for naming conventions.
    *   **Black & isort:** Code formatting and import sorting are automated using `Black` and `isort`.
    *   **Flake8:** Linting is performed using `Flake8`.
    *   **Pre-Commit Hooks:** These tools are enforced automatically via pre-commit hooks to ensure consistency before code is committed.
3.  **Design Patterns:**
    *   **Strategy Pattern:** Used for authentication mechanisms and response parsing strategies.
    *   **Template Method Pattern:** Used in the API class for endpoint registration.
    *   **Composition over Inheritance:** While inheritance is used for extension, composition is preferred for core functionality (e.g., API composes Client).

4.  **Single Responsibility Principle (SRP):**
    *   We aim for classes and methods to have a single, well-defined purpose.
    *   Functionality is organized into logically named files and modules.

5.  **Pydantic Integration:**
    *   Pydantic is used extensively in the `Crud` layer for request data serialization (`model_dump`) and response data parsing/validation. This leverages Pydantic's powerful data validation capabilities.

6.  **Testing Philosophy:**
    *   **Pytest:** Tests are written using `pytest`.
    *   **Unit Tests:** Focus on testing individual components in isolation, using mocking (`requests-mock` or the internal `crudclient.testing` framework) for external dependencies. Located in `tests/unit`.
    *   **Integration Tests:** Validate the library against real or simulated external APIs (potentially using `crudclient.testing.FakeAPI`) to ensure end-to-end functionality. Located in `tests/integration`.
    *   **High Coverage:** We aim for high test coverage, enforced via pre-commit/pre-push hooks.

7.  **Dependency Management:**
    *   **Poetry:** Project dependencies, packaging, and publishing are managed using `Poetry`.

8.  **Development Environment:**
    *   **Dev Containers:** A VS Code Dev Container configuration is provided (`.devcontainer/devcontainer.json`) to ensure a consistent and reproducible development environment for all contributors.

## Testing Framework (`crudclient.testing`)

The `crudclient.testing` module provides a comprehensive testing framework designed to facilitate testing applications that utilize the `crudclient` library. It offers a variety of test doubles, including mocks, stubs, fakes, and spies, allowing developers to simulate the behavior of `crudclient` components during tests.

**Key Components:**

*   **Core Mocks:** `MockClient` (simulates `crudclient.Client`) and `MockHTTPClient` (simulates the low-level HTTP layer).
*   **Advanced Doubles:**
    *   `FakeAPI`: A sophisticated, in-memory fake of `crudclient.API`, backed by a `DataStore` that simulates a database. Ideal for integration tests without external dependencies.
    *   `StubClient`: A simpler stub returning predefined responses based on request patterns.
*   **Verification:** `Verifier` class and specific helpers for asserting interactions with test doubles.

**Structure:**

The framework is organized into submodules like `core`, `auth`, `crud`, `doubles`, `spy`, `verification`, `helpers`, and `response_builder`, each focusing on specific aspects of testing.

## Future Directions (Considerations)

*   **Asynchronous Support:** Potential addition of `asyncio`/`httpx` support.
*   **Enhanced Pydantic Strategies:** Refining how Pydantic models handle diverse API response structures.
*   **Stricter Typing:** Enabling more rigorous `mypy` checks once the API stabilizes.
# CrudClient Architecture and Design Principles

This document outlines the architectural philosophy, design decisions, and conventions used in the `crudclient` project. It aims to guide contributors and maintainers in understanding the structure and rationale behind the codebase.

## Core Goal

The primary goal of `crudclient` is to provide a **flexible, reusable, and robust base library** for creating Python clients that interact with RESTful APIs, with a strong focus on simplifying common CRUD (Create, Read, Update, Delete) operations.

## Key Architectural Principles

1.  **Modularity and Separation of Concerns:**
    *   The library is divided into distinct components with clear responsibilities:
        *   `config.py` (`ClientConfig`): Handles client configuration (URL, auth, timeouts, retries).
        *   `client.py` (`Client`): Manages HTTP requests/responses using `requests`, handles authentication logic based on config, implements retries.
        *   `crud.py` (`Crud`): Provides a generic abstraction for CRUD operations on API resources, handling endpoint construction and data model conversion (using Pydantic).
        *   `api.py` (`API`): Acts as an entry point, composing the `Client` and registering `Crud` resource endpoints.
        *   `models.py`: Defines base Pydantic models for common API patterns (like `ApiResponse`).
        *   `exceptions.py`: Defines custom exceptions for the library.
    *   This separation makes the library easier to understand, test, and maintain.

2.  **Extensibility:**
    *   The core classes (`ClientConfig`, `Crud`, `API`) are designed to be subclassed by users to adapt the client to specific API requirements (e.g., custom authentication flows, unique endpoint structures, specific response models).

3.  **Convention over Configuration (where sensible):**
    *   The library provides sensible defaults (e.g., for retries, timeouts, common CRUD method names) but allows easy overrides through configuration or subclassing.

## Design Decisions and Conventions

1.  **Type Hinting Strategy:**
    *   **Emphasis on Static Typing:** We strive for comprehensive type hinting to improve code correctness and maintainability, leveraging Python's typing features.
    *   **`.pyi` Stub Files:** Type hints for the public API and detailed docstrings are primarily located in `.pyi` stub files (`client.pyi`, `config.pyi`, etc.).
        *   **Rationale:** This provides excellent type information and documentation for library *consumers* (e.g., via IDE autocompletion and type checkers) without cluttering the implementation (`.py`) files, keeping the core logic cleaner for *maintainers*.
    *   **Mypy:** Static type checking is enforced using `mypy`. Configuration is in `mypy.ini`. (Note: Stricter checks may be enabled post-alpha).

2.  **Code Style and Formatting:**
    *   **PEP 8:** We follow PEP 8 guidelines, particularly for naming conventions.
    *   **Black & isort:** Code formatting and import sorting are automated using `Black` and `isort`.
    *   **Flake8:** Linting is performed using `Flake8`.
    *   **Pre-Commit Hooks:** These tools are enforced automatically via pre-commit hooks to ensure consistency before code is committed.

3.  **Single Responsibility Principle (SRP):**
    *   We aim for classes and methods to have a single, well-defined purpose.
    *   Functionality is organized into logically named files.

4.  **Pydantic Integration:**
    *   Pydantic is used extensively in the `Crud` layer for request data serialization (`model_dump`) and response data parsing/validation. This leverages Pydantic's powerful data validation capabilities.

5.  **Testing Philosophy:**
    *   **Pytest:** Tests are written using `pytest`.
    *   **Unit Tests:** Focus on testing individual components in isolation, using mocking (`requests-mock`) for external dependencies. Located in `tests/unit`.
    *   **Integration Tests:** Validate the library against real or simulated external APIs to ensure end-to-end functionality. Located in `tests/integration`.
    *   **High Coverage:** We aim for high test coverage, enforced via pre-commit/pre-push hooks.

6.  **Dependency Management:**
    *   **Poetry:** Project dependencies, packaging, and publishing are managed using `Poetry`.

7.  **Development Environment:**
    *   **Dev Containers:** A VS Code Dev Container configuration is provided (`.devcontainer/devcontainer.json`) to ensure a consistent and reproducible development environment for all contributors.

## Future Directions (Considerations)

*   **Asynchronous Support:** Potential addition of `asyncio`/`httpx` support.
*   **Enhanced Pydantic Strategies:** Refining how Pydantic models handle diverse API response structures.
*   **Stricter Typing:** Enabling more rigorous `mypy` checks once the API stabilizes.
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
        *   `http/` (HTTP Layer): Contains components (`client.py`, `request.py`, `response.py`, `errors.py`, `retry.py`, `session.py`, `retry_strategies.py`, `retry_conditions.py`) responsible for raw HTTP communication, request/response object handling, HTTP-specific error management, sophisticated retry logic, and session management (e.g., using `requests`).
        *   `crud/` (CRUD Abstraction): Contains components (`base.py`, `endpoint.py`, `operations.py`, `response_conversion.py`) providing abstractions for defining and executing CRUD operations on API endpoints, including URL construction and Pydantic model conversion.
        *   `groups.py` (`ResourceGroup`): Defines the `ResourceGroup` class which inherits from `Crud` and enables typed, hierarchical nesting of API resources. It allows for organizing related resources under a common path segment while also supporting its own CRUD operations.
        *   `response_strategies/`: Provides different strategies (e.g., `DefaultResponseStrategy`, `PathBasedResponseStrategy`) for parsing and extracting relevant data from diverse API response structures.
        *   `api.py` (`API`): Acts as an entry point, composing the `Client` and registering both `Crud` resource endpoints and `ResourceGroup` instances.
        *   `models.py`: Defines base Pydantic models for common API patterns (like `ApiResponse`).
        *   `exceptions.py`: Defines custom exceptions specific to the `crudclient` library's logic.
        *   `testing/`: Contains a comprehensive testing framework with factories and various test doubles (mocks, stubs, spies) to facilitate testing applications built with `crudclient`. (See dedicated section below).
    *   This separation makes the library easier to understand, test, and maintain.

2.  **Extensibility:**
    *   The core classes (`ClientConfig`, `Crud`, `ResourceGroup`, `API`) are designed to be subclassed by users to adapt the client to specific API requirements (e.g., custom authentication flows, unique endpoint structures, specific response models, hierarchical resource organization).

3.  **Convention over Configuration (where sensible):**
    *   The library provides sensible defaults (e.g., for retries, timeouts, common CRUD method names) but allows easy overrides through configuration or subclassing.

## Design Decisions and Conventions

1.  **Type Hinting Strategy:**
    *   **Emphasis on Static Typing:** We strive for comprehensive type hinting to improve code correctness and maintainability, leveraging Python's typing features.
    *   **Inline Type Annotations:** Type hints and detailed docstrings are included directly in the `.py` files.
        *   **Rationale:** This provides excellent type information and documentation for both library *consumers* (e.g., via IDE autocompletion and type checkers) and *maintainers* in a single location, making the codebase more maintainable and easier to understand.
    *   **Mypy:** Static type checking is enforced using `mypy`. Configuration is in `mypy.ini`.

2.  **Code Style, Formatting, and Linting:**
    *   **PEP 8:** We follow PEP 8 guidelines, particularly for naming conventions.
    *   **Black & isort:** Code formatting and import sorting are automated using `Black` and `isort`.
    *   **Flake8:** Linting is performed using `Flake8`. Configuration is in `.flake8`.
    *   **Pre-Commit Hooks:** These tools, along with custom checks (like docstring validation, stub file checks, file length limits located in `hooks/`), are enforced automatically via pre-commit hooks defined in `.pre-commit-config.yaml` to ensure consistency and quality before code is committed.

3.  **Design Patterns:**
    *   **Strategy Pattern:** Used for authentication mechanisms, response parsing strategies, and retry logic.
    *   **Factory Pattern:** Used extensively within the `crudclient.testing` framework.
    *   **Template Method Pattern:** Used in the `API` class for endpoint registration.
    *   **Composition over Inheritance:** Preferred for core functionality (e.g., `API` composes `Client`).

4.  **Single Responsibility Principle (SRP):**
    *   Classes and methods aim for a single, well-defined purpose. Functionality is organized into logically named files and modules.

5.  **Pydantic Integration:**
    *   Pydantic is used extensively in the `Crud` layer for request data serialization and response data parsing/validation, leveraging its data validation capabilities.

6.  **Testing Philosophy:**
    *   **Pytest Framework:** Tests are written using `pytest`.
    *   **Unit & Integration Tests:** The project includes both unit tests (isolating components using the `crudclient.testing` framework) and integration tests (validating against real or simulated APIs).
    *   **High Coverage Goal:** Test coverage is tracked (`coverage.py`) and maintained at a high level.

7.  **Dependency Management:**
    *   **Poetry:** Project dependencies, environment management, packaging, and publishing are managed using `Poetry`. Key files are `pyproject.toml` and `poetry.lock`.

8.  **Development Environment:**
    *   The project aims for a consistent development environment, primarily managed through `Poetry`. Using `poetry install` sets up the necessary dependencies within a virtual environment.

9.  **Continuous Integration (CI):**
    *   The project utilizes CI pipelines (e.g., GitHub Actions) to automate essential quality checks on every commit and pull request.
    *   Typical CI steps include:
        *   Running linters (`Flake8`)
        *   Running formatters (`Black`, `isort` - check mode)
        *   Performing static type checking (`Mypy`)
        *   Executing the full test suite (`pytest`) with coverage analysis
        *   Running pre-commit hooks in CI mode

## Testing Framework (`crudclient.testing`)

The `crudclient.testing` module provides a sophisticated, factory-based testing framework designed to facilitate testing applications that utilize the `crudclient` library. It offers a variety of configurable test doubles and verification tools.

**Key Concepts & Components:**

*   **Factories:**
    *   `MockClientFactory`: The primary factory for creating highly configurable mock `Client` instances.
    *   `SimpleMockFactory`: A simpler factory for basic request/response mocking.
    *   Specialized factories exist for components like authentication.
*   **Test Doubles:** The framework provides various types of doubles (mocks, stubs, spies) generated via the factories, tailored for different testing needs.
*   **Verification:** Tools are provided to assert that interactions with mock objects occurred as expected.
*   **Response Building:** Helpers exist to easily construct mock `requests.Response` objects.
*   **Modular Structure:** The framework is organized into submodules (`auth`, `core`, `crud`, `doubles`, `helpers`, `response_builder`, `simple_mock`, `spy`, `verification`) reflecting the structure of the main library, allowing for targeted mocking and testing.

This framework enables robust unit and integration testing by providing fine-grained control over the simulated behavior of `crudclient` components. Refer to `crudclient/testing/README.md` for more detailed usage examples.
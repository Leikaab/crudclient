# Contributing to CrudClient

Thank you for your interest in contributing to CrudClient! We welcome contributions from the community. Please follow these guidelines to ensure a smooth process.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Setting Up the Development Environment](#setting-up-the-development-environment)
  - [Prerequisites](#prerequisites)
  - [Using Dev Containers](#using-dev-containers)
- [Running Tests](#running-tests)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [Coverage](#coverage)
- [Code Style and Quality](#code-style-and-quality)
  - [Linters and Formatters](#linters-and-formatters)
  - [Type Checking](#type-checking)
  - [Pre-Commit Hooks](#pre-commit-hooks)
- [Managing Dependencies](#managing-dependencies)
  - [Adding Dependencies](#adding-dependencies)
  - [Updating Dependencies](#updating-dependencies)
- [Branching Strategy](#branching-strategy)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request (PR) Process](#pull-request-pr-process)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. Please review [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before participating.

## Setting Up the Development Environment

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Visual Studio Code](https://code.visualstudio.com/)
- [Remote - Containers VS Code Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### Using Dev Containers

This project is configured to use VS Code Dev Containers for a consistent development environment.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Leikaab/crudclient.git
    cd crudclient
    ```
2.  **Open in Container:**
    - Open the cloned repository folder in VS Code.
    - VS Code should prompt you to "Reopen in Container". Click it.
    - Alternatively, open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P`) and select "Remote-Containers: Reopen in Container".

The dev container includes Python, Poetry, and all necessary tools and VS Code extensions pre-configured. Dependencies specified in `poetry.lock` will be installed automatically within the container.

## Running Tests

Tests are written using `pytest`.

### Unit Tests

Unit tests mock external dependencies and test individual components.

```bash
pytest tests/unit
```

### Integration Tests

Integration tests may interact with external APIs (like JSONPlaceholder) or require specific setup (like API keys for Fiken/Oneflow, potentially via environment variables). Refer to `tests/integration/README.md` if available, or the specific test files for setup details.

```bash
# Example for JSONPlaceholder (no extra setup needed)
pytest tests/integration/test_jsonplaceholder.py

# Example for others (might require environment variables)
# export FIKEN_API_KEY=...
# pytest tests/integration/test_fiken.py
```

### Coverage

To run all tests and generate a coverage report:

```bash
pytest --cov=crudclient --cov-report=term-missing --cov-report=html
```

This will print a summary to the terminal and create an HTML report in the `coverage_html_report/` directory. The pre-push hook enforces 100% coverage.

## Code Style and Quality

We use several tools to maintain code quality and consistency.

### Linters and Formatters

- **Black:** For code formatting.
- **isort:** For sorting imports.
- **Flake8:** For general linting.

Configuration for these tools can be found in `pyproject.toml` and `.flake8`.

### Type Checking

- **Mypy:** For static type checking. Configuration is in `mypy.ini`. Type hints should be added for all code, primarily within `.pyi` stub files.

## Authentication Strategies

When contributing to the authentication system, follow these guidelines:

1. **Strategy Pattern:** All authentication strategies must implement the `AuthStrategy` abstract base class defined in `crudclient/auth/base.py`.
2. **Required Methods:** Each strategy must implement:
   - `prepare_request_headers()`: Returns a dictionary of headers for authentication.
   - `prepare_request_params()`: Returns a dictionary of query parameters for authentication.
3. **Naming Convention:** Name your strategy class with a descriptive suffix followed by `Auth` (e.g., `BearerAuth`, `ApiKeyAuth`).
4. **Immutability:** Authentication strategies should be immutable after initialization.
5. **Documentation:** Include comprehensive docstrings explaining the strategy's purpose and usage.
6. **Testing:** Write unit tests for each new authentication strategy.

### Pre-Commit Hooks

We use `pre-commit` to automatically run these checks before you commit changes. Ensure it's installed in your environment (it should be in the dev container).

```bash
# Install hooks (usually needed only once)
pre-commit install
pre-commit install --hook-type pre-push
```

Now, the checks (black, isort, flake8, mypy, pytest unit tests) will run automatically on `git commit`. The pre-push hook runs `pytest` with coverage checks.

## Managing Dependencies

We use [Poetry](https://python-poetry.org/) to manage project dependencies.

### Adding Dependencies

- **Runtime Dependency:**
  ```bash
  poetry add <package_name>
  ```
- **Development Dependency:**
  ```bash
  poetry add --group dev <package_name>
  ```

Commit both the updated `pyproject.toml` and `poetry.lock` files.

### Updating Dependencies

```bash
# Update all dependencies to latest allowed versions
poetry update

# Update a specific package
poetry update <package_name>
```

Commit the updated `poetry.lock` file.

## Branching Strategy

- Create feature branches off the `main` branch.
- Use descriptive branch names, like `feat/improve-error-logging` or `fix/config-merge-bug`.
- Avoid committing directly to `main`.

## Commit Message Guidelines

Please follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification. This helps automate changelog generation and versioning.

Examples:

- `feat: add support for custom authentication headers`
- `fix: correct handling of non-JSON error responses`
- `docs: update CONTRIBUTING.md with commit guidelines`
- `refactor: simplify endpoint construction logic in Crud class`
- `test: add unit tests for ClientConfig merging`

## Pull Request (PR) Process

1.  Ensure all tests pass and pre-commit checks are successful.
2.  Push your feature branch to your fork on GitHub.
3.  Create a Pull Request targeting the `main` branch of the `Leikaab/crudclient` repository.
4.  Provide a clear description of the changes in the PR. Link to any relevant issues.
5.  Ensure CI checks pass on the PR.
6.  Engage in code review and address any feedback.

## Reporting Issues

If you encounter a bug or have a feature request, please check existing issues first. If it's a new issue, create one using the appropriate template on GitHub Issues. Provide as much detail as possible.
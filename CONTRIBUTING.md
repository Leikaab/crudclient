# Contributing to CrudClient

Thank you for your interest in contributing to CrudClient! We welcome contributions from the community. Please follow these guidelines to ensure a smooth process.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Setting Up the Development Environment](#setting-up-the-development-environment)
  - [Prerequisites](#prerequisites)
  - [Setup Steps](#setup-steps)
- [Running Tests](#running-tests)
  - [Unit Tests](#unit-tests)
  - [Integration Tests](#integration-tests)
  - [Coverage](#coverage)
- [Code Style and Quality](#code-style-and-quality)
  - [Linters and Formatters](#linters-and-formatters)
  - [Type Checking](#type-checking)
- [Authentication Strategies](#authentication-strategies)
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

- [Python](https://www.python.org/downloads/) (Version 3.8 or higher recommended)
- [Poetry](https://python-poetry.org/docs/#installation) (for dependency management and virtual environments)

### Setup Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Leikaab/crudclient.git
    cd crudclient
    ```
2.  **Install dependencies:**
    - Poetry manages project dependencies and creates a virtual environment.
    - Run the following command to install all required dependencies, including development tools:
    ```bash
    poetry install --all-extras
    ```
    - Activate the virtual environment created by Poetry:
    ```bash
    poetry shell
    ```
    (Alternatively, prefix commands with `poetry run`, e.g., `poetry run pytest`)

## Running Tests

Tests are written using `pytest` and leverage custom factories for mocking (see `crudclient/testing/`).

### Unit Tests

Unit tests mock external dependencies and test individual components in isolation.

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

To run all unit tests and generate a coverage report:

```bash
pytest tests/unit --cov=crudclient --cov-report=term-missing --cov-report=html
```

This will print a summary to the terminal and create an HTML report in the `coverage_html_report/` directory. The pre-push hook (see below) enforces 100% unit test coverage.

## Code Style and Quality

We use several tools to maintain code quality and consistency. These are typically run automatically via pre-commit hooks.

### Linters and Formatters

- **Black:** For code formatting.
- **isort:** For sorting imports.
- **Flake8:** For general linting (style guide enforcement, complexity checks).
- **autoflake:** Removes unused imports and variables.

Configuration for these tools can be found in `pyproject.toml` and `.flake8`.

### Type Checking

- **Mypy:** For static type checking. Configuration is in `mypy.ini`. Type hints should be added for all code, primarily within `.pyi` stub files.

## Authentication Strategies

When contributing to the authentication system, follow these guidelines:

1. **Strategy Pattern:** All authentication strategies must implement the `AuthStrategy` abstract base class defined in `crudclient/auth/base.py`.
2. **Required Methods:** Each strategy must implement methods necessary for applying authentication details to requests (e.g., `prepare_request_headers`, `prepare_request_params`). Refer to the base class and existing strategies.
3. **Naming Convention:** Name your strategy class with a descriptive suffix followed by `Auth` (e.g., `BearerAuth`, `ApiKeyAuth`).
4. **Immutability:** Authentication strategies should generally be immutable after initialization.
5. **Documentation:** Include comprehensive docstrings explaining the strategy's purpose and usage.
6. **Testing:** Write unit tests for each new authentication strategy using the testing framework provided in `crudclient/testing/`.

## Pre-Commit Hooks

We use [`pre-commit`](https://pre-commit.com/) to automatically run checks before commits and pushes. This helps ensure code quality and consistency before changes enter the main codebase.

**Installation:**

Ensure `pre-commit` is installed (it's included in the development dependencies via `poetry install`). Then, install the git hooks:

```bash
# Install hooks (run once per clone)
pre-commit install       # Installs pre-commit hooks
pre-commit install --hook-type pre-push  # Installs pre-push hooks
```

**Checks Performed:**

-   **On `git commit`:**
    -   Basic checks (trailing whitespace, end-of-file fix, etc.).
    -   Code Formatting (`autoflake`, `isort`, `black`).
    -   Linting (`flake8`).
    -   Static Type Checking (`mypy`).
    -   Custom Project Checks (`check-docstrings`, `check-stub-files`, `check-file-length`).
    -   Unit tests (`pytest`) are run *only on changed files* relevant to the commit for faster feedback.
-   **On `git push`:**
    -   Full unit test suite (`pytest tests/unit`) with 100% code coverage enforcement (`--cov`).

If any hook fails, the commit or push will be aborted. Address the reported issues and try committing/pushing again. You can also run all pre-commit hooks manually: `pre-commit run --all-files`.

## Managing Dependencies

We use [Poetry](https://python-poetry.org/) to manage project dependencies.

### Adding Dependencies

- **Runtime Dependency:**
  ```bash
  poetry add <package_name>
  ```
- **Development Dependency (tools, testing, etc.):**
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
- `docs: update CONTRIBUTING.md with poetry setup`
- `refactor: simplify endpoint construction logic in Crud class`
- `test: add unit tests for ClientConfig merging`

## Pull Request (PR) Process

1.  Ensure all tests pass (`pytest tests/unit`) and pre-commit/pre-push checks are successful locally.
2.  Push your feature branch to your fork on GitHub.
3.  Create a Pull Request targeting the `main` branch of the `Leikaab/crudclient` repository.
4.  Provide a clear description of the changes in the PR. Link to any relevant issues.
5.  **CI Checks:** Automated checks (including linters, type checkers, and tests across multiple Python versions) will run via GitHub Actions on your PR. Ensure these pass.
6.  Engage in code review and address any feedback promptly.

## Reporting Issues

If you encounter a bug or have a feature request, please check existing issues first. If it's a new issue, create one using the appropriate template on GitHub Issues. Provide as much detail as possible, including steps to reproduce, expected behavior, and actual behavior.
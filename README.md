# Create base client model for restful libraries

## Badges and quicklinks

### Open project for development in container
[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Leikaab/crudclient)

### Status of project
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/crudclient)
![PyPI - Version](https://img.shields.io/pypi/v/crudclient)

### Status of testing
[![Test DevContainer Build](https://github.com/Leikaab/crudclient/actions/workflows/test_devcontainer.yml/badge.svg)](https://github.com/Leikaab/crudclient/actions/workflows/test_devcontainer.yml)
[![Run Tests](https://github.com/Leikaab/crudclient/actions/workflows/tests.yml/badge.svg)](https://github.com/Leikaab/crudclient/actions/workflows/tests.yml)
[![Publish to PyPI](https://github.com/Leikaab/crudclient/actions/workflows/publish.yml/badge.svg)](https://github.com/Leikaab/crudclient/actions/workflows/publish.yml)
[![Dependabot Updates](https://github.com/Leikaab/crudclient/actions/workflows/dependabot/dependabot-updates/badge.svg)](https://github.com/Leikaab/crudclient/actions/workflows/dependabot/dependabot-updates)

<details>
  <summary>Project Overview</summary>

  ## Project Overview

  This project is a foundational framework designed to streamline the creation of API clients and CRUD (Create, Read, Update, Delete) classes. It is intended to be a reusable package that can be implemented in various projects, providing a consistent and DRY (Don't Repeat Yourself) approach to coding.

  ### Key Features

  - **Authentication**: The framework provides a robust system for handling API authentication, simplifying the integration of secure and efficient authentication methods into your projects.

  - **API Construction**: This package offers tools to easily define and structure your API interactions, allowing for dynamic and flexible API client creation that adapts to the specific needs of different projects.

  - **CRUD Class Mixins**: The project includes reusable class mixins for building CRUD operations. These mixins promote code reusability and consistency across multiple projects, ensuring that common functionality is implemented efficiently and with minimal duplication.

  This framework is designed to help developers focus on implementing the specific logic required for their APIs while relying on a solid, reusable foundation for the underlying infrastructure. It supports a modular approach, making it easier to manage and scale API client development across various projects.

</details>


<details>
  <summary>Using Dev Containers</summary>

## Project uses devcontainers

### Run project locally via dev-containers

A **development container** is a running [Docker](https://www.docker.com) container with a well-defined tool/runtime stack and its prerequisites.

[![Open in Remote - Containers](https://img.shields.io/static/v1?label=Remote%20-%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Leikaab/crudclient)

If you already have VS Code and Docker installed, you can click the badge above to automatically install the Remote - Containers extension if needed, clone the source code into a container volume, and spin up a dev container for use.

If this is your first time using a development container, please ensure your system meets the prerequisites (i.e. have Docker installed) in the [getting started steps](https://aka.ms/vscode-remote/containers/getting-started).

### Test out project

Once you have this project opened, you'll be able to work with it like you would locally.

Note that ha bounch of key extentions are allready installed + there is local project settings set up in the background, even though there is no settings.json file. These settings are made to match with developmental team standards.

> **Note:** This container runs as a non-root user with sudo access by default.

</details>

<details>
  <summary>Testing and Coverage</summary>

  ## Testing and Coverage

  This project employs `pytest` as the primary testing framework to ensure the reliability and correctness of the codebase. `pytest` is configured to run comprehensive tests across the project, providing detailed feedback on the results, including which tests pass or fail, and offering powerful tools like fixtures and parameterization to create flexible and scalable tests.

  ### Coverage with Coverage.py

  The project also integrates `coverage.py` to measure code coverage during testing. Code coverage analysis helps identify untested parts of the codebase, ensuring that the tests cover as much of the code as possible. This approach enhances the robustness of the code by verifying that all critical paths and edge cases are tested.

  The configuration for `coverage.py` is set up in the `.coveragerc` file, which specifies which parts of the code should be included or omitted from the coverage report. The generated coverage reports provide insights into the percentage of code that is tested, helping to maintain high standards for test completeness.

  The setup is optimized for use within the development container, which forwards a custom port (5051) to serve the live coverage reports, making it easy to view and analyze test coverage in real-time.

  ### Running Tests

  To run the tests and generate a coverage report, simply use the following commands within the container:

  ```bash
  pytest --cov=your_package_name --cov-report=html
  ```

  This command will execute all tests and generate an HTML report that you can view in your browser, providing a visual representation of the code coverage.

</details>

<details>
  <summary>Pre-Commit and Pre-Push Hooks</summary>

  ## Pre-Commit and Pre-Push Hooks

  This project integrates pre-commit and pre-push hooks to ensure that code quality is maintained and that all changes meet the project's standards before they are committed or pushed to the repository. These hooks are configured using the `.pre-commit-config.yaml` file, which specifies the various tools and checks that are automatically run at different stages of the Git workflow.

  ### Pre-Commit Hooks

  Pre-commit hooks are executed before each commit is finalized. These hooks ensure that the code adheres to the project's style guidelines and passes initial validation checks. The following tools are configured to run as part of the pre-commit hooks:

  - **isort**: Ensures that imports are properly sorted according to the project's style.
  - **black**: Formats the code to comply with the `black` code style, with a line length of 120 characters.
  - **flake8**: Runs linting checks to identify any potential issues in the code, excluding `setup.py`.
  - **mypy**: Performs static type checking to ensure type safety in the codebase.
  - **pytest**: Runs the unit tests to verify that the code changes do not break existing functionality.

  These tools are configured to run automatically when you attempt to make a commit, helping to catch errors early and maintain a high standard of code quality.

  ### Pre-Push Hook

  The pre-push hook is executed before any changes are pushed to the remote repository. This hook includes an additional layer of testing to ensure that the code meets the required coverage standards:

  - **pytest with coverage**: Runs the full test suite with coverage analysis, ensuring that the codebase meets the required coverage threshold (configured to fail if coverage is below 100%).

  By enforcing these checks before pushing, the project ensures that all changes are thoroughly validated, reducing the risk of introducing issues into the main codebase.

</details>

<details>
  <summary>Poetry Usage</summary>

  ## Poetry Usage

  This project leverages Poetry as the primary tool for dependency management, packaging, versioning, and general project configuration. Poetry is a powerful tool that simplifies the entire lifecycle of a Python project, from development to distribution.

  ### Package Management

  Poetry is configured to handle all aspects of package management for this project. It allows you to define dependencies clearly in the `pyproject.toml` file, ensuring that the correct versions of each package are used. Poetry's dependency resolver manages compatibility between packages and installs them in a reproducible environment.

  Poetry handles:

  - **Dependency Resolution**: Ensuring that all dependencies and their sub-dependencies are compatible and correctly installed.
  - **Package Installation**: Installing all required dependencies as defined in the `pyproject.toml` file, ensuring consistency across different environments.

  ### Publishing to PyPI

   We use Poetryto publish packages to PyPI through our CI/CD pipeline with GitHub actions / workflows.
   These workflows automate the process of building, packaging, and publishing the package to PyPI, ensuring that the deployment process is consistent and error-free. See chapter CD/CI for more information.

  ### Versioning

  Poetry is used to manage the versioning of the project. Version numbers are specified in the `pyproject.toml` file and can be automatically updated as part of the release process. We follow semantic versioning practices, where version numbers indicate the nature of changes (major, minor, patch) and help maintain backward compatibility.

  ### Other Uses of Poetry

  - **Script Management**: Poetry allows us to define custom scripts that can be run within the project, streamlining repetitive tasks and ensuring consistency across environments.

  - **Development Dependencies**: Poetry distinguishes between production and development dependencies, ensuring that only the necessary packages are included in the final distribution, keeping it lightweight and efficient.

  - **Environment Configuration**: Although Poetry typically creates a virtual environment (`venv`) for each project, in this setup, we have configured Poetry to avoid creating virtual environments due to our use of development containers. This ensures that dependencies are installed directly into the container environment, simplifying the setup and avoiding potential conflicts.

  This configuration is particularly beneficial in a devcontainer environment, where the container itself acts as the isolated development environment, eliminating the need for a separate virtual environment.

</details>

<details>
  <summary>CI/CD with GitHub Workflows</summary>

  ## CI/CD with GitHub Workflows

  This project utilizes GitHub Actions to automate continuous integration and continuous deployment (CI/CD) processes. The workflows are designed to ensure code quality, test the development environment, and automatically publish the package to PyPI upon successful testing.

  ### Test Workflow (`tests.yml`)

  The `tests.yml` workflow is responsible for running the project's test suite across multiple operating systems (Ubuntu, Windows, and macOS) whenever code is pushed to the repository. This workflow ensures that the codebase is robust and compatible across different environments.

  Key steps in this workflow include:
  - **Checkout Code**: Retrieves the latest code from the repository.
  - **Set up Python**: Configures the appropriate Python environment.
  - **Install Dependencies**: Installs the project's dependencies using Poetry.
  - **Run Linting and Formatting Checks**: Uses `isort`, `black`, `flake8`, and `mypy` to enforce code quality.
  - **Run Tests**: Executes the test suite with `pytest` and checks for 100% code coverage.

  This workflow is triggered on every push to the repository, ensuring continuous verification of the code's integrity.

  > Add `[skip ci]` to commit message to not run github actions for testing

  ### Publish Workflow (`publish.yml`)

  The `publish.yml` workflow automates the process of publishing the package to PyPI. This workflow is triggered only after the `tests.yml` workflow completes successfully, ensuring that only thoroughly tested code is released.

  Key steps in this workflow include:
  - **Checkout Code**: Retrieves the full history of the repository, which is necessary for versioning.
  - **Set up Python**: Configures the appropriate Python environment.
  - **Install Dependencies**: Installs the necessary dependencies without development dependencies.
  - **Version Check**: Compares the current version in `pyproject.toml` with the latest Git tag to determine if a new version should be published.
  - **Publish to PyPI**: Publishes the package to PyPI using Poetry, making it available for installation via `pip`.
  - **Create New Tag**: If a new version is published, the workflow automatically tags the release in the GitHub repository.

  This workflow ensures that the package is consistently versioned and available to the public after passing all tests. The workflow only runs if code is pushed to main, and is not touched by versioning that are done in the branches.

  ### DevContainer Test Workflow (`test_devcontainer.yml`)

  The `test_devcontainer.yml` workflow is designed to verify the development container setup, ensuring that other developers can seamlessly use the devcontainer environment.

  Key steps in this workflow include:
  - **Checkout Code**: Retrieves the latest code from the repository.
  - **Set up Docker (for macOS)**: Ensures Docker is running on macOS systems.
  - **Set up Devcontainer CLI**: Installs the DevContainer CLI to interact with the development container.
  - **Build and Test DevContainer**: Builds the development container and runs basic tests to verify the setup.
  - **Validate DevContainer**: Ensures that critical tools like Poetry are correctly installed and configured within the container.

  This workflow is triggered whenever changes are made to the `.devcontainer` folder, ensuring that the development environment remains stable and usable. Currently because of limitations in github actions enviroments we are only testing devcontainers on ubuntu through cd/ci. Issues with MacOS or Windows needs to be rapported in the issues section on github.

</details>

<details>
  <summary>Non-functional plans and useful links</summary>

  ## Bagdes for project

  - https://pypi.org/project/pybadges/
  - https://github.com/badges/shields
  - https://shields.io/badges/dynamic-toml-badge

</details>
## Logging

```python

import logging
# Use the API library
from crudclient import API

# Configure logging for the application
logging.basicConfig(level=logging.DEBUG)

# Configure specific logging for the crudclient library
logging.getLogger('crudclient').setLevel(logging.INFO)

# Or you could configure at a module level if needed
logging.getLogger('crudclient.api').setLevel(logging.WARNING)

# Example usage of the library
with api as active_api:
    resource = active_api.use_custom_resource(MyCrudResource)
    # Interact with the resourc

```
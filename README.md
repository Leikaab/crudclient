# Create base client model for restful libraries


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

## notes

add `[skip ci]` to commit message to not run github actions for testing
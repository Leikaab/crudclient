# DevContainer Setup for Python Development

This DevContainer setup is designed to facilitate a streamlined Python development environment using Visual Studio Code (VSCode) and Docker. Below you will find a detailed explanation of the configurations and instructions to get started.

The DevContainer setup is now tested using a github actions workflow on latest ubuntu. Currently we are having problems TESTING on macos and windows, because of limitations on Github Actions, but it runs fine in pratice.

[![Test DevContainer Build](https://github.com/Leikaab/crudclient/actions/workflows/test_devcontainer.yml/badge.svg)](https://github.com/Leikaab/crudclient/actions/workflows/test_devcontainer.yml)

## Project Structure

- **`devcontainer.json`**: Configuration file for the DevContainer setup.
- **`docker-compose.yml`**: Defines the services and configurations to build and run the Docker containers.
- **`Dockerfile`**: Specifies the base image and additional dependencies for the container.
- **`settings.json`**: VSCode settings specific to this project, including Python linting, formatting, and testing tools.
- **`postCreateCommand.sh`**: A script that runs after the container is created to perform additional setup steps.

## DevContainer Configuration

### 1. `devcontainer.json`

- **Name**: `"Python 3"` - The name of the container configuration.
- **Docker Compose File**: `"dockerComposeFile": "docker-compose.yml"` - Indicates the use of Docker Compose for setting up services.
- **Service**: `"service": "app"` - Specifies the service defined in the `docker-compose.yml` to be used.
- **Workspace Folder**: `"workspaceFolder": "/workspace"` - The folder inside the container where your project files will be located.
- **Features**:
  - **Git**: Uses the `ghcr.io/devcontainers/features/git:1` feature with the PPA version of Git.
- **Customizations**:
  - **VSCode Settings**: Includes the settings from `settings.json` for Python linting, formatting, and testing.
  - **Extensions**:
    - Python support (`ms-python.python`, `ms-python.vscode-pylance`)
    - GitHub integration (`vscode-github-actions`, `vscode-pull-request-github`, `GitHub.copilot`, `GitHub.copilot-chat`)
- **Port Forwarding**:
  - **Port 5051**: Forwarded for live server coverage with a label `"Coverage - Live Server"`.
  - **Port 6333**: Forwarded for Qdrant HTTP API with a label `"Qdrant HTTP API"`.
- **Post Create Command**:
  - Executes `postCreateCommand.sh` to set up the environment further.
- **Remote User**: The container runs as the `"vscode"` user by default.

> **Note:** This container runs as a non-root user with sudo access by default. Comment out `"remoteUser": "vscode"` in `.devcontainer/devcontainer.json` if you'd prefer to run as root.


### 2. `docker-compose.yml`

- **Service `app`**:
  - **Build Context**: Points to the directory containing the `Dockerfile`.
  - **Dockerfile**: Located at `.devcontainer/Dockerfile`.
  - **Build Args**: `VARIANT: 1-3.12-bullseye` - Specifies the Python version and base image variant.
  - **Volumes**: Mounts the project directory into the container as `/workspace`.
  - **Command**: Runs the container indefinitely using `sleep infinity` to keep it alive.
  - **Optional User Configuration**: Optionally, the container can be run as a non-root user by uncommenting the `user: vscode` line.

- **Service `qdrant`**:
  - **Image**: Uses the latest Qdrant vector database image (`qdrant/qdrant:latest`).
  - **Ports**:
    - **6333**: HTTP API port for Qdrant
    - **6334**: gRPC API port for Qdrant
  - **Volumes**: Mounts `../data/qdrant` to `/qdrant/storage` for persistent data storage between container rebuilds.
  - **Environment Variables**: Configures HTTP and gRPC ports.
  - **Restart Policy**: `unless-stopped` ensures the service restarts automatically.

### 3. `settings.json`

- **Python Interpreter**: Set to `/usr/local/bin/python`.
- **Linting and Formatting**:
  - Linting enabled with multiple linters such as Pylint, Flake8, Bandit, etc.
  - Formatting tools configured, including AutoPEP8, Black, and YAPF.
  - **Format on Save**: Disabled globally but enabled specifically for Python files.
- **Testing**:
  - Pytest is enabled for running tests.

### 4. `postCreateCommand.sh`

This script is executed after the container is created. It currently includes commented-out commands for setting up Git and pre-commit hooks. These can be activated as needed by uncommenting the relevant lines.

## Instructions for Use

### 1. Open in VSCode

- Ensure you have the Docker and Remote - Containers extensions installed in VSCode.
- Open the project folder in VSCode. You should be prompted to open the folder in a DevContainer. If not, press <kbd>F1</kbd> and select **Remote-Containers: Reopen in Container**.

### 2. Modifying the Container

- To make changes to the container (e.g., installing new tools), update the relevant files (`Dockerfile`, `devcontainer.json`, `settings.json`).
- After making changes, rebuild the container by pressing <kbd>F1</kbd> and selecting **Remote-Containers: Rebuild Container**.

### 3. Port Forwarding

- By default, the following ports are forwarded:
  - **Port 5051**: Live server coverage
  - **Port 6333**: Qdrant HTTP API (accessible at http://localhost:6333)
- You can modify or add more ports in `devcontainer.json` under `"forwardPorts"`.

### 4. Qdrant Vector Database

The setup includes a Qdrant vector database service that provides:
- **HTTP API**: Available at http://localhost:6333 (from host) or http://qdrant:6333 (from inside devcontainer)
- **gRPC API**: Available at localhost:6334 (from host) or qdrant:6334 (from inside devcontainer)
- **Persistent Storage**: Data is stored in `./data/qdrant/` directory for persistence between container rebuilds
- **Web UI**: Qdrant provides a web interface accessible through the HTTP API endpoint

To interact with Qdrant:
- **From your host machine**: Use http://localhost:6333 for HTTP API and http://localhost:6333/dashboard for web UI
- **From inside the devcontainer**: Use http://qdrant:6333 for HTTP API (e.g., `curl http://qdrant:6333`)
- **Client libraries**:
  - From host: Point to `localhost:6333`
  - From devcontainer: Point to `qdrant:6333`

### 5. Extension Data Persistence

The devcontainer is configured to persist VS Code extension data between container rebuilds:

- **Volume**: `vscode_extensions_data` mounted to `/home/vscode/.vscode-server/data/User/globalStorage`
- **Purpose**: Preserves chat logs, settings, and other data for VS Code extensions (like Roo-Cline)
- **Permissions**: Set to 777 for maximum compatibility with different extension user contexts
- **Benefits**:
  - Chat history and extension settings survive container rebuilds
  - No need to reconfigure extensions after rebuilding
  - Seamless development experience across container lifecycle

The setup uses broad permissions (777) for the globalStorage directory to ensure VS Code extensions can write data regardless of user context, preventing permission conflicts when mounting Docker volumes.

### 6. Customization

- **VSCode Extensions**: You can add more extensions in `devcontainer.json` under `"customizations" > "vscode" > "extensions"`.
- **User Configuration**: Adjust the user settings by modifying the `"remoteUser"` property in `devcontainer.json`.

### 7. Post Create Commands

- Modify the `postCreateCommand.sh` script to perform additional setup tasks after the container is built. Uncomment the existing commands if needed or add your own.

# DevContainer Setup for Python Development

This DevContainer setup is designed to facilitate a streamlined Python development environment using Visual Studio Code (VSCode) and Docker. Below you will find a detailed explanation of the configurations and instructions to get started.

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
- Open the project folder in VSCode. You should be prompted to open the folder in a DevContainer. If not, press F1 and select **Remote-Containers: Reopen in Container**.

### 2. Modifying the Container

- To make changes to the container (e.g., installing new tools), update the relevant files (`Dockerfile`, `devcontainer.json`, `settings.json`).
- After making changes, rebuild the container by pressing F1 and selecting **Remote-Containers: Rebuild Container**.

### 3. Port Forwarding

- By default, port 5051 is forwarded for the live server coverage. You can modify or add more ports in `devcontainer.json` under `"forwardPorts"`.

### 4. Customization

- **VSCode Extensions**: You can add more extensions in `devcontainer.json` under `"customizations" > "vscode" > "extensions"`.
- **User Configuration**: Adjust the user settings by modifying the `"remoteUser"` property in `devcontainer.json`.

### 5. Post Create Commands

- Modify the `postCreateCommand.sh` script to perform additional setup tasks after the container is built. Uncomment the existing commands if needed or add your own.












> **Note:** This container runs as a non-root user with sudo access by default. Comment out `"remoteUser": "vscode"` in `.devcontainer/devcontainer.json` if you'd prefer to run as root.


4. **Rebuild or update your container**

   You may want to make changes to your container, such as installing a different version of a software or forwarding a new port. You'll rebuild your container for your changes to take effect. 

   **Open browser automatically:** As an example change, let's update the `portsAttributes` in the `.devcontainer/devcontainer.json` file to open a browser when our port is automatically forwarded.
   
   - Open the `.devcontainer/devcontainer.json` file.
   - Modify the `"onAutoForward"` attribute in your `portsAttributes` from `"notify"` to `"openBrowser"`.
   - Press <kbd>F1</kbd> and select the **Remote-Containers: Rebuild Container** command so the modifications are picked up.  
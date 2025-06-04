ARG VARIANT=1-3.13-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

ENV PYTHONUNBUFFERED 1

# Install pipx and Poetry globally
RUN pip install --upgrade pip
RUN pip install poetry

# Set the PATH environment variable for both root and vscode users
ENV PATH="/root/.local/bin:/home/vscode/.local/bin:$PATH"

# Copy poetry configuration first to respect in-project venv settings
COPY poetry.toml ./

# First, copy only the pyproject.toml file
COPY pyproject.toml ./

# Run poetry lock to update the lock file if needed
RUN poetry lock

# Now copy the lock file and other files
COPY poetry.lock README.md ./

# Install dependencies using Poetry (this will create .venv in project)
RUN poetry install --no-interaction --no-ansi --with dev --no-root

# Add the project's .venv to PATH for all users
ENV PATH="/workspace/.venv/bin:$PATH"

# Install act for local GitHub Actions testing
# Using a more controlled installation method
RUN apt-get update && apt-get install -y curl && \
    curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | bash -s -- -b /usr/local/bin && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create .vscode-server directory structure and set proper ownership
# This prevents permission issues when VS Code tries to create these directories
RUN mkdir -p /home/vscode/.vscode-server/data/User/globalStorage && \
    chown -R vscode:vscode /home/vscode/.vscode-server

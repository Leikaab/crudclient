ARG VARIANT=1-3.13-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

ENV PYTHONUNBUFFERED 1

# Install pipx and Poetry globally
RUN pip install --upgrade pip
RUN pip install poetry

# Set the PATH environment variable for both root and vscode users
ENV PATH="/root/.local/bin:/home/vscode/.local/bin:$PATH"

# Disable poetry from creating virtual environments globally
#RUN poetry config virtualenvs.create false

# Verify the poetry configuration
#RUN poetry config --list | grep virtualenvs.create

# First, copy only the pyproject.toml file
COPY pyproject.toml ./

# Run poetry lock to update the lock file if needed
RUN poetry lock

# Now copy the lock file and other files
COPY poetry.lock README.md ./

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-ansi --with dev --no-root

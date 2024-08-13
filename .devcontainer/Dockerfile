ARG VARIANT=1-3.12-bullseye
FROM mcr.microsoft.com/vscode/devcontainers/python:${VARIANT}

ENV PYTHONUNBUFFERED 1

# Install pipx
RUN pip install --user pipx
RUN pip install --upgrade pip

# Install Poetry using pipx
RUN pipx install poetry

# Set the PATH environment variable
ENV PATH="/root/.local/bin:$PATH"

# Set up Poetry
RUN poetry config virtualenvs.create false

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-interaction --no-ansi --with dev
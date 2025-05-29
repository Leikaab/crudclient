#!/bin/sh

# Fix permissions of the mounted globalStorage directory
# Give broad access to ensure VS Code extensions can write regardless of user context
sudo chmod -R 777 /home/vscode/.vscode-server/data/User/globalStorage

# Reload the shell environment
. ~/.bashrc

# Ensure the virtual environment is in PATH for Git hooks
export PATH="/workspace/.venv/bin:/home/vscode/.local/bin:/root/.local/bin:$PATH"

# Check if the .env file exists
if [ -f .env ]; then
    # Export the variables from .env
    export $(grep -v '^#' .env | xargs)
fi

# Authenticate GitHub CLI if GITHUB_TOKEN is set
if [ -n "$GITHUB_TOKEN" ]; then
    echo "Attempting GitHub CLI authentication..."
    echo "$GITHUB_TOKEN" | gh auth login --with-token
    gh auth status # Optional: verify status
else
    echo "GITHUB_TOKEN not set, skipping GitHub CLI authentication."
fi

# Add the virtual environment to the user's PATH permanently
echo 'export PATH="/workspace/.venv/bin:$PATH"' >> ~/.bashrc

# Wait until poetry is available
for i in {1..5}; do
    if command -v poetry &> /dev/null
    then
        echo "Poetry found"
        break
    else
        echo "Waiting for Poetry to be available..."
        sleep 2
    fi
done

echo "Checking poetry by direct invocation:"
if /usr/local/py-utils/bin/poetry --version &> /dev/null
then
    echo "Poetry is available and working"

    # Ensure dependencies are installed in the virtual environment
    echo "Installing dependencies with poetry..."
    poetry install --no-interaction --no-ansi --with dev

    # Set up pre-commit hooks after dependencies are installed
    echo "Setting up pre-commit hooks..."
    poetry run pre-commit install -t pre-commit
    poetry run pre-commit install -t pre-push

    echo "Pre-commit hooks installed successfully"
else
    echo "Poetry could not be found"
fi

echo "Development environment setup complete!"
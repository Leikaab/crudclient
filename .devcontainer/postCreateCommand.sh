#!/bin/sh

# Reload the shell environment
. ~/.bashrc

# Check if the .env file exists
if [ -f .env ]; then
    # Export the variables from .env
    export $(grep -v '^#' .env | xargs)
fi

# set up pre-commit hooks, commented out for now
poetry run pre-commit install -t pre-commit
poetry run pre-commit install -t pre-push

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
    poetry config virtualenvs.create false --local
else
    echo "Poetry could not be found"
fi

# Ensure the .roo directory exists
mkdir -p .roo

# Make sure the MCP servers script is executable
chmod +x ./.devcontainer/startMcpServers.sh

# Install MCP server packages globally
echo "Installing MCP server packages..."
npm install -g @modelcontextprotocol/server-github @modelcontextprotocol/server-browser

# Verify installations
echo "Verifying MCP server packages installation..."
if command -v npx &> /dev/null; then
    npx --no-install @modelcontextprotocol/server-github --version || echo "GitHub MCP server not properly installed"
    npx --no-install @modelcontextprotocol/server-browser --version || echo "Browser MCP server not properly installed"
else
    echo "Warning: npx command not available, cannot verify MCP server packages"
fi

echo "Development environment setup complete!"
#!/bin/bash

echo "Setting up RooCode environment..."

# Ensure the .roo directory exists
mkdir -p .roo

# Make sure the MCP servers script is executable
chmod +x ./.devcontainer/startMcpServers.sh

# Verify MCP server installations
echo "Verifying MCP server installations..."
if command -v npx &> /dev/null; then
    npx --no-install @modelcontextprotocol/server-github --version || echo "GitHub MCP server not properly installed"
else
    echo "Warning: npx command not available, cannot verify MCP servers"
fi

echo "RooCode environment setup complete!"
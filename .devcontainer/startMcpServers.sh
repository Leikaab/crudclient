#!/bin/bash

# Check if the .env file exists and load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Create a log directory if it doesn't exist
mkdir -p ./.mcp-logs

# Start the GitHub MCP server in the background
if [ -n "$GITHUB_TOKEN" ]; then
    echo "Starting GitHub MCP server..."
    npx -y @modelcontextprotocol/server-github > ./.mcp-logs/github-server.log 2>&1 &
    echo "GitHub MCP server started with PID $!"
else
    echo "GITHUB_TOKEN not found. GitHub MCP server will not be started."
fi

# Start the Browser MCP server in the background
echo "Starting Browser MCP server..."
npx -y @modelcontextprotocol/server-browser > ./.mcp-logs/browser-server.log 2>&1 &
echo "Browser MCP server started with PID $!"

# Notify about where to find logs
echo "MCP servers started. Logs are available in ./.mcp-logs/"
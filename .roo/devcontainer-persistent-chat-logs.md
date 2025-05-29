# Persistent Chat Logs for Roocode in DevContainer

## Overview

The devcontainer has been configured to persist roocode chat logs across container rebuilds. This ensures that your conversation history with the AI assistant is maintained even when the container is rebuilt.

## Configuration

The persistence is achieved through a Docker named volume that mounts the roocode chat logs directory:

- **Source**: `/home/vscode/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline`
- **Volume**: `roo_chat_logs`
- **Mount Type**: `cached` for optimal performance

## What is Persisted

The following roocode data is now persistent:

- **Chat History**: All conversation history with AI assistants
- **Task Metadata**: Information about individual tasks and sessions
- **UI Messages**: Complete message history for the user interface
- **Checkpoints**: Task state checkpoints for recovery
- **Settings**: User preferences and configuration
- **Cache**: Performance optimization data

## File Structure

The persistent volume contains:
```
/home/vscode/.vscode-server/data/User/globalStorage/rooveterinaryinc.roo-cline/
├── cache/                    # Performance cache data
├── settings/                 # User settings and preferences
├── tasks/                    # Individual task directories
│   └── [task-id]/
│       ├── api_conversation_history.json
│       ├── ui_messages.json
│       ├── task_metadata.json
│       └── checkpoints/
└── roo-index-cache-*.json   # Search index cache
```

## Usage

1. **No Action Required**: The persistence works automatically once the container is rebuilt
2. **First Rebuild**: Your existing chat logs will be preserved
3. **Subsequent Rebuilds**: All chat history continues to persist
4. **Volume Management**: The `roo_chat_logs` volume is managed by Docker

## Troubleshooting

If you encounter issues with chat log persistence:

1. **Check Volume**: Verify the volume exists with `docker volume ls`
2. **Inspect Volume**: Check volume details with `docker volume inspect roo_chat_logs`
3. **Permissions**: Ensure the `vscode` user has proper permissions in the container
4. **Clean Start**: If needed, remove the volume with `docker volume rm roo_chat_logs` for a fresh start

## Technical Details

- **Docker Compose Version**: 3.8
- **Volume Type**: Named volume (managed by Docker)
- **Cache Mode**: `cached` for optimal performance in development
- **User Context**: Runs as `vscode` user (UID/GID handled by devcontainer)
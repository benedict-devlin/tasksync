<!-- Use this file to provide workspace-specific custom instructions to Copilot -->

# TaskSync - Google Tasks & Todoist Sync

This is a Python package for synchronizing tasks between Google Tasks and Todoist.

## Project Architecture

- **tasksync/google_tasks.py**: Google Tasks API client using OAuth2
- **tasksync/todoist_client.py**: Todoist API client wrapper
- **tasksync/sync.py**: Main synchronization engine
- **tasksync/config.py**: Configuration management
- **tasksync/models.py**: Data models for tasks
- **tasksync/cli.py**: CLI interface using Click
- **tests/**: Test suite with pytest

## Key Features

- One-way sync from Google Tasks to Todoist
- Automatic deletion of Google Tasks after successful sync
- OAuth2 authentication for Google
- Token management and refresh
- Support for task properties (title, description, due date)
- Dry-run mode for testing
- Configurable sync intervals

## Development Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black tasksync/
isort tasksync/

# Lint
flake8 tasksync/
```

## API Keys Required

1. Google Cloud Console: OAuth2 credentials for Google Tasks API
2. Todoist: API token from https://todoist.com/app/settings/integrations/developer

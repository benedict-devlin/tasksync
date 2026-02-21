# TaskSync

Sync Google Tasks with Todoist automatically. Keep your tasks synchronized across both platforms.

## Features

- 🔄 One-way sync from Google Tasks to Todoist
- 🗑️ Automatic deletion of Google Tasks after successful sync to Todoist
- 📅 Automatic task creation in Todoist with all task details
- 🔐 Secure OAuth2 authentication
- ⚙️ Configurable sync behavior
- 🎯 Command-line interface for easy management
- 📝 Support for task descriptions, due dates, and priorities

## Installation

```bash
pip install tasksync
```

Or from source:

```bash
git clone https://github.com/yourusername/tasksync.git
cd tasksync
pip install -e .
```

## Prerequisites

### Google Tasks

1. Enable the Google Tasks API in the Google Cloud Console
2. Create OAuth2 credentials (Desktop application)
3. Download the credentials as `credentials.json`

### Todoist

1. Get your Todoist API token from https://todoist.com/app/settings/integrations/developer
2. Create a `.env` file in your project root

## Configuration

Create a `.env` file in your project root:

```env
TODOIST_API_TOKEN=your_todoist_api_token_here
GOOGLE_CREDENTIALS_PATH=./credentials.json
SYNC_INTERVAL=300
```

## Usage

### Command Line

Initialize and perform first sync:

```bash
tasksync init
tasksync sync
```

Start continuous synchronization:

```bash
tasksync start
```

Get sync status:

```bash
tasksync status
```

### Running on Raspberry Pi (Systemd)

For Raspberry Pi and other Linux systems, you can run TaskSync as a systemd service for automatic background execution and auto-restart on boot.

**Quick Setup:**

```bash
cd ~/tasksync
chmod +x install-systemd.sh
./install-systemd.sh
```

**Manual Setup:**

```bash
systemctl --user enable tasksync.service
systemctl --user start tasksync.service
```

**Check Status:**

```bash
systemctl --user status tasksync.service
journalctl --user -u tasksync.service -f  # Follow logs
```

For detailed instructions, see [SYSTEMD_SETUP.md](SYSTEMD_SETUP.md).

### Python API

```python
from tasksync.sync import TaskSyncer

syncer = TaskSyncer()
syncer.authenticate()
syncer.sync()
```

## Project Structure

```
tasksync/
├── tasksync/
│   ├── __init__.py
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration management
│   ├── sync.py             # Main sync logic
│   ├── google_tasks.py     # Google Tasks API client
│   ├── todoist_client.py   # Todoist API client
│   └── models.py           # Data models
├── tests/
│   ├── __init__.py
│   ├── test_sync.py
│   ├── test_google_tasks.py
│   └── test_todoist_client.py
├── pyproject.toml
├── setup.py
├── requirements.txt
└── README.md
```

## Development

### Install development dependencies

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=tasksync
```

### Format code

```bash
black tasksync/
isort tasksync/
```

### Lint code

```bash
flake8 tasksync/
mypy tasksync/
```

## Architecture

TaskSync uses a modular architecture with one-way synchronization:

- **Google Tasks Client**: Handles authentication and API calls to Google Tasks
- **Todoist Client**: Handles API calls to the Todoist API
- **Task Syncer**: Orchestrates one-way synchronization from Google Tasks to Todoist
- **CLI**: Provides command-line interface for user interaction

### Sync Flow

1. Fetches all tasks from Google Tasks
2. Checks if task already exists in Todoist (by title)
3. If new task found: Creates it in Todoist with all details
4. After successful creation in Todoist: Deletes the task from Google Tasks
5. Reports sync results (created, errors)

## Security

- OAuth2 tokens are stored securely
- API credentials are never logged
- .env files are included in .gitignore
- Token refresh is handled automatically

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email your.email@example.com or open an issue on GitHub.

## Roadmap

- [ ] Support for task subtasks
- [ ] Color/label synchronization
- [ ] Recurring task support
- [ ] Scheduled sync at specific times
- [ ] Web dashboard for monitoring syncs
- [ ] Webhook support for real-time sync

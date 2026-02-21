"""Configuration management for TaskSync."""

import os
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, validator

from tasksync.models import SyncConfig


class Config(BaseModel):
    """Application configuration."""

    # Google Tasks
    google_credentials_path: str = "./credentials.json"
    tasks_created_after: Optional[datetime] = None  # Only sync tasks created after this date

    # Todoist
    todoist_api_token: str

    # Sync settings
    sync_interval: int = 300  # seconds
    dry_run: bool = False
    sync_completed_tasks: bool = True
    skip_descriptions: bool = False

    # Logging
    log_level: str = "INFO"

    class Config:
        """Pydantic config."""

        case_sensitive = False

    @validator("sync_interval")
    def sync_interval_must_be_positive(cls, v):
        """Validate sync interval."""
        if v < 5:
            raise ValueError("sync_interval must be at least 5 seconds")
        return v

    @validator("google_credentials_path")
    def credentials_path_must_exist(cls, v):
        """Validate credentials path."""
        if not os.path.exists(v):
            raise ValueError(f"Google credentials file not found: {v}")
        return v


def load_config(env_file: Optional[str] = ".env") -> Config:
    """Load configuration from environment variables and .env file.

    Args:
        env_file: Path to .env file

    Returns:
        Config object
    """
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file)

    # Parse created_after date if provided
    tasks_created_after = None
    created_after_str = os.getenv("TASKS_CREATED_AFTER", "")
    if created_after_str:
        try:
            tasks_created_after = datetime.fromisoformat(created_after_str)
        except ValueError:
            raise ValueError(f"Invalid date format for TASKS_CREATED_AFTER: {created_after_str}")

    # Load from environment or use defaults
    return Config(
        google_credentials_path=os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json"),
        tasks_created_after=tasks_created_after,
        todoist_api_token=os.getenv("TODOIST_API_TOKEN", ""),
        sync_interval=int(os.getenv("SYNC_INTERVAL", "300")),
        dry_run=os.getenv("DRY_RUN", "false").lower() == "true",
        sync_completed_tasks=os.getenv("SYNC_COMPLETED_TASKS", "true").lower() == "true",
        skip_descriptions=os.getenv("SKIP_DESCRIPTIONS", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


def get_sync_config(env_file: Optional[str] = ".env") -> SyncConfig:
    """Get sync configuration.

    Args:
        env_file: Path to .env file

    Returns:
        SyncConfig object
    """
    config = load_config(env_file)
    return SyncConfig(
        google_credentials_path=config.google_credentials_path,
        todoist_api_token=config.todoist_api_token,
        sync_interval=config.sync_interval,
        dry_run=config.dry_run,
        sync_completed_tasks=config.sync_completed_tasks,
        skip_descriptions=config.skip_descriptions,
    )

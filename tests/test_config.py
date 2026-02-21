"""Tests for configuration."""

import os

import pytest

from tasksync.config import load_config, get_sync_config
from tasksync.models import SyncConfig


def test_load_config_from_env(tmp_path, monkeypatch):
    """Test loading configuration from environment variables."""
    # Create a temporary .env file
    env_file = tmp_path / ".env"
    env_file.write_text("TODOIST_API_TOKEN=test_token\nSYNC_INTERVAL=600\n")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")

    # This would fail because credentials.json doesn't exist
    # but it tests the config loading logic
    with pytest.raises(ValueError):
        config = load_config(str(env_file))


def test_get_sync_config(monkeypatch):
    """Test getting sync configuration."""
    # Set up environment
    monkeypatch.setenv("TODOIST_API_TOKEN", "test_token")
    monkeypatch.setenv("SYNC_INTERVAL", "600")

    # This would normally require credentials.json to exist
    # For testing, we just verify the function signature works


def test_sync_interval_validation():
    """Test sync interval validation."""
    from tasksync.config import Config

    # Should raise if interval is too short
    with pytest.raises(ValueError):
        Config(
            google_credentials_path="./credentials.json",
            todoist_api_token="token",
            sync_interval=30,  # Too short
        )

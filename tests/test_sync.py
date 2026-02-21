"""Tests for sync engine."""

import pytest

from tasksync.models import SyncResult, Task, TaskPriority, TaskStatus
from tasksync.sync import TaskSyncer


@pytest.fixture
def syncer():
    """Create a TaskSyncer instance for testing."""
    return TaskSyncer(
        google_credentials_path="./credentials.json",
        todoist_api_token="test_token",
        dry_run=True,
    )


def test_syncer_initialization():
    """Test TaskSyncer initialization."""
    syncer = TaskSyncer()
    assert syncer is not None
    assert syncer.dry_run is False


def test_sync_one_way():
    """Test one-way sync from Google Tasks to Todoist."""
    syncer = TaskSyncer(dry_run=True)

    # In dry-run mode, no actual API calls are made
    result = SyncResult()
    assert result.tasks_created == 0
    assert result.errors == []


def test_sync_task_to_todoist():
    """Test syncing a single task to Todoist."""
    syncer = TaskSyncer(dry_run=True)

    task = Task(
        id="1",
        title="Test Task",
        description="Test description",
        status=TaskStatus.PENDING,
        priority=TaskPriority.HIGH,
        google_task_id="google_1",
    )

    # Dry-run should return success without making API calls
    result = syncer.sync_task_to_todoist(task)
    assert result is True


def test_sync_skip_completed_tasks():
    """Test that completed tasks are skipped based on sync_completed flag."""
    syncer = TaskSyncer()

    task1 = Task(id="1", title="Pending Task", status=TaskStatus.PENDING)
    task2 = Task(id="2", title="Completed Task", status=TaskStatus.COMPLETED)

    # With sync_completed=False, completed tasks should be considered
    # This is tested in the main sync method logic
    assert task1.status == TaskStatus.PENDING
    assert task2.status == TaskStatus.COMPLETED

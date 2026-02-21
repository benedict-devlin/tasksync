"""Tests for Todoist client."""

import pytest

from tasksync.models import Task, TaskStatus, TaskPriority
from tasksync.todoist_client import TodoistClient


@pytest.fixture
def client():
    """Create a TodoistClient instance for testing."""
    return TodoistClient(api_token="test_token")


def test_convert_todoist_task():
    """Test converting Todoist API response to Task model."""
    client = TodoistClient("test_token")

    todoist_task = {
        "id": "task123",
        "content": "Test Task",
        "description": "Test description",
        "priority": 2,
        "is_completed": False,
        "due": {"date": "2024-12-31"},
    }

    task = client._convert_todoist_task_to_task(todoist_task)

    assert task is not None
    assert task.id == "task123"
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.status == TaskStatus.PENDING


def test_convert_completed_todoist_task():
    """Test converting completed Todoist task."""
    client = TodoistClient("test_token")

    todoist_task = {
        "id": "task456",
        "content": "Completed Task",
        "priority": 2,
        "is_completed": True,
    }

    task = client._convert_todoist_task_to_task(todoist_task)

    assert task is not None
    assert task.status == TaskStatus.COMPLETED


def test_convert_todoist_task_priority():
    """Test priority conversion from Todoist format."""
    client = TodoistClient("test_token")

    # High priority
    todoist_task = {
        "id": "task1",
        "content": "High Priority Task",
        "priority": 4,
    }
    task = client._convert_todoist_task_to_task(todoist_task)
    assert task.priority == TaskPriority.HIGH

    # Low priority
    todoist_task["priority"] = 1
    task = client._convert_todoist_task_to_task(todoist_task)
    assert task.priority == TaskPriority.LOW

"""Tests for Google Tasks client."""

import pytest

from tasksync.models import Task, TaskStatus
from tasksync.google_tasks import GoogleTasksClient


@pytest.fixture
def client():
    """Create a GoogleTasksClient instance for testing."""
    return GoogleTasksClient(credentials_path="./credentials.json")


def test_convert_google_task():
    """Test converting Google Task API response to Task model."""
    client = GoogleTasksClient()

    google_task = {
        "id": "task123",
        "title": "Test Task",
        "notes": "Test description",
        "status": "needsAction",
    }

    task = client._convert_google_task_to_task(google_task)

    assert task is not None
    assert task.id == "task123"
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.status == TaskStatus.PENDING


def test_convert_completed_google_task():
    """Test converting completed Google Task."""
    client = GoogleTasksClient()

    google_task = {
        "id": "task456",
        "title": "Completed Task",
        "status": "completed",
    }

    task = client._convert_google_task_to_task(google_task)

    assert task is not None
    assert task.status == TaskStatus.COMPLETED


def test_convert_google_task_no_title():
    """Test converting Google Task without title returns None."""
    client = GoogleTasksClient()

    google_task = {
        "id": "task789",
        "notes": "No title",
    }

    task = client._convert_google_task_to_task(google_task)
    assert task is None

"""Data models for tasks and sync operations."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""

    COMPLETED = "completed"
    PENDING = "pending"


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(BaseModel):
    """Task model representing a task in Google Tasks or Todoist."""

    id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Platform-specific identifiers
    google_task_id: Optional[str] = None
    todoist_task_id: Optional[str] = None

    class Config:
        """Pydantic config."""

        use_enum_values = True


class SyncResult(BaseModel):
    """Result of a sync operation."""

    tasks_synced: int = 0
    tasks_created: int = 0
    tasks_updated: int = 0
    tasks_deleted: int = 0
    errors: List[str] = Field(default_factory=list)
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class SyncConfig(BaseModel):
    """Configuration for sync operations."""

    google_credentials_path: str = "./credentials.json"
    todoist_api_token: str
    sync_interval: int = 300  # seconds
    dry_run: bool = False
    sync_completed_tasks: bool = True
    skip_descriptions: bool = False

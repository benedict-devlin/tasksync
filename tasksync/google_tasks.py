"""Google Tasks API client."""

import os
import pickle
from datetime import datetime
from typing import List, Optional

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from tasksync.models import Task, TaskPriority, TaskStatus


class GoogleTasksClient:
    """Client for Google Tasks API."""

    SCOPES = ["https://www.googleapis.com/auth/tasks"]

    def __init__(self, credentials_path: str = "./credentials.json"):
        """Initialize Google Tasks client.

        Args:
            credentials_path: Path to Google OAuth2 credentials file
        """
        self.credentials_path = credentials_path
        self.service = None
        self.creds = None

    def authenticate(self):
        """Authenticate with Google Tasks API using OAuth2."""
        creds = None

        # Check for existing token
        if os.path.exists("token.json"):
            with open("token.json", "rb") as token:
                creds = pickle.load(token)

        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                # Try to open browser, but fall back to manual URL if headless
                try:
                    creds = flow.run_local_server(port=0, open_browser=True)
                except Exception as e:
                    print(f"\n⚠️  Browser auto-open failed (headless environment): {e}")
                    print("\n📋 Manual OAuth Setup:")
                    print("   Please open this URL in your browser on another machine:")
                    creds = flow.run_local_server(port=0, open_browser=False)

            # Save the credentials for next time
            with open("token.json", "wb") as token:
                pickle.dump(creds, token)

        self.creds = creds
        self.service = build("tasks", "v1", credentials=creds)

    def get_tasklists(self) -> List[dict]:
        """Get all task lists.

        Returns:
            List of task lists
        """
        if not self.service:
            self.authenticate()

        results = self.service.tasklists().list().execute()
        return results.get("items", [])

    def get_tasks(
        self, tasklist_id: str = "@default", created_after: Optional[datetime] = None
    ) -> List[Task]:
        """Get all tasks from a task list.

        Args:
            tasklist_id: ID of the task list (default: @default)
            created_after: Only return tasks created after this date

        Returns:
            List of tasks
        """
        if not self.service:
            self.authenticate()

        try:
            results = self.service.tasks().list(tasklist=tasklist_id, showCompleted=True).execute()
        except Exception as e:
            raise RuntimeError(f"Error fetching Google Tasks: {e}")

        tasks = []
        for item in results.get("items", []):
            task = self._convert_google_task_to_task(item)
            if task:
                # Filter by created_after if specified
                if created_after and task.created_at < created_after:
                    continue
                tasks.append(task)

        return tasks

    def create_task(
        self,
        title: str,
        tasklist_id: str = "@default",
        description: Optional[str] = None,
        due: Optional[datetime] = None,
        status: TaskStatus = TaskStatus.PENDING,
    ) -> Task:
        """Create a new task.

        Args:
            title: Task title
            tasklist_id: ID of the task list
            description: Task description
            due: Due date
            status: Task status

        Returns:
            Created task
        """
        if not self.service:
            self.authenticate()

        task_data = {
            "title": title,
            "notes": description,
        }

        if due:
            task_data["due"] = due.isoformat()

        if status == TaskStatus.COMPLETED:
            task_data["status"] = "completed"

        try:
            result = self.service.tasks().insert(tasklist=tasklist_id, body=task_data).execute()
        except Exception as e:
            raise RuntimeError(f"Error creating Google Task: {e}")

        return self._convert_google_task_to_task(result)

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due: Optional[datetime] = None,
        status: Optional[TaskStatus] = None,
        tasklist_id: str = "@default",
    ) -> Task:
        """Update an existing task.

        Args:
            task_id: ID of the task to update
            title: New title
            description: New description
            due: New due date
            status: New status
            tasklist_id: ID of the task list

        Returns:
            Updated task
        """
        if not self.service:
            self.authenticate()

        # Get current task
        try:
            current = self.service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        except Exception as e:
            raise RuntimeError(f"Error fetching task: {e}")

        # Update fields
        if title is not None:
            current["title"] = title
        if description is not None:
            current["notes"] = description
        if due is not None:
            current["due"] = due.isoformat()
        if status is not None:
            current["status"] = "completed" if status == TaskStatus.COMPLETED else "needsAction"

        try:
            result = (
                self.service.tasks()
                .update(tasklist=tasklist_id, task=task_id, body=current)
                .execute()
            )
        except Exception as e:
            raise RuntimeError(f"Error updating Google Task: {e}")

        return self._convert_google_task_to_task(result)

    def delete_task(self, task_id: str, tasklist_id: str = "@default"):
        """Delete a task.

        Args:
            task_id: ID of the task to delete
            tasklist_id: ID of the task list
        """
        if not self.service:
            self.authenticate()

        try:
            self.service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
        except Exception as e:
            raise RuntimeError(f"Error deleting Google Task: {e}")

    def _convert_google_task_to_task(self, google_task: dict) -> Optional[Task]:
        """Convert Google Task API response to Task model.

        Args:
            google_task: Google Task API response

        Returns:
            Task model or None
        """
        if not google_task.get("title"):
            return None

        due_date = None
        if google_task.get("due"):
            try:
                due_date = datetime.fromisoformat(google_task["due"].replace("Z", "+00:00"))
            except (ValueError, KeyError):
                pass

        # Parse created timestamp
        created_at = datetime.utcnow()
        if google_task.get("created"):
            try:
                created_at = datetime.fromisoformat(google_task["created"].replace("Z", "+00:00"))
            except (ValueError, KeyError):
                pass

        status = (
            TaskStatus.COMPLETED if google_task.get("status") == "completed" else TaskStatus.PENDING
        )

        return Task(
            id=google_task.get("id", ""),
            title=google_task.get("title", ""),
            description=google_task.get("notes"),
            status=status,
            priority=TaskPriority.MEDIUM,  # Google Tasks doesn't have priorities
            due_date=due_date,
            created_at=created_at,
            google_task_id=google_task.get("id"),
        )

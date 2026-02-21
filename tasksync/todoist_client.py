"""Todoist API client."""

from datetime import datetime
from typing import List, Optional

import requests

from tasksync.models import Task, TaskPriority, TaskStatus


class TodoistClient:
    """Client for Todoist API."""

    BASE_URL = "https://api.todoist.com/api/v1"

    def __init__(self, api_token: str):
        """Initialize Todoist client.

        Args:
            api_token: Todoist API token
        """
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

    def get_tasks(self, project_id: Optional[str] = None) -> List[Task]:
        """Get all tasks.

        Args:
            project_id: Optional project ID to filter by

        Returns:
            List of tasks
        """
        url = f"{self.BASE_URL}/tasks"

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Error fetching Todoist tasks: {e}")

        tasks = []
        response_data = response.json()

        # Handle v1 API response format which wraps tasks in 'results'
        items = response_data.get("results", []) if isinstance(response_data, dict) else response_data

        for item in items:
            if project_id and item.get("project_id") != project_id:
                continue
            task = self._convert_todoist_task_to_task(item)
            if task:
                tasks.append(task)

        return tasks

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        project_id: Optional[str] = None,
    ) -> Task:
        """Create a new task.

        Args:
            title: Task title
            description: Task description
            due_date: Due date
            priority: Task priority
            project_id: Project ID

        Returns:
            Created task
        """
        url = f"{self.BASE_URL}/tasks"

        # Convert priority to Todoist format (1-4, where 4 is most urgent)
        todoist_priority = {
            TaskPriority.LOW: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.HIGH: 4,
        }.get(priority, 2)

        task_data = {
            "content": title,
            "priority": todoist_priority,
        }

        if description:
            task_data["description"] = description

        if due_date:
            task_data["due_date"] = due_date.date().isoformat()

        if project_id:
            task_data["project_id"] = project_id

        try:
            response = requests.post(url, headers=self.headers, json=task_data)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Error creating Todoist task: {e}")

        return self._convert_todoist_task_to_task(response.json())

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        priority: Optional[TaskPriority] = None,
        is_completed: bool = False,
    ) -> Task:
        """Update an existing task.

        Args:
            task_id: ID of the task to update
            title: New title
            description: New description
            due_date: New due date
            priority: New priority
            is_completed: Whether task is completed

        Returns:
            Updated task
        """
        url = f"{self.BASE_URL}/tasks/{task_id}"

        task_data = {}

        if title is not None:
            task_data["content"] = title

        if description is not None:
            task_data["description"] = description

        if due_date is not None:
            task_data["due_date"] = due_date.date().isoformat()

        if priority is not None:
            todoist_priority = {
                TaskPriority.LOW: 1,
                TaskPriority.MEDIUM: 2,
                TaskPriority.HIGH: 4,
            }.get(priority, 2)
            task_data["priority"] = todoist_priority

        try:
            response = requests.post(url, headers=self.headers, json=task_data)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Error updating Todoist task: {e}")

        result = response.json()

        if is_completed:
            self.close_task(task_id)

        return self._convert_todoist_task_to_task(result)

    def close_task(self, task_id: str):
        """Mark a task as completed.

        Args:
            task_id: ID of the task to close
        """
        url = f"{self.BASE_URL}/tasks/{task_id}/close"

        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Error closing Todoist task: {e}")

    def reopen_task(self, task_id: str):
        """Reopen a completed task.

        Args:
            task_id: ID of the task to reopen
        """
        url = f"{self.BASE_URL}/tasks/{task_id}/reopen"

        try:
            response = requests.post(url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Error reopening Todoist task: {e}")

    def delete_task(self, task_id: str):
        """Delete a task.

        Args:
            task_id: ID of the task to delete
        """
        url = f"{self.BASE_URL}/tasks/{task_id}"

        try:
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
        except requests.RequestException as e:
            raise RuntimeError(f"Error deleting Todoist task: {e}")

    def _convert_todoist_task_to_task(self, todoist_task: dict) -> Optional[Task]:
        """Convert Todoist API response to Task model.

        Args:
            todoist_task: Todoist API response

        Returns:
            Task model or None
        """
        if not todoist_task.get("content"):
            return None

        # Convert Todoist priority (1-4) to our priority format
        todoist_priority = todoist_task.get("priority", 2)
        priority_map = {
            1: TaskPriority.LOW,
            2: TaskPriority.MEDIUM,
            3: TaskPriority.HIGH,
            4: TaskPriority.HIGH,
        }
        priority = priority_map.get(todoist_priority, TaskPriority.MEDIUM)

        due_date = None
        if todoist_task.get("due") and isinstance(todoist_task["due"], dict):
            if todoist_task["due"].get("date"):
                try:
                    due_date = datetime.fromisoformat(todoist_task["due"]["date"])
                except ValueError:
                    pass

        status = TaskStatus.COMPLETED if todoist_task.get("checked") else TaskStatus.PENDING

        return Task(
            id=todoist_task.get("id", ""),
            title=todoist_task.get("content", ""),
            description=todoist_task.get("description") or None,
            status=status,
            priority=priority,
            due_date=due_date,
            todoist_task_id=todoist_task.get("id"),
        )

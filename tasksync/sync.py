"""Main synchronization engine for TaskSync."""

import logging
from datetime import datetime
from typing import Dict, Optional

from tasksync.google_tasks import GoogleTasksClient
from tasksync.models import SyncResult, Task, TaskStatus
from tasksync.todoist_client import TodoistClient


class TaskSyncer:
    """Main sync engine for synchronizing tasks between Google Tasks and Todoist."""

    def __init__(
        self,
        google_credentials_path: str = "./credentials.json",
        todoist_api_token: str = "",
        dry_run: bool = False,
        created_after: Optional[datetime] = None,
    ):
        """Initialize TaskSyncer.

        Args:
            google_credentials_path: Path to Google credentials
            todoist_api_token: Todoist API token
            dry_run: If True, don't make actual changes
            created_after: Only sync tasks created after this date
        """
        self.google_client = GoogleTasksClient(google_credentials_path)
        self.todoist_client = TodoistClient(todoist_api_token)
        self.dry_run = dry_run
        self.created_after = created_after
        self.logger = logging.getLogger(__name__)

    def authenticate(self):
        """Authenticate with both services."""
        self.logger.info("Authenticating with Google Tasks...")
        self.google_client.authenticate()
        self.logger.info("Authentication successful!")

    def sync(self, sync_completed: bool = True) -> SyncResult:
        """Perform a one-way sync from Google Tasks to Todoist.

        Syncs tasks from Google Tasks to Todoist and deletes the original
        Google Task after successful sync.

        Args:
            sync_completed: Whether to sync completed tasks

        Returns:
            SyncResult with statistics
        """
        result = SyncResult()

        try:
            self.logger.info("Starting task synchronization (Google Tasks → Todoist)...")
            if self.created_after:
                self.logger.info(
                    f"Only syncing tasks created after {self.created_after.isoformat()}"
                )

            # Get tasks from Google Tasks
            self.logger.debug("Fetching tasks from Google Tasks...")
            google_tasks = self.google_client.get_tasks(created_after=self.created_after)

            # Get existing tasks in Todoist
            self.logger.debug("Fetching tasks from Todoist...")
            todoist_tasks = self.todoist_client.get_tasks()

            # Build lookup map for Todoist tasks
            todoist_by_title: Dict[str, Task] = {t.title: t for t in todoist_tasks}

            # Sync from Google Tasks to Todoist
            for google_task in google_tasks:
                if not sync_completed and google_task.status == TaskStatus.COMPLETED:
                    self.logger.debug(
                        f"Skipping completed task (sync_completed=False): {google_task.title}"
                    )
                    continue

                if google_task.title in todoist_by_title:
                    # Task already exists in Todoist, skip it
                    self.logger.debug(
                        f"Task already synced to Todoist, skipping: {google_task.title}"
                    )
                    continue
                else:
                    # Create new task in Todoist
                    self.logger.debug(f"Syncing task to Todoist: {google_task.title}")
                    if not self.dry_run:
                        try:
                            self.todoist_client.create_task(
                                title=google_task.title,
                                description=google_task.description,
                                due_date=google_task.due_date,
                                priority=google_task.priority,
                            )
                            # Successfully synced, now delete from Google Tasks
                            self.logger.debug(
                                f"Deleting synced task from Google Tasks: {google_task.title}"
                            )
                            self.google_client.delete_task(google_task.google_task_id)
                            result.tasks_created += 1
                        except Exception as e:
                            self.logger.error(f"Error syncing task {google_task.title}: {e}")
                            result.errors.append(f"Failed to sync '{google_task.title}': {str(e)}")
                    else:
                        # Dry run mode - just count
                        result.tasks_created += 1

            result.tasks_synced = len(google_tasks)
            self.logger.info(f"Synchronization complete: {result}")

        except Exception as e:
            self.logger.error(f"Error during synchronization: {e}")
            result.errors.append(str(e))

        return result

    def sync_task_to_todoist(self, google_task: Task) -> bool:
        """Sync a single task from Google Tasks to Todoist.

        Args:
            google_task: Task from Google Tasks

        Returns:
            True if successful
        """
        try:
            self.logger.debug(f"Syncing task to Todoist: {google_task.title}")
            if not self.dry_run:
                self.todoist_client.create_task(
                    title=google_task.title,
                    description=google_task.description,
                    due_date=google_task.due_date,
                    priority=google_task.priority,
                )
                # Delete from Google Tasks after successful sync
                self.logger.debug(f"Deleting synced task from Google Tasks: {google_task.title}")
                self.google_client.delete_task(google_task.google_task_id)
            return True
        except Exception as e:
            self.logger.error(f"Error syncing task to Todoist: {e}")
            return False

    def _should_update(self, existing_task: Task, new_task: Task) -> bool:
        """Determine if a task should be updated.

        Args:
            existing_task: Current task
            new_task: New task data

        Returns:
            True if task should be updated
        """
        # Update if descriptions differ
        if existing_task.description != new_task.description:
            return True

        # Update if due dates differ
        if existing_task.due_date != new_task.due_date:
            return True

        # Update if status differs
        if existing_task.status != new_task.status:
            return True

        return False

"""Command-line interface for TaskSync."""

import logging
import os
import sys
import time

import click

from tasksync.config import load_config
from tasksync.sync import TaskSyncer


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose):
    """TaskSync - Sync Google Tasks with Todoist."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
def init():
    """Initialize TaskSync with credentials and configuration."""
    click.echo("TaskSync Initialization")
    click.echo("=" * 40)

    # Check for Google credentials
    if not os.path.exists("credentials.json"):
        click.echo("\n⚠️  Google credentials not found at credentials.json")
        click.echo("Please download credentials from Google Cloud Console:")
        click.echo("https://console.cloud.google.com/apis/credentials")
        click.echo("Save the JSON file as credentials.json in this directory.")
    else:
        click.echo("✓ Google credentials found")

    # Check for .env file
    if not os.path.exists(".env"):
        click.echo("\n📝 Creating .env file...")
        todoist_token = click.prompt("Enter your Todoist API token")
        with open(".env", "w") as f:
            f.write(f"TODOIST_API_TOKEN={todoist_token}\n")
            f.write("GOOGLE_CREDENTIALS_PATH=./credentials.json\n")
            f.write("SYNC_INTERVAL=300\n")
            f.write("SYNC_COMPLETED_TASKS=true\n")
        click.echo("✓ .env file created")
    else:
        click.echo("✓ .env file exists")

    click.echo("\n✓ Initialization complete!")


@cli.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Perform a dry run without making changes",
)
def sync(dry_run):
    """Perform a sync between Google Tasks and Todoist."""
    try:
        config = load_config()
        click.echo("Starting sync...")

        syncer = TaskSyncer(
            google_credentials_path=config.google_credentials_path,
            todoist_api_token=config.todoist_api_token,
            dry_run=dry_run,
            created_after=config.tasks_created_after,
        )

        syncer.authenticate()
        result = syncer.sync(sync_completed=config.sync_completed_tasks)

        click.echo("\nSync completed!")
        click.echo(f"  Tasks synced: {result.tasks_synced}")
        click.echo(f"  Created: {result.tasks_created}")
        click.echo(f"  Updated: {result.tasks_updated}")

        if result.errors:
            click.echo("\nErrors encountered:")
            for error in result.errors:
                click.echo(f"  - {error}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def start():
    """Start continuous synchronization."""
    try:
        config = load_config()
        click.echo("Starting continuous sync...")
        click.echo(f"Sync interval: {config.sync_interval} seconds")
        click.echo("Press Ctrl+C to stop")

        syncer = TaskSyncer(
            google_credentials_path=config.google_credentials_path,
            todoist_api_token=config.todoist_api_token,
            created_after=config.tasks_created_after,
        )

        syncer.authenticate()

        iteration = 0
        while True:
            iteration += 1
            click.echo(f"\n[{iteration}] Syncing at {time.strftime('%Y-%m-%d %H:%M:%S')}")

            try:
                result = syncer.sync(sync_completed=config.sync_completed_tasks)
                click.echo(
                    f"  Synced: {result.tasks_synced}, "
                    f"Created: {result.tasks_created}, "
                    f"Updated: {result.tasks_updated}"
                )
            except Exception as e:
                click.echo(f"  Error: {e}", err=True)

            click.echo(f"Next sync in {config.sync_interval} seconds...")
            time.sleep(config.sync_interval)

    except KeyboardInterrupt:
        click.echo("\n\nSync stopped by user")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Show sync status and configuration."""
    try:
        config = load_config()

        click.echo("TaskSync Status")
        click.echo("=" * 40)
        click.echo(f"Google credentials: {config.google_credentials_path}")
        click.echo(f"Dry run mode: {config.dry_run}")
        click.echo(f"Sync interval: {config.sync_interval}s")
        click.echo(f"Sync completed tasks: {config.sync_completed_tasks}")
        if config.tasks_created_after:
            click.echo(f"Tasks created after: {config.tasks_created_after.isoformat()}")

        # Try to get task count
        try:
            syncer = TaskSyncer(
                google_credentials_path=config.google_credentials_path,
                todoist_api_token=config.todoist_api_token,
                created_after=config.tasks_created_after,
            )
            syncer.authenticate()

            google_tasks = syncer.google_client.get_tasks()
            todoist_tasks = syncer.todoist_client.get_tasks()

            click.echo(f"\nGoogle Tasks: {len(google_tasks)} tasks")
            click.echo(f"Todoist: {len(todoist_tasks)} tasks")
        except Exception as e:
            click.echo(f"\nError fetching status: {e}", err=True)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()

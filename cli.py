import argparse
from typing import Optional

from models import Task
from storage import TaskStorage


class TaskCLI:
    """Command-line interface for task management operations.

    Provides methods for listing, creating, updating, and deleting tasks
    through a command-line interface. Handles argument parsing and
    user-friendly output formatting.

    Attributes:
        storage (TaskStorage): Storage instance for database operations.

    """

    def __init__(self, storage: Optional[TaskStorage] = None):
        """Initialize CLI with storage instance.

        Args:
            storage: Optional TaskStorage instance. Creates new one if not provided.
        """
        self.storage = storage or TaskStorage()

    def format_task(self, task: Task, detailed: bool = False) -> str:
        """Format a task object for human-readable display.

        Args:
            task: Task instance to format.
            detailed: Whether to include all fields (currently same as regular).

        Returns:
            str: Formatted string representation of the task.
        """
        lines = [
            f"ID: {task.task_id}",
            f"Title: {task.title}",
            f"Status: {task.status}",
            f"Priority: {task.priority}",
            f"Created: {task.created_date}",
        ]

        if task.description:
            lines.append(f"Description: {task.description}")

        if task.due_date:
            lines.append(f"Due Date: {task.due_date}")

        return "\n".join(lines)

    def list_tasks(self, status: Optional[str] = None, priority: Optional[str] = None):
        """List all tasks with optional filtering.

        Displays tasks in a formatted table with separators. Shows count
        and handles empty results gracefully.

        Args:
            status: Optional status filter (pending, in_progress, completed, overdue).
            priority: Optional priority filter (low, medium, high).
        """
        tasks = self.storage.get_all_tasks(status=status, priority=priority)

        if not tasks:
            print("No tasks found.")
            return

        print(f"\nFound {len(tasks)} task(s):\n")
        print("=" * 60)

        for i, task in enumerate(tasks, 1):
            print(f"\n[{i}] {self.format_task(task)}")
            if i < len(tasks):
                print("-" * 60)

        print("\n" + "=" * 60)

    def create_task(
        self,
        title: str,
        description: str = "",
        status: str = "pending",
        priority: str = "medium",
        due_date: Optional[str] = None,
    ):
        """Create a new task and display the result.

        Args:
            title: Task title (required).
            description: Task description. Defaults to empty string.
            status: Task status. Defaults to "pending".
            priority: Task priority. Defaults to "medium".
            due_date: Optional due date in ISO format.

        Prints success message and task details, or error message on failure.
        """
        try:
            task = Task(
                title=title,
                description=description,
                status=status,
                priority=priority,
                due_date=due_date,
            )

            self.storage.create_task(task)
            print(f"\nTask created successfully!")
            print(self.format_task(task, detailed=True))

        except ValueError as e:
            print(f"Error: {e}")
        except RuntimeError as e:
            print(f"Error: Database operation failed - {e}")
        except Exception as e:
            print(f"Error: Unexpected error occurred - {e}")

    def get_task(self, task_id: str):
        """Get and display a task by its ID.

        Args:
            task_id: Unique task identifier (UUID string).

        Prints formatted task details or error message if not found.
        """
        task = self.storage.get_task(task_id)

        if task:
            print("\n" + "=" * 60)
            print(self.format_task(task, detailed=True))
            print("=" * 60)
        else:
            print(f"Task with ID '{task_id}' not found.")

    def update_task(self, task_id: str, **kwargs):
        """Update a task with specified fields.

        Args:
            task_id: Unique task identifier (UUID string).
            **kwargs: Field names and values to update (e.g., status="completed",
                     title="New title", priority="high").

        Prints success message and updated task details, or error message on failure.
        """
        # Remove None values
        update_data = {k: v for k, v in kwargs.items() if v is not None}

        if not update_data:
            print("Error: No fields to update.")
            return

        try:
            task = self.storage.update_task(task_id, **update_data)

            if task:
                print(f"\nTask updated successfully!")
                print(self.format_task(task, detailed=True))
            else:
                print(f"Error: Task with ID '{task_id}' not found.")

        except ValueError as e:
            print(f"Error: {e}")
        except RuntimeError as e:
            print(f"Error: Database operation failed - {e}")
        except Exception as e:
            print(f"Error: Unexpected error occurred - {e}")

    def delete_task(self, task_id: str):
        """Delete a task by its ID.

        Args:
            task_id: Unique task identifier (UUID string).

        Prints success or error message.
        """
        if self.storage.delete_task(task_id):
            print(f"Task '{task_id}' deleted successfully.")
        else:
            print(f"Task with ID '{task_id}' not found.")

    def run(self):
        """Run the CLI with command-line argument parsing.

        Parses command-line arguments and executes the appropriate command
        (list, create, get, update, delete). Displays help if no command provided.
        """
        parser = argparse.ArgumentParser(
            description="Task Management CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # List command
        list_parser = subparsers.add_parser("list", help="List all tasks")
        list_parser.add_argument(
            "--status",
            choices=["pending", "in_progress", "completed", "overdue"],
            help="Filter by status",
        )
        list_parser.add_argument(
            "--priority", choices=["low", "medium", "high"], help="Filter by priority"
        )

        # Create command
        create_parser = subparsers.add_parser("create", help="Create a new task")
        create_parser.add_argument("title", help="Task title")
        create_parser.add_argument(
            "-d", "--description", default="", help="Task description"
        )
        create_parser.add_argument(
            "-s",
            "--status",
            choices=["pending", "in_progress", "completed", "overdue"],
            default="pending",
            help="Task status",
        )
        create_parser.add_argument(
            "-p",
            "--priority",
            choices=["low", "medium", "high"],
            default="medium",
            help="Task priority",
        )
        create_parser.add_argument("--due-date", help="Due date (ISO format)")

        # Get command
        get_parser = subparsers.add_parser("get", help="Get a task by ID")
        get_parser.add_argument("task_id", help="Task ID")

        # Update command
        update_parser = subparsers.add_parser("update", help="Update a task")
        update_parser.add_argument("task_id", help="Task ID")
        update_parser.add_argument("--title", help="Update title")
        update_parser.add_argument("--description", help="Update description")
        update_parser.add_argument(
            "--status",
            choices=["pending", "in_progress", "completed", "overdue"],
            help="Update status (use 'completed' to mark complete, 'pending' to mark incomplete)",
        )
        update_parser.add_argument(
            "--priority", choices=["low", "medium", "high"], help="Update priority"
        )
        update_parser.add_argument("--due-date", help="Update due date (ISO format)")

        # Delete command
        delete_parser = subparsers.add_parser("delete", help="Delete a task")
        delete_parser.add_argument("task_id", help="Task ID")

        args = parser.parse_args()

        if not args.command:
            parser.print_help()
            return

        try:
            if args.command == "list":
                self.list_tasks(status=args.status, priority=args.priority)

            elif args.command == "create":
                self.create_task(
                    title=args.title,
                    description=args.description,
                    status=args.status,
                    priority=args.priority,
                    due_date=args.due_date,
                )

            elif args.command == "get":
                self.get_task(args.task_id)

            elif args.command == "update":
                self.update_task(
                    task_id=args.task_id,
                    title=args.title,
                    description=args.description,
                    status=args.status,
                    priority=args.priority,
                    due_date=args.due_date,
                )

            elif args.command == "delete":
                self.delete_task(args.task_id)

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    cli = TaskCLI()
    cli.run()

import sqlite3
from contextlib import contextmanager
from typing import List
from typing import Optional

from models import Task


class TaskStorage:
    """Manages task persistence using SQLite database.

    Provides methods for creating, reading, updating, and deleting tasks
    with proper transaction handling and error management. The database
    is automatically initialized on first use.

    Attributes:
        db_file (str): Path to the SQLite database file.
    """

    def __init__(self, db_file: str = "tasks.db"):
        """Initialize TaskStorage with database file.

        Args:
            db_file: Path to SQLite database file. Defaults to "tasks.db".
                    Database and tables are created automatically if they don't exist.

        Raises:
            RuntimeError: If database initialization fails.
        """
        self.db_file = db_file
        try:
            self._ensure_database()
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to initialize database: {e}") from e

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections.

        Provides a database connection with automatic commit on success
        and rollback on error. Connection is automatically closed when done.

        Yields:
            sqlite3.Connection: Database connection object.

        Raises:
            sqlite3.Error: If database operation fails.
        """
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_database(self):
        """Create database and tables if they don't exist.

        Creates the tasks table with appropriate columns and indexes
        for query performance. This method is called automatically during
        initialization.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'pending',
                    priority TEXT NOT NULL DEFAULT 'medium',
                    created_date TEXT NOT NULL,
                    due_date TEXT
                )
            """
            )
            # Create indexes for better query performance
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority)
            """
            )

    def _row_to_task(self, row: sqlite3.Row):
        """Convert a database row to a Task object.

        Args:
            row: SQLite Row object from database query.

        Returns:
            Task: Task instance created from database row data.
        """
        return Task.from_dict(
            {
                "task_id": row["task_id"],
                "title": row["title"],
                "description": row["description"] or "",
                "status": row["status"],
                "priority": row["priority"],
                "created_date": row["created_date"],
                "due_date": row["due_date"],
            }
        )

    def create_task(self, task: Task):
        """Create a new task in the database.

        Args:
            task: Task instance to save to database.

        Returns:
            Task: The created task (same instance passed in).

        Raises:
            ValueError: If task with same ID already exists.
            RuntimeError: If database operation fails.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO tasks (task_id, title, description, status, priority, created_date, due_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        task.task_id,
                        task.title,
                        task.description,
                        task.status,
                        task.priority,
                        task.created_date,
                        task.due_date,
                    ),
                )
            return task
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Task with ID '{task.task_id}' already exists") from e
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to create task: {e}") from e

    def get_task(self, task_id: str):
        """Retrieve a task by its unique ID.

        Args:
            task_id: Unique task identifier (UUID string).

        Returns:
            Optional[Task]: Task instance if found, None otherwise.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM tasks WHERE task_id = ?
            """,
                (task_id,),
            )
            row = cursor.fetchone()
            if row:
                return self._row_to_task(row)
        return None

    def get_all_tasks(
        self, status: Optional[str] = None, priority: Optional[str] = None
    ):
        """Retrieve all tasks with optional filtering.

        Args:
            status: Optional status filter (pending, in_progress, completed, overdue).
            priority: Optional priority filter (low, medium, high).

        Returns:
            List[Task]: List of Task instances matching the filters,
                       ordered by creation date (newest first).
        """
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)

        if priority:
            query += " AND priority = ?"
            params.append(priority)

        query += " ORDER BY created_date DESC"

        tasks = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            for row in cursor.fetchall():
                tasks.append(self._row_to_task(row))

        return tasks

    def update_task(self, task_id: str, **kwargs):
        """Update an existing task in the database.

        Args:
            task_id: Unique task identifier (UUID string).
            **kwargs: Field names and values to update (e.g., status="completed",
                     title="New title", priority="high").

        Returns:
            Optional[Task]: Updated Task instance if found, None if task doesn't exist.

        Raises:
            ValueError: If validation fails during update.
            RuntimeError: If database operation fails.
        """
        try:
            # First, get the existing task
            existing_task = self.get_task(task_id)
            if not existing_task:
                return None

            existing_task.update(**kwargs)

            update_fields = []
            update_values = []

            if "title" in kwargs and kwargs["title"] is not None:
                update_fields.append("title = ?")
                update_values.append(existing_task.title)

            if "description" in kwargs:
                update_fields.append("description = ?")
                update_values.append(existing_task.description)

            if "status" in kwargs and kwargs["status"] is not None:
                update_fields.append("status = ?")
                update_values.append(existing_task.status)

            if "priority" in kwargs and kwargs["priority"] is not None:
                update_fields.append("priority = ?")
                update_values.append(existing_task.priority)

            if "due_date" in kwargs:
                update_fields.append("due_date = ?")
                update_values.append(existing_task.due_date)

            if not update_fields:
                return existing_task

            update_values.append(task_id)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE task_id = ?"
                cursor.execute(query, update_values)

            return existing_task
        except ValueError:
            raise  # Re-raise validation errors
        except sqlite3.Error as e:
            raise RuntimeError(f"Failed to update task: {e}") from e

    def delete_task(self, task_id: str):
        """Delete a task from the database.

        Args:
            task_id: Unique task identifier (UUID string).

        Returns:
            bool: True if task was deleted, False if task not found.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
            return cursor.rowcount > 0

    def get_task_count(self) -> int:
        """Get the total number of tasks in the database.

        Returns:
            int: Total count of tasks in the database.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks")
            return cursor.fetchone()[0]

    def close(self):
        """Close database connections.

        Note: SQLite connections are automatically managed by context managers,
        so this method is a no-op. It exists for API compatibility and potential
        future use with connection pooling.
        """
        # SQLite connections are managed by context managers, so this is a no-op
        # but included for potential future use or API compatibility
        pass

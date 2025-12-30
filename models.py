import uuid
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Optional


class Task:
    """Represents a task in the task management system.

    A task has a title, description, status, priority, creation date, and
    optional due date. All task data is validated upon creation and update.
    """

    VALID_STATUSES = ["pending", "in_progress", "completed", "overdue"]
    VALID_PRIORITIES = ["low", "medium", "high"]

    def __init__(
        self,
        title: str,
        description: str = "",
        status: str = "pending",
        priority: str = "medium",
        due_date: Optional[str] = None,
        task_id: Optional[str] = None,
        created_date: Optional[str] = None,
    ):
        """Initialize a new Task instance.

        Raises:
            ValueError: If validation fails (empty title, invalid status/priority,
                       invalid date format, or exceeds length limits).
        """
        self.task_id = task_id or self._generate_id()
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.created_date = created_date or datetime.now().isoformat()
        self.due_date = due_date

        self._validate()

    def _validate(self):
        """Validate all task data fields.

        Checks that title is not empty, field lengths are within limits,
        status and priority are valid values, and date format is correct.

        Raises:
            ValueError: If any validation check fails.
        """
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")

        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")

        if len(self.description) > 2000:
            raise ValueError("Task description cannot exceed 2000 characters")

        if self.status not in self.VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(self.VALID_STATUSES)}")

        if self.priority not in self.VALID_PRIORITIES:
            raise ValueError(
                f"Priority must be one of: {', '.join(self.VALID_PRIORITIES)}"
            )

        if self.due_date:
            self._validate_date(self.due_date)

    @staticmethod
    def _validate_date(date_string: str):
        """Validate that a date string is in ISO format.

        Args:
            date_string: Date string to validate.

        Raises:
            ValueError: If date string is not in valid ISO format.
        """
        try:
            datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(
                "Date must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
            )

    @staticmethod
    def _generate_id():
        """Generate a unique task ID using UUID4.

        Returns:
            str: A UUID4 string representation.
        """
        return str(uuid.uuid4())

    def to_dict(self):
        """Convert task instance to dictionary representation.

        Returns:
            dict: Dictionary containing all task fields with their values.
        """
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "created_date": self.created_date,
            "due_date": self.due_date,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Create a Task instance from a dictionary.

        Args:
            data: Dictionary containing task data. Must have 'title' key.
                  Other fields are optional with defaults.

        Returns:
            Task: A new Task instance created from the dictionary data.

        Raises:
            ValueError: If validation fails during task creation.
        """
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "pending"),
            priority=data.get("priority", "medium"),
            due_date=data.get("due_date"),
            task_id=data.get("task_id"),
            created_date=data.get("created_date"),
        )

    def update(self, **kwargs):
        """Update task fields with validation.

        Updates the specified fields and re-validates the entire task.
        Only fields that exist on the task and have non-None values are updated.

        Args:
            **kwargs: Field names and values to update (e.g., status="completed",
                    priority="high", title="New title").

        Raises:
            ValueError: If validation fails after update.
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        self._validate()

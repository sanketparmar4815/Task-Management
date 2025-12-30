import json
import urllib.parse
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from typing import Optional

from models import Task
from storage import TaskStorage


class TaskAPIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for task management API endpoints.

    Handles GET, POST, PUT, PATCH, DELETE, and OPTIONS requests for
    task management operations. Provides JSON responses and proper
    HTTP status codes.

    Attributes:
        storage (TaskStorage): Storage instance for database operations.
    """

    def __init__(self, *args, storage: TaskStorage = None, **kwargs):
        """Initialize the API handler with storage instance.

        Args:
            *args: Positional arguments passed to BaseHTTPRequestHandler.
            storage: Optional TaskStorage instance. Creates new one if not provided.
            **kwargs: Keyword arguments passed to BaseHTTPRequestHandler.
        """
        self.storage = storage or TaskStorage()
        super().__init__(*args, **kwargs)

    def _send_response(
        self,
        status_code: int,
        data: Optional[dict] = None,
        message: Optional[str] = None,
    ):
        """Send HTTP JSON response with proper headers.

        Args:
            status_code: HTTP status code (e.g., 200, 201, 404).
            data: Optional response data to include in JSON body.
            message: Optional message to include in JSON body.
        """
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

        response = {}
        if message:
            response["message"] = message
        if data is not None:
            response["data"] = data

        self.wfile.write(json.dumps(response).encode("utf-8"))

    def _send_error(self, status_code: int, message: str):
        """Send HTTP error response.

        Args:
            status_code: HTTP error status code (e.g., 400, 404, 500).
            message: Error message to include in response.
        """
        self._send_response(status_code, message=message)

    def _parse_path(self):
        """Parse URL path to extract resource type and task ID.

        Returns:
            tuple: (resource_type, task_id) where resource_type is "task",
                   "tasks", or None, and task_id is the task ID if present.
        """
        path = self.path.split("?")[0]  # Remove query string
        parts = [p for p in path.split("/") if p]

        if not parts or parts[0] != "api" or parts[1] != "tasks":
            return None, None

        if len(parts) > 2:
            return "task", parts[2]
        return "tasks", None

    def _parse_query_params(self):
        """Parse URL query parameters into a dictionary.

        Returns:
            dict: Dictionary of query parameter names and values.
        """
        if "?" not in self.path:
            return {}

        query_string = self.path.split("?")[1]
        return dict(urllib.parse.parse_qsl(query_string))

    def _read_body(self):
        """Read and parse JSON request body.

        Returns:
            dict: Parsed JSON body as dictionary, or empty dict if body is empty
                  or invalid JSON.
        """
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}

        body = self.rfile.read(content_length)
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self):
        """Handle CORS preflight OPTIONS requests.

        Responds with appropriate CORS headers to allow cross-origin requests
        from web applications.
        """
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests for retrieving tasks.

        Supports:
        - GET /api/tasks - List all tasks (with optional query filters)
        - GET /api/tasks/{id} - Get single task by ID
        """
        resource, task_id = self._parse_path()

        if resource is None:
            self._send_error(404, "Not Found")
            return

        if resource == "task" and task_id:
            # Get single task
            task = self.storage.get_task(task_id)
            if task:
                self._send_response(200, data=task.to_dict())
            else:
                self._send_error(404, "Task not found")

        elif resource == "tasks":
            # Get all tasks with optional filtering
            query_params = self._parse_query_params()
            status = query_params.get("status")
            priority = query_params.get("priority")

            tasks = self.storage.get_all_tasks(status=status, priority=priority)
            self._send_response(200, data=[t.to_dict() for t in tasks])

        else:
            self._send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests for creating new tasks.

        Endpoint: POST /api/tasks
        Body: JSON with task data (title required, other fields optional).
        """
        resource, _ = self._parse_path()

        if resource != "tasks":
            self._send_error(404, "Not Found")
            return

        body = self._read_body()

        try:
            task = Task(
                title=body.get("title", ""),
                description=body.get("description", ""),
                status=body.get("status", "pending"),
                priority=body.get("priority", "medium"),
                due_date=body.get("due_date"),
            )

            self.storage.create_task(task)
            self._send_response(
                201, data=task.to_dict(), message="Task created successfully"
            )

        except ValueError as e:
            self._send_error(400, str(e))
        except RuntimeError as e:
            self._send_error(500, str(e))
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")

    def do_PUT(self):
        """Handle PUT requests for full task updates.

        Endpoint: PUT /api/tasks/{id}
        Body: JSON with all task fields to update.
        """
        resource, task_id = self._parse_path()

        if resource != "task" or not task_id:
            self._send_error(404, "Not Found")
            return

        body = self._read_body()

        # Remove None values
        update_data = {k: v for k, v in body.items() if v is not None}

        try:
            task = self.storage.update_task(task_id, **update_data)

            if task:
                self._send_response(
                    200, data=task.to_dict(), message="Task updated successfully"
                )
            else:
                self._send_error(404, "Task not found")

        except ValueError as e:
            self._send_error(400, str(e))
        except RuntimeError as e:
            self._send_error(500, str(e))
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")

    def do_PATCH(self):
        """Handle PATCH requests for partial task updates.

        Endpoint: PATCH /api/tasks/{id}
        Body: JSON with only fields to update (partial update).
        """
        resource, task_id = self._parse_path()

        if resource != "task" or not task_id:
            self._send_error(404, "Not Found")
            return

        body = self._read_body()

        if not body:
            self._send_error(400, "Request body is required for PATCH")
            return

        # Remove None values
        update_data = {k: v for k, v in body.items() if v is not None}

        if not update_data:
            self._send_error(400, "No valid fields to update")
            return

        try:
            task = self.storage.update_task(task_id, **update_data)

            if task:
                self._send_response(
                    200, data=task.to_dict(), message="Task updated successfully"
                )
            else:
                self._send_error(404, "Task not found")

        except ValueError as e:
            self._send_error(400, str(e))
        except RuntimeError as e:
            self._send_error(500, str(e))
        except Exception as e:
            self._send_error(500, f"Internal server error: {str(e)}")

    def do_DELETE(self):
        """Handle DELETE requests for removing tasks.

        Endpoint: DELETE /api/tasks/{id}
        """
        resource, task_id = self._parse_path()

        if resource != "task" or not task_id:
            self._send_error(404, "Not Found")
            return

        if self.storage.delete_task(task_id):
            self._send_response(200, message="Task deleted successfully")
        else:
            self._send_error(404, "Task not found")

    def log_message(self, format, *args):
        """Override to customize HTTP request log format.

        Args:
            format: Log message format string.
            *args: Arguments for format string.
        """
        print(f"[API] {format % args}")


def create_handler_class(storage: TaskStorage):
    """Create a handler class bound to a specific storage instance.

    Args:
        storage: TaskStorage instance to use for all requests.

    Returns:
        type: Handler class with storage instance bound.
    """

    class Handler(TaskAPIHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, storage=storage, **kwargs)

    return Handler


def run_server(host: str = "localhost", port: int = 8000):
    """Start and run the task management API server.

    Creates a new storage instance and starts an HTTP server listening
    on the specified host and port. The server runs until interrupted
    (Ctrl+C).

    Args:
        host: Server host address. Defaults to "localhost".
        port: Server port number. Defaults to 8000.
    """
    storage = TaskStorage()
    handler_class = create_handler_class(storage)

    server = HTTPServer((host, port), handler_class)
    print(f"Task Management API server running on http://{host}:{port}")
    print("API endpoints:")
    print("  GET    /api/tasks - List all tasks")
    print("  GET    /api/tasks?status=pending - Filter by status")
    print("  GET    /api/tasks?priority=high - Filter by priority")
    print("  GET    /api/tasks/{id} - Get task by ID")
    print("  POST   /api/tasks - Create new task")
    print("  PUT    /api/tasks/{id} - Update task")
    print("  PATCH  /api/tasks/{id} - Partially update task")
    print("  DELETE /api/tasks/{id} - Delete task")
    print("\nPress Ctrl+C to stop the server")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()


if __name__ == "__main__":
    run_server()

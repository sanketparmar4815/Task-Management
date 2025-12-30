# Task Management System

A RESTful Task Management system with both an API backend and a command-line interface, built with Python 3.8+.

## Features

- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ RESTful API with filtering capabilities
- ✅ Command-line interface for terminal usage
- ✅ SQLite database for persistent data storage
- ✅ Task validation and error handling
- ✅ Filter tasks by status and priority
- ✅ Mark tasks as complete/incomplete

## Project Structure

```
Task-Management/
├── main.py           # Main entry point
├── api_server.py     # RESTful API server
├── cli.py            # Command-line interface
├── models.py         # Task data model
├── storage.py        # Database storage layer
├── requirements.txt  # Dependencies (none - uses stdlib)
└── README.md         # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- No external dependencies required (uses Python standard library only)

### Installation

1. Clone or download this repository:
   ```bash
   cd Task-Management
   ```

2. (Optional) Create a virtual environment:
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. The database (`tasks.db`) will be created automatically on first run.

## Usage

### Running the API Server

Start the RESTful API server:

```bash
python main.py api
```

Or with custom host/port:

```bash
python main.py api --host 0.0.0.0 --port 8080
```

The server will start on `http://localhost:8000` by default.

### Running the CLI

Use the command-line interface:

```bash
python main.py cli <command> [options]
```

Or directly:

```bash
python cli.py <command> [options]
```

## API Documentation

For detailed API documentation with complete endpoint descriptions, request/response examples, and code samples, see [API.md](API.md).

### Quick API Reference

Base URL: `http://localhost:8000/api/tasks`

### Available Endpoints

- `GET /api/tasks` - List all tasks (with optional filtering)
- `GET /api/tasks/{id}` - Get task by ID
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/{id}` - Update task (full update)
- `PATCH /api/tasks/{id}` - Update task (partial update)
- `DELETE /api/tasks/{id}` - Delete task

**Quick Examples:**

```bash
# List all tasks
curl http://localhost:8000/api/tasks

# Create a task
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "priority": "high"}'

# Mark task as complete
curl -X PATCH http://localhost:8000/api/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

See [API.md](API.md) for complete documentation with all endpoints, request/response formats, error codes, and code examples in multiple languages.

## CLI Usage Examples

### List Tasks

List all tasks:
```bash
python main.py cli list
```

Filter by status:
```bash
python main.py cli list --status pending
python main.py cli list --status completed
```

Filter by priority:
```bash
python main.py cli list --priority high
```

Combine filters:
```bash
python main.py cli list --status in_progress --priority medium
```

### Create Task

Basic task:
```bash
python main.py cli create "Complete project"
```

With all options:
```bash
python main.py cli create "Review code" \
  --description "Review pull requests" \
  --status in_progress \
  --priority high \
  --due-date "2024-12-31"
```

### Get Task

```bash
python main.py cli get <task_id>
```

### Update Task

Update status (mark as complete):
```bash
python main.py cli update <task_id> --status completed
```

Update status (mark as incomplete):
```bash
python main.py cli update <task_id> --status pending
```

Update multiple fields:
```bash
python main.py cli update <task_id> \
  --title "Updated Title" \
  --description "New description" \
  --priority high \
  --status in_progress \
  --due-date "2024-12-31"
```

### Delete Task

```bash
python main.py cli delete <task_id>
```

## Task Model

Each task has the following fields:

- **task_id** (string, UUID): Unique identifier (auto-generated)
- **title** (string, required): Task title (max 200 characters)
- **description** (string, optional): Task description (max 2000 characters)
- **status** (string): One of `pending`, `in_progress`, `completed`, `overdue` (default: `pending`)
- **priority** (string): One of `low`, `medium`, `high` (default: `medium`)
- **created_date** (string, ISO format): Auto-generated creation timestamp
- **due_date** (string, ISO format, optional): Task due date

### Status Values
- `pending`: Task not started
- `in_progress`: Task in progress
- `completed`: Task completed
- `overdue`: Task past due date

### Priority Values
- `low`: Low priority
- `medium`: Medium priority (default)
- `high`: High priority

## Data Persistence

The application uses SQLite for data storage. The database file (`tasks.db`) is created automatically in the project directory on first run. All data persists between application restarts.

**Note:** The database file is excluded from version control (see `.gitignore`).

## Validation and Error Handling

The system includes comprehensive validation:

- Title cannot be empty or exceed 200 characters
- Description cannot exceed 2000 characters
- Status and priority must be from valid lists
- Dates must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- Proper error messages for invalid operations

## Assumptions Made

1. **Database**: SQLite was chosen for simplicity and zero-configuration setup. It's file-based and perfect for single-user or small-scale applications.

2. **No External Dependencies**: The project uses only Python standard library to minimize setup complexity and ensure portability.

3. **Date Format**: ISO 8601 format is used for dates (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS) for consistency and interoperability.

4. **Task IDs**: UUIDs are used for task identification to ensure uniqueness without requiring a centralized ID generator.

5. **Status Management**: "Mark as complete/incomplete" is implemented by updating the status field to `completed` or `pending` respectively.

6. **API Design**: RESTful principles are followed with appropriate HTTP methods (GET, POST, PUT, PATCH, DELETE).

7. **CORS**: CORS headers are enabled for API endpoints to allow cross-origin requests (useful for web frontends).

## Error Responses

The API returns appropriate HTTP status codes:

- `200 OK`: Successful operation
- `201 Created`: Task created successfully
- `400 Bad Request`: Validation error or invalid input
- `404 Not Found`: Task not found
- `500 Internal Server Error`: Server/database error

Error response format:
```json
{
  "message": "Error description"
}
```

## Testing

### Test API Endpoints

You can test the API using `curl` or any HTTP client:

```bash
# Start server
python main.py api

# In another terminal, test endpoints
curl http://localhost:8000/api/tasks
```

### Test CLI

```bash
# Create a task
python main.py cli create "Test Task" --priority high

# List tasks
python main.py cli list

# Get task by ID (use ID from list output)
python main.py cli get <task_id>

# Update task
python main.py cli update <task_id> --status completed

# Delete task
python main.py cli delete <task_id>
```

## Code Quality

- Follows PEP 8 style guidelines
- Type hints used where appropriate
- Comprehensive error handling
- Clear separation of concerns (models, storage, API, CLI)
- Context managers for database connections
- Proper transaction handling

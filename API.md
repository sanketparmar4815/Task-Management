# Task Management API Documentation

## Base URL

```
http://localhost:8000/api/tasks
```

## Authentication

No authentication is required for this API.

## Content Type

All requests and responses use `application/json` content type.

## CORS

CORS headers are enabled to allow cross-origin requests from web applications.

---

## Endpoints

### 1. List All Tasks

Retrieve all tasks with optional filtering by status and/or priority.

**Endpoint:** `GET /api/tasks`

**Query Parameters:**

| Parameter | Type | Required | Description | Valid Values |
|-----------|------|----------|-------------|--------------|
| `status` | string | No | Filter tasks by status | `pending`, `in_progress`, `completed`, `overdue` |
| `priority` | string | No | Filter tasks by priority | `low`, `medium`, `high` |

**Request Example:**

```bash
# Get all tasks
curl http://localhost:8000/api/tasks

# Filter by status
curl http://localhost:8000/api/tasks?status=pending

# Filter by priority
curl http://localhost:8000/api/tasks?priority=high

# Filter by both status and priority
curl http://localhost:8000/api/tasks?status=in_progress&priority=medium
```

**Response:**

**Status Code:** `200 OK`

```json
{
  "data": [
    {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project documentation",
      "description": "Write comprehensive README and API docs",
      "status": "pending",
      "priority": "high",
      "created_date": "2024-01-15T10:30:00",
      "due_date": "2024-12-31"
    },
    {
      "task_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Review code changes",
      "description": "Review pull requests and provide feedback",
      "status": "in_progress",
      "priority": "medium",
      "created_date": "2024-01-16T09:00:00",
      "due_date": null
    }
  ]
}
```

**Empty Result:**

```json
{
  "data": []
}
```

---

### 2. Get Task by ID

Retrieve a specific task by its unique identifier.

**Endpoint:** `GET /api/tasks/{task_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | Unique task identifier |

**Request Example:**

```bash
curl http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Response:**

**Status Code:** `200 OK`

```json
{
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project documentation",
    "description": "Write comprehensive README and API docs",
    "status": "pending",
    "priority": "high",
    "created_date": "2024-01-15T10:30:00",
    "due_date": "2024-12-31"
  }
}
```

**Error Response:**

**Status Code:** `404 Not Found`

```json
{
  "message": "Task not found"
}
```

---

### 3. Create Task

Create a new task in the system.

**Endpoint:** `POST /api/tasks`

**Request Body:**

| Field | Type | Required | Description | Constraints |
|-------|------|----------|-------------|-------------|
| `title` | string | Yes | Task title | Max 200 characters, cannot be empty |
| `description` | string | No | Task description | Max 2000 characters |
| `status` | string | No | Task status | Default: `pending`. Valid: `pending`, `in_progress`, `completed`, `overdue` |
| `priority` | string | No | Task priority | Default: `medium`. Valid: `low`, `medium`, `high` |
| `due_date` | string | No | Due date in ISO format | Format: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS` |

**Request Example:**

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement new feature",
    "description": "Add user authentication to the API",
    "status": "pending",
    "priority": "high",
    "due_date": "2024-12-31"
  }'
```

**Minimal Request (only title required):**

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Simple task"
  }'
```

**Response:**

**Status Code:** `201 Created`

```json
{
  "message": "Task created successfully",
  "data": {
    "task_id": "770e8400-e29b-41d4-a716-446655440002",
    "title": "Implement new feature",
    "description": "Add user authentication to the API",
    "status": "pending",
    "priority": "high",
    "created_date": "2024-01-17T14:20:00",
    "due_date": "2024-12-31"
  }
}
```

**Error Responses:**

**Status Code:** `400 Bad Request` (Validation Error)

```json
{
  "message": "Task title cannot be empty"
}
```

```json
{
  "message": "Status must be one of: pending, in_progress, completed, overdue"
}
```

```json
{
  "message": "Date must be in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
}
```

**Status Code:** `500 Internal Server Error`

```json
{
  "message": "Failed to create task: [error details]"
}
```

---

### 4. Update Task (Full Update)

Update all fields of an existing task. All fields must be provided.

**Endpoint:** `PUT /api/tasks/{task_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | Unique task identifier |

**Request Body:**

Same structure as Create Task, but all fields are optional (though at least one should be provided).

**Request Example:**

```bash
curl -X PUT http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated task title",
    "description": "Updated description",
    "status": "completed",
    "priority": "low",
    "due_date": "2024-12-31"
  }'
```

**Response:**

**Status Code:** `200 OK`

```json
{
  "message": "Task updated successfully",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Updated task title",
    "description": "Updated description",
    "status": "completed",
    "priority": "low",
    "created_date": "2024-01-15T10:30:00",
    "due_date": "2024-12-31"
  }
}
```

**Error Responses:**

**Status Code:** `404 Not Found`

```json
{
  "message": "Task not found"
}
```

**Status Code:** `400 Bad Request` (Validation Error)

```json
{
  "message": "Task title cannot exceed 200 characters"
}
```

---

### 5. Update Task (Partial Update)

Update specific fields of an existing task. Only provided fields will be updated.

**Endpoint:** `PATCH /api/tasks/{task_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | Unique task identifier |

**Request Body:**

Provide only the fields you want to update. All fields are optional.

**Request Examples:**

**Mark Task as Complete:**

```bash
curl -X PATCH http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

**Mark Task as Incomplete:**

```bash
curl -X PATCH http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "pending"
  }'
```

**Update Multiple Fields:**

```bash
curl -X PATCH http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "high",
    "description": "Updated description"
  }'
```

**Response:**

**Status Code:** `200 OK`

```json
{
  "message": "Task updated successfully",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project documentation",
    "description": "Updated description",
    "status": "in_progress",
    "priority": "high",
    "created_date": "2024-01-15T10:30:00",
    "due_date": "2024-12-31"
  }
}
```

**Error Responses:**

**Status Code:** `400 Bad Request`

```json
{
  "message": "Request body is required for PATCH"
}
```

```json
{
  "message": "No valid fields to update"
}
```

**Status Code:** `404 Not Found`

```json
{
  "message": "Task not found"
}
```

---

### 6. Delete Task

Delete a task from the system.

**Endpoint:** `DELETE /api/tasks/{task_id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | string (UUID) | Yes | Unique task identifier |

**Request Example:**

```bash
curl -X DELETE http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Response:**

**Status Code:** `200 OK`

```json
{
  "message": "Task deleted successfully"
}
```

**Error Response:**

**Status Code:** `404 Not Found`

```json
{
  "message": "Task not found"
}
```

---

## Data Models

### Task Object

```json
{
  "task_id": "string (UUID)",
  "title": "string (required, max 200 chars)",
  "description": "string (optional, max 2000 chars)",
  "status": "string (pending | in_progress | completed | overdue)",
  "priority": "string (low | medium | high)",
  "created_date": "string (ISO 8601 format)",
  "due_date": "string (ISO 8601 format, optional)"
}
```

### Field Descriptions

- **task_id**: Automatically generated UUID v4. Unique identifier for the task.
- **title**: Required field. Task title/name. Cannot be empty or exceed 200 characters.
- **description**: Optional field. Detailed description of the task. Maximum 2000 characters.
- **status**: Current status of the task. Default: `pending`.
  - `pending`: Task has not been started
  - `in_progress`: Task is currently being worked on
  - `completed`: Task has been finished
  - `overdue`: Task has passed its due date
- **priority**: Importance level of the task. Default: `medium`.
  - `low`: Low priority task
  - `medium`: Normal priority task
  - `high`: High priority task
- **created_date**: Automatically set timestamp when task is created. ISO 8601 format.
- **due_date**: Optional target completion date. ISO 8601 format (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`).

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| `200 OK` | Request successful |
| `201 Created` | Resource created successfully |
| `400 Bad Request` | Invalid request data or validation error |
| `404 Not Found` | Resource not found |
| `500 Internal Server Error` | Server or database error |

---

## Error Response Format

All error responses follow this format:

```json
{
  "message": "Error description"
}
```

---

## Date Format

All dates must be in ISO 8601 format:

- **Date only**: `YYYY-MM-DD` (e.g., `2024-12-31`)
- **Date and time**: `YYYY-MM-DDTHH:MM:SS` (e.g., `2024-12-31T23:59:59`)
- **With timezone**: `YYYY-MM-DDTHH:MM:SS+00:00` or `YYYY-MM-DDTHH:MM:SSZ`

Examples:
- `2024-12-31`
- `2024-12-31T23:59:59`
- `2024-12-31T23:59:59+00:00`
- `2024-12-31T23:59:59Z`

---

## Common Use Cases

### Create and Complete a Task

```bash
# 1. Create a task
TASK_ID=$(curl -s -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Finish API documentation",
    "priority": "high"
  }' | jq -r '.data.task_id')

# 2. Mark as complete
curl -X PATCH http://localhost:8000/api/tasks/$TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Filter and Update Tasks

```bash
# 1. Get all high priority pending tasks
curl http://localhost:8000/api/tasks?status=pending&priority=high

# 2. Update a specific task to in_progress
curl -X PATCH http://localhost:8000/api/tasks/{task_id} \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

### Bulk Operations (using shell script)

```bash
#!/bin/bash

# Create multiple tasks
for i in {1..5}; do
  curl -X POST http://localhost:8000/api/tasks \
    -H "Content-Type: application/json" \
    -d "{\"title\": \"Task $i\", \"priority\": \"medium\"}"
done

# List all tasks
curl http://localhost:8000/api/tasks
```

---

## Testing with Different Tools

### Using cURL

All examples above use `curl`. Make sure to:
- Include `Content-Type: application/json` header for POST/PUT/PATCH
- Use `-X` flag to specify HTTP method
- Use `-d` flag for request body

### Using HTTPie

```bash
# Install: pip install httpie

# GET request
http GET http://localhost:8000/api/tasks status==pending priority==high

# POST request
http POST http://localhost:8000/api/tasks \
  title="New Task" \
  description="Task description" \
  priority=high \
  status=pending

# PATCH request
http PATCH http://localhost:8000/api/tasks/{task_id} status=completed
```

### Using Postman

1. Set method (GET, POST, PUT, PATCH, DELETE)
2. Enter URL: `http://localhost:8000/api/tasks` or `http://localhost:8000/api/tasks/{task_id}`
3. For POST/PUT/PATCH:
   - Go to Headers tab
   - Add: `Content-Type: application/json`
   - Go to Body tab
   - Select "raw" and "JSON"
   - Enter JSON payload
4. Click Send

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000/api/tasks"

# Create task
response = requests.post(
    BASE_URL,
    json={
        "title": "Python task",
        "description": "Created via Python",
        "priority": "high"
    }
)
task = response.json()["data"]
task_id = task["task_id"]

# Get task
response = requests.get(f"{BASE_URL}/{task_id}")
print(response.json())

# Update task
response = requests.patch(
    f"{BASE_URL}/{task_id}",
    json={"status": "completed"}
)

# Delete task
response = requests.delete(f"{BASE_URL}/{task_id}")
```

### Using JavaScript (fetch)

```javascript
const BASE_URL = 'http://localhost:8000/api/tasks';

// Create task
fetch(BASE_URL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: 'JavaScript task',
    description: 'Created via JavaScript',
    priority: 'high'
  })
})
  .then(res => res.json())
  .then(data => {
    const taskId = data.data.task_id;

    // Get task
    return fetch(`${BASE_URL}/${taskId}`);
  })
  .then(res => res.json())
  .then(data => console.log(data));

// Update task
fetch(`${BASE_URL}/${taskId}`, {
  method: 'PATCH',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ status: 'completed' })
});

// Delete task
fetch(`${BASE_URL}/${taskId}`, { method: 'DELETE' });
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. All requests are processed immediately.

## Notes

- The API server must be running before making requests
- Start the server with: `python main.py api`
- The database (`tasks.db`) is created automatically on first use
- All timestamps are in UTC
- Task IDs are UUIDs and cannot be changed after creation
- The `created_date` field is automatically set and cannot be modified

---

## Support

For issues or questions, refer to the main [README.md](README.md) file.


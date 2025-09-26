# API Endpoints Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://your-backend-domain.render.com`

## Authentication
Currently, no authentication is required. All endpoints are publicly accessible.

## Endpoints

### Health Check

#### GET `/`
Check if the API is running.

**Response:**
```json
{
  "status": "ok",
  "message": "Scheduler Management API is running",
  "version": "1.0.0"
}
```

### Schedulers

#### GET `/schedulers`
Get all schedulers.

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Daily Report",
    "description": "Generate daily sales report",
    "job_type": "report_generation",
    "frequency": "cron",
    "frequency_config": {
      "cron_expression": "0 9 * * *",
      "timezone": "UTC"
    },
    "is_active": true,
    "created_at": "2023-01-01T00:00:00",
    "updated_at": "2023-01-01T00:00:00",
    "last_run": null,
    "next_run": "2023-01-02T09:00:00"
  }
]
```

#### POST `/schedulers`
Create a new scheduler.

**Request Body:**
```json
{
  "name": "Daily Report",
  "description": "Generate daily sales report",
  "job_type": "report_generation",
  "frequency": "cron",
  "frequency_config": {
    "cron_expression": "0 9 * * *",
    "timezone": "UTC"
  }
}
```

**Response:** Same as GET `/schedulers/{id}`

#### GET `/schedulers/{scheduler_id}`
Get a specific scheduler by ID.

**Response:** Same as scheduler object in GET `/schedulers`

#### PUT `/schedulers/{scheduler_id}`
Update a scheduler.

**Request Body:** Same as POST `/schedulers` but all fields are optional

**Response:** Updated scheduler object

#### POST `/schedulers/{scheduler_id}/pause`
Pause a scheduler.

**Response:**
```json
{
  "status": "paused",
  "scheduler_id": "uuid"
}
```

#### POST `/schedulers/{scheduler_id}/resume`
Resume a scheduler.

**Response:**
```json
{
  "status": "resumed",
  "scheduler_id": "uuid"
}
```

#### DELETE `/schedulers/{scheduler_id}`
Delete a scheduler.

**Response:**
```json
{
  "status": "deleted",
  "scheduler_id": "uuid"
}
```

### Logs

#### GET `/logs`
Get all execution logs.

**Query Parameters:**
- `limit` (optional): Number of logs to retrieve (default: 100)

**Response:**
```json
[
  {
    "id": "uuid",
    "scheduler_id": "uuid",
    "job_type": "report_generation",
    "status": "success",
    "message": "Job completed successfully",
    "started_at": "2023-01-01T09:00:00",
    "completed_at": "2023-01-01T09:01:30",
    "duration": 90
  }
]
```

#### GET `/schedulers/{scheduler_id}/logs`
Get execution logs for a specific scheduler.

**Query Parameters:**
- `limit` (optional): Number of logs to retrieve (default: 100)

**Response:** Same as GET `/logs`

### Statistics

#### GET `/stats`
Get execution statistics.

**Response:**
```json
{
  "total_schedulers": 5,
  "active_schedulers": 3,
  "paused_schedulers": 2,
  "total_executions": 150,
  "successful_executions": 142,
  "failed_executions": 8,
  "executions_by_job_type": {
    "email_notification": 50,
    "data_backup": 30,
    "report_generation": 70
  },
  "executions_by_date": {
    "2023-01-01": 25,
    "2023-01-02": 30,
    "2023-01-03": 28
  },
  "average_execution_duration": 45.2
}
```

## Data Models

### Job Types
- `email_notification`: Email Notification
- `data_backup`: Data Backup
- `report_generation`: Report Generation
- `api_call`: API Call
- `file_cleanup`: File Cleanup
- `custom`: Custom

### Frequency Types
- `cron`: Cron expression scheduling
- `interval`: Interval-based scheduling
- `date`: One-time scheduling

### Frequency Configurations

#### Cron Configuration
```json
{
  "cron_expression": "0 9 * * *",
  "timezone": "UTC"
}
```

#### Interval Configuration
```json
{
  "seconds": 30,
  "minutes": 5,
  "hours": 2,
  "days": 1
}
```
*At least one interval must be specified*

#### Date Configuration
```json
{
  "run_date": "2023-12-25T09:00:00"
}
```

### Log Status
- `success`: Job completed successfully
- `error`: Job failed with error
- `running`: Job is currently running

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 404 Not Found
```json
{
  "detail": "Scheduler not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Cron Expression Examples

- `0 9 * * *` - Every day at 9:00 AM
- `0 */2 * * *` - Every 2 hours
- `0 0 * * 1` - Every Monday at midnight
- `30 14 * * 1-5` - Every weekday at 2:30 PM
- `0 0 1 * *` - First day of every month at midnight

## Rate Limits

Currently, no rate limits are implemented. Consider implementing rate limiting for production use.

## Pagination

Currently, only the `limit` parameter is supported for logs. Future versions may include offset-based or cursor-based pagination.

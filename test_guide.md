# MCP Todo Server Testing Guide

This guide provides comprehensive instructions for testing the MCP Todo Server implementation.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install mcp
   ```

2. **Download all files:**
   - `mcp_todo_server.py` - Main server
   - `test_todo_mcp.py` - Unit tests  
   - `mcp_client_test.py` - Integration tests

3. **Run tests:**
   ```bash
   python test_todo_mcp.py          # Unit tests
   python mcp_client_test.py        # Integration tests
   ```

## Testing Methods

### 1. Unit Tests (Recommended First)

Run comprehensive unit tests that don't require the MCP server to be running:

```bash
python test_todo_mcp.py
```

**Tests included:**
- ✅ Task creation and validation
- ✅ Task sorting by due time
- ✅ Binary search efficiency
- ✅ CRUD operations
- ✅ CSV persistence
- ✅ Error handling
- ✅ Recurring task logic
- ✅ Time window queries

### 2. Integration Tests

Test the actual MCP server with a mock client:

```bash
python mcp_client_test.py
```

**Choose from:**
- **Comprehensive Tests** - Automated test suite
- **Interactive Tests** - Manual testing session
- **Setup Instructions** - View complete setup guide

### 3. Manual Testing

Quick manual verification:

```python
from test_todo_mcp import run_manual_tests
run_manual_tests()
```

### 4. Live Server Testing

Start the server and test with real MCP clients:

```bash
# Terminal 1: Start server
python mcp_todo_server.py

# Terminal 2: Use MCP client tools
# (Connect with your preferred MCP client)
```

## Test Scenarios

### Basic CRUD Operations

```python
# Create a task
{
    "name": "create_task",
    "arguments": {
        "summary": "Complete project documentation",
        "details": "Write comprehensive API and user documentation",
        "is_recurring": false,
        "recurrence_type": "one_off",
        "due_time": "2024-03-15T17:00:00"
    }
}

# List all tasks
{
    "name": "get_all_tasks",
    "arguments": {}
}

# Update a task
{
    "name": "update_task", 
    "arguments": {
        "task_id": "task_123",
        "summary": "Updated task summary",
        "due_time": "2024-03-15T18:00:00"
    }
}

# Delete a task
{
    "name": "delete_task",
    "arguments": {
        "task_id": "task_123"
    }
}
```

### Advanced Features

```python
# Recurring task
{
    "name": "create_task",
    "arguments": {
        "summary": "Daily standup meeting",
        "details": "Team synchronization meeting",
        "is_recurring": true,
        "recurrence_type": "daily",
        "recurrence_interval": 1,
        "due_time": "2024-03-15T09:00:00",
        "alert_times": ["2024-03-15T08:45:00"]
    }
}

# Time window query
{
    "name": "get_tasks_in_window",
    "arguments": {
        "start_time": "2024-03-15T00:00:00",
        "end_time": "2024-03-15T23:59:59"
    }
}

# Advance recurring task
{
    "name": "advance_recurring_task",
    "arguments": {
        "task_id": "task_recurring_123"
    }
}
```

## Expected Test Results

### Unit Tests Output
```
Running unit tests...
test_create_task_valid ... ok
test_create_task_invalid_summary ... ok
test_task_sorting ... ok
test_get_task_by_id ... ok
test_csv_persistence ... ok
...
Ran 12 tests in 0.145s
OK
```

### Integration Tests Output
```
🚀 Starting MCP Todo Server Test Suite
==================================================
✅ MCP server started successfully

📋 Test 1: Listing available tools
✅ Found 7 tools:
   - create_task: Create a new todo task
   - get_task: Get a task by ID
   - update_task: Update an existing task
   ...

📝 Test 2: Creating a one-off task
✅ One-off task created successfully

✅ All tests completed!
```

## Troubleshooting

### Common Issues

1. **"mcp module not found"**
   ```bash
   pip install mcp
   ```

2. **"mcp_todo_server.py not found"**
   - Ensure all files are in the same directory
   - Check file permissions

3. **CSV permission errors**
   - Ensure write permissions in project directory
   - Check if file is locked by another process

4. **Date format errors**
   - Use ISO format: `YYYY-MM-DDTHH:MM:SS`
   - Example: `2024-03-15T17:30:00`

5. **Server won't start**
   - Check Python version (3.8+)
   - Verify MCP installation
   - Check for port conflicts

### Performance Testing

Test with large datasets:

```python
# Create 1000 tasks and measure performance
import time
from datetime import datetime, timedelta

start_time = time.time()
for i in range(1000):
    todo_manager.create_task(
        summary=f"Task {i}",
        details=f"Details for task {i}",
        is_recurring=False,
        recurrence_type="one_off",
        recurrence_interval=1,
        due_time=datetime.now() + timedelta(hours=i)
    )
end_time = time.time()

print(f"Created 1000 tasks in {end_time - start_time:.2f} seconds")
```

## Test Coverage

The test suite covers:

- **Functionality**: All CRUD operations
- **Validation**: Input validation and error handling
- **Performance**: Binary search efficiency
- **Persistence**: CSV file operations
- **Edge Cases**: Empty inputs, past dates, invalid IDs
- **Integration**: MCP protocol compliance
- **Concurrency**: Multiple operations
- **Data Integrity**: Sorting maintenance

## Next Steps

After successful testing:

1. **Deploy the server** in your MCP environment
2. **Configure client applications** to use the server
3. **Monitor performance** with real workloads
4. **Set up backups** for the CSV data file
5. **Consider scaling** for production use

## Contributing

To add new tests:

1. Add unit tests to `test_todo_mcp.py`
2. Add integration tests to `mcp_client_test.py`
3. Update this README with new test scenarios
4. Ensure all tests pass before submitting changes

## Support

If you encounter issues:

1. Check the troubleshooting section
2. Review the test output for specific error messages
3. Verify all dependencies are installed
4. Ensure file permissions are correct







# Unit Tests (Test individual functions):
bashpython test_mcp_todo.py --unit
Manual Tests (Interactive testing with real data):
bashpython test_mcp_todo.py --manual
Performance Tests (Test with 1000+ tasks):
bashpython test_mcp_todo.py --performance
MCP Tools Tests (Test the MCP interface):
bashpython test_mcp_client.py
3. Example Usage
bashpython example_usage.py
4. Running the MCP Server
bash# Direct execution
python todo_mcp_server.py

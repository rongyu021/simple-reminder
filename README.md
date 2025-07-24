# Simple Reminder

Simple reminder app that allows users to simply chat to the app like a family member on the future tasks for which they'd like to receive a reminder, e.g. taking medicine on time

This personal project is still work in progress. It currently contains:
- A todo MCP server for todo list management.
- A simple LLM agent to chat with to manage todos. Currently it only support command line interface. 

## MCP Todo Server

A Model Context Protocol (MCP) server for managing to-do tasks with Claude Desktop. This server provides comprehensive task management capabilities including CRUD operations, recurring tasks, time-based filtering, and CSV persistence.

### Features

- **Task Management**: Create, read, update, and delete tasks
- **Recurring Tasks**: Support for daily, weekly, monthly, yearly, and custom interval recurrence
- **Time-based Filtering**: Get tasks within specific time windows
- **Sorted Storage**: Tasks are automatically sorted by due time for efficient retrieval
- **CSV Persistence**: Tasks are saved to a CSV file for data persistence
- **Alert System**: Support for multiple alert times per task
- **Efficient Search**: Binary search implementation for fast task retrieval


## Run the Agent

1. **Clone or download** this repository to your local machine

2. **Install required dependencies** (REQUIRED):
   ```bash
   pip install -r requirements.txt
   ```
3.  **Configure the settings**:
    
    Create a .env file from .env.sample and populate the settings based on your own environment such as LLM. 

4. **Run the agent**:
   ```bash
   python todo_agent.py
   ```
   If successful, you should see the agent start without errors. 


## Usage Examples

You can interact with your todo agent through natural language:

### Creating Tasks

```
"Create a task to buy groceries tomorrow at 3 PM with details about getting milk, bread, and eggs"

"Add a recurring daily task to take vitamins at 8 AM"

"Schedule a monthly task to pay rent on the 1st at 9 AM"
```

### Viewing Tasks

```
"Show me all my tasks"

"What tasks do I have this week?"

"List my upcoming tasks for the next 3 days"
```

### Updating Tasks

```
"Update the grocery task to be due at 4 PM instead"

"Change the details of my vitamin task"

"Make the rent payment task due at 10 AM"
```

### Deleting Tasks

```
"Delete the grocery task"

"Remove all completed tasks"

"Clear all my tasks"
```

## Unit-test the MCP server

Run test_todo_server.py to test the MCP server.

### Run unit testing

   ```bash
   python test_todo_server.py --unit
   ```
### Run manual testing

   ```bash
   python test_todo_server.py --manual
   ```
### Run performance testing

   ```bash
   python test_todo_server.py --performance
   ```   

## Test the MCP server in Claude Desktop

### Step 1: Configure Claude Desktop

1. **Locate your Claude Desktop configuration file**:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/claude/claude_desktop_config.json`

2. **Edit the configuration file** to add the MCP server:

```json
{
  "mcpServers": {
    "todo-server": {
      "command": "python",
      "args": ["/path/to/your/mcp_todo_server.py"],
      "env": {
        "TASKS_CSV_PATH": "/path/to/your/tasks.csv"
      }
    }
  }
}
```

**Important**: Replace `/path/to/your/mcp_todo_server.py` with the actual full path to where you saved the server file.

**Important**: Claude Desktop does not automatically install Python dependencies. You must install the required packages manually before configuring the server.

### Step 2: Restart Claude Desktop

After updating the configuration file, completely quit and restart Claude Desktop for the changes to take effect.

### Step 3: Verify Installation

In Claude Desktop, you should now be able to use todo-related commands. Try asking Claude to:
- "Create a new task"
- "Show me all my tasks"
- "What tasks do I have coming up?"


## Data Storage

- Tasks are stored in a `tasks.csv` file in the .data/ folder under the same directory as the server script
- The CSV file is automatically created when you add your first task
- All task data persists between sessions

## Available MCP Tools

The server provides these tools that Claude can use:

- `create_task`: Create a new task
- `update_task`: Update an existing task
- `delete_task`: Delete a specific task
- `get_task`: Get details of a specific task
- `get_all_tasks`: Get all tasks
- `get_tasks_in_timeframe`: Get tasks within a date range
- `list_upcoming_tasks`: Get tasks due in the next N days
- `delete_all_tasks`: Delete all tasks

## Troubleshooting

### Server Not Starting

1. **Check Python installation**: Ensure Python 3.8+ is installed
2. **Install missing dependencies**: Run `pip install mcp fastmcp` (this is the most common issue)
3. **Verify dependencies are installed**: Run `python -c "import mcp; import fastmcp"`
4. **Test server manually**: Run `python mcp_todo_server.py` to see actual error messages
5. **Check file path**: Ensure the path in the configuration is correct
6. **File permissions**: Make sure the script is readable

### Claude Desktop Not Recognizing Server

1. **Verify JSON syntax**: Ensure the configuration file is valid JSON
2. **Check file location**: Confirm you're editing the correct config file
3. **Restart completely**: Fully quit and restart Claude Desktop
4. **Check logs**: Look for error messages in Claude Desktop

### Tasks Not Persisting

1. **File permissions**: Ensure the script can write to its directory
2. **Disk space**: Check available disk space
3. **File locks**: Ensure no other process is accessing the CSV file

## Configuration File Examples

### Basic Configuration
```json
{
  "mcpServers": {
    "todo-server": {
      "command": "python",
      "args": ["/Users/username/mcp_todo_server.py"]
    }
  }
}
```

### With Virtual Environment
```json
{
  "mcpServers": {
    "todo-server": {
      "command": "/path/to/venv/bin/python",
      "args": ["/path/to/mcp_todo_server.py"]
      "env": {
        "TASKS_CSV_PATH": "/path/to/tasks.csv"
      }
    }
  }
}
```

### With Custom CSV Location
```json
{
  "mcpServers": {
    "todo-server": {
      "command": "python",
      "args": ["/path/to/mcp_todo_server.py"],
      "env": {
        "CSV_FILE": "/path/to/custom/tasks.csv"
      }
    }
  }
}
```

## Security Notes

- The server only operates on local files
- No network connections are made
- Task data is stored locally in CSV format
- Ensure proper file permissions on your task data

## Contributing

Feel free to submit issues or pull requests to improve the server functionality.

## License

This project is provided as-is for educational and personal use.
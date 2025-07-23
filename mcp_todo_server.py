#!/usr/bin/env python3
"""
MCP Server for To-Do Task List Management
Supports CRUD operations with efficient sorted task management and CSV persistence.
"""

import asyncio
import csv
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from bisect import bisect_left, insort
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Task data structure
@dataclass(kw_only=True)
class Task:
    task_id: str
    summary: str
    details: str
    is_recurring: bool
    recurrence_type: Optional[str] = None  # 'daily', 'weekly', 'monthly', 'yearly', 'days', 'weeks', 'months'
    recurrence_value: Optional[int] = None  # For 'days', 'weeks', 'months' - the number
    due_time: str  # ISO format datetime string
    alert_times: List[str]  # List of ISO format datetime strings
    created_at: str  # ISO format datetime string
    
    def __post_init__(self):
        if not self.alert_times:
            self.alert_times = [self.due_time]
    
    @property
    def due_datetime(self) -> datetime:
        return datetime.fromisoformat(self.due_time)
    
    @property
    def created_datetime(self) -> datetime:
        return datetime.fromisoformat(self.created_at)

class TaskManager:
    def __init__(self, csv_file: str = None):
        if csv_file is None:
            csv_path = os.environ.get('TASKS_CSV_PATH')
            if csv_path:
                self.csv_file = csv_path
            else:
                # Get the directory where the script is located
                script_dir = Path(__file__).parent
                self.csv_file = script_dir / "tasks.csv"
        else:
            self.csv_file = csv_file
        self.tasks: List[Task] = []
        self.load_from_csv()
        self.managed_timewindow = timedelta(days=5*365)  # Default to 5 years for task management
    
    def load_from_csv(self):
        """Load tasks from CSV file at initialization"""
        if not os.path.exists(self.csv_file):
            return
        
        #clean up the tasks list
        self.tasks = []

        try:
            with open(self.csv_file, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Parse alert_times from JSON string
                    alert_times = json.loads(row['alert_times']) if row['alert_times'] else []
                    
                    task = Task(
                        task_id=row['task_id'],
                        summary=row['summary'],
                        details=row['details'],
                        is_recurring=row['is_recurring'].lower() == 'true',
                        recurrence_type=row['recurrence_type'] if row['recurrence_type'] else None,
                        recurrence_value=int(row['recurrence_value']) if row['recurrence_value'] else None,
                        due_time=row['due_time'],
                        alert_times=alert_times,
                        created_at=row['created_at']
                    )
                    self.tasks.append(task)
            
            # Sort tasks by due time after loading
            self.tasks.sort(key=lambda t: t.due_datetime)
            
        except Exception as e:
            print(f"Error loading tasks from CSV: {e}")
    
    def save_to_csv(self):
        """Save tasks to CSV file"""
        try:
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as file:
                if not self.tasks:
                    # Write empty file with headers
                    writer = csv.writer(file)
                    writer.writerow(['task_id', 'summary', 'details', 'is_recurring', 
                                   'recurrence_type', 'recurrence_value', 'due_time', 
                                   'alert_times', 'created_at'])
                    return
                
                fieldnames = ['task_id', 'summary', 'details', 'is_recurring', 
                            'recurrence_type', 'recurrence_value', 'due_time', 
                            'alert_times', 'created_at']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for task in self.tasks:
                    row = asdict(task)
                    row['alert_times'] = json.dumps(row['alert_times'])
                    writer.writerow(row)
                    
        except Exception as e:
            print(f"Error saving tasks to CSV: {e}")
    
    def generate_task_id(self, due_time: datetime) -> str:
        """Generate a unique task ID with format {UUID}_{dueTimestamp}"""
        task_uuid = str(uuid.uuid4())
        timestamp = int(due_time.timestamp())
        return f"{task_uuid}_{timestamp}"
    
    def find_task_index(self, task_id: str) -> int:
        """Efficiently find task index using binary search on timestamp"""
        try:
            # Extract timestamp from task_id
            timestamp = int(task_id.split('_')[-1])
            target_datetime = datetime.fromtimestamp(timestamp)
            
            # Binary search for the position
            left, right = 0, len(self.tasks)-1
            while left < right:
                mid = (left + right) // 2
                if self.tasks[mid].due_datetime < target_datetime:
                    left = mid + 1
                else:
                    right = mid
            
            # Search forwards from left-1 to find exact match
            for i in range(max(0, left - 1), len(self.tasks)):
                if self.tasks[i].task_id == task_id:
                    return i
                if self.tasks[i].due_datetime > target_datetime:
                    # If we passed the target, stop searching
                    break
            
            return -1
        except (ValueError, IndexError):
            # Fallback to linear search if timestamp parsing fails
            for i, task in enumerate(self.tasks):
                if task.task_id == task_id:
                    return i
            return -1
    
    def insert_task_sorted(self, task: Task):
        """Insert task maintaining sorted order by due time"""
        # Use binary search to find insertion point
        insertion_point = bisect_left(self.tasks, task.due_datetime, key=lambda t: t.due_datetime)
        self.tasks.insert(insertion_point, task)
    
    def calculate_next_due_time(self, task: Task) -> datetime:
        """Calculate the next due time for a recurring task"""
        current_due = task.due_datetime
        
        if task.recurrence_type == 'daily':
            return current_due + timedelta(days=1)
        elif task.recurrence_type == 'weekly':
            return current_due + timedelta(weeks=1)
        elif task.recurrence_type == 'monthly':
            # Add one month (approximate)
            if current_due.month == 12:
                return current_due.replace(year=current_due.year + 1, month=1)
            else:
                return current_due.replace(month=current_due.month + 1)
        elif task.recurrence_type == 'yearly':
            return current_due.replace(year=current_due.year + 1)
        elif task.recurrence_type == 'days' and task.recurrence_value:
            return current_due + timedelta(days=task.recurrence_value)
        elif task.recurrence_type == 'weeks' and task.recurrence_value:
            return current_due + timedelta(weeks=task.recurrence_value)
        elif task.recurrence_type == 'months' and task.recurrence_value:
            # Add specified number of months
            months_to_add = task.recurrence_value
            year = current_due.year
            month = current_due.month
            
            month += months_to_add
            while month > 12:
                year += 1
                month -= 12
            
            return current_due.replace(year=year, month=month)
        
        return current_due
    
    def create_task(self, summary: str, details: str, is_recurring: bool,
                   recurrence_type: Optional[str], recurrence_value: Optional[int],
                   due_time: str, alert_times: Optional[List[str]] = None) -> Task:
        """Create a new task"""
        # Validate inputs
        if not summary.strip():
            raise ValueError("Task summary cannot be empty")
        if not details.strip():
            raise ValueError("Task details cannot be empty")
        
        # Parse and validate due time
        try:
            due_datetime = datetime.fromisoformat(due_time)
        except ValueError:
            raise ValueError("Invalid due time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        if due_datetime <= datetime.now():
            raise ValueError("Due time must be in the future")
        
        # Validate recurrence settings
        if is_recurring:
            if not recurrence_type:
                raise ValueError("Recurrence type is required for recurring tasks")
            #lowercase the recurrence type for consistency
            recurrence_type = recurrence_type.lower()
            if recurrence_type not in ['daily', 'weekly', 'monthly', 'yearly', 'days', 'weeks', 'months']:
                raise ValueError(f"Invalid recurrence type: {recurrence_type}")
            if recurrence_type in ['days', 'weeks', 'months'] and not recurrence_value:
                raise ValueError(f"Recurrence value is required for {recurrence_type}")
        
        # Create task
        created_at = datetime.now()
        task_id = self.generate_task_id(due_datetime)
        
        task = Task(
            task_id=task_id,
            summary=summary.strip(),
            details=details.strip(),
            is_recurring=is_recurring,
            recurrence_type=recurrence_type,
            recurrence_value=recurrence_value,
            due_time=due_time,
            alert_times=alert_times or [due_time],
            created_at=created_at.isoformat()
        )
        
        # Insert maintaining sorted order
        self.insert_task_sorted(task)
        self.save_to_csv() 
        
        #calculate next due time if recurring
        if is_recurring:
            next_due_time = self.calculate_next_due_time(task)
            while next_due_time <= datetime.now() + self.managed_timewindow:
                #create a new task for the next recurrence
                task2 = Task(
                    task_id=self.generate_task_id(next_due_time),
                    summary=task.summary,
                    details=task.details,
                    is_recurring=True,
                    recurrence_type=task.recurrence_type,
                    recurrence_value=task.recurrence_value,
                    due_time=next_due_time.isoformat(),
                    alert_times=[next_due_time.isoformat()],
                    created_at=datetime.now().isoformat()
                )
                # Insert in sorted order
                self.insert_task_sorted(task2)
                next_due_time = self.calculate_next_due_time(task2)
            self.save_to_csv()
              
        return task
        
    def update_task(self, task_id: str, **kwargs) -> Task:
        """Update an existing task"""
        index = self.find_task_index(task_id)
        if index == -1:
            raise ValueError(f"Task with ID {task_id} not found")
        
        task = self.tasks[index]
        
        # Update fields
        if 'summary' in kwargs:
            if not kwargs['summary'].strip():
                raise ValueError("Task summary cannot be empty")
            task.summary = kwargs['summary'].strip()
        
        if 'details' in kwargs:
            if not kwargs['details'].strip():
                raise ValueError("Task details cannot be empty")
            task.details = kwargs['details'].strip()
        
        if 'is_recurring' in kwargs:
            task.is_recurring = kwargs['is_recurring']
        
        if 'recurrence_type' in kwargs:
            task.recurrence_type = kwargs['recurrence_type']
        
        if 'recurrence_value' in kwargs:
            task.recurrence_value = kwargs['recurrence_value']
        
        if 'due_time' in kwargs:
            try:
                due_datetime = datetime.fromisoformat(kwargs['due_time'])
                if due_datetime <= datetime.now():
                    raise ValueError("Due time must be in the future")
                
                # Remove task from current position
                self.tasks.pop(index)
                task.due_time = kwargs['due_time']
                # Re-insert in sorted order
                self.insert_task_sorted(task)
            except ValueError as e:
                raise ValueError(f"Invalid due time: {e}")
        
        if 'alert_times' in kwargs:
            task.alert_times = kwargs['alert_times']
        
        self.save_to_csv()
        return task
    
    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        index = self.find_task_index(task_id)
        if index == -1:
            return False
        
        self.tasks.pop(index)
        self.save_to_csv()
        return True
    
    def get_tasks_in_timeframe(self, start_time: str, end_time: str) -> List[Task]:
        """Get tasks within a time window"""
        try:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.fromisoformat(end_time)
        except ValueError:
            raise ValueError("Invalid time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        if start_dt > end_dt:
            raise ValueError("Start time must be before end time")
        
        # Binary search for start and end positions
        start_idx = bisect_left(self.tasks, start_dt, key=lambda t: t.due_datetime)
        end_idx = bisect_left(self.tasks, end_dt, key=lambda t: t.due_datetime)
        
        # Include tasks at end_dt
        while end_idx < len(self.tasks) and self.tasks[end_idx].due_datetime <= end_dt:
            end_idx += 1
        
        return self.tasks[start_idx:end_idx]
    
    def get_all_tasks(self) -> List[Task]:
        """Get all tasks"""
        return self.tasks.copy()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a specific task by ID"""
        index = self.find_task_index(task_id)
        return self.tasks[index] if index != -1 else None

    def delete_all_tasks(self) -> bool:
        """Delete all tasks"""
        if not self.tasks:
            return False
        
        self.tasks.clear()
        self.save_to_csv()
        return True

# Initialize FastMCP server
mcp = FastMCP("Todo Task Manager")
task_manager = TaskManager()

@mcp.tool()
def create_task(
    summary: str,
    details: str,
    is_recurring: bool,
    due_time: str,
    recurrence_type: Optional[str] = None,
    recurrence_value: Optional[int] = None,
    alert_times: Optional[List[str]] = None
) -> str:
    """
    Create a new task
    
    Args:
        summary: One sentence summary of the task (required)
        details: Detailed description of the task (required)
        is_recurring: Whether this is a recurring task
        due_time: Due time in ISO format (YYYY-MM-DDTHH:MM:SS)
        recurrence_type: Type of recurrence ('daily', 'weekly', 'monthly', 'yearly', 'days', 'weeks', 'months')
        recurrence_value: Number for 'days', 'weeks', 'months' recurrence types
        alert_times: List of alert times in ISO format (defaults to due time)
    
    Returns:
        Dictionary representation of the created task
    """
    try:
        task = task_manager.create_task(
            summary=summary,
            details=details,
            is_recurring=is_recurring,
            recurrence_type=recurrence_type,
            recurrence_value=recurrence_value,
            due_time=due_time,
            alert_times=alert_times
        )
        # return asdict(task)
        # return a string with task details
        return f"Task created successfully: {task.summary} (ID: {task.task_id}, Due: {task.due_time})"
    except Exception as e:
        return f"error: {str(e)}"

@mcp.tool()
def update_task(
    task_id: str, 
    summary: Optional[str] = None,
    details: Optional [str] = None,
    is_recurring: Optional[bool] = None,
    recurrence_type: Optional[str] = None,
    recurrence_value: Optional[int] = None,
    due_time: Optional[str] = None,
    alert_times: Optional[List[str]] = None
    ) -> Dict[str, Any]:
    """
    Update an existing task
    
    Args:
        task_id: ID of the task to update
        **kwargs: Fields to update (summary, details, is_recurring, recurrence_type, recurrence_value, due_time, alert_times)
    
    Returns:
        Dictionary representation of the updated task
    """
    try:
        # populate kwargs with the provided parameters
        kwargs = {k: v for k, v in locals().items() if v is not None and k != 'task_id'}
        if not kwargs:
            return {"Skipped": "No fields to update. Provide at least one field to update."}
        task = task_manager.update_task(task_id, **kwargs)
        return asdict(task)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_task(task_id: str) -> Dict[str, Any]:
    """
    Delete a task
    
    Args:
        task_id: ID of the task to delete
    
    Returns:
        Success status
    """
    try:
        success = task_manager.delete_task(task_id)
        return {"success": success, "message": "Task deleted successfully" if success else "Task not found"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_tasks_in_timeframe(start_time: str, end_time: str) -> Dict[str, Any]:
    """
    Get tasks within a time window
    
    Args:
        start_time: Start time in ISO format (YYYY-MM-DDTHH:MM:SS)
        end_time: End time in ISO format (YYYY-MM-DDTHH:MM:SS)
    
    Returns:
        List of tasks within the time window
    """
    try:
        tasks = task_manager.get_tasks_in_timeframe(start_time, end_time)
        return {"tasks": [asdict(task) for task in tasks]}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_all_tasks() -> Dict[str, Any]:
    """
    Get all tasks sorted by due time
    
    Returns:
        List of all tasks
    """
    try:
        tasks = task_manager.get_all_tasks()
        return {"tasks": [asdict(task) for task in tasks]}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_task(task_id: str) -> Dict[str, Any]:
    """
    Get a specific task by ID
    
    Args:
        task_id: ID of the task to retrieve
    
    Returns:
        Task details or error message
    """
    try:
        task = task_manager.get_task(task_id)
        if task:
            return asdict(task)
        else:
            return {"error": "Task not found"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def list_upcoming_tasks(days_ahead: int = 7) -> Dict[str, Any]:
    """
    Get tasks due within the next specified number of days
    
    Args:
        days_ahead: Number of days to look ahead (default: 7)
    
    Returns:
        List of upcoming tasks
    """
    try:
        now = datetime.now()
        future_time = now + timedelta(days=days_ahead)
        
        tasks = task_manager.get_tasks_in_timeframe(
            now.isoformat(),
            future_time.isoformat()
        )
        return {"tasks": [asdict(task) for task in tasks]}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def GetCurrentTime() -> str:
    """
    Get the current time in ISO format
    
    Returns:
        The current time in ISO format (YYYY-MM-DDTHH:MM:SS)
    """
    try:
        now = datetime.now()
        return f"current time: {now.isoformat()}"
    except Exception as e:
        return f"error: {str(e)}"

@mcp.tool()
def delete_all_tasks() -> Dict[str, Any]:
    """
    Delete all tasks
    
    Returns:
        Success status
    """
    try:
        success = task_manager.delete_all_tasks()
        return {"success": success, "message": "All tasks deleted successfully" if success else "No tasks to delete"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

#!/usr/bin/env python3
"""
Test Suite for MCP Todo Task Manager Server
Includes unit tests, integration tests, and manual testing examples
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch
import sys

# Add the current directory to Python path to import our server
sys.path.insert(0, '.')

# Import the classes from our server
from mcp_todo_server import TaskManager, Task

class TestTaskManager(unittest.TestCase):
    """Unit tests for TaskManager class"""
    
    def setUp(self):
        """Set up test fixtures before each test method"""
        # Create a temporary CSV file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        self.temp_file.close()
        self.task_manager = TaskManager(csv_file=self.temp_file.name)
    
    def tearDown(self):
        """Clean up after each test method"""
        # Remove the temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_create_task_basic(self):
        """Test creating a basic one-off task"""
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        task = self.task_manager.create_task(
            summary="Test task",
            details="This is a test task",
            is_recurring=False,
            recurrence_type=None,
            recurrence_value=None,
            due_time=future_time
        )
        # print(task)
        self.assertEqual(task.summary, "Test task")
        self.assertEqual(task.details, "This is a test task")
        self.assertFalse(task.is_recurring)
        self.assertEqual(len(self.task_manager.tasks), 1)
        self.assertEqual(task.alert_times, [future_time])
    
    def test_create_recurring_task(self):
        """Test creating a recurring task"""
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        task = self.task_manager.create_task(
            summary="Weekly meeting",
            details="Team standup meeting",
            is_recurring=True,
            recurrence_type="weekly",
            recurrence_value=None,
            due_time=future_time
        )
        
        self.assertTrue(task.is_recurring)
        self.assertEqual(task.recurrence_type, "weekly")
    
    def test_create_task_validation(self):
        """Test task creation validation"""
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        # Test empty summary
        with self.assertRaises(ValueError) as context:
            self.task_manager.create_task(
                summary="",
                details="Test details",
                is_recurring=False,
                recurrence_type=None,
                recurrence_value=None,
                due_time=future_time
            )
        self.assertIn("summary cannot be empty", str(context.exception))
        
        # Test empty details
        with self.assertRaises(ValueError) as context:
            self.task_manager.create_task(
                summary="Test summary",
                details="",
                is_recurring=False,
                recurrence_type=None,
                recurrence_value=None,
                due_time=future_time
            )
        self.assertIn("details cannot be empty", str(context.exception))
        
        # Test past due time
        past_time = (datetime.now() - timedelta(days=1)).isoformat()
        with self.assertRaises(ValueError) as context:
            self.task_manager.create_task(
                summary="Test summary",
                details="Test details",
                is_recurring=False,
                recurrence_type=None,
                recurrence_value=None,
                due_time=past_time
            )
        self.assertIn("must be in the future", str(context.exception))
    
    def test_task_sorting(self):
        """Test that tasks are sorted by due time"""
        now = datetime.now()
        
        # Create tasks with different due times
        task1 = self.task_manager.create_task(
            summary="Task 1", details="First task", is_recurring=False,
            recurrence_type=None, recurrence_value=None,
            due_time=(now + timedelta(days=3)).isoformat()
        )
        
        task2 = self.task_manager.create_task(
            summary="Task 2", details="Second task", is_recurring=False,
            recurrence_type=None, recurrence_value=None,
            due_time=(now + timedelta(days=1)).isoformat()
        )
        
        task3 = self.task_manager.create_task(
            summary="Task 3", details="Third task", is_recurring=False,
            recurrence_type=None, recurrence_value=None,
            due_time=(now + timedelta(days=2)).isoformat()
        )
        
        # Check that tasks are sorted by due time
        self.assertEqual(self.task_manager.tasks[0].task_id, task2.task_id)
        self.assertEqual(self.task_manager.tasks[1].task_id, task3.task_id)
        self.assertEqual(self.task_manager.tasks[2].task_id, task1.task_id)
    
    def test_find_task_by_id(self):
        """Test finding tasks by ID"""
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        task = self.task_manager.create_task(
            summary="Test task", details="Test details", is_recurring=False,
            recurrence_type=None, recurrence_value=None, due_time=future_time
        )
        
        # Test finding existing task
        found_task = self.task_manager.get_task(task.task_id)
        self.assertIsNotNone(found_task)
        self.assertEqual(found_task.task_id, task.task_id)
        
        # Test finding non-existent task
        not_found = self.task_manager.get_task("nonexistent_id")
        self.assertIsNone(not_found)
    
    def test_update_task(self):
        """Test updating a task"""
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        task = self.task_manager.create_task(
            summary="Original task", details="Original details", is_recurring=False,
            recurrence_type=None, recurrence_value=None, due_time=future_time
        )
        
        # Update the task
        updated_task = self.task_manager.update_task(
            task.task_id,
            summary="Updated task",
            details="Updated details"
        )
        
        self.assertEqual(updated_task.summary, "Updated task")
        self.assertEqual(updated_task.details, "Updated details")
        self.assertEqual(updated_task.task_id, task.task_id)
    
    def test_delete_task(self):
        """Test deleting a task"""
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        task = self.task_manager.create_task(
            summary="To be deleted", details="This task will be deleted",
            is_recurring=False, recurrence_type=None, recurrence_value=None,
            due_time=future_time
        )
        
        # Verify task exists
        self.assertEqual(len(self.task_manager.tasks), 1)
        
        # Delete the task
        result = self.task_manager.delete_task(task.task_id)
        self.assertTrue(result)
        self.assertEqual(len(self.task_manager.tasks), 0)
        
        # Try to delete non-existent task
        result = self.task_manager.delete_task("nonexistent_id")
        self.assertFalse(result)
    
    def test_get_tasks_in_timeframe(self):
        """Test getting tasks within a time window"""
        now = datetime.now()
        
        # Create tasks with different due times
        task1 = self.task_manager.create_task(
            summary="Task 1", details="First task", is_recurring=False,
            recurrence_type=None, recurrence_value=None,
            due_time=(now + timedelta(days=1)).isoformat()
        )
        
        task2 = self.task_manager.create_task(
            summary="Task 2", details="Second task", is_recurring=False,
            recurrence_type=None, recurrence_value=None,
            due_time=(now + timedelta(days=5)).isoformat()
        )
        
        task3 = self.task_manager.create_task(
            summary="Task 3", details="Third task", is_recurring=False,
            recurrence_type=None, recurrence_value=None,
            due_time=(now + timedelta(days=10)).isoformat()
        )
        
        # Get tasks in a specific timeframe
        start_time = now.isoformat()
        end_time = (now + timedelta(days=6)).isoformat()
        
        tasks_in_range = self.task_manager.get_tasks_in_timeframe(start_time, end_time)
        
        self.assertEqual(len(tasks_in_range), 2)
        self.assertIn(task1, tasks_in_range)
        self.assertIn(task2, tasks_in_range)
        self.assertNotIn(task3, tasks_in_range)
    
    def test_csv_persistence(self):
        """Test saving and loading from CSV"""
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        # Create a task
        task = self.task_manager.create_task(
            summary="Persistent task", details="This should persist",
            is_recurring=True, recurrence_type="weekly", recurrence_value=None,
            due_time=future_time, alert_times=[future_time]
        )

        # Create a new task manager instance with the same CSV file
        new_task_manager = TaskManager(csv_file=self.temp_file.name)
        
        # Check that the task was loaded
        self.assertGreater(len(new_task_manager.tasks), 10)
        loaded_task = new_task_manager.tasks[0]
        self.assertEqual(loaded_task.summary, task.summary)
        self.assertEqual(loaded_task.details, task.details)
        self.assertEqual(loaded_task.is_recurring, task.is_recurring)
        self.assertEqual(loaded_task.recurrence_type, task.recurrence_type)

class TestMCPTools(unittest.TestCase):
    """Integration tests for MCP tools"""

    def setUp(self):
        """Set up test fixtures"""

    
    def tearDown(self):
        """Clean up after tests"""
        from mcp_todo_server import delete_all_tasks
        delete_all_tasks()  # Clear all tasks after each test
    
    def test_create_task_tool(self):
        """Test the create_task MCP tool"""
        from mcp_todo_server import create_task
        
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        result = create_task(
            summary="MCP Test Task",
            details="Testing MCP tool functionality",
            is_recurring=False,
            due_time=future_time
        )
        #print(result)
        self.assertNotIn("error", result)
        # check if the result contains the task summary, task ID, and due time
        self.assertIn("MCP Test Task", result)
        self.assertIn(future_time, result)
    
    def test_get_all_tasks_tool(self):
        """Test the get_all_tasks MCP tool"""
        from mcp_todo_server import get_all_tasks, create_task
        
        future_time = (datetime.now() + timedelta(days=1)).isoformat()
        
        # Create a task first
        create_task(
            summary="Test Task",
            details="Test Details",
            is_recurring=False,
            due_time=future_time
        )
        
        # Get all tasks
        result = get_all_tasks()
        
        self.assertNotIn("error", result)
        self.assertIn("tasks", result)
        self.assertEqual(len(result["tasks"]), 1)
        self.assertEqual(result["tasks"][0]["summary"], "Test Task")


def run_manual_tests():
    """Manual testing functions for interactive testing"""
    
    print("=== Manual Testing of MCP Todo Server ===\n")
    
    # Create a test task manager
    test_manager = TaskManager("test_manual.csv")
    
    try:
        # Test 1: Create tasks
        print("1. Creating tasks...")
        now = datetime.now()
        
        task1 = test_manager.create_task(
            summary="Buy groceries",
            details="Buy milk, bread, eggs, and vegetables from the supermarket",
            is_recurring=False,
            recurrence_type=None,
            recurrence_value=None,
            due_time=(now + timedelta(days=1)).isoformat()
        )
        print(f"   Created task: {task1.task_id}")
        
        task2 = test_manager.create_task(
            summary="Monthly team meeting",
            details="Attend the monthly team meeting on 1st of the month at 10 AM",
            is_recurring=False,
            recurrence_type="monthly",
            recurrence_value=None,
            due_time=(now + timedelta(days=2)).isoformat()
        )
        print(f"   Created recurring task: {task2.task_id}")
        
        for i in range(3):
            task3 = test_manager.create_task(
                summary=f"Task {i+3}",
                details=f"Details for task {i+1}",
                is_recurring=False,
                recurrence_type=None,
                recurrence_value=None,
                due_time=(now + timedelta(days=i+3)).isoformat()
            )
 
        # Test 2: List all tasks
        print("\n2. Listing all tasks...")
        all_tasks = test_manager.get_all_tasks()
        for task in all_tasks:
            print(f"   - {task.summary} (Due: {task.due_time}, ID: {task.task_id})")
        
        # Test 3: Update a task
        print("\n3. Updating a task...")
        updated_task = test_manager.update_task(
            task1.task_id,
            summary="Buy groceries and household items",
            details="Buy milk, bread, eggs, vegetables, and cleaning supplies"
        )
        print(f"   Updated task: {updated_task.summary}")
        
        # Test 4: Get tasks in timeframe
        print("\n4. Getting tasks in next 3 days...")
        start_time = now.isoformat()
        end_time = (now + timedelta(days=3)).isoformat()
        tasks_in_range = test_manager.get_tasks_in_timeframe(start_time, end_time)
        print(f"   Found {len(tasks_in_range)} tasks in range")
        
        # Test 5: Delete a task
        print("\n5. Deleting a task...")
        delete_result = test_manager.delete_task(task1.task_id)
        print(f"   Delete result: {delete_result}")
        
        print("\n6. Final task count:", len(test_manager.get_all_tasks()))
        
        print("\n=== Manual tests completed successfully! ===")
        
    except Exception as e:
        print(f"Manual test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test file
        if os.path.exists("test_manual.csv"):
            os.unlink("test_manual.csv")


def run_performance_tests():
    """Performance tests for large numbers of tasks"""
    
    print("=== Performance Testing ===\n")
    
    test_manager = TaskManager("test_performance.csv")
    
    try:
        import time
        
        # Create many tasks
        print("Creating 1000 tasks...")
        start_time = time.time()
        
        now = datetime.now()
        for i in range(1000):
            test_manager.create_task(
                summary=f"Task {i}",
                details=f"Details for task {i}",
                is_recurring=False,
                recurrence_type=None,
                recurrence_value=None,
                due_time=(now + timedelta(days=i % 30+1)).isoformat()
            )
        
        create_time = time.time() - start_time
        print(f"Created 1000 tasks in {create_time:.2f} seconds")
        
        # Test search performance
        print("Testing search performance...")
        start_time = time.time()
        
        # Search for tasks in different time windows
        for i in range(100):
            start_window = (now + timedelta(days=i % 10)).isoformat()
            end_window = (now + timedelta(days=(i % 10) + 5)).isoformat()
            tasks = test_manager.get_tasks_in_timeframe(start_window, end_window)
        
        search_time = time.time() - start_time
        print(f"Performed 100 searches in {search_time:.2f} seconds")
        
        print(f"Average search time: {search_time/100*1000:.2f} ms")
        
    except Exception as e:
        print(f"Performance test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if os.path.exists("test_performance.csv"):
            os.unlink("test_performance.csv")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the MCP Todo Server")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--manual", action="store_true", help="Run manual tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if args.all or args.unit or (not args.manual and not args.performance):
        print("Running unit tests...")
        unittest.main(argv=[''], exit=False, verbosity=2)
    
    if args.all or args.manual:
        run_manual_tests()
    
    if args.all or args.performance:
        run_performance_tests()

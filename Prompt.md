### Prompt: write python code for to-do list management

Please write a MCP server in python for to-do task list management:
-  It should supports CRUD operation: create a new task, update a task, delete a task, get a list of tasks in a time window.
- Every to-do task should have the following properties
    - task id. The format is {UUID}_{dueTimestamp}.
    - task summary. It's one sentence. It can't be empty.
    - task details. It can be multiple sentences. It can't be emtpy
    - Is it an one off task or a recurring one?
    - If a recurring task, how often it recurs (daily, weekly, monthly,yearly, number of days, number of weeks, number of months).
    - task due time. This can't be empty. For a new task being created, the due time must be a time in the future.
    - A series of times to alert user ahead of the due time. Default is to alert user at the due time.
- Store tasks in a list. Always sort tasks based on the due time, from the earlist to the last. Please make locating a task very efficient since the list is already sorted by the timestamp. For example you should not re-sort the whole list when adding a new task. 
- To get a task from the list, use the timestamp in the task ID to help quickly locate the task in the list.
- The to-do list should be saved to a local .CSV file. At the initialization, the code should read the list from the file. When there is a write operation such as creating a new task or updating a task or deleting a task the code should save the change to the file.  
- Use FastMCP




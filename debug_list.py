import sys
sys.path.insert(0, '.')

from core.task_submitter import list_tasks

print("Testing list_tasks with status='pending', limit=10")
tasks = list_tasks(status='pending', limit=10)
print(f"Returned {len(tasks)} tasks")

for i, task in enumerate(tasks, 1):
    print(f"\n{i}. {task['id']}")
    print(f"   Type: {task['type']}")
    print(f"   Priority: {task['priority']}")
    print(f"   Status: {task['status']}")
    print(f"   Description: {task['description']}")

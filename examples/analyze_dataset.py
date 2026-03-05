"""
Example: Analyze a dataset using AIOS task queue.

Usage:
    python examples/analyze_dataset.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.task_submitter import submit_task, get_task

# Submit an analysis task
task_id = submit_task(
    description="Analyze system logs for error patterns",
    task_type="analysis",
    priority="high",
)

print(f"Task submitted: {task_id}")

# Check task status
task = get_task(task_id)
if task:
    print(f"Status: {task.get('status', 'pending')}")
    print(f"Type:   {task.get('type', 'unknown')}")
    print(f"Priority: {task.get('priority', 'normal')}")

"""
Example: Submit a code generation task to AIOS.

Usage:
    python examples/code_generation.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.task_submitter import submit_task

# Submit a code task
task_id = submit_task(
    description="Generate a Python sorting algorithm with benchmarks",
    task_type="code",
    priority="normal",
)

print(f"Code task submitted: {task_id}")
print("Heartbeat v5.0 will pick it up automatically.")

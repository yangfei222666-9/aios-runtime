"""
AIOS System Call Interface

The single entry point for agents to access kernel services.
Agents create an AgentContext and use it for all operations.

This is the "API boundary" between kernel and SDK:
- Kernel internals (EventBus, Scheduler, Queues) are hidden
- Agents get a clean, safe interface

Usage:
    from aios.syscall import AgentContext

    ctx = AgentContext("coder-001")

    # Planning (LLM)
    answer = ctx.plan.query("How should I fix this bug?")
    plan = ctx.plan.plan("Refactor the scheduler")

    # Actions (tools)
    result = ctx.act.shell("python -m pytest tests/")
    ctx.act.register_tool("lint", my_lint_fn)
    result = ctx.act.tool("lint", file="main.py")

    # Memory
    ctx.mem.set("current_file", "scheduler.py")
    ctx.mem.add_message("user", "Fix the timeout issue")
    context = ctx.mem.get_context(max_tokens=2000)
    ctx.mem.remember("lesson", "Always validate inputs")

    # Storage
    ctx.store.put("config", {"timeout": 30})
    ctx.store.append_log("tasks", {"action": "fix_bug", "status": "done"})

    # Events
    ctx.emit("agent.task_completed", task="fix_bug", duration_ms=5000)

    # Stats
    print(ctx.stats())
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional

import sys
from pathlib import Path

AIOS_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(AIOS_ROOT))

from sdk.planning import PlanningModule
from sdk.action import ActionModule
from sdk.memory import MemoryModule
from sdk.storage import StorageModule
from core.event import create_event
from core.event_bus import get_event_bus, EventBus


class AgentContext:
    """
    System call interface for a single agent.

    Bundles all four SDK modules + kernel event access
    into one object. Each agent gets its own context.
    """

    def __init__(
        self,
        agent_id: str,
        bus: Optional[EventBus] = None,
        storage_dir: Optional[Path] = None,
        default_priority: str = "normal",
    ):
        self.agent_id = agent_id
        self._bus = bus or get_event_bus()
        self._created_at = time.monotonic()

        # SDK modules
        self.plan = PlanningModule(agent_id=agent_id, default_priority=default_priority)
        self.act = ActionModule(agent_id=agent_id)
        self.mem = MemoryModule(agent_id=agent_id, storage_dir=storage_dir)
        self.store = StorageModule(agent_id=agent_id, base_dir=storage_dir)

    # ------------------------------------------------------------------
    # Event emission (kernel access)
    # ------------------------------------------------------------------

    def emit(self, event_type: str, **payload) -> None:
        """Emit an event to the kernel EventBus."""
        try:
            self._bus.emit(create_event(
                event_type,
                source=f"agent.{self.agent_id}",
                agent_id=self.agent_id,
                **payload,
            ))
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Convenience: combined operations
    # ------------------------------------------------------------------

    def execute_with_plan(
        self,
        task: str,
        priority: str = "normal",
    ) -> Dict[str, Any]:
        """
        Plan a task, then execute each step.

        Returns:
            {
                "plan": {...},
                "results": [ActionResult, ...],
                "success": bool,
                "total_ms": int
            }
        """
        start = time.monotonic()

        # Plan
        plan = self.plan.plan(task)
        steps = plan.get("steps", [])

        # Execute each step
        results = []
        all_success = True
        for step in steps:
            action = step.get("action", "")
            self.mem.add_message("system", f"Executing step: {action}")

            # Simple heuristic: if it looks like a command, run it
            if action.startswith("$") or action.startswith("python"):
                cmd = action.lstrip("$ ")
                result = self.act.shell(cmd, timeout=60)
            else:
                # Store as a note
                result = type("R", (), {
                    "success": True, "output": action,
                    "to_dict": lambda self: {"success": True, "output": action}
                })()

            results.append(result.to_dict() if hasattr(result, "to_dict") else {"output": action})
            if hasattr(result, "success") and not result.success:
                all_success = False

        total_ms = int((time.monotonic() - start) * 1000)

        return {
            "plan": plan,
            "results": results,
            "success": all_success,
            "total_ms": total_ms,
        }

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, Any]:
        uptime = time.monotonic() - self._created_at
        return {
            "agent_id": self.agent_id,
            "uptime_sec": round(uptime, 1),
            "memory": self.mem.stats(),
            "storage": self.store.stats(),
            "actions": len(self.act.audit_log),
            "planning_history": len(self.plan.history),
        }


# ---------------------------------------------------------------------------
# Convenience: create context
# ---------------------------------------------------------------------------

def create_agent_context(
    agent_id: str,
    priority: str = "normal",
    storage_dir: Optional[Path] = None,
) -> AgentContext:
    """Create an AgentContext (the recommended way)."""
    return AgentContext(
        agent_id=agent_id,
        default_priority=priority,
        storage_dir=storage_dir,
    )

"""
AIOS Kernel - Context Manager

Manages agent execution contexts: save, restore, switch, and isolate.
Each agent gets its own context that tracks working state, message history,
and resource usage. The kernel uses this for preemption and scheduling.

Usage:
    cm = ContextManager()

    # Create context for an agent
    ctx = cm.create("coder-001")

    # Save state before preemption
    cm.save("coder-001", {"current_file": "main.py", "line": 42})

    # Restore after resuming
    state = cm.restore("coder-001")

    # Switch between agents (save current, restore next)
    cm.switch("coder-001", "analyst-002")

    # Snapshot for persistence
    cm.snapshot("coder-001", "/path/to/snapshots/")
"""
from __future__ import annotations

import json
import time
import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class AgentContext:
    """Execution context for a single agent."""

    agent_id: str
    state: Dict[str, Any] = field(default_factory=dict)
    messages: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Resource tracking
    llm_calls: int = 0
    actions_taken: int = 0
    tokens_used: int = 0
    memory_bytes: int = 0

    # Lifecycle
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    suspended_at: Optional[float] = None
    status: str = "active"  # active | suspended | terminated

    # Limits
    max_messages: int = 100
    max_tokens: int = 50000
    max_actions: int = 200

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "state": self.state,
            "messages": self.messages,
            "metadata": self.metadata,
            "llm_calls": self.llm_calls,
            "actions_taken": self.actions_taken,
            "tokens_used": self.tokens_used,
            "memory_bytes": self.memory_bytes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "suspended_at": self.suspended_at,
            "status": self.status,
            "max_messages": self.max_messages,
            "max_tokens": self.max_tokens,
            "max_actions": self.max_actions,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentContext":
        ctx = cls(agent_id=data["agent_id"])
        for key in (
            "state", "messages", "metadata",
            "llm_calls", "actions_taken", "tokens_used", "memory_bytes",
            "created_at", "updated_at", "suspended_at", "status",
            "max_messages", "max_tokens", "max_actions",
        ):
            if key in data:
                setattr(ctx, key, data[key])
        return ctx

    def is_within_limits(self) -> bool:
        """Check if agent is within resource limits."""
        return (
            len(self.messages) <= self.max_messages
            and self.tokens_used <= self.max_tokens
            and self.actions_taken <= self.max_actions
        )

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({
            "role": role,
            "content": content,
            "ts": time.time(),
        })
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]
        self.updated_at = time.time()

    def record_llm_call(self, tokens: int = 0) -> None:
        self.llm_calls += 1
        self.tokens_used += tokens
        self.updated_at = time.time()

    def record_action(self) -> None:
        self.actions_taken += 1
        self.updated_at = time.time()


class ContextManager:
    """
    Kernel-level context manager.

    Responsibilities:
    - Create/destroy agent contexts
    - Save/restore state for preemption
    - Context switching between agents
    - Snapshot/restore for persistence
    - Resource limit enforcement
    """

    def __init__(self, snapshot_dir: Optional[Path] = None):
        self._contexts: Dict[str, AgentContext] = {}
        self._active_agent: Optional[str] = None
        self._switch_log: List[Dict[str, Any]] = []

        if snapshot_dir is None:
            snapshot_dir = Path(__file__).resolve().parent.parent / "data" / "contexts"
        self._snapshot_dir = snapshot_dir
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def create(
        self,
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        limits: Optional[Dict[str, int]] = None,
    ) -> AgentContext:
        """Create a new context for an agent."""
        if agent_id in self._contexts:
            return self._contexts[agent_id]

        ctx = AgentContext(
            agent_id=agent_id,
            metadata=metadata or {},
        )
        if limits:
            if "max_messages" in limits:
                ctx.max_messages = limits["max_messages"]
            if "max_tokens" in limits:
                ctx.max_tokens = limits["max_tokens"]
            if "max_actions" in limits:
                ctx.max_actions = limits["max_actions"]

        self._contexts[agent_id] = ctx
        return ctx

    def get(self, agent_id: str) -> Optional[AgentContext]:
        """Get an agent's context."""
        return self._contexts.get(agent_id)

    def destroy(self, agent_id: str) -> bool:
        """Destroy an agent's context."""
        if agent_id in self._contexts:
            self._contexts[agent_id].status = "terminated"
            del self._contexts[agent_id]
            if self._active_agent == agent_id:
                self._active_agent = None
            return True
        return False

    def list_contexts(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all contexts, optionally filtered by status."""
        results = []
        for ctx in self._contexts.values():
            if status and ctx.status != status:
                continue
            results.append({
                "agent_id": ctx.agent_id,
                "status": ctx.status,
                "messages": len(ctx.messages),
                "llm_calls": ctx.llm_calls,
                "tokens_used": ctx.tokens_used,
                "actions_taken": ctx.actions_taken,
                "created_at": ctx.created_at,
                "updated_at": ctx.updated_at,
            })
        return results

    # ------------------------------------------------------------------
    # Save / Restore (preemption support)
    # ------------------------------------------------------------------

    def save(self, agent_id: str, extra_state: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save agent state for preemption.
        Merges extra_state into the context's state dict.
        """
        ctx = self._contexts.get(agent_id)
        if ctx is None:
            return False

        if extra_state:
            ctx.state.update(extra_state)
        ctx.suspended_at = time.time()
        ctx.status = "suspended"
        ctx.updated_at = time.time()
        return True

    def restore(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Restore agent state after preemption.
        Returns the saved state dict.
        """
        ctx = self._contexts.get(agent_id)
        if ctx is None:
            return None

        ctx.status = "active"
        ctx.suspended_at = None
        ctx.updated_at = time.time()
        return copy.deepcopy(ctx.state)

    # ------------------------------------------------------------------
    # Context switching
    # ------------------------------------------------------------------

    def switch(
        self,
        from_agent: str,
        to_agent: str,
        save_state: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Switch from one agent to another.
        Saves current agent's state, restores target agent's state.

        Returns:
            The restored state of to_agent, or None on failure.
        """
        # Save current
        if from_agent in self._contexts:
            self.save(from_agent, save_state)

        # Restore target
        restored = self.restore(to_agent)
        if restored is not None:
            self._active_agent = to_agent
            self._switch_log.append({
                "from": from_agent,
                "to": to_agent,
                "ts": time.time(),
            })
        return restored

    @property
    def active_agent(self) -> Optional[str]:
        return self._active_agent

    @property
    def switch_count(self) -> int:
        return len(self._switch_log)

    # ------------------------------------------------------------------
    # Snapshot / Persist (disk-level)
    # ------------------------------------------------------------------

    def snapshot(self, agent_id: str) -> bool:
        """Save context to disk for crash recovery."""
        ctx = self._contexts.get(agent_id)
        if ctx is None:
            return False

        path = self._snapshot_dir / f"{agent_id}.json"
        try:
            path.write_text(
                json.dumps(ctx.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            return True
        except Exception:
            return False

    def load_snapshot(self, agent_id: str) -> Optional[AgentContext]:
        """Load context from disk snapshot."""
        path = self._snapshot_dir / f"{agent_id}.json"
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            ctx = AgentContext.from_dict(data)
            self._contexts[agent_id] = ctx
            return ctx
        except Exception:
            return None

    def snapshot_all(self) -> int:
        """Snapshot all active contexts. Returns count saved."""
        count = 0
        for agent_id in list(self._contexts.keys()):
            if self.snapshot(agent_id):
                count += 1
        return count

    def load_all_snapshots(self) -> int:
        """Load all snapshots from disk. Returns count loaded."""
        count = 0
        for path in self._snapshot_dir.glob("*.json"):
            agent_id = path.stem
            if self.load_snapshot(agent_id):
                count += 1
        return count

    # ------------------------------------------------------------------
    # Resource enforcement
    # ------------------------------------------------------------------

    def check_limits(self, agent_id: str) -> Dict[str, Any]:
        """Check if agent is within resource limits."""
        ctx = self._contexts.get(agent_id)
        if ctx is None:
            return {"exists": False}

        return {
            "exists": True,
            "within_limits": ctx.is_within_limits(),
            "messages": {"used": len(ctx.messages), "max": ctx.max_messages},
            "tokens": {"used": ctx.tokens_used, "max": ctx.max_tokens},
            "actions": {"used": ctx.actions_taken, "max": ctx.max_actions},
        }

    def enforce_limits(self, agent_id: str) -> Optional[str]:
        """
        Enforce limits. Returns violation type or None if OK.
        Suspends agent if limits exceeded.
        """
        ctx = self._contexts.get(agent_id)
        if ctx is None:
            return None

        if ctx.tokens_used > ctx.max_tokens:
            ctx.status = "suspended"
            return "token_limit"
        if ctx.actions_taken > ctx.max_actions:
            ctx.status = "suspended"
            return "action_limit"
        return None

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, Any]:
        active = sum(1 for c in self._contexts.values() if c.status == "active")
        suspended = sum(1 for c in self._contexts.values() if c.status == "suspended")
        return {
            "total_contexts": len(self._contexts),
            "active": active,
            "suspended": suspended,
            "active_agent": self._active_agent,
            "switch_count": len(self._switch_log),
            "total_tokens": sum(c.tokens_used for c in self._contexts.values()),
            "total_actions": sum(c.actions_taken for c in self._contexts.values()),
        }

"""
AIOS SDK - Memory Module

Provides context management and agent memory.
Backed by the kernel's MemoryQueue for fair scheduling.

Usage:
    mem = MemoryModule(agent_id="coder-001")

    # Store context
    mem.set("current_task", {"file": "main.py", "action": "refactor"})

    # Retrieve
    task = mem.get("current_task")

    # Conversation context
    mem.add_message("user", "Fix the bug in scheduler.py")
    mem.add_message("assistant", "I'll look at the error...")
    context = mem.get_context(max_tokens=2000)

    # Persistent memory (survives restarts)
    mem.remember("lesson", "Always check return codes")
    lessons = mem.recall("lesson")
"""
from __future__ import annotations

import json
import time
from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Optional

import sys

AIOS_ROOT = Path(__file__).resolve().parent.parent
if str(AIOS_ROOT) not in sys.path:
    sys.path.insert(0, str(AIOS_ROOT))

try:
    from aios.core.event import create_event
    from aios.core.event_bus import get_event_bus
except ImportError:
    # Fallback for direct execution
    from core.event import create_event
    from core.event_bus import get_event_bus


# Default context window
_DEFAULT_MAX_MESSAGES = 50
_DEFAULT_MAX_TOKENS = 4000


class MemoryModule:
    """
    Agent memory and context management.

    Two layers:
    - Working memory: in-process dict + message history (fast, volatile)
    - Long-term memory: file-backed key-value store (persistent)
    """

    def __init__(
        self,
        agent_id: str,
        storage_dir: Optional[Path] = None,
        max_messages: int = _DEFAULT_MAX_MESSAGES,
    ):
        self.agent_id = agent_id
        self.max_messages = max_messages
        self._bus = get_event_bus()

        # Working memory
        self._store: Dict[str, Any] = {}
        self._messages: List[Dict[str, str]] = []

        # Long-term storage
        if storage_dir is None:
            storage_dir = Path(AIOS_ROOT) / "data" / "agent_memory"
        self._storage_dir = storage_dir
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        self._ltm_file = self._storage_dir / f"{agent_id}.json"
        self._ltm: Dict[str, Any] = self._load_ltm()

    # ------------------------------------------------------------------
    # Working memory (volatile)
    # ------------------------------------------------------------------

    def set(self, key: str, value: Any) -> None:
        """Store a value in working memory."""
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from working memory."""
        return self._store.get(key, default)

    def delete(self, key: str) -> bool:
        """Remove a key from working memory."""
        return self._store.pop(key, None) is not None

    def keys(self) -> List[str]:
        return list(self._store.keys())

    def clear(self) -> None:
        """Clear all working memory."""
        self._store.clear()

    # ------------------------------------------------------------------
    # Message history (context window)
    # ------------------------------------------------------------------

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self._messages.append({
            "role": role,
            "content": content,
            "timestamp": time.time(),
        })
        # Trim to max
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages:]

    def get_context(self, max_tokens: int = _DEFAULT_MAX_TOKENS) -> List[Dict[str, str]]:
        """
        Get recent messages that fit within token budget.
        Estimates ~4 chars per token.
        """
        result = []
        budget = max_tokens * 4  # rough char estimate
        for msg in reversed(self._messages):
            cost = len(msg["content"])
            if budget - cost < 0 and result:
                break
            budget -= cost
            result.append({"role": msg["role"], "content": msg["content"]})
        result.reverse()
        return result

    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get raw message history."""
        if limit:
            return list(self._messages[-limit:])
        return list(self._messages)

    def clear_messages(self) -> None:
        self._messages.clear()

    # ------------------------------------------------------------------
    # Long-term memory (persistent)
    # ------------------------------------------------------------------

    def remember(self, key: str, value: Any) -> None:
        """Store a value in persistent long-term memory."""
        self._ltm[key] = {
            "value": value,
            "updated_at": time.time(),
        }
        self._save_ltm()

    def recall(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from long-term memory."""
        entry = self._ltm.get(key)
        if entry is None:
            return default
        return entry.get("value", default)

    def forget(self, key: str) -> bool:
        """Remove a key from long-term memory."""
        if key in self._ltm:
            del self._ltm[key]
            self._save_ltm()
            return True
        return False

    def recall_all(self) -> Dict[str, Any]:
        """Get all long-term memories."""
        return {k: v["value"] for k, v in self._ltm.items()}

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Simple keyword search across long-term memory.
        Returns matching entries sorted by relevance.
        """
        query_lower = query.lower()
        results = []
        for key, entry in self._ltm.items():
            value_str = str(entry.get("value", "")).lower()
            key_lower = key.lower()
            if query_lower in key_lower or query_lower in value_str:
                score = 2 if query_lower in key_lower else 1
                results.append({
                    "key": key,
                    "value": entry["value"],
                    "score": score,
                    "updated_at": entry.get("updated_at"),
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_ltm(self) -> Dict[str, Any]:
        if self._ltm_file.exists():
            try:
                return json.loads(self._ltm_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_ltm(self) -> None:
        try:
            self._ltm_file.write_text(
                json.dumps(self._ltm, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "working_memory_keys": len(self._store),
            "message_count": len(self._messages),
            "ltm_keys": len(self._ltm),
        }

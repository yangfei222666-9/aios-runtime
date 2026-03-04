"""
AIOS SDK - Storage Module

Provides persistent data storage for agents.
Backed by the kernel's StorageQueue for I/O scheduling.

Usage:
    store = StorageModule(agent_id="coder-001")

    # Key-value store
    store.put("config", {"timeout": 30, "retries": 3})
    config = store.get("config")

    # Append-only log (events, metrics, etc.)
    store.append_log("task_log", {"task": "fix_bug", "status": "done"})
    entries = store.read_log("task_log", limit=10)

    # File operations
    store.write_file("output/report.md", "# Report\n...")
    content = store.read_file("output/report.md")
"""
from __future__ import annotations

import json
import time
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


class StorageModule:
    """
    Persistent storage for agents.

    Three storage patterns:
    - Key-value: JSON-backed dict (get/put/delete)
    - Append log: JSONL files for event streams
    - File I/O: raw file read/write within agent sandbox
    """

    def __init__(
        self,
        agent_id: str,
        base_dir: Optional[Path] = None,
    ):
        self.agent_id = agent_id
        self._bus = get_event_bus()

        if base_dir is None:
            base_dir = Path(AIOS_ROOT) / "data" / "agent_storage"
        self._base = base_dir / agent_id
        self._base.mkdir(parents=True, exist_ok=True)

        # KV store
        self._kv_file = self._base / "kv_store.json"
        self._kv: Dict[str, Any] = self._load_kv()

        # Stats
        self._reads = 0
        self._writes = 0

    # ------------------------------------------------------------------
    # Key-Value store
    # ------------------------------------------------------------------

    def put(self, key: str, value: Any) -> None:
        """Store a value (JSON-serializable)."""
        self._kv[key] = {
            "value": value,
            "updated_at": time.time(),
        }
        self._save_kv()
        self._writes += 1

    def get(self, key: str, default: Any = None) -> Any:
        """Retrieve a value."""
        self._reads += 1
        entry = self._kv.get(key)
        if entry is None:
            return default
        return entry.get("value", default)

    def delete(self, key: str) -> bool:
        """Delete a key."""
        if key in self._kv:
            del self._kv[key]
            self._save_kv()
            self._writes += 1
            return True
        return False

    def keys(self) -> List[str]:
        return list(self._kv.keys())

    def has(self, key: str) -> bool:
        return key in self._kv

    # ------------------------------------------------------------------
    # Append-only log
    # ------------------------------------------------------------------

    def append_log(self, log_name: str, entry: Dict[str, Any]) -> None:
        """Append an entry to a named JSONL log."""
        log_file = self._base / f"{log_name}.jsonl"
        entry["_ts"] = time.time()
        entry["_agent"] = self.agent_id
        try:
            with log_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self._writes += 1
        except Exception:
            pass

    def read_log(
        self,
        log_name: str,
        limit: Optional[int] = None,
        since: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Read entries from a named log.

        Args:
            log_name: Log name
            limit: Max entries (from end)
            since: Unix timestamp filter
        """
        log_file = self._base / f"{log_name}.jsonl"
        if not log_file.exists():
            return []

        self._reads += 1
        entries = []
        try:
            with log_file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    if since and entry.get("_ts", 0) < since:
                        continue
                    entries.append(entry)
        except Exception:
            pass

        if limit:
            entries = entries[-limit:]
        return entries

    def log_size(self, log_name: str) -> int:
        """Get number of entries in a log."""
        log_file = self._base / f"{log_name}.jsonl"
        if not log_file.exists():
            return 0
        count = 0
        try:
            with log_file.open("r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        count += 1
        except Exception:
            pass
        return count

    # ------------------------------------------------------------------
    # File I/O (sandboxed to agent directory)
    # ------------------------------------------------------------------

    def write_file(self, path: str, content: str) -> bool:
        """Write a file within the agent's storage directory."""
        target = self._resolve_path(path)
        if target is None:
            return False
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            self._writes += 1
            return True
        except Exception:
            return False

    def read_file(self, path: str) -> Optional[str]:
        """Read a file from the agent's storage directory."""
        target = self._resolve_path(path)
        if target is None or not target.exists():
            return None
        self._reads += 1
        try:
            return target.read_text(encoding="utf-8")
        except Exception:
            return None

    def file_exists(self, path: str) -> bool:
        target = self._resolve_path(path)
        return target is not None and target.exists()

    def list_files(self, subdir: str = "") -> List[str]:
        """List files in a subdirectory."""
        target = self._base / subdir if subdir else self._base
        if not target.exists():
            return []
        return [
            str(f.relative_to(self._base))
            for f in target.rglob("*")
            if f.is_file()
        ]

    def _resolve_path(self, path: str) -> Optional[Path]:
        """Resolve and validate path is within sandbox."""
        resolved = (self._base / path).resolve()
        if not str(resolved).startswith(str(self._base.resolve())):
            return None  # path traversal attempt
        return resolved

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _load_kv(self) -> Dict[str, Any]:
        if self._kv_file.exists():
            try:
                return json.loads(self._kv_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_kv(self) -> None:
        try:
            self._kv_file.write_text(
                json.dumps(self._kv, ensure_ascii=False, indent=2),
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
            "kv_keys": len(self._kv),
            "reads": self._reads,
            "writes": self._writes,
            "base_dir": str(self._base),
        }

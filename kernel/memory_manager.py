"""
AIOS Kernel - Memory Manager

Manages memory allocation and limits for agents.
Tracks per-agent memory usage, enforces quotas, and provides
eviction policies when the system is under pressure.

Usage:
    mm = MemoryManager(global_limit_mb=512)

    # Allocate memory for an agent
    mm.allocate("coder-001", size_bytes=1024*1024)

    # Check usage
    usage = mm.usage("coder-001")

    # Release memory
    mm.release("coder-001", size_bytes=512*1024)

    # Evict under pressure
    evicted = mm.evict_lru(target_free_mb=100)
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class AgentMemoryBlock:
    """Memory allocation record for one agent."""

    agent_id: str
    allocated_bytes: int = 0
    peak_bytes: int = 0
    quota_bytes: int = 0  # 0 = no limit
    alloc_count: int = 0
    release_count: int = 0
    last_access: float = field(default_factory=time.time)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "allocated_bytes": self.allocated_bytes,
            "allocated_mb": round(self.allocated_bytes / (1024 * 1024), 2),
            "peak_bytes": self.peak_bytes,
            "peak_mb": round(self.peak_bytes / (1024 * 1024), 2),
            "quota_bytes": self.quota_bytes,
            "quota_mb": round(self.quota_bytes / (1024 * 1024), 2) if self.quota_bytes else 0,
            "alloc_count": self.alloc_count,
            "release_count": self.release_count,
            "last_access": self.last_access,
        }


class MemoryManager:
    """
    Kernel-level memory manager.

    Responsibilities:
    - Per-agent memory allocation tracking
    - Quota enforcement (per-agent and global)
    - LRU eviction under memory pressure
    - Usage statistics and monitoring
    """

    def __init__(self, global_limit_mb: float = 512.0):
        self._blocks: Dict[str, AgentMemoryBlock] = {}
        self._global_limit = int(global_limit_mb * 1024 * 1024)
        self._total_allocated: int = 0
        self._eviction_log: List[Dict[str, Any]] = []
        
        # Cached stats (updated on alloc/release)
        self._total_allocs: int = 0
        self._total_releases: int = 0
        self._stats_cache: Optional[Dict[str, Any]] = None
        self._stats_cache_ts: float = 0.0
        self._stats_cache_ttl: float = 5.0  # 5 seconds

    # ------------------------------------------------------------------
    # Allocation
    # ------------------------------------------------------------------

    def register(
        self,
        agent_id: str,
        quota_mb: float = 0,
    ) -> AgentMemoryBlock:
        """Register an agent with optional memory quota."""
        if agent_id in self._blocks:
            return self._blocks[agent_id]

        block = AgentMemoryBlock(
            agent_id=agent_id,
            quota_bytes=int(quota_mb * 1024 * 1024) if quota_mb > 0 else 0,
        )
        self._blocks[agent_id] = block
        return block

    def allocate(self, agent_id: str, size_bytes: int) -> Tuple[bool, str]:
        """
        Allocate memory for an agent.

        Returns:
            (success, reason)
        """
        if agent_id not in self._blocks:
            self.register(agent_id)

        block = self._blocks[agent_id]

        # Check per-agent quota
        if block.quota_bytes > 0:
            if block.allocated_bytes + size_bytes > block.quota_bytes:
                return False, f"agent quota exceeded ({block.allocated_bytes + size_bytes} > {block.quota_bytes})"

        # Check global limit
        if self._total_allocated + size_bytes > self._global_limit:
            return False, f"global limit exceeded ({self._total_allocated + size_bytes} > {self._global_limit})"

        block.allocated_bytes += size_bytes
        block.alloc_count += 1
        block.last_access = time.time()
        if block.allocated_bytes > block.peak_bytes:
            block.peak_bytes = block.allocated_bytes
        self._total_allocated += size_bytes
        
        # Update cached stats
        self._total_allocs += 1
        self._stats_cache = None  # Invalidate cache
        
        return True, "ok"

    def release(self, agent_id: str, size_bytes: int) -> bool:
        """Release memory from an agent."""
        block = self._blocks.get(agent_id)
        if block is None:
            return False

        actual = min(size_bytes, block.allocated_bytes)
        block.allocated_bytes -= actual
        block.release_count += 1
        block.last_access = time.time()
        self._total_allocated -= actual
        
        # Update cached stats
        self._total_releases += 1
        self._stats_cache = None  # Invalidate cache
        
        return True

    def release_all(self, agent_id: str) -> int:
        """Release all memory for an agent. Returns bytes freed."""
        block = self._blocks.get(agent_id)
        if block is None:
            return 0

        freed = block.allocated_bytes
        self._total_allocated -= freed
        block.allocated_bytes = 0
        block.release_count += 1
        block.last_access = time.time()
        return freed

    def unregister(self, agent_id: str) -> int:
        """Unregister agent and free all memory. Returns bytes freed."""
        freed = self.release_all(agent_id)
        self._blocks.pop(agent_id, None)
        return freed

    # ------------------------------------------------------------------
    # Quota management
    # ------------------------------------------------------------------

    def set_quota(self, agent_id: str, quota_mb: float) -> bool:
        """Set or update per-agent memory quota."""
        block = self._blocks.get(agent_id)
        if block is None:
            return False
        block.quota_bytes = int(quota_mb * 1024 * 1024)
        return True

    def set_global_limit(self, limit_mb: float) -> None:
        """Update global memory limit."""
        self._global_limit = int(limit_mb * 1024 * 1024)

    # ------------------------------------------------------------------
    # Eviction
    # ------------------------------------------------------------------

    def evict_lru(self, target_free_bytes: Optional[int] = None) -> List[str]:
        """
        Evict least-recently-used agents until target free space is reached.
        If no target, evicts the single LRU agent.

        Returns:
            List of evicted agent_ids.
        """
        if not self._blocks:
            return []

        if target_free_bytes is None:
            target_free_bytes = 0

        free_space = self._global_limit - self._total_allocated
        if free_space >= target_free_bytes and target_free_bytes > 0:
            return []

        # Sort by last_access (oldest first)
        sorted_agents = sorted(
            self._blocks.values(),
            key=lambda b: b.last_access,
        )

        evicted = []
        for block in sorted_agents:
            if block.allocated_bytes == 0:
                continue

            freed = block.allocated_bytes
            self._total_allocated -= freed
            block.allocated_bytes = 0
            evicted.append(block.agent_id)

            self._eviction_log.append({
                "agent_id": block.agent_id,
                "freed_bytes": freed,
                "ts": time.time(),
            })

            free_space = self._global_limit - self._total_allocated
            if target_free_bytes > 0 and free_space >= target_free_bytes:
                break
            if target_free_bytes == 0 and evicted:
                break  # just evict one

        return evicted

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def usage(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get memory usage for an agent."""
        block = self._blocks.get(agent_id)
        if block is None:
            return None
        return block.to_dict()

    def usage_all(self) -> List[Dict[str, Any]]:
        """Get memory usage for all agents."""
        return [b.to_dict() for b in self._blocks.values()]

    def top(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get top N agents by memory usage."""
        sorted_blocks = sorted(
            self._blocks.values(),
            key=lambda b: b.allocated_bytes,
            reverse=True,
        )
        return [b.to_dict() for b in sorted_blocks[:n]]

    @property
    def total_allocated(self) -> int:
        return self._total_allocated

    @property
    def total_allocated_mb(self) -> float:
        return round(self._total_allocated / (1024 * 1024), 2)

    @property
    def global_limit_mb(self) -> float:
        return round(self._global_limit / (1024 * 1024), 2)

    @property
    def free_bytes(self) -> int:
        return max(0, self._global_limit - self._total_allocated)

    @property
    def free_mb(self) -> float:
        return round(self.free_bytes / (1024 * 1024), 2)

    @property
    def utilization(self) -> float:
        """Memory utilization as percentage (0-100)."""
        if self._global_limit == 0:
            return 0.0
        return round(self._total_allocated / self._global_limit * 100, 2)

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> Dict[str, Any]:
        """Get memory manager statistics (cached for 5 seconds)."""
        now = time.time()
        
        # Return cached stats if still valid
        if self._stats_cache and (now - self._stats_cache_ts) < self._stats_cache_ttl:
            return self._stats_cache
        
        # Rebuild cache
        self._stats_cache = {
            "agents": len(self._blocks),
            "total_allocated_mb": self.total_allocated_mb,
            "global_limit_mb": self.global_limit_mb,
            "free_mb": self.free_mb,
            "utilization_pct": self.utilization,
            "evictions": len(self._eviction_log),
            "total_allocs": self._total_allocs,
            "total_releases": self._total_releases,
        }
        self._stats_cache_ts = now
        
        return self._stats_cache

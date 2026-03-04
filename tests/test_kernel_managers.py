"""
Tests for Context Manager and Memory Manager.
"""
import sys
import json
import tempfile
from pathlib import Path

# Setup path - import directly to avoid package conflicts
AIOS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AIOS_ROOT / "kernel"))

from context_manager import ContextManager, AgentContext
from memory_manager import MemoryManager


def test_context_create_and_get():
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    ctx = cm.create("agent-1", metadata={"role": "coder"})
    assert ctx.agent_id == "agent-1"
    assert ctx.status == "active"
    assert ctx.metadata["role"] == "coder"

    got = cm.get("agent-1")
    assert got is ctx
    print("  [PASS] context create and get")


def test_context_save_restore():
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    cm.create("agent-1")

    cm.save("agent-1", {"file": "main.py", "line": 42})
    ctx = cm.get("agent-1")
    assert ctx.status == "suspended"
    assert ctx.state["file"] == "main.py"

    state = cm.restore("agent-1")
    assert state["file"] == "main.py"
    assert state["line"] == 42
    assert cm.get("agent-1").status == "active"
    print("  [PASS] context save and restore")


def test_context_switch():
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    cm.create("agent-1")
    cm.create("agent-2")

    cm.get("agent-1").state["task"] = "coding"
    cm.get("agent-2").state["task"] = "analysis"

    restored = cm.switch("agent-1", "agent-2", save_state={"progress": 50})
    assert restored["task"] == "analysis"
    assert cm.active_agent == "agent-2"
    assert cm.get("agent-1").status == "suspended"
    assert cm.get("agent-1").state["progress"] == 50
    assert cm.switch_count == 1
    print("  [PASS] context switch")


def test_context_snapshot_disk():
    tmp = Path(tempfile.mkdtemp())
    cm = ContextManager(snapshot_dir=tmp)
    cm.create("agent-1")
    cm.get("agent-1").state["important"] = True
    cm.get("agent-1").add_message("user", "hello")

    assert cm.snapshot("agent-1")
    assert (tmp / "agent-1.json").exists()

    # Load in fresh manager
    cm2 = ContextManager(snapshot_dir=tmp)
    ctx = cm2.load_snapshot("agent-1")
    assert ctx is not None
    assert ctx.state["important"] is True
    assert len(ctx.messages) == 1
    print("  [PASS] context snapshot to disk")


def test_context_resource_tracking():
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    ctx = cm.create("agent-1", limits={"max_tokens": 1000, "max_actions": 5})

    ctx.record_llm_call(tokens=200)
    ctx.record_llm_call(tokens=300)
    ctx.record_action()
    assert ctx.llm_calls == 2
    assert ctx.tokens_used == 500
    assert ctx.actions_taken == 1
    assert ctx.is_within_limits()

    limits = cm.check_limits("agent-1")
    assert limits["within_limits"] is True
    assert limits["tokens"]["used"] == 500
    print("  [PASS] context resource tracking")


def test_context_limit_enforcement():
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    ctx = cm.create("agent-1", limits={"max_tokens": 100})
    ctx.tokens_used = 150

    violation = cm.enforce_limits("agent-1")
    assert violation == "token_limit"
    assert ctx.status == "suspended"
    print("  [PASS] context limit enforcement")


def test_context_destroy():
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    cm.create("agent-1")
    assert cm.destroy("agent-1")
    assert cm.get("agent-1") is None
    assert not cm.destroy("agent-1")  # already gone
    print("  [PASS] context destroy")


def test_context_list():
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    cm.create("agent-1")
    cm.create("agent-2")
    cm.save("agent-2")

    all_ctx = cm.list_contexts()
    assert len(all_ctx) == 2

    active = cm.list_contexts(status="active")
    assert len(active) == 1
    assert active[0]["agent_id"] == "agent-1"

    suspended = cm.list_contexts(status="suspended")
    assert len(suspended) == 1
    assert suspended[0]["agent_id"] == "agent-2"
    print("  [PASS] context list with filter")


# ======================================================================
# Memory Manager Tests
# ======================================================================

def test_mm_register_and_allocate():
    mm = MemoryManager(global_limit_mb=10)
    mm.register("agent-1", quota_mb=5)

    ok, reason = mm.allocate("agent-1", 1024 * 1024)  # 1MB
    assert ok
    assert reason == "ok"
    assert mm.total_allocated == 1024 * 1024
    print("  [PASS] memory register and allocate")


def test_mm_quota_enforcement():
    mm = MemoryManager(global_limit_mb=100)
    mm.register("agent-1", quota_mb=2)

    ok, _ = mm.allocate("agent-1", 1 * 1024 * 1024)  # 1MB
    assert ok

    ok, reason = mm.allocate("agent-1", 2 * 1024 * 1024)  # 2MB more = 3MB > 2MB quota
    assert not ok
    assert "quota" in reason
    print("  [PASS] memory quota enforcement")


def test_mm_global_limit():
    mm = MemoryManager(global_limit_mb=1)  # 1MB global

    ok, _ = mm.allocate("agent-1", 512 * 1024)  # 0.5MB
    assert ok

    ok, reason = mm.allocate("agent-2", 600 * 1024)  # 0.6MB, total > 1MB
    assert not ok
    assert "global" in reason
    print("  [PASS] memory global limit")


def test_mm_release():
    mm = MemoryManager(global_limit_mb=10)
    mm.allocate("agent-1", 1024 * 1024)

    assert mm.release("agent-1", 512 * 1024)
    assert mm.total_allocated == 512 * 1024

    freed = mm.release_all("agent-1")
    assert freed == 512 * 1024
    assert mm.total_allocated == 0
    print("  [PASS] memory release")


def test_mm_evict_lru():
    mm = MemoryManager(global_limit_mb=10)

    # Allocate for 3 agents with different access times
    mm.register("old-agent")
    mm.allocate("old-agent", 2 * 1024 * 1024)
    mm._blocks["old-agent"].last_access = 1000  # oldest

    mm.register("mid-agent")
    mm.allocate("mid-agent", 3 * 1024 * 1024)
    mm._blocks["mid-agent"].last_access = 2000

    mm.register("new-agent")
    mm.allocate("new-agent", 1 * 1024 * 1024)
    mm._blocks["new-agent"].last_access = 3000  # newest

    # Evict LRU (should evict old-agent first)
    evicted = mm.evict_lru()
    assert evicted == ["old-agent"]
    assert mm._blocks["old-agent"].allocated_bytes == 0
    print("  [PASS] memory evict LRU")


def test_mm_evict_target():
    mm = MemoryManager(global_limit_mb=10)

    mm.register("a1")
    mm.allocate("a1", 3 * 1024 * 1024)
    mm._blocks["a1"].last_access = 1000

    mm.register("a2")
    mm.allocate("a2", 3 * 1024 * 1024)
    mm._blocks["a2"].last_access = 2000

    mm.register("a3")
    mm.allocate("a3", 2 * 1024 * 1024)
    mm._blocks["a3"].last_access = 3000

    # Need 5MB free (currently ~2MB free out of 10MB, 8MB used)
    evicted = mm.evict_lru(target_free_bytes=5 * 1024 * 1024)
    # Should evict a1 (3MB) + a2 (3MB) to get 8MB free
    assert "a1" in evicted
    assert len(evicted) >= 1
    assert mm.free_bytes >= 5 * 1024 * 1024
    print("  [PASS] memory evict with target")


def test_mm_usage_and_stats():
    mm = MemoryManager(global_limit_mb=10)
    mm.allocate("agent-1", 1024 * 1024)
    mm.allocate("agent-2", 2 * 1024 * 1024)

    usage = mm.usage("agent-1")
    assert usage is not None
    assert usage["allocated_mb"] == 1.0

    top = mm.top(1)
    assert top[0]["agent_id"] == "agent-2"

    stats = mm.stats()
    assert stats["agents"] == 2
    assert stats["total_allocated_mb"] == 3.0
    print("  [PASS] memory usage and stats")


def test_mm_unregister():
    mm = MemoryManager(global_limit_mb=10)
    mm.allocate("agent-1", 1024 * 1024)

    freed = mm.unregister("agent-1")
    assert freed == 1024 * 1024
    assert mm.total_allocated == 0
    assert mm.usage("agent-1") is None
    print("  [PASS] memory unregister")


# ======================================================================
# Run all tests
# ======================================================================

if __name__ == "__main__":
    print("\n=== Context Manager Tests ===")
    test_context_create_and_get()
    test_context_save_restore()
    test_context_switch()
    test_context_snapshot_disk()
    test_context_resource_tracking()
    test_context_limit_enforcement()
    test_context_destroy()
    test_context_list()

    print("\n=== Memory Manager Tests ===")
    test_mm_register_and_allocate()
    test_mm_quota_enforcement()
    test_mm_global_limit()
    test_mm_release()
    test_mm_evict_lru()
    test_mm_evict_target()
    test_mm_usage_and_stats()
    test_mm_unregister()

    print(f"\n{'='*50}")
    print("ALL 16 TESTS PASSED")
    print(f"{'='*50}")

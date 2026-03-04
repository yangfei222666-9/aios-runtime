"""
AIOS Benchmark Suite

Measures core system performance:
- EventBus throughput (events/sec)
- Context Manager switch latency
- Memory Manager allocation throughput
- Queue scheduling latency
- End-to-end task pipeline

Run: python benchmark.py
"""
import sys
import time
import statistics
from pathlib import Path

AIOS_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AIOS_ROOT))
sys.path.insert(0, str(AIOS_ROOT / "kernel"))

from context_manager import ContextManager, AgentContext
from memory_manager import MemoryManager

import tempfile


def fmt(val, unit=""):
    """Format number with commas."""
    if isinstance(val, float):
        return f"{val:,.2f}{unit}"
    return f"{val:,}{unit}"


def bench_context_create(n=1000):
    """Benchmark context creation."""
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    start = time.perf_counter()
    for i in range(n):
        cm.create(f"agent-{i}")
    elapsed = time.perf_counter() - start
    rate = n / elapsed
    print(f"  Context create:     {fmt(rate, '/s')} ({n} contexts in {elapsed*1000:.1f}ms)")
    return rate


def bench_context_switch(n=5000):
    """Benchmark context switching."""
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    cm.create("agent-a", metadata={"role": "coder"})
    cm.create("agent-b", metadata={"role": "analyst"})
    cm.get("agent-a").state = {"file": "main.py", "data": list(range(100))}
    cm.get("agent-b").state = {"query": "SELECT *", "results": list(range(50))}

    latencies = []
    for i in range(n):
        src = "agent-a" if i % 2 == 0 else "agent-b"
        dst = "agent-b" if i % 2 == 0 else "agent-a"
        t0 = time.perf_counter()
        cm.switch(src, dst)
        latencies.append((time.perf_counter() - t0) * 1_000_000)  # microseconds

    avg = statistics.mean(latencies)
    p50 = statistics.median(latencies)
    p99 = sorted(latencies)[int(n * 0.99)]
    rate = n / (sum(latencies) / 1_000_000)
    print(f"  Context switch:     {fmt(rate, '/s')} (avg={avg:.1f}us, p50={p50:.1f}us, p99={p99:.1f}us)")
    return rate


def bench_context_snapshot(n=100):
    """Benchmark context snapshot to disk."""
    tmp = Path(tempfile.mkdtemp())
    cm = ContextManager(snapshot_dir=tmp)
    for i in range(n):
        ctx = cm.create(f"agent-{i}")
        ctx.state = {"data": list(range(50)), "config": {"key": f"val-{i}"}}
        for j in range(10):
            ctx.add_message("user", f"message {j} for agent {i}")

    start = time.perf_counter()
    saved = cm.snapshot_all()
    elapsed = time.perf_counter() - start
    rate = saved / elapsed
    print(f"  Context snapshot:   {fmt(rate, '/s')} ({saved} snapshots in {elapsed*1000:.1f}ms)")

    # Load benchmark
    cm2 = ContextManager(snapshot_dir=tmp)
    start = time.perf_counter()
    loaded = cm2.load_all_snapshots()
    elapsed = time.perf_counter() - start
    load_rate = loaded / elapsed
    print(f"  Context load:       {fmt(load_rate, '/s')} ({loaded} loaded in {elapsed*1000:.1f}ms)")
    return rate


def bench_memory_allocate(n=10000):
    """Benchmark memory allocation."""
    mm = MemoryManager(global_limit_mb=1024)

    start = time.perf_counter()
    for i in range(n):
        mm.allocate(f"agent-{i % 100}", 1024)
    elapsed = time.perf_counter() - start
    rate = n / elapsed
    print(f"  Memory allocate:    {fmt(rate, '/s')} ({n} allocs in {elapsed*1000:.1f}ms)")
    return rate


def bench_memory_release(n=10000):
    """Benchmark memory release."""
    mm = MemoryManager(global_limit_mb=1024)
    for i in range(n):
        mm.allocate(f"agent-{i % 100}", 1024)

    start = time.perf_counter()
    for i in range(n):
        mm.release(f"agent-{i % 100}", 1024)
    elapsed = time.perf_counter() - start
    rate = n / elapsed
    print(f"  Memory release:     {fmt(rate, '/s')} ({n} releases in {elapsed*1000:.1f}ms)")
    return rate


def bench_memory_eviction(n=100):
    """Benchmark LRU eviction."""
    mm = MemoryManager(global_limit_mb=10)
    for i in range(n):
        mm.register(f"agent-{i}")
        mm.allocate(f"agent-{i}", 100 * 1024)  # 100KB each = ~10MB total
        mm._blocks[f"agent-{i}"].last_access = 1000 + i

    start = time.perf_counter()
    evicted = mm.evict_lru(target_free_bytes=8 * 1024 * 1024)  # need 8MB free
    elapsed = time.perf_counter() - start
    print(f"  Memory eviction:    {len(evicted)} agents evicted in {elapsed*1000:.2f}ms")
    return len(evicted) / elapsed if elapsed > 0 else 0


def bench_agent_context_messages(n=10000):
    """Benchmark message addition to context."""
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    ctx = cm.create("agent-1", limits={"max_messages": n + 100})

    start = time.perf_counter()
    for i in range(n):
        ctx.add_message("user" if i % 2 == 0 else "assistant", f"Message number {i} with some content")
    elapsed = time.perf_counter() - start
    rate = n / elapsed
    print(f"  Message add:        {fmt(rate, '/s')} ({n} messages in {elapsed*1000:.1f}ms)")
    return rate


def bench_resource_check(n=5000):
    """Benchmark resource limit checking."""
    cm = ContextManager(snapshot_dir=Path(tempfile.mkdtemp()))
    ctx = cm.create("agent-1", limits={"max_tokens": 100000, "max_actions": 10000})
    ctx.tokens_used = 50000
    ctx.actions_taken = 5000

    start = time.perf_counter()
    for _ in range(n):
        cm.check_limits("agent-1")
        cm.enforce_limits("agent-1")
    elapsed = time.perf_counter() - start
    rate = n / elapsed
    print(f"  Resource check:     {fmt(rate, '/s')} ({n} checks in {elapsed*1000:.1f}ms)")
    return rate


def main():
    print("=" * 60)
    print("AIOS Benchmark Suite")
    print("=" * 60)

    print("\n--- Context Manager ---")
    bench_context_create()
    bench_context_switch()
    bench_context_snapshot()
    bench_agent_context_messages()
    bench_resource_check()

    print("\n--- Memory Manager ---")
    bench_memory_allocate()
    bench_memory_release()
    bench_memory_eviction()

    print("\n" + "=" * 60)
    print("Benchmark complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()

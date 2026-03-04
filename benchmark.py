"""
AIOS Benchmark Suite v1.0

Comprehensive performance benchmarks for AIOS kernel and SDK modules.

Usage:
    python benchmark.py           # Run all benchmarks
    python benchmark.py --json    # Output JSON report
"""
from __future__ import annotations

import sys
import time
import json
import statistics
import argparse
import tempfile
import importlib.util
from pathlib import Path
from typing import Any, Callable, Dict, List

AIOS_ROOT = Path(__file__).resolve().parent

# Ensure AIOS_ROOT is in sys.path for absolute imports
if str(AIOS_ROOT) not in sys.path:
    sys.path.insert(0, str(AIOS_ROOT))
# Also add parent so 'aios' package can be found
_PARENT = str(AIOS_ROOT.parent)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)


def _import_module(dotted: str):
    """Import a module by file path to avoid package conflicts."""
    parts = dotted.split(".")
    file_path = AIOS_ROOT / Path(*parts).with_suffix(".py")
    if not file_path.exists():
        file_path = AIOS_ROOT / Path(*parts) / "__init__.py"
    spec = importlib.util.spec_from_file_location(dotted, str(file_path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[dotted] = mod
    spec.loader.exec_module(mod)
    return mod


# ── Benchmark Harness ──────────────────────────────────────────────

class BenchmarkResult:
    def __init__(self, name: str, ops: int, elapsed: float, unit: str = "ops/sec"):
        self.name = name
        self.ops = ops
        self.elapsed = elapsed
        self.unit = unit
        self.rate = ops / elapsed if elapsed > 0 else float("inf")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "ops": self.ops,
            "elapsed_sec": round(self.elapsed, 6),
            "rate": round(self.rate, 2),
            "unit": self.unit,
            "avg_us": round(self.elapsed / self.ops * 1_000_000, 2) if self.ops > 0 else 0,
        }


def bench(name: str, fn: Callable, n: int = 10000, warmup: int = 100) -> BenchmarkResult:
    for _ in range(warmup):
        fn()
    t0 = time.perf_counter()
    for _ in range(n):
        fn()
    elapsed = time.perf_counter() - t0
    return BenchmarkResult(name, n, elapsed)


def bench_latency(name: str, fn: Callable, n: int = 10000, warmup: int = 100) -> Dict[str, Any]:
    for _ in range(warmup):
        fn()
    latencies = []
    for _ in range(n):
        t0 = time.perf_counter()
        fn()
        latencies.append((time.perf_counter() - t0) * 1_000_000)
    return {
        "name": name,
        "n": n,
        "p50_us": round(statistics.median(latencies), 2),
        "p95_us": round(sorted(latencies)[int(n * 0.95)], 2),
        "p99_us": round(sorted(latencies)[int(n * 0.99)], 2),
        "min_us": round(min(latencies), 2),
        "max_us": round(max(latencies), 2),
        "avg_us": round(statistics.mean(latencies), 2),
    }


# ── Kernel: Context Manager ───────────────────────────────────────

def bench_context_manager() -> List[Dict[str, Any]]:
    cm_mod = _import_module("kernel.context_manager")
    ContextManager = cm_mod.ContextManager
    results = []
    tmp = Path(tempfile.mkdtemp())

    # 1. Create 100 agents
    def create_ctx():
        cm = ContextManager(snapshot_dir=tmp)
        for i in range(100):
            cm.create(f"agent-{i}", metadata={"role": "worker"})
    r = bench("context.create (100 agents)", create_ctx, n=1000, warmup=10)
    results.append(r.to_dict())

    # 2. Context switch
    cm = ContextManager(snapshot_dir=tmp)
    cm.create("a1"); cm.create("a2"); cm.restore("a1")
    toggle = [0]
    def switch_ctx():
        f, t = ("a1", "a2") if toggle[0] % 2 == 0 else ("a2", "a1")
        cm.switch(f, t, save_state={"step": toggle[0]})
        toggle[0] += 1
    r = bench("context.switch", switch_ctx, n=100000)
    results.append(r.to_dict())
    results.append(bench_latency("context.switch (latency)", switch_ctx, n=50000))

    # 3. Message add
    cm2 = ContextManager(snapshot_dir=tmp)
    ctx = cm2.create("msg-agent")
    def add_msg():
        ctx.add_message("user", "hello world")
    r = bench("context.add_message", add_msg, n=100000)
    results.append(r.to_dict())

    # 4. Snapshot to disk
    cm3 = ContextManager(snapshot_dir=tmp)
    ctx3 = cm3.create("snap-agent")
    for i in range(50):
        ctx3.add_message("user", f"message {i}")
    def snapshot():
        cm3.snapshot("snap-agent")
    r = bench("context.snapshot (50 msgs)", snapshot, n=5000, warmup=50)
    results.append(r.to_dict())

    # 5. Load from disk
    def load_snap():
        cm3.load_snapshot("snap-agent")
    r = bench("context.load_snapshot", load_snap, n=5000, warmup=50)
    results.append(r.to_dict())

    # 6. Resource limit check
    cm4 = ContextManager(snapshot_dir=tmp)
    ctx4 = cm4.create("limit-agent")
    ctx4.tokens_used = 25000; ctx4.actions_taken = 100
    def check_limits():
        cm4.check_limits("limit-agent")
    r = bench("context.check_limits", check_limits, n=100000)
    results.append(r.to_dict())

    # 7. Save + restore cycle
    cm5 = ContextManager(snapshot_dir=tmp)
    cm5.create("sr-agent")
    def save_restore():
        cm5.save("sr-agent", {"key": "value"})
        cm5.restore("sr-agent")
    r = bench("context.save_restore_cycle", save_restore, n=100000)
    results.append(r.to_dict())

    return results


# ── Kernel: Memory Manager ─────────────────────────────────────────

def bench_memory_manager() -> List[Dict[str, Any]]:
    mm_mod = _import_module("kernel.memory_manager")
    MemoryManager = mm_mod.MemoryManager
    results = []

    # 1. Allocate 100 agents
    def alloc_cycle():
        mm = MemoryManager(global_limit_mb=1024)
        for i in range(100):
            mm.register(f"agent-{i}", quota_mb=10)
            mm.allocate(f"agent-{i}", 1024 * 1024)
    r = bench("memory.alloc_100_agents", alloc_cycle, n=1000, warmup=10)
    results.append(r.to_dict())

    # 2. Single allocate
    mm = MemoryManager(global_limit_mb=1024)
    mm.register("fast-agent", quota_mb=512)
    counter = [0]
    def single_alloc():
        mm.allocate("fast-agent", 1024)
        counter[0] += 1
        if counter[0] % 100 == 0:
            mm.release("fast-agent", 1024 * 100)
    r = bench("memory.allocate_single", single_alloc, n=100000)
    results.append(r.to_dict())

    # 3. Release
    mm2 = MemoryManager(global_limit_mb=1024)
    mm2.register("rel-agent", quota_mb=512)
    mm2.allocate("rel-agent", 100 * 1024 * 1024)
    def release():
        mm2.release("rel-agent", 1024)
    r = bench("memory.release", release, n=100000)
    results.append(r.to_dict())

    # 4. LRU eviction
    def lru_evict():
        mm = MemoryManager(global_limit_mb=100)
        for i in range(80):
            mm.register(f"agent-{i}")
            mm.allocate(f"agent-{i}", 1024 * 1024)
        mm.evict_lru(target_free_bytes=50 * 1024 * 1024)
    r = bench("memory.evict_lru (80 agents)", lru_evict, n=500, warmup=5)
    results.append(r.to_dict())

    # 5. Usage query
    mm3 = MemoryManager(global_limit_mb=1024)
    for i in range(50):
        mm3.register(f"q-agent-{i}", quota_mb=10)
        mm3.allocate(f"q-agent-{i}", 1024 * 1024)
    def query_usage():
        mm3.usage_all()
    r = bench("memory.usage_all (50 agents)", query_usage, n=10000)
    results.append(r.to_dict())

    # 6. Top N
    def top_n():
        mm3.top(10)
    r = bench("memory.top(10)", top_n, n=10000)
    results.append(r.to_dict())

    # 7. Stats
    def stats():
        mm3.stats()
    r = bench("memory.stats", stats, n=100000)
    results.append(r.to_dict())

    return results


# ── SDK: Planning ──────────────────────────────────────────────────

def bench_planning() -> List[Dict[str, Any]]:
    results = []
    try:
        plan_mod = _import_module("sdk.planning")
        PlanningModule = plan_mod.PlanningModule
        planner = PlanningModule(agent_id="bench-planner")

        def create_plan():
            planner.plan("Refactor the scheduler module to support priority queues")
        r = bench("planning.plan (CoT)", create_plan, n=5000, warmup=50)
        results.append(r.to_dict())

        def analyze_deps():
            planner.analyze_dependencies([
                {"id": "t1", "desc": "Design API", "deps": []},
                {"id": "t2", "desc": "Implement core", "deps": ["t1"]},
                {"id": "t3", "desc": "Write tests", "deps": ["t2"]},
                {"id": "t4", "desc": "Deploy", "deps": ["t2", "t3"]},
            ])
        r = bench("planning.analyze_deps", analyze_deps, n=5000, warmup=50)
        results.append(r.to_dict())
    except Exception as e:
        results.append({"name": "sdk.planning (skipped)", "error": str(e)})
    return results


# ── SDK: Action Engine ─────────────────────────────────────────────

def bench_action_engine() -> List[Dict[str, Any]]:
    results = []
    try:
        act_mod = _import_module("sdk.action")
        ActionEngine = act_mod.ActionEngine
        ae = ActionEngine(agent_id="bench-action")
        ae.register_tool("echo", lambda x: x, risk="low")

        def exec_tool():
            ae.execute("echo", "hello")
        r = bench("action.execute (low risk)", exec_tool, n=50000)
        results.append(r.to_dict())
    except Exception as e:
        results.append({"name": "sdk.action (skipped)", "error": str(e)})
    return results


# ── SDK: Memory ────────────────────────────────────────────────────

def bench_memory_sdk() -> List[Dict[str, Any]]:
    results = []
    try:
        mem_mod = _import_module("sdk.memory")
        MemoryModule = mem_mod.MemoryModule
        mem = MemoryModule(agent_id="bench-mem")

        counter = [0]
        def store_retrieve():
            key = f"key-{counter[0]}"
            mem.store(key, {"data": counter[0]}, layer="working")
            mem.retrieve(key)
            counter[0] += 1
        r = bench("memory_sdk.store_retrieve", store_retrieve, n=50000)
        results.append(r.to_dict())

        for i in range(100):
            mem.store(f"doc-{i}", {"text": f"document about topic {i % 10}"}, layer="long_term")
        def search():
            mem.search("topic 5", top_k=10)
        r = bench("memory_sdk.search (100 docs)", search, n=5000, warmup=50)
        results.append(r.to_dict())
    except Exception as e:
        results.append({"name": "sdk.memory (skipped)", "error": str(e)})
    return results


# ── Storage ────────────────────────────────────────────────────────

def bench_storage() -> List[Dict[str, Any]]:
    results = []
    try:
        import asyncio
        sm_mod = _import_module("storage.storage_manager")
        StorageManager = sm_mod.StorageManager

        async def run():
            sm = StorageManager(":memory:")
            await sm.initialize()

            # save_agent_state (agent_id, role, state)
            t0 = time.perf_counter()
            for i in range(1000):
                await sm.save_agent_state(f"agent-{i}", "worker", "active",
                                          goal=f"task-{i}", stats={"score": i})
            elapsed = time.perf_counter() - t0
            results.append(BenchmarkResult("storage.save_state (1000)", 1000, elapsed).to_dict())

            # get_agent_state
            t0 = time.perf_counter()
            for i in range(1000):
                await sm.get_agent_state(f"agent-{i}")
            elapsed = time.perf_counter() - t0
            results.append(BenchmarkResult("storage.get_state (1000)", 1000, elapsed).to_dict())

            # log_event
            t0 = time.perf_counter()
            for i in range(1000):
                await sm.log_event(f"test.event.{i % 10}", {"index": i})
            elapsed = time.perf_counter() - t0
            results.append(BenchmarkResult("storage.log_event (1000)", 1000, elapsed).to_dict())

            # list_events
            t0 = time.perf_counter()
            for _ in range(100):
                await sm.list_events(event_type="test.event.5", limit=50)
            elapsed = time.perf_counter() - t0
            results.append(BenchmarkResult("storage.list_events (100q)", 100, elapsed).to_dict())

            # log_task + get_task
            t0 = time.perf_counter()
            for i in range(500):
                await sm.log_task(f"task-{i}", f"agent-{i%10}", "code")
            elapsed = time.perf_counter() - t0
            results.append(BenchmarkResult("storage.log_task (500)", 500, elapsed).to_dict())

            t0 = time.perf_counter()
            for i in range(500):
                await sm.get_task(f"task-{i}")
            elapsed = time.perf_counter() - t0
            results.append(BenchmarkResult("storage.get_task (500)", 500, elapsed).to_dict())

            await sm.close()

        asyncio.run(run())
    except Exception as e:
        results.append({"name": "storage (skipped)", "error": str(e)})
    return results


# ── Report ─────────────────────────────────────────────────────────

BASELINES = {
    "context.switch": 50000,
    "context.add_message": 100000,
    "context.check_limits": 500000,
    "memory.allocate_single": 100000,
    "memory.release": 100000,
    "memory.stats": 500000,
}


def format_rate(rate: float) -> str:
    if rate >= 1_000_000:
        return f"{rate/1_000_000:.2f}M"
    elif rate >= 1_000:
        return f"{rate/1_000:.1f}K"
    else:
        return f"{rate:.0f}"


def print_report(all_results: Dict[str, List[Dict[str, Any]]]) -> None:
    print("=" * 72)
    print("  AIOS Benchmark Report v1.0")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Platform: {sys.platform}")
    print("=" * 72)

    total_ops = 0
    for module, results in all_results.items():
        print(f"\n  [{module}]")
        print(f"  {'Name':<45} {'Rate':>10} {'Avg':>10}")
        print(f"  {'-'*45} {'-'*10} {'-'*10}")
        for r in results:
            if "error" in r:
                print(f"  {r['name']:<45} {'SKIP':>10} {r.get('error','')[:30]}")
                continue
            if "p50_us" in r:
                print(f"  {r['name']:<45} {'p50':>4}={r['p50_us']:>5.1f}us  p99={r['p99_us']:>6.1f}us")
                continue
            rate_str = format_rate(r.get("rate", 0))
            avg_str = f"{r.get('avg_us', 0):.1f}us"
            name = r["name"]
            marker = ""
            for bname, bmin in BASELINES.items():
                if bname in name:
                    marker = " [PASS]" if r.get("rate", 0) >= bmin else " [SLOW]"
                    break
            print(f"  {name:<45} {rate_str:>10} {avg_str:>10}{marker}")
            total_ops += r.get("ops", 0)

    print(f"\n  Total operations: {total_ops:,}")
    print("=" * 72)


def main():
    parser = argparse.ArgumentParser(description="AIOS Benchmark Suite")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--module", type=str)
    args = parser.parse_args()

    all_results: Dict[str, List[Dict[str, Any]]] = {}
    modules = {
        "kernel.context_manager": bench_context_manager,
        "kernel.memory_manager": bench_memory_manager,
        "sdk.planning": bench_planning,
        "sdk.action": bench_action_engine,
        "sdk.memory": bench_memory_sdk,
        "storage": bench_storage,
    }

    for name, fn in modules.items():
        if args.module and args.module not in name:
            continue
        try:
            if not args.json:
                print(f"  Running {name}...", end=" ", flush=True)
            results = fn()
            all_results[name] = results
            if not args.json:
                print(f"done ({len(results)} tests)")
        except Exception as e:
            all_results[name] = [{"name": name, "error": str(e)}]
            if not args.json:
                print(f"ERROR: {e}")

    if args.json:
        print(json.dumps(all_results, indent=2, ensure_ascii=False))
    else:
        print_report(all_results)

    # Save report
    report_path = AIOS_ROOT / "benchmark_report.json"
    report_path.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    if not args.json:
        print(f"\n  Report saved to: {report_path}")


if __name__ == "__main__":
    main()

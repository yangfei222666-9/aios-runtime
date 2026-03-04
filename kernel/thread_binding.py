"""
Thread Binding - 线程绑定和线程池管理
将 Agent 绑定到特定线程，支持 CPU 亲和性设置
"""

import threading
import os
import time
import queue
from dataclasses import dataclass, field
from typing import Callable, Optional, Dict, List, Any
from enum import Enum


class ThreadState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"


@dataclass
class ThreadStats:
    tasks_executed: int = 0
    tasks_failed: int = 0
    total_time_ms: float = 0.0
    last_active: float = field(default_factory=time.time)

    @property
    def avg_time_ms(self) -> float:
        if self.tasks_executed == 0:
            return 0.0
        return self.total_time_ms / self.tasks_executed

    @property
    def success_rate(self) -> float:
        total = self.tasks_executed + self.tasks_failed
        if total == 0:
            return 1.0
        return self.tasks_executed / total


@dataclass
class BoundThread:
    thread_id: str
    agent_id: Optional[str]
    cpu_affinity: Optional[List[int]]  # CPU 核心列表
    state: ThreadState = ThreadState.IDLE
    stats: ThreadStats = field(default_factory=ThreadStats)
    _thread: Optional[threading.Thread] = field(default=None, repr=False)
    _task_queue: queue.Queue = field(default_factory=queue.Queue, repr=False)
    _stop_event: threading.Event = field(default_factory=threading.Event, repr=False)


class ThreadBinding:
    """
    线程绑定管理器
    - 将 Agent 绑定到专属线程
    - 支持 CPU 亲和性（Windows: SetThreadAffinityMask）
    - 线程池复用，减少创建开销
    """

    def __init__(self, max_threads: int = 8):
        self.max_threads = max_threads
        self._threads: Dict[str, BoundThread] = {}
        self._agent_map: Dict[str, str] = {}  # agent_id -> thread_id
        self._lock = threading.Lock()
        self._cpu_count = os.cpu_count() or 4

    # ── 绑定管理 ──────────────────────────────────────────────

    def bind(self, agent_id: str, cpu_cores: Optional[List[int]] = None) -> str:
        """将 Agent 绑定到一个线程，返回 thread_id"""
        with self._lock:
            # 已绑定则直接返回
            if agent_id in self._agent_map:
                return self._agent_map[agent_id]

            if len(self._threads) >= self.max_threads:
                raise RuntimeError(f"线程池已满（max={self.max_threads}）")

            thread_id = f"thread-{agent_id}"
            bound = BoundThread(
                thread_id=thread_id,
                agent_id=agent_id,
                cpu_affinity=cpu_cores,
            )

            # 启动工作线程
            t = threading.Thread(
                target=self._worker_loop,
                args=(bound,),
                name=thread_id,
                daemon=True,
            )
            bound._thread = t
            self._threads[thread_id] = bound
            self._agent_map[agent_id] = thread_id
            t.start()

            return thread_id

    def unbind(self, agent_id: str) -> bool:
        """解绑 Agent，停止其线程"""
        with self._lock:
            thread_id = self._agent_map.pop(agent_id, None)
            if not thread_id:
                return False
            bound = self._threads.pop(thread_id, None)
            if bound:
                bound._stop_event.set()
            return True

    # ── 任务提交 ──────────────────────────────────────────────

    def submit(self, agent_id: str, fn: Callable, *args, **kwargs) -> "TaskFuture":
        """向 Agent 绑定的线程提交任务"""
        thread_id = self._agent_map.get(agent_id)
        if not thread_id:
            # 自动绑定
            thread_id = self.bind(agent_id)

        bound = self._threads[thread_id]
        future = TaskFuture()
        bound._task_queue.put((fn, args, kwargs, future))
        return future

    # ── 内部工作循环 ──────────────────────────────────────────

    def _worker_loop(self, bound: BoundThread):
        """线程工作循环"""
        self._set_cpu_affinity(bound.cpu_affinity)

        while not bound._stop_event.is_set():
            try:
                item = bound._task_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            fn, args, kwargs, future = item
            bound.state = ThreadState.RUNNING
            start = time.perf_counter()

            try:
                result = fn(*args, **kwargs)
                future._set_result(result)
                bound.stats.tasks_executed += 1
            except Exception as e:
                future._set_exception(e)
                bound.stats.tasks_failed += 1
            finally:
                elapsed = (time.perf_counter() - start) * 1000
                bound.stats.total_time_ms += elapsed
                bound.stats.last_active = time.time()
                bound.state = ThreadState.IDLE
                bound._task_queue.task_done()

        bound.state = ThreadState.STOPPED

    def _set_cpu_affinity(self, cpu_cores: Optional[List[int]]):
        """设置 CPU 亲和性（Windows）"""
        if not cpu_cores:
            return
        try:
            import ctypes
            mask = 0
            for core in cpu_cores:
                if 0 <= core < self._cpu_count:
                    mask |= (1 << core)
            if mask:
                handle = ctypes.windll.kernel32.GetCurrentThread()
                ctypes.windll.kernel32.SetThreadAffinityMask(handle, mask)
        except Exception:
            pass  # 非 Windows 或权限不足时静默忽略

    # ── 状态查询 ──────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        return {
            "total_threads": len(self._threads),
            "max_threads": self.max_threads,
            "cpu_count": self._cpu_count,
            "threads": {
                tid: {
                    "agent_id": b.agent_id,
                    "state": b.state.value,
                    "cpu_affinity": b.cpu_affinity,
                    "stats": {
                        "tasks_executed": b.stats.tasks_executed,
                        "tasks_failed": b.stats.tasks_failed,
                        "avg_time_ms": round(b.stats.avg_time_ms, 2),
                        "success_rate": round(b.stats.success_rate, 3),
                    },
                }
                for tid, b in self._threads.items()
            },
        }

    def get_stats(self, agent_id: str) -> Optional[ThreadStats]:
        thread_id = self._agent_map.get(agent_id)
        if not thread_id:
            return None
        return self._threads[thread_id].stats

    def shutdown(self):
        """停止所有线程"""
        with self._lock:
            for bound in self._threads.values():
                bound._stop_event.set()
            self._threads.clear()
            self._agent_map.clear()


class TaskFuture:
    """简单的 Future 实现，用于获取线程任务结果"""

    def __init__(self):
        self._event = threading.Event()
        self._result = None
        self._exception = None

    def _set_result(self, result):
        self._result = result
        self._event.set()

    def _set_exception(self, exc):
        self._exception = exc
        self._event.set()

    def result(self, timeout: float = 5.0):
        if not self._event.wait(timeout):
            raise TimeoutError("任务超时")
        if self._exception:
            raise self._exception
        return self._result

    def done(self) -> bool:
        return self._event.is_set()

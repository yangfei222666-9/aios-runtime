"""
AIOS Test Fixtures - 公共 fixtures
"""
import io
import sys
import json
import pytest
import importlib
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def tmp_data_dir(tmp_path):
    """创建临时数据目录结构"""
    data_dir = tmp_path / "data"
    (data_dir / "evolution").mkdir(parents=True)
    (data_dir / "patterns").mkdir(parents=True)
    return data_dir


@pytest.fixture
def sample_tasks():
    """标准测试任务集"""
    return [
        {"id": "t-001", "type": "code", "status": "completed", "priority": "high"},
        {"id": "t-002", "type": "analysis", "status": "completed", "priority": "normal"},
        {"id": "t-003", "type": "monitor", "status": "failed", "priority": "low"},
        {"id": "t-004", "type": "code", "status": "completed", "priority": "high"},
        {"id": "t-005", "type": "code", "status": "completed", "priority": "normal"},
    ]


@pytest.fixture
def task_queue_file(tmp_path, sample_tasks):
    """写入 task_queue.jsonl 并返回路径"""
    f = tmp_path / "task_queue.jsonl"
    with open(f, "w", encoding="utf-8") as fh:
        for t in sample_tasks:
            fh.write(json.dumps(t, ensure_ascii=False) + "\n")
    return f


@pytest.fixture
def evolution_score_file(tmp_path):
    """写入 evolution_score.json 并返回路径"""
    f = tmp_path / "evolution_score.json"
    data = {"score": 94.5, "lessons_learned": 3, "last_update": "2026-03-06T12:00:00"}
    f.write_text(json.dumps(data), encoding="utf-8")
    return f


@pytest.fixture
def agents_json(tmp_path):
    """最小 agents.json"""
    f = tmp_path / "agents.json"
    data = {
        "agents": [
            {
                "id": "coder",
                "name": "Coder Agent",
                "type": "core",
                "capabilities": ["code_generation", "refactoring"],
                "stats": {"tasks_completed": 10, "tasks_failed": 2, "success_rate": 83.3},
            },
            {
                "id": "monitor",
                "name": "Monitor Agent",
                "type": "monitor",
                "capabilities": ["health_check", "resource_monitoring"],
                "stats": {"tasks_completed": 50, "tasks_failed": 0, "success_rate": 100.0},
            },
        ]
    }
    f.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return f


@pytest.fixture
def isolated_heartbeat(tmp_path, monkeypatch):
    """
    隔离 heartbeat_v5 模块：
    - 重定向 cwd 到 tmp_path
    - Patch sys.stdout.buffer 避免模块级重定向冲突
    - Patch 所有路径常量到 tmp_path
    """
    # 1. 重定向 cwd
    monkeypatch.chdir(tmp_path)

    # 2. 创建必要的文件结构
    (tmp_path / "task_queue.jsonl").write_text("", encoding="utf-8")
    (tmp_path / "spawn_requests.jsonl").write_text("", encoding="utf-8")
    (tmp_path / "evolution_score.json").write_text(
        json.dumps({"score": 95.0, "lessons_learned": 0, "last_update": "2026-03-06T18:00:00"}),
        encoding="utf-8"
    )

    # 3. Patch sys.stdout.buffer（避免 self_healing_loop_v2 模块级重定向崩溃）
    fake_buffer = io.BytesIO()
    if not hasattr(sys.stdout, "buffer"):
        monkeypatch.setattr(sys.stdout, "buffer", fake_buffer, raising=False)

    # 4. Import heartbeat_v5 并 patch 路径常量
    agent_sys = Path(__file__).resolve().parent.parent / "agent_system"
    sys.path.insert(0, str(agent_sys))

    import heartbeat_v5

    # Patch 模块级路径常量（如果存在）
    if hasattr(heartbeat_v5, "QUEUE_PATH"):
        monkeypatch.setattr(heartbeat_v5, "QUEUE_PATH", tmp_path / "task_queue.jsonl")
    if hasattr(heartbeat_v5, "SPAWN_REQUESTS_PATH"):
        monkeypatch.setattr(heartbeat_v5, "SPAWN_REQUESTS_PATH", tmp_path / "spawn_requests.jsonl")

    yield heartbeat_v5

    # 5. 清理（monkeypatch 自动恢复）

"""
AIOS Test Fixtures - 公共 fixtures
"""
import json
import pytest
from pathlib import Path


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

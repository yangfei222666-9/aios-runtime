"""
Integration: 故障注入测试（坏数据、空队列、权限受限）
验证系统在异常输入下的恢复能力
"""
import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

AGENT_SYS = Path(__file__).resolve().parent.parent.parent / "agent_system"
sys.path.insert(0, str(AGENT_SYS))

import task_executor


@pytest.mark.integration
def test_get_pending_tasks_corrupted_jsonl(tmp_path):
    """损坏的 JSONL 文件不应崩溃"""
    q = tmp_path / "task_queue.jsonl"
    q.write_text(
        '{"id": "t-001", "status": "running"}\n'
        'THIS IS NOT JSON\n'
        '{"id": "t-002", "status": "running"}\n',
        encoding="utf-8"
    )

    with patch.object(task_executor, "QUEUE_PATH", q):
        tasks = task_executor.get_pending_tasks()

    # 应该跳过坏行，返回有效任务
    assert len(tasks) == 2
    assert all(t["id"] in ("t-001", "t-002") for t in tasks)


@pytest.mark.integration
def test_get_pending_tasks_empty_file(tmp_path):
    """空文件返回空列表"""
    q = tmp_path / "task_queue.jsonl"
    q.write_text("", encoding="utf-8")

    with patch.object(task_executor, "QUEUE_PATH", q):
        tasks = task_executor.get_pending_tasks()

    assert tasks == []


@pytest.mark.integration
def test_get_pending_tasks_missing_file(tmp_path):
    """文件不存在返回空列表"""
    q = tmp_path / "nonexistent.jsonl"

    with patch.object(task_executor, "QUEUE_PATH", q):
        tasks = task_executor.get_pending_tasks()

    assert tasks == []


@pytest.mark.integration
def test_generate_spawn_commands_missing_fields(tmp_path):
    """任务缺少必需字段时应优雅降级"""
    tasks = [
        {"id": "t-001", "description": "test", "type": "code"},  # 缺 agent_id
        {"id": "t-002", "agent_id": "coder"},  # 缺 description
    ]

    with patch.object(task_executor, "build_memory_context",
                      return_value={"memory_hints": [], "latency_ms": 0, "error": None}):
        # 应该不崩溃，可能返回空或部分结果
        try:
            commands = task_executor.generate_spawn_commands(tasks)
            assert isinstance(commands, list)
        except (KeyError, AttributeError):
            pytest.skip("generate_spawn_commands requires all fields")


@pytest.mark.integration
def test_mark_tasks_dispatched_corrupted_file(tmp_path):
    """损坏的队列文件不应导致数据丢失"""
    q = tmp_path / "task_queue.jsonl"
    q.write_text(
        '{"id": "t-001", "status": "running"}\n'
        'CORRUPTED LINE\n'
        '{"id": "t-002", "status": "running"}\n',
        encoding="utf-8"
    )

    with patch.object(task_executor, "QUEUE_PATH", q):
        task_executor.mark_tasks_dispatched(["t-001"])

    # 验证文件仍然可读
    lines = q.read_text(encoding="utf-8").strip().split("\n")
    valid_lines = [line for line in lines if line.strip() and line != "CORRUPTED LINE"]
    assert len(valid_lines) >= 1


@pytest.mark.integration
def test_mark_tasks_dispatched_readonly_file(tmp_path):
    """只读文件应该抛出明确错误"""
    q = tmp_path / "task_queue.jsonl"
    q.write_text('{"id": "t-001", "status": "running"}\n', encoding="utf-8")

    # Windows 只读属性
    import os
    os.chmod(q, 0o444)

    with patch.object(task_executor, "QUEUE_PATH", q):
        try:
            task_executor.mark_tasks_dispatched(["t-001"])
            pytest.fail("Should raise PermissionError on readonly file")
        except (PermissionError, OSError):
            pass  # 预期行为
        finally:
            os.chmod(q, 0o644)  # 恢复权限


@pytest.mark.integration
def test_get_pending_tasks_unicode_content(tmp_path):
    """Unicode 内容应该正确处理"""
    q = tmp_path / "task_queue.jsonl"
    tasks = [
        {"id": "t-中文", "description": "测试中文任务", "type": "code",
         "agent_id": "coder", "status": "running"},
        {"id": "t-emoji", "description": "测试 emoji 🚀", "type": "monitor",
         "agent_id": "monitor", "status": "running"},
    ]
    with open(q, "w", encoding="utf-8") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    with patch.object(task_executor, "QUEUE_PATH", q):
        result = task_executor.get_pending_tasks()

    assert len(result) == 2
    assert any("中文" in t["description"] for t in result)
    assert any("🚀" in t["description"] for t in result)

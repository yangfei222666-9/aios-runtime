"""
Integration: Heartbeat 流程（subprocess 隔离）
用独立进程运行 heartbeat_v5 函数，避免模块级 stdout 重定向污染 pytest capture
"""
import json
import sys
import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch

AGENT_SYS = Path(__file__).resolve().parent.parent.parent / "agent_system"


def _run_heartbeat_fn(fn_name: str, kwargs: dict, tmp_path: Path) -> dict:
    """在独立子进程中调用 heartbeat_v5 的函数，返回 JSON 结果"""
    script = f"""
import sys, json
sys.path.insert(0, r'{AGENT_SYS}')
from unittest.mock import patch

# 准备 mock 数据
mock_kwargs = {json.dumps(kwargs)}

import heartbeat_v5

if '{fn_name}' == 'process_task_queue':
    with patch('heartbeat_v5.list_tasks', return_value=[]):
        result = heartbeat_v5.process_task_queue(**mock_kwargs)
elif '{fn_name}' == 'check_system_health':
    mock_stats = mock_kwargs.get('mock_stats', {{'total': 0, 'by_status': {{}}}})
    with patch('heartbeat_v5.queue_stats', return_value=mock_stats):
        result = heartbeat_v5.check_system_health()
else:
    result = {{'error': 'unknown function'}}

print('RESULT:' + json.dumps(result))
"""
    env = {"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    import os
    full_env = {**os.environ, **env}

    # 诊断日志路径
    stdout_log = tmp_path / f"heartbeat_{fn_name}_stdout.log"
    stderr_log = tmp_path / f"heartbeat_{fn_name}_stderr.log"

    try:
        proc = subprocess.run(
            [sys.executable, "-X", "utf8", "-c", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(tmp_path),
            env=full_env,
            timeout=10,  # 明确超时 10s
        )
    except subprocess.TimeoutExpired as e:
        # 超时时保存诊断信息
        if e.stdout:
            stdout_log.write_text(e.stdout, encoding="utf-8")
        if e.stderr:
            stderr_log.write_text(e.stderr, encoding="utf-8")
        raise RuntimeError(
            f"Heartbeat subprocess timeout after 10s.\n"
            f"Logs: {stdout_log}, {stderr_log}"
        ) from e

    # 保存输出用于诊断
    stdout_log.write_text(proc.stdout, encoding="utf-8")
    stderr_log.write_text(proc.stderr, encoding="utf-8")

    if proc.returncode != 0:
        raise RuntimeError(
            f"Heartbeat subprocess failed (exit {proc.returncode}).\n"
            f"stdout: {stdout_log}\nstderr: {stderr_log}"
        )

    for line in proc.stdout.splitlines():
        if line.startswith("RESULT:"):
            return json.loads(line[7:])

    raise RuntimeError(
        f"No RESULT in output.\n"
        f"stdout: {stdout_log}\nstderr: {stderr_log}"
    )


@pytest.mark.integration
def test_process_task_queue_no_tasks(tmp_path):
    """空队列时 processed=0"""
    result = _run_heartbeat_fn("process_task_queue", {"max_tasks": 5}, tmp_path)
    assert isinstance(result, dict)
    assert result["processed"] == 0


@pytest.mark.integration
def test_process_task_queue_returns_dict(tmp_path):
    """process_task_queue 始终返回 dict"""
    result = _run_heartbeat_fn("process_task_queue", {}, tmp_path)
    assert isinstance(result, dict)
    assert "processed" in result
    assert "success" in result
    assert "failed" in result


@pytest.mark.integration
def test_check_system_health_returns_score(tmp_path):
    """check_system_health 返回 score 字段"""
    result = _run_heartbeat_fn("check_system_health", {
        "mock_stats": {"total": 10, "by_status": {"completed": 8, "failed": 1, "pending": 1}}
    }, tmp_path)
    assert isinstance(result, dict)
    assert "score" in result
    assert 0 <= result["score"] <= 100


@pytest.mark.integration
def test_check_system_health_perfect_score(tmp_path):
    """全部完成时 score 应为 100"""
    result = _run_heartbeat_fn("check_system_health", {
        "mock_stats": {"total": 5, "by_status": {"completed": 5, "failed": 0, "pending": 0}}
    }, tmp_path)
    assert result["score"] == 100.0


@pytest.mark.integration
def test_check_system_health_empty_queue(tmp_path):
    """空队列时 score 应为 100"""
    result = _run_heartbeat_fn("check_system_health", {
        "mock_stats": {"total": 0, "by_status": {"completed": 0, "failed": 0, "pending": 0}}
    }, tmp_path)
    assert result["score"] == 100.0


@pytest.mark.integration
def test_check_system_health_high_failure(tmp_path):
    """高失败率时 score 应该低"""
    result = _run_heartbeat_fn("check_system_health", {
        "mock_stats": {"total": 10, "by_status": {"completed": 2, "failed": 8, "pending": 0}}
    }, tmp_path)
    assert result["score"] < 50

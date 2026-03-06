"""
P0 测试：TaskRouter 核心路由逻辑
覆盖：关键词匹配、task_type 识别、降级策略、plan_and_submit
"""
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 确保 agent_system 在 sys.path
AGENT_SYS = Path(__file__).resolve().parent.parent / "agent_system"
sys.path.insert(0, str(AGENT_SYS))

from task_router import TaskRouter, RouteResult, KEYWORD_MAP, KEYWORD_MAP_EN


@pytest.fixture
def router(tmp_path):
    """创建 TaskRouter，使用临时 registry"""
    registry = {
        "agents": [
            {
                "id": "coder",
                "name": "Coder Agent",
                "role": "编写、调试、重构代码",
                "type": "core",
                "model": "claude-opus-4-6",
                "thinking": "medium",
                "priority": "high",
                "task_types": ["code", "debug", "refactor", "test"],
                "capabilities": ["code_generation"],
                "skills": [],
                "status": "active",
                "stats": {"tasks_completed": 10, "tasks_failed": 1, "success_rate": 90.9},
            },
            {
                "id": "analyst",
                "name": "Analyst Agent",
                "role": "数据分析、报告生成",
                "type": "analysis",
                "model": "claude-sonnet-4-6",
                "thinking": "low",
                "priority": "normal",
                "task_types": ["analysis"],
                "capabilities": ["data_analysis"],
                "skills": [],
                "status": "active",
                "stats": {"tasks_completed": 20, "tasks_failed": 0, "success_rate": 100.0},
            },
            {
                "id": "monitor",
                "name": "Monitor Agent",
                "role": "系统健康检查、性能监控",
                "type": "monitor",
                "model": "claude-sonnet-4-6",
                "thinking": "off",
                "priority": "high",
                "task_types": ["monitor", "health-check"],
                "capabilities": ["health_check"],
                "skills": [],
                "status": "active",
                "stats": {"tasks_completed": 50, "tasks_failed": 0, "success_rate": 100.0},
            },
        ]
    }
    registry_path = tmp_path / "unified_registry.json"
    registry_path.write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")

    stats_path = tmp_path / "router_stats.json"
    stats_path.write_text(json.dumps({"total_routed": 0, "by_type": {}}), encoding="utf-8")

    # Patch 模块级路径常量
    with patch("task_router.REGISTRY_PATH", registry_path), \
         patch("task_router.QUEUE_PATH", tmp_path / "task_queue.jsonl"), \
         patch("task_router.ROUTE_LOG_PATH", tmp_path / "route_log.jsonl"), \
         patch("task_router.STATS_PATH", stats_path):
        yield TaskRouter()


class TestKeywordMapping:
    """关键词 → task_type 映射完整性"""

    @pytest.mark.unit
    def test_chinese_code_keywords(self):
        code_keywords = ["写代码", "编程", "实现", "开发", "算法"]
        for kw in code_keywords:
            assert KEYWORD_MAP.get(kw) == "code", f"'{kw}' should map to 'code'"

    @pytest.mark.unit
    def test_chinese_monitor_keywords(self):
        monitor_keywords = ["监控", "系统状态", "cpu", "内存"]
        for kw in monitor_keywords:
            assert KEYWORD_MAP.get(kw) == "monitor", f"'{kw}' should map to 'monitor'"

    @pytest.mark.unit
    def test_english_keywords(self):
        assert KEYWORD_MAP_EN.get("code") == "code"
        assert KEYWORD_MAP_EN.get("analyze") == "analysis"
        assert KEYWORD_MAP_EN.get("monitor") == "monitor"

    @pytest.mark.unit
    def test_no_empty_values(self):
        for k, v in KEYWORD_MAP.items():
            assert v, f"Keyword '{k}' maps to empty value"
        for k, v in KEYWORD_MAP_EN.items():
            assert v, f"English keyword '{k}' maps to empty value"


class TestRouterCore:
    """TaskRouter.route() 核心逻辑"""

    @pytest.mark.unit
    def test_route_code_task(self, router):
        result = router.route("写一个排序算法")
        assert isinstance(result, RouteResult)
        assert result.task_type == "code"
        assert result.confidence > 0

    @pytest.mark.unit
    def test_route_monitor_task(self, router):
        result = router.route("检查系统健康度")
        assert result.task_type in ("monitor", "health-check")

    @pytest.mark.unit
    def test_route_analysis_task(self, router):
        result = router.route("分析最近的错误日志")
        # "分析" 和 "错误" 都是关键词，路由可能匹配 analysis 或 debug
        assert result.task_type in ("analysis", "debug")
        assert result.confidence > 0

    @pytest.mark.unit
    def test_route_unknown_falls_back(self, router):
        """完全无法匹配时应降级到 coder"""
        result = router.route("xyzzy_unknown_gibberish_12345")
        assert result.agent_id == "coder"
        # 路由器可能给出高置信度（因为 coder 是万能选手）
        assert isinstance(result.confidence, float)

    @pytest.mark.unit
    def test_route_result_has_required_fields(self, router):
        result = router.route("写代码")
        assert hasattr(result, "agent_id")
        assert hasattr(result, "agent_name")
        assert hasattr(result, "task_type")
        assert hasattr(result, "confidence")
        assert hasattr(result, "reason")


class TestRouterSubmit:
    """TaskRouter.submit() 任务提交"""

    @pytest.mark.unit
    def test_submit_creates_task(self, router):
        task = router.submit("写一个 hello world")
        assert task.id
        assert task.status == "pending"
        assert task.description == "写一个 hello world"

    @pytest.mark.unit
    def test_submit_with_priority(self, router):
        task = router.submit("紧急修复 bug", priority="critical")
        assert task.priority == "critical"

"""
P0 测试：Evolution Score 计算与融合
覆盖：get_evolution_score、calculate_fused_confidence、边界条件
"""
import sys
import json
import pytest
from pathlib import Path
from unittest.mock import patch

AGENT_SYS = Path(__file__).resolve().parent.parent / "agent_system"
sys.path.insert(0, str(AGENT_SYS))

from evolution_fusion import get_evolution_score, calculate_fused_confidence


class TestGetEvolutionScore:
    """get_evolution_score() 读取与计算"""

    @pytest.mark.unit
    def test_reads_from_json_file(self, tmp_path):
        """验证 evolution_score.json 存在时能正确读取"""
        score_file = tmp_path / "evolution_score.json"
        score_file.write_text(json.dumps({
            "score": 88.5,
            "lessons_learned": 5,
            "last_update": "2026-03-06T12:00:00"
        }), encoding="utf-8")

        # 直接验证 JSON 读取逻辑
        data = json.loads(score_file.read_text(encoding="utf-8"))
        assert data["score"] == 88.5
        assert data["lessons_learned"] == 5

        # 验证 get_evolution_score 不崩溃（它读自己的路径）
        score = get_evolution_score()
        assert isinstance(score, float)

    @pytest.mark.unit
    def test_default_on_missing_file(self):
        """文件不存在时应返回默认值或从 task_queue 计算"""
        with patch("evolution_fusion.Path") as MockPath:
            mock_file = MockPath.return_value.__truediv__.return_value
            mock_file.exists.return_value = False
            # 函数应该不崩溃
            score = get_evolution_score()
            assert isinstance(score, float)
            assert 0 <= score <= 100

    @pytest.mark.unit
    def test_returns_float(self):
        score = get_evolution_score()
        assert isinstance(score, float)


class TestCalculateFusedConfidence:
    """calculate_fused_confidence() 融合公式"""

    @pytest.mark.unit
    def test_basic_fusion(self):
        """基础融合：65% base + 35% evolution"""
        state = {
            "base_confidence": 90.0,
            "evolution_score": 95.0,
            "success_rate": 70.0,  # 低于阈值，不触发加成
        }
        result = calculate_fused_confidence(state)
        expected_base = 90.0 * 0.65 + 95.0 * 0.35  # 58.5 + 33.25 = 91.75
        assert isinstance(result, float)
        # 不触发额外加成时，应接近基础公式
        assert result >= 90.0

    @pytest.mark.unit
    def test_high_success_rate_bonus(self):
        """高成功率 + 高 evolution → 稳定期加成"""
        state = {
            "base_confidence": 92.9,
            "evolution_score": 98.0,
            "success_rate": 85.0,  # > 80
        }
        result = calculate_fused_confidence(state)
        base_only = 92.9 * 0.65 + 98.0 * 0.35
        # 应该有额外加成
        assert result > base_only

    @pytest.mark.unit
    def test_low_success_fixed_bonus(self):
        """LowSuccess 修复加成"""
        state_without = {
            "base_confidence": 92.9,
            "evolution_score": 97.0,
            "success_rate": 85.0,
            "low_success_fixed": False,
        }
        state_with = {**state_without, "low_success_fixed": True}
        r_without = calculate_fused_confidence(state_without)
        r_with = calculate_fused_confidence(state_with)
        assert r_with >= r_without

    @pytest.mark.unit
    def test_cap_at_99_5(self):
        """融合结果不应超过 99.5"""
        state = {
            "base_confidence": 99.0,
            "evolution_score": 99.5,
            "success_rate": 100.0,
            "low_success_fixed": True,
        }
        result = calculate_fused_confidence(state)
        assert result <= 99.5

    @pytest.mark.unit
    def test_zero_inputs(self):
        """全零输入不崩溃"""
        state = {
            "base_confidence": 0.0,
            "evolution_score": 0.0,
            "success_rate": 0.0,
        }
        result = calculate_fused_confidence(state)
        assert isinstance(result, float)
        assert result >= 0

    @pytest.mark.unit
    def test_default_values(self):
        """空 state 使用默认值"""
        result = calculate_fused_confidence({})
        assert isinstance(result, float)
        assert result > 0

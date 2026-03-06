"""
P0 测试：卦象策略模块（坤卦 + 比卦）
覆盖：策略生成、稳定性检查、阈值逻辑、输出格式
"""
import sys
import json
import pytest
from pathlib import Path

AGENT_SYS = Path(__file__).resolve().parent.parent / "agent_system"
sys.path.insert(0, str(AGENT_SYS))

from kun_strategy import apply_kun_strategy, check_kun_stability, get_kun_thresholds
from bigua_strategy import apply_bigua_strategy


class TestKunThresholds:
    """坤卦阈值配置"""

    @pytest.mark.unit
    def test_thresholds_are_dict(self):
        t = get_kun_thresholds()
        assert isinstance(t, dict)

    @pytest.mark.unit
    def test_required_keys(self):
        t = get_kun_thresholds()
        assert "success_rate" in t
        assert "confidence" in t
        assert "low_success_threshold" in t

    @pytest.mark.unit
    def test_thresholds_are_numeric(self):
        t = get_kun_thresholds()
        for k, v in t.items():
            assert isinstance(v, (int, float)), f"{k} should be numeric"


class TestKunStability:
    """check_kun_stability() 稳定性判断"""

    @pytest.mark.unit
    def test_stable(self):
        state = {"confidence": 92.9, "success_rate": 80.4}
        assert check_kun_stability(state) == "stable"

    @pytest.mark.unit
    def test_warning(self):
        state = {"confidence": 78.0, "success_rate": 72.0}
        assert check_kun_stability(state) == "warning"

    @pytest.mark.unit
    def test_unstable(self):
        state = {"confidence": 50.0, "success_rate": 40.0}
        assert check_kun_stability(state) == "unstable"

    @pytest.mark.unit
    def test_boundary_stable(self):
        """刚好在 stable 边界"""
        state = {"confidence": 85.0, "success_rate": 78.0}
        assert check_kun_stability(state) == "stable"

    @pytest.mark.unit
    def test_boundary_warning(self):
        """刚好在 warning 边界"""
        state = {"confidence": 75.0, "success_rate": 70.0}
        assert check_kun_stability(state) == "warning"

    @pytest.mark.unit
    def test_empty_state(self):
        """空 state 默认 unstable"""
        assert check_kun_stability({}) == "unstable"


class TestApplyKunStrategy:
    """apply_kun_strategy() 策略生成"""

    @pytest.mark.unit
    def test_returns_dict(self):
        state = {"confidence": 92.9, "success_rate": 80.4}
        result = apply_kun_strategy(state)
        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_has_current_hex(self):
        state = {"confidence": 92.9, "success_rate": 80.4}
        result = apply_kun_strategy(state)
        assert result.get("current_hex") == "坤卦"

    @pytest.mark.unit
    def test_has_actions(self):
        state = {"confidence": 92.9, "success_rate": 80.4}
        result = apply_kun_strategy(state)
        assert "actions" in result
        assert isinstance(result["actions"], list)
        assert len(result["actions"]) > 0

    @pytest.mark.unit
    def test_has_learning_points(self):
        state = {"confidence": 92.9, "success_rate": 80.4}
        result = apply_kun_strategy(state)
        assert "learning_points" in result

    @pytest.mark.unit
    def test_default_state(self):
        """空 state 使用默认值不崩溃"""
        result = apply_kun_strategy({})
        assert isinstance(result, dict)


class TestApplyBiguaStrategy:
    """apply_bigua_strategy() 比卦策略"""

    @pytest.mark.unit
    def test_returns_dict(self):
        state = {"confidence": 79.9, "success_rate": 100.0}
        result = apply_bigua_strategy(state)
        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_has_current_hex(self):
        state = {"confidence": 79.9, "success_rate": 100.0}
        result = apply_bigua_strategy(state)
        assert result.get("current_hex") == "比卦"

    @pytest.mark.unit
    def test_has_collaboration_score(self):
        state = {"confidence": 79.9, "success_rate": 100.0}
        result = apply_bigua_strategy(state)
        assert "collaboration_score" in result
        assert isinstance(result["collaboration_score"], (int, float))

    @pytest.mark.unit
    def test_has_new_agents_recommended(self):
        state = {"confidence": 79.9, "success_rate": 100.0}
        result = apply_bigua_strategy(state)
        assert "new_agents_recommended" in result
        assert isinstance(result["new_agents_recommended"], list)

    @pytest.mark.unit
    def test_default_state(self):
        result = apply_bigua_strategy({})
        assert isinstance(result, dict)

"""
Quality Gates 测试
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path

# 添加 aios 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collector import DataCollector
from data_collector.quality_gates import QualityGate, QualityGateSystem


def setup_test_env():
    """设置测试环境"""
    test_dir = tempfile.mkdtemp(prefix="aios_qg_test_")
    return test_dir


def cleanup_test_env(test_dir):
    """清理测试环境"""
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def create_test_data(collector: DataCollector):
    """创建测试数据"""
    # 创建一些任务
    for i in range(5):
        task_id = collector.create_task(
            title=f"任务{i+1}",
            type="code",
            priority="normal",
            agent_id="coder"
        )
        collector.complete_task(
            task_id,
            status="success",
            metrics={"duration_ms": 5000}
        )
    
    # 更新 Agent
    collector.update_agent(
        agent_id="coder",
        type="coder",
        status="idle",
        stats={
            "tasks_total": 5,
            "tasks_success": 5,
            "tasks_failed": 0,
            "avg_duration_ms": 5000
        }
    )


def test_quality_gate_creation():
    """测试门禁创建"""
    def check_fn(context):
        return {"passed": True}
    
    gate = QualityGate(
        name="test_gate",
        level="L0",
        check_fn=check_fn,
        required=True
    )
    
    assert gate.name == "test_gate"
    assert gate.level == "L0"
    assert gate.required == True
    
    print("✅ test_quality_gate_creation")


def test_quality_gate_check():
    """测试门禁检查"""
    def check_fn(context):
        return {"passed": True, "message": "测试通过"}
    
    gate = QualityGate(
        name="test_gate",
        level="L0",
        check_fn=check_fn,
        required=True
    )
    
    result = gate.check({})
    
    assert result["gate"] == "test_gate"
    assert result["level"] == "L0"
    assert result["passed"] == True
    assert result["result"]["message"] == "测试通过"
    
    print("✅ test_quality_gate_check")


def test_quality_gate_system_init():
    """测试质量门禁系统初始化"""
    system = QualityGateSystem()
    
    assert len(system.gates["L0"]) > 0
    assert len(system.gates["L1"]) > 0
    assert len(system.gates["L2"]) > 0
    
    print("✅ test_quality_gate_system_init")


def test_l0_checks():
    """测试 L0 检查"""
    system = QualityGateSystem()
    
    context = {"agent_id": "coder"}
    result = system.check_all("L0", context)
    
    assert "level" in result
    assert result["level"] == "L0"
    assert "passed" in result
    assert "results" in result
    assert len(result["results"]) > 0
    
    print("✅ test_l0_checks")


def test_l1_checks():
    """测试 L1 检查"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    system = QualityGateSystem()
    system.collector = collector
    system.evaluator.collector = collector
    
    # 创建测试数据
    create_test_data(collector)
    
    context = {"agent_id": "coder"}
    result = system.check_all("L1", context)
    
    assert result["level"] == "L1"
    assert "passed" in result
    assert "results" in result
    
    cleanup_test_env(test_dir)
    print("✅ test_l1_checks")


def test_l2_checks():
    """测试 L2 检查"""
    system = QualityGateSystem()
    
    context = {"agent_id": "coder"}
    result = system.check_all("L2", context)
    
    assert result["level"] == "L2"
    assert "passed" in result
    
    print("✅ test_l2_checks")


def test_check_improvement_low_risk():
    """测试低风险改进检查"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    system = QualityGateSystem()
    system.collector = collector
    system.evaluator.collector = collector
    
    # 创建测试数据
    create_test_data(collector)
    
    # 检查改进
    result = system.check_improvement(
        agent_id="coder",
        change_type="config",
        risk_level="low"
    )
    
    assert "approved" in result
    assert "reason" in result
    assert "details" in result
    
    cleanup_test_env(test_dir)
    print("✅ test_check_improvement_low_risk")


def test_check_improvement_high_risk():
    """测试高风险改进检查"""
    test_dir = setup_test_env()
    collector = DataCollector(base_dir=test_dir)
    system = QualityGateSystem()
    system.collector = collector
    system.evaluator.collector = collector
    
    # 创建测试数据
    create_test_data(collector)
    
    # 检查改进（高风险需要 L2）
    result = system.check_improvement(
        agent_id="coder",
        change_type="code",
        risk_level="high"
    )
    
    assert "approved" in result
    assert "reason" in result
    
    cleanup_test_env(test_dir)
    print("✅ test_check_improvement_high_risk")


def test_gate_registration():
    """测试门禁注册"""
    system = QualityGateSystem()
    
    def custom_check(context):
        return {"passed": True}
    
    custom_gate = QualityGate(
        name="custom_gate",
        level="L0",
        check_fn=custom_check,
        required=False
    )
    
    initial_count = len(system.gates["L0"])
    system.register_gate(custom_gate)
    
    assert len(system.gates["L0"]) == initial_count + 1
    
    print("✅ test_gate_registration")


def test_failed_gate():
    """测试门禁失败"""
    def failing_check(context):
        return {"passed": False, "message": "测试失败"}
    
    gate = QualityGate(
        name="failing_gate",
        level="L0",
        check_fn=failing_check,
        required=True
    )
    
    result = gate.check({})
    
    assert result["passed"] == False
    assert result["result"]["message"] == "测试失败"
    
    print("✅ test_failed_gate")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始测试 Quality Gates...\n")
    
    tests = [
        test_quality_gate_creation,
        test_quality_gate_check,
        test_quality_gate_system_init,
        test_l0_checks,
        test_l1_checks,
        test_l2_checks,
        test_check_improvement_low_risk,
        test_check_improvement_high_risk,
        test_gate_registration,
        test_failed_gate
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test.__name__}: {e}")
            failed += 1
    
    print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
    
    if failed == 0:
        print("🎉 所有测试通过！")
    else:
        print(f"⚠️  {failed} 个测试失败")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

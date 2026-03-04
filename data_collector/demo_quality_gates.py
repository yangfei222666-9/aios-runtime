"""
Quality Gates 演示脚本

展示质量门禁系统的核心功能：
1. L0 自动测试
2. L1 回归测试
3. L2 人工审核
4. 改进检查
"""

import sys
from pathlib import Path

# 添加 aios 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collector import DataCollector
from data_collector.quality_gates import QualityGateSystem


def demo():
    """演示 Quality Gates 功能"""
    print("🚀 Quality Gates 演示\n")
    
    # 初始化
    collector = DataCollector()
    system = QualityGateSystem()
    print("✅ Quality Gates 初始化完成\n")
    
    # 创建一些测试数据
    print("📝 创建测试数据...")
    
    for i in range(5):
        task_id = collector.create_task(
            title=f"测试任务 {i+1}",
            type="code",
            priority="normal",
            agent_id="coder"
        )
        collector.complete_task(
            task_id,
            status="success",
            metrics={"duration_ms": 5000 + i * 100}
        )
    
    collector.update_agent(
        agent_id="coder",
        type="coder",
        status="idle",
        stats={
            "tasks_total": 5,
            "tasks_success": 5,
            "tasks_failed": 0,
            "avg_duration_ms": 5200
        }
    )
    
    print("   创建了 5 个成功任务\n")
    
    # 1. L0 自动测试
    print("🔍 L0 自动测试（秒级反馈）...")
    l0_result = system.check_all("L0", {"agent_id": "coder"})
    print(f"   总门禁数: {l0_result['total']}")
    print(f"   通过数: {l0_result['passed_count']}")
    print(f"   失败数: {l0_result['failed_count']}")
    print(f"   整体结果: {'✅ 通过' if l0_result['passed'] else '❌ 失败'}")
    for result in l0_result['results']:
        status = "✅" if result['passed'] else "❌"
        print(f"     {status} {result['gate']}")
    print()
    
    # 2. L1 回归测试
    print("🔬 L1 回归测试（分钟级反馈）...")
    l1_result = system.check_all("L1", {"agent_id": "coder"})
    print(f"   总门禁数: {l1_result['total']}")
    print(f"   通过数: {l1_result['passed_count']}")
    print(f"   失败数: {l1_result['failed_count']}")
    print(f"   整体结果: {'✅ 通过' if l1_result['passed'] else '❌ 失败'}")
    for result in l1_result['results']:
        status = "✅" if result['passed'] else "❌"
        message = result['result'].get('message', '')
        print(f"     {status} {result['gate']}: {message}")
    print()
    
    # 3. L2 人工审核
    print("👤 L2 人工审核（需要人工确认）...")
    l2_result = system.check_all("L2", {"agent_id": "coder"})
    print(f"   总门禁数: {l2_result['total']}")
    print(f"   通过数: {l2_result['passed_count']}")
    print(f"   失败数: {l2_result['failed_count']}")
    print(f"   整体结果: {'✅ 通过' if l2_result['passed'] else '❌ 失败'}")
    for result in l2_result['results']:
        status = "✅" if result['passed'] else "❌"
        print(f"     {status} {result['gate']}")
    print()
    
    # 4. 低风险改进检查
    print("🟢 低风险改进检查（config 修改）...")
    low_risk_result = system.check_improvement(
        agent_id="coder",
        change_type="config",
        risk_level="low"
    )
    print(f"   审批结果: {'✅ 批准' if low_risk_result['approved'] else '❌ 拒绝'}")
    print(f"   原因: {low_risk_result['reason']}")
    print(f"   检查层级: L0 + L1")
    print()
    
    # 5. 中风险改进检查
    print("🟡 中风险改进检查（prompt 修改）...")
    medium_risk_result = system.check_improvement(
        agent_id="coder",
        change_type="prompt",
        risk_level="medium"
    )
    print(f"   审批结果: {'✅ 批准' if medium_risk_result['approved'] else '❌ 拒绝'}")
    print(f"   原因: {medium_risk_result['reason']}")
    print(f"   检查层级: L0 + L1")
    print()
    
    # 6. 高风险改进检查
    print("🔴 高风险改进检查（code 修改）...")
    high_risk_result = system.check_improvement(
        agent_id="coder",
        change_type="code",
        risk_level="high"
    )
    print(f"   审批结果: {'✅ 批准' if high_risk_result['approved'] else '❌ 拒绝'}")
    print(f"   原因: {high_risk_result['reason']}")
    print(f"   检查层级: L0 + L1 + L2")
    print()
    
    print("🎉 演示完成！")
    print("\n📂 质量门禁结果已保存到:")
    print(f"   - {system.results_dir}/gate_*.json")
    
    print("\n💡 质量门禁三层防护:")
    print("   L0（自动测试）- 语法检查、单元测试、导入检查")
    print("   L1（回归测试）- 成功率、耗时、固定测试集")
    print("   L2（人工审核）- 关键改进需要人工确认")
    
    print("\n🛡️  风险分级:")
    print("   低风险（config）- L0 + L1")
    print("   中风险（prompt）- L0 + L1")
    print("   高风险（code）  - L0 + L1 + L2")


if __name__ == "__main__":
    demo()

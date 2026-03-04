"""
Evaluator 演示脚本

展示 Evaluator 的核心功能：
1. 任务评估
2. Agent 评估
3. 系统评估
4. 改进评估
5. 报告生成
"""

import sys
from pathlib import Path

# 添加 aios 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_collector import DataCollector
from data_collector.evaluator import Evaluator


def demo():
    """演示 Evaluator 功能"""
    print("🚀 Evaluator 演示\n")
    
    # 初始化
    collector = DataCollector()
    evaluator = Evaluator()
    print("✅ Evaluator 初始化完成\n")
    
    # 创建一些测试数据
    print("📝 创建测试数据...")
    
    # 创建 5 个任务（4 成功，1 失败）
    for i in range(5):
        task_id = collector.create_task(
            title=f"测试任务 {i+1}",
            type="code",
            priority="normal" if i < 3 else "high",
            agent_id="coder"
        )
        collector.update_task(task_id, status="running")
        
        status = "success" if i < 4 else "failed"
        collector.complete_task(
            task_id,
            status=status,
            result={"output": f"任务{i+1}完成"} if status == "success" else {},
            metrics={
                "duration_ms": 5000 + i * 500,
                "tokens_used": 1000 + i * 100,
                "cost_usd": 0.01 + i * 0.005
            }
        )
    
    # 更新 Agent 统计
    collector.update_agent(
        agent_id="coder",
        type="coder",
        status="idle",
        stats={
            "tasks_total": 5,
            "tasks_success": 4,
            "tasks_failed": 1,
            "avg_duration_ms": 5500,
            "total_cost_usd": 0.06
        }
    )
    
    print("   创建了 5 个任务（4 成功，1 失败）\n")
    
    # 1. 评估任务
    print("📋 评估任务...")
    task_eval = evaluator.evaluate_tasks(time_window_hours=24)
    print(f"   总任务数: {task_eval['total']}")
    print(f"   成功任务: {task_eval['success']}")
    print(f"   失败任务: {task_eval['failed']}")
    print(f"   成功率: {task_eval['success_rate']:.2%}")
    print(f"   平均耗时: {task_eval['avg_duration_ms']:.0f} ms")
    print(f"   平均成本: ${task_eval['avg_cost_usd']:.4f}\n")
    
    # 2. 评估 Agent
    print("🤖 评估 Agent...")
    agent_eval = evaluator.evaluate_agent("coder")
    print(f"   Agent ID: {agent_eval['agent_id']}")
    print(f"   状态: {agent_eval['status']}")
    print(f"   成功率: {agent_eval['success_rate']:.2%}")
    print(f"   平均耗时: {agent_eval['avg_duration_ms']:.0f} ms")
    print(f"   总成本: ${agent_eval['total_cost_usd']:.4f}")
    print(f"   综合评分: {agent_eval['score']:.2f}/100")
    print(f"   等级: {agent_eval['grade']}\n")
    
    # 3. 评估所有 Agent
    print("📊 评估所有 Agent...")
    all_agents = evaluator.evaluate_all_agents()
    print(f"   Agent 数量: {len(all_agents)}")
    for agent in all_agents:
        print(f"     - {agent['agent_id']}: {agent['score']:.2f}/100 ({agent['grade']})")
    print()
    
    # 4. 评估系统
    print("🏥 评估系统健康度...")
    system_eval = evaluator.evaluate_system(time_window_hours=24)
    print(f"   健康评分: {system_eval['health_score']:.2f}/100")
    print(f"   等级: {system_eval['grade']}")
    print(f"   事件统计:")
    print(f"     - 总事件: {system_eval['events']['total']}")
    print(f"     - 错误事件: {system_eval['events']['error']}")
    print(f"     - 警告事件: {system_eval['events']['warning']}")
    print(f"     - 错误率: {system_eval['events']['error_rate']:.2%}")
    print(f"   任务统计:")
    print(f"     - 总任务: {system_eval['tasks']['total']}")
    print(f"     - 成功率: {system_eval['tasks']['success_rate']:.2%}")
    print(f"   Agent 统计:")
    print(f"     - Agent 数量: {system_eval['agents']['total']}")
    print(f"     - 平均评分: {system_eval['agents']['avg_score']:.2f}/100\n")
    
    # 5. 生成报告
    print("📄 生成评估报告...")
    report = evaluator.generate_report(time_window_hours=24)
    print(f"   报告时间: {report['timestamp']}")
    print(f"   时间窗口: {report['time_window_hours']} 小时")
    print(f"   系统健康度: {report['system']['health_score']:.2f}/100 ({report['system']['grade']})")
    print(f"   报告已保存到: {evaluator.results_dir}\n")
    
    print("🎉 演示完成！")
    print("\n📂 评估数据已保存到:")
    print(f"   - {evaluator.results_dir}/report_*.json")


if __name__ == "__main__":
    demo()

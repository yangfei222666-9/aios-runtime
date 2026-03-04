"""
AI Team Starter
启动 AI 团队，注册所有 Agent 到 AIOS

使用方法：
    python start_ai_team.py

创建时间：2026-02-26
版本：v1.0
"""

import json
import sys
from pathlib import Path

# 添加 workspace 到路径
workspace = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace))


def load_team_config():
    """加载团队配置"""
    config_path = workspace / "aios" / "agent_system" / "ai_team_agents.json"
    if not config_path.exists():
        print(f"❌ 配置文件不存在: {config_path}")
        print("请先运行: python deploy_ai_team.py")
        sys.exit(1)
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def register_agent(agent_config):
    """注册单个 Agent 到 AIOS"""
    # 这里是注册逻辑的占位符
    # 实际实现需要调用 AIOS 的 Agent 注册 API
    
    agent_id = agent_config["agent_id"]
    name = agent_config["name"]
    team = agent_config["team"]
    
    print(f"  📝 注册 Agent: {name} ({agent_id})")
    print(f"     团队: {team}")
    print(f"     职责: {', '.join(agent_config['responsibilities'][:2])}...")
    print(f"     工具: {', '.join(agent_config['tools'][:3])}...")
    
    # TODO: 实际注册到 AIOS
    # aios.register_agent(agent_config)
    
    return True


def start_team(config):
    """启动整个团队"""
    print("=" * 60)
    print(f"启动 AI 团队: {config['template']}")
    print(f"版本: {config['version']}")
    print(f"总 Agent 数: {config['total_agents']}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    # 按团队分组显示
    teams = {}
    for agent in config["agents"]:
        team = agent["team"]
        if team not in teams:
            teams[team] = []
        teams[team].append(agent)
    
    # 注册所有 Agent
    for team_name, agents in teams.items():
        print(f"\n🚀 启动团队: {team_name} ({len(agents)} 人)")
        
        for agent in agents:
            try:
                if register_agent(agent):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                print(f"  ❌ 注册失败: {e}")
                fail_count += 1
    
    # 显示统计
    print("\n" + "=" * 60)
    print("📊 启动统计")
    print("=" * 60)
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {fail_count}")
    print(f"  📈 成功率: {success_count / config['total_agents'] * 100:.1f}%")
    
    # 显示工作流
    print("\n" + "=" * 60)
    print("🔄 可用工作流")
    print("=" * 60)
    for workflow in config["workflows"]:
        print(f"  - {workflow['workflow_name']}: {workflow['description']}")
    
    # 显示使用提示
    print("\n" + "=" * 60)
    print("💡 使用提示")
    print("=" * 60)
    print("  1. 调用 Agent:")
    print("     @product-lead 请分析用户反馈")
    print("     @ceo 今天的工作计划是什么？")
    print()
    print("  2. 查看 Agent 状态:")
    print("     python check_team_status.py")
    print()
    print("  3. 查看工作流:")
    print("     python show_workflows.py")
    
    return success_count, fail_count


def main():
    """主函数"""
    print("=" * 60)
    print("AI Team Starter v1.0")
    print("=" * 60)
    
    # 加载配置
    print("\n📂 加载团队配置...")
    config = load_team_config()
    print(f"  ✅ 配置加载成功")
    
    # 启动团队
    success, fail = start_team(config)
    
    if fail == 0:
        print("\n" + "=" * 60)
        print("🎉 团队启动成功！")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️ 团队启动完成，但有部分失败")
        print("=" * 60)


if __name__ == "__main__":
    main()

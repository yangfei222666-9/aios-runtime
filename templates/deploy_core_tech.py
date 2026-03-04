"""
部署核心技术专家组
"""
import json
from pathlib import Path

# 读取核心技术团队
team_path = Path(__file__).parent / "core_tech_team.json"
with open(team_path, "r", encoding="utf-8") as f:
    team = json.load(f)

print("=" * 60)
print(f"部署核心技术专家组")
print(f"团队规模: {team['team_size']} 人")
print("=" * 60)

for agent in team["agents"]:
    print(f"\n✅ {agent['role']} ({agent['agent_id']})")
    print(f"   目标: {agent['goal']}")
    print(f"   工作时间: {agent['working_hours']}")
    print(f"   每日任务数: {len(agent['daily_tasks'])}")
    print(f"   关键职责:")
    for resp in agent['responsibilities'][:3]:
        print(f"     - {resp}")

print("\n" + "=" * 60)
print("🎉 核心技术专家组部署完成！")
print("=" * 60)
print("\n📊 团队总览:")
print("  - AIOS Kernel 架构师: 系统心脏")
print("  - Multi-Agent 编排专家: 核心功能")
print("  - MLOps / AgentOps 工程师: 生产级保障")

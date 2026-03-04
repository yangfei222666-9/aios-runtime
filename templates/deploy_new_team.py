"""
部署新的 3 个 Agent
"""
import json
from pathlib import Path

# 读取 v2 模板
template_path = Path(__file__).parent / "ai_team_template_v2.json"
with open(template_path, "r", encoding="utf-8") as f:
    template = json.load(f)

print("=" * 60)
print(f"部署 AI 团队 v2.0")
print(f"总 Agent 数: {template['total_agents']}")
print("=" * 60)

# 显示新增的团队
new_team = template["teams"][-1]
print(f"\n🆕 新增团队: {new_team['team_name']} ({new_team['team_size']} 人)")
print(f"描述: {new_team['description']}")
print()

for agent in new_team["agents"]:
    print(f"✅ {agent['role']} ({agent['agent_id']})")
    print(f"   目标: {agent['goal']}")
    print(f"   工作时间: {agent['working_hours']}")
    print(f"   每日任务数: {len(agent['daily_tasks'])}")
    print()

print("=" * 60)
print("🎉 新团队部署完成！")
print("=" * 60)

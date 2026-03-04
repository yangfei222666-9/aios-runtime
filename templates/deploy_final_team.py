"""
部署社区与安全组 - 完成 25 人企业级团队
"""
import json
from pathlib import Path

# 读取社区与安全组
team_path = Path(__file__).parent / "community_safety_team.json"
with open(team_path, "r", encoding="utf-8") as f:
    team = json.load(f)

print("=" * 60)
print(f"部署社区与安全组 - 最后 3 人")
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
print("🎉 社区与安全组部署完成！")
print("=" * 60)
print("\n📊 最终团队总览（25人）:")
print("  1. 产品增长队（5人）")
print("  2. 技术平台队（8人）")
print("  3. 营销增长队（5人）")
print("  4. 设计与研究队（3人）")
print("  5. 社区与安全组（3人）✨ 新增")
print("  6. 总办（1人）")
print("\n🚀 完整的企业级团队！")
print("🎯 目标：AIOS 从 5.2k stars → 10k+ stars！")

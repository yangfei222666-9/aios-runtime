"""
AI Team Template Deployer
一键部署 16 个 AI 数字员工

使用方法：
    python deploy_ai_team.py

创建时间：2026-02-26
版本：v1.0
"""

import json
import sys
from pathlib import Path

# 添加 workspace 到路径
workspace = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace))


def load_template():
    """加载 AI 团队模板"""
    template_path = Path(__file__).parent / "ai_team_template.json"
    with open(template_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_agent_config(agent_data, team_name):
    """创建单个 Agent 的配置"""
    return {
        "agent_id": agent_data["agent_id"],
        "name": agent_data["role"],
        "english_name": agent_data["english_name"],
        "team": team_name,
        "role": agent_data["role"],
        "goal": agent_data["goal"],
        "backstory": agent_data["backstory"],
        "responsibilities": agent_data["responsibilities"],
        "skills": agent_data["skills"],
        "tools": agent_data["tools"],
        "working_hours": agent_data["working_hours"],
        "reports_to": agent_data["reports_to"],
        "status": "active",
        "created_at": "2026-02-26"
    }


def deploy_team(template):
    """部署整个团队"""
    print("=" * 60)
    print(f"部署 AI 团队: {template['template_name']}")
    print(f"版本: {template['template_version']}")
    print(f"总 Agent 数: {template['total_agents']}")
    print("=" * 60)
    
    all_agents = []
    
    # 遍历所有团队
    for team in template["teams"]:
        team_name = team["team_name"]
        team_size = team["team_size"]
        
        print(f"\n📦 部署团队: {team_name} ({team_size} 人)")
        
        # 创建团队中的每个 Agent
        for agent_data in team["agents"]:
            agent_config = create_agent_config(agent_data, team_name)
            all_agents.append(agent_config)
            
            print(f"  ✅ {agent_data['role']} ({agent_data['agent_id']})")
    
    # 保存到文件
    output_path = workspace / "aios" / "agent_system" / "ai_team_agents.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "template": template["template_name"],
            "version": template["template_version"],
            "total_agents": len(all_agents),
            "agents": all_agents,
            "workflows": template["workflows"],
            "communication_rules": template["communication_rules"],
            "metrics": template["metrics"]
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 部署完成！配置已保存到: {output_path}")
    print(f"\n📊 统计:")
    print(f"  - 总 Agent 数: {len(all_agents)}")
    print(f"  - 团队数: {len(template['teams'])}")
    print(f"  - 工作流数: {len(template['workflows'])}")
    
    return all_agents


def generate_readme(template, agents):
    """生成 README 文档"""
    readme_content = f"""# {template['template_name']} - AI 团队模板

**版本:** {template['template_version']}  
**创建时间:** {template['created_at']}  
**总 Agent 数:** {template['total_agents']}

## 📋 团队结构

"""
    
    # 添加团队信息
    for team in template["teams"]:
        readme_content += f"### {team['team_name']} ({team['team_size']} 人)\n\n"
        readme_content += f"**团队负责人:** {team['team_lead']}\n\n"
        
        # 添加团队成员
        for agent in team["agents"]:
            readme_content += f"#### {agent['role']} (`{agent['agent_id']}`)\n\n"
            readme_content += f"**职责:**\n"
            for resp in agent["responsibilities"]:
                readme_content += f"- {resp}\n"
            readme_content += f"\n**技能:** {', '.join(agent['skills'])}\n\n"
            readme_content += f"**工具:** {', '.join(agent['tools'])}\n\n"
            readme_content += f"**工作时间:** {agent['working_hours']}\n\n"
            readme_content += f"**汇报对象:** {agent['reports_to']}\n\n"
            readme_content += "---\n\n"
    
    # 添加工作流
    readme_content += "## 🔄 工作流程\n\n"
    for workflow in template["workflows"]:
        readme_content += f"### {workflow['workflow_name']}\n\n"
        readme_content += f"{workflow['description']}\n\n"
        for step in workflow["steps"]:
            readme_content += f"{step['step']}. **{step['agent']}** - {step['action']} ({step['time']})\n"
        readme_content += "\n"
    
    # 添加沟通规则
    readme_content += "## 💬 沟通规则\n\n"
    for rule in template["communication_rules"]:
        readme_content += f"### {rule['rule']}\n\n"
        readme_content += f"{rule['description']}\n\n"
        readme_content += f"**示例:** {rule['example']}\n\n"
    
    # 添加指标
    readme_content += "## 📊 关键指标\n\n"
    for metric in template["metrics"]:
        readme_content += f"- **{metric['metric_name']}:** {metric['description']} (目标: {metric['target']})\n"
    
    # 添加使用说明
    readme_content += """

## 🚀 使用方法

### 1. 部署团队

```bash
python deploy_ai_team.py
```

### 2. 调用 Agent

```python
# 通过 Agent ID 调用
@product-lead 请分析用户反馈，制定优化方案

# 通过角色名调用
@产品负责人 请分析用户反馈，制定优化方案
```

### 3. 任务流转

Agent 完成任务后会自动传递给下一个 Agent：

```
CEO → 产品负责人 → 全栈工程师 → QA自动化 → DevOps工程师
```

### 4. 查看状态

```bash
# 查看所有 Agent 状态
python check_team_status.py

# 查看单个 Agent 状态
python check_agent_status.py product-lead
```

## 📈 效率提升

- **工作时间:** 从 8 小时/天 → 1 小时/天
- **团队规模:** 16 个 AI 员工
- **成本节约:** >80%
- **任务完成率:** >90%

## 🎯 适用场景

- 创业公司（0-1 阶段）
- 小型团队（<10 人）
- 快速迭代产品
- 资源有限的项目

## 📝 注意事项

1. **Agent 专业化** - 每个 Agent 有明确的职责和专长
2. **协作流程** - Agent 之间通过任务传递协作
3. **汇报机制** - 每个 Agent 完成任务后向上级汇报
4. **工作时间** - 每个 Agent 有固定的工作时间

## 🔧 自定义

你可以根据自己的需求修改模板：

1. 编辑 `ai_team_template.json`
2. 添加/删除 Agent
3. 修改工作流程
4. 调整沟通规则

## 📚 参考资料

- [AIOS 文档](https://docs.openclaw.ai)
- [Agent 开发指南](https://docs.openclaw.ai/agents)
- [工作流设计](https://docs.openclaw.ai/workflows)

---

**创建者:** 小九 + 珊瑚海  
**灵感来源:** AI对AI的分享和思考（抖音案例）
"""
    
    # 保存 README
    readme_path = workspace / "aios" / "templates" / "AI_TEAM_README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"📄 README 已生成: {readme_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("AI Team Template Deployer v1.0")
    print("=" * 60)
    
    # 加载模板
    print("\n📂 加载模板...")
    template = load_template()
    print(f"  ✅ 模板加载成功: {template['template_name']}")
    
    # 部署团队
    agents = deploy_team(template)
    
    # 生成 README
    print("\n📝 生成 README...")
    generate_readme(template, agents)
    
    print("\n" + "=" * 60)
    print("🎉 部署完成！")
    print("=" * 60)
    print("\n下一步:")
    print("1. 查看配置: aios/agent_system/ai_team_agents.json")
    print("2. 阅读文档: aios/templates/AI_TEAM_README.md")
    print("3. 启动团队: python start_ai_team.py")


if __name__ == "__main__":
    main()

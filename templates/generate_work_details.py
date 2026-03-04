"""
生成 16 个 AI 员工的具体工作内容文档
"""

import json
from pathlib import Path

# 读取模板
template_path = Path(__file__).parent / "ai_team_template.json"
with open(template_path, "r", encoding="utf-8") as f:
    template = json.load(f)

# 读取工作细节
work_details_path = Path(__file__).parent / "agent_work_details.py"
with open(work_details_path, "r", encoding="utf-8") as f:
    work_details_content = f.read()

# 生成 Markdown
md = "# 16 个 AI 数字员工 - 具体工作内容\n\n"
md += "**创建时间：** 2026-02-26\n"
md += "**版本：** v1.0\n"
md += "**总员工数：** 16 人\n"
md += "**团队数：** 4 个\n\n"
md += "---\n\n"

md += "## 📋 目录\n\n"
for team in template["teams"]:
    md += f"### {team['team_name']} ({team['team_size']} 人)\n"
    for agent in team["agents"]:
        md += f"- [{agent['role']}](#{agent['agent_id']})\n"
    md += "\n"

md += "---\n\n"

# 详细内容
for team in template["teams"]:
    md += f"## {team['team_name']} ({team['team_size']} 人)\n\n"
    md += f"**团队负责人：** {team['team_lead']}\n\n"
    
    for agent in team["agents"]:
        md += f"### <a name='{agent['agent_id']}'></a>{agent['role']}\n\n"
        md += f"**Agent ID：** `{agent['agent_id']}`\n\n"
        md += f"**英文名：** {agent['english_name']}\n\n"
        md += f"**工作时间：** {agent['working_hours']}\n\n"
        md += f"**汇报对象：** {agent['reports_to'] or '无'}\n\n"
        
        md += f"#### 🎯 目标\n\n"
        md += f"{agent['goal']}\n\n"
        
        md += f"#### 📖 背景\n\n"
        md += f"{agent['backstory']}\n\n"
        
        md += f"#### 📋 职责\n\n"
        for i, resp in enumerate(agent['responsibilities'], 1):
            md += f"{i}. {resp}\n"
        md += "\n"
        
        md += f"#### 🛠️ 技能\n\n"
        for skill in agent['skills']:
            md += f"- {skill}\n"
        md += "\n"
        
        md += f"#### 🔧 使用工具\n\n"
        for tool in agent['tools']:
            md += f"- `{tool}`\n"
        md += "\n"
        
        # 添加每日时间表（如果有）
        if 'daily_schedule' in agent:
            md += f"#### ⏰ 每日时间表\n\n"
            for schedule in agent['daily_schedule']:
                md += f"**{schedule['time']}** - {schedule['task']}\n\n"
                md += f"*任务详情：*\n"
                for key, value in schedule.items():
                    if key not in ['time', 'task']:
                        md += f"- {key}: {value}\n"
                md += "\n"
        
        # 添加具体工作示例
        md += f"#### 💼 具体工作示例\n\n"
        
        if agent['agent_id'] == 'product-lead':
            md += "**09:00-09:30 - 查看昨日数据报告**\n"
            md += "- **输入：** 用户数据、转化率、留存率、反馈数据\n"
            md += "- **输出：** 数据分析报告\n"
            md += "- **示例：** \"分析昨日新增用户 100 人，转化率 15%，发现注册流程有 30% 流失\"\n\n"
            
            md += "**09:30-10:30 - 制定今日产品优化方案**\n"
            md += "- **输入：** 数据分析报告、用户反馈、竞品分析\n"
            md += "- **输出：** 优化方案文档\n"
            md += "- **示例：** \"方案：简化注册流程，从 5 步减少到 3 步，预期提升转化率 10%\"\n\n"
        
        elif agent['agent_id'] == 'fullstack-dev':
            md += "**10:30-12:00 - 功能开发（前端）**\n"
            md += "- **输入：** 设计稿、需求文档\n"
            md += "- **输出：** 前端代码 + 组件\n"
            md += "- **示例：** \"实现新的注册表单组件，支持手机号/邮箱双通道\"\n\n"
            
            md += "**14:00-16:00 - 功能开发（后端）**\n"
            md += "- **输入：** API 设计、数据库设计\n"
            md += "- **输出：** 后端代码 + API\n"
            md += "- **示例：** \"实现注册 API，支持验证码验证 + 用户信息存储\"\n\n"
        
        elif agent['agent_id'] == 'ceo':
            md += "**08:00-09:00 - 审阅数据报告**\n"
            md += "- **输入：** 情报简报、用户反馈、行为洞察\n"
            md += "- **输出：** 战略洞察\n"
            md += "- **示例：** \"发现用户增长放缓，需要加大营销投入\"\n\n"
            
            md += "**09:00-12:00 - Squad 例会 + 关键决策**\n"
            md += "- **输入：** 团队汇报、问题清单\n"
            md += "- **输出：** 决策清单\n"
            md += "- **示例：** \"决策：批准注册流程优化方案，预算 10 万元\"\n\n"
        
        md += "---\n\n"

# 添加工作流
md += "## 🔄 工作流程\n\n"
for workflow in template["workflows"]:
    md += f"### {workflow['workflow_name']}\n\n"
    md += f"**描述：** {workflow['description']}\n\n"
    md += "**流程：**\n\n"
    for step in workflow["steps"]:
        agent_name = next((a['role'] for t in template['teams'] for a in t['agents'] if a['agent_id'] == step['agent']), step['agent'])
        md += f"{step['step']}. **{step['time']}** - {agent_name}: {step['action']}\n"
    md += "\n"

# 保存
output_path = Path(__file__).parent / "16_AI_EMPLOYEES_WORK_DETAILS.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(md)

print(f"✅ 文档已生成: {output_path}")
print(f"📄 文件大小: {len(md)} 字符")

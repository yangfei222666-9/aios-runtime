"""
AI Team Workflow Executor
执行完整的工作流，模拟 Agent 之间的协作

使用方法：
    python execute_workflow.py product-development

创建时间：2026-02-26
版本：v1.0
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# 添加 workspace 到路径
workspace = Path(__file__).parent.parent.parent
sys.path.insert(0, str(workspace))


class WorkflowExecutor:
    """工作流执行器"""
    
    def __init__(self):
        self.agents = self.load_agents()
        self.workflows = self.load_workflows()
        self.execution_log = []
    
    def load_agents(self):
        """加载 Agent 配置"""
        config_path = workspace / "aios" / "agent_system" / "ai_team_agents.json"
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 转换为字典
        agents_dict = {}
        for agent in config["agents"]:
            agents_dict[agent["agent_id"]] = agent
        
        return agents_dict
    
    def load_workflows(self):
        """加载工作流配置"""
        template_path = workspace / "aios" / "templates" / "ai_team_template.json"
        with open(template_path, "r", encoding="utf-8") as f:
            template = json.load(f)
        
        return template["workflows"]
    
    def execute_workflow(self, workflow_name: str):
        """执行工作流"""
        # 查找工作流
        workflow = None
        for wf in self.workflows:
            if wf["workflow_name"] == workflow_name or \
               wf["workflow_name"].lower().replace(" ", "-") == workflow_name.lower():
                workflow = wf
                break
        
        if not workflow:
            print(f"❌ 工作流不存在: {workflow_name}")
            return
        
        print("=" * 60)
        print(f"执行工作流: {workflow['workflow_name']}")
        print(f"描述: {workflow['description']}")
        print("=" * 60)
        
        # 执行每个步骤
        for step in workflow["steps"]:
            self.execute_step(step, workflow)
            time.sleep(0.5)  # 模拟执行时间
        
        # 显示执行日志
        self.show_execution_log()
    
    def execute_step(self, step, workflow):
        """执行单个步骤"""
        agent_id = step["agent"]
        action = step["action"]
        step_time = step["time"]
        step_num = step["step"]
        
        # 获取 Agent 信息
        agent = self.agents.get(agent_id)
        if not agent:
            print(f"❌ Agent 不存在: {agent_id}")
            return
        
        agent_name = agent["name"]
        
        # 显示执行信息
        print(f"\n[步骤 {step_num}] {step_time}")
        print(f"👤 Agent: {agent_name} ({agent_id})")
        print(f"📋 任务: {action}")
        
        # 模拟执行
        print(f"⏳ 执行中...")
        
        # 生成输出（模拟）
        output = self.generate_output(agent_id, action)
        print(f"✅ 完成: {output}")
        
        # 记录日志
        self.execution_log.append({
            "step": step_num,
            "time": step_time,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "action": action,
            "output": output,
            "timestamp": datetime.now().isoformat()
        })
    
    def generate_output(self, agent_id: str, action: str) -> str:
        """生成输出（模拟）"""
        # 根据 Agent 和任务生成模拟输出
        outputs = {
            "ceo": {
                "派发任务": "已派发任务给产品负责人：优化注册流程，提升转化率"
            },
            "product-lead": {
                "分析需求": "需求分析完成：简化注册流程从 5 步到 3 步，预期提升转化率 10%",
                "制定方案": "优化方案：手机号 → 验证码 → 完成（3 步）"
            },
            "user-researcher": {
                "用户研究": "用户研究完成：50% 用户反馈注册流程太复杂，建议简化",
                "验证需求": "需求验证通过：用户对简化方案满意度 85%"
            },
            "ux-designer": {
                "设计交互原型": "交互原型完成：新注册流程设计，符合用户习惯"
            },
            "fullstack-dev": {
                "功能开发实现": "开发完成：前端 + 后端实现，单元测试通过"
            },
            "qa-automation": {
                "自动化测试": "测试完成：功能测试 + 性能测试通过，无阻塞问题"
            },
            "devops-engineer": {
                "部署上线": "部署完成：灰度发布 10% 流量，监控正常"
            },
            "technical-writer": {
                "更新文档": "文档更新完成：API 文档 + 用户手册已发布"
            },
            "content-strategist": {
                "发布更新公告": "公告发布完成：已推送给所有用户，阅读率 60%"
            }
        }
        
        # 查找匹配的输出
        if agent_id in outputs:
            for key, value in outputs[agent_id].items():
                if key in action:
                    return value
        
        # 默认输出
        return f"{action}完成"
    
    def show_execution_log(self):
        """显示执行日志"""
        print("\n" + "=" * 60)
        print("📊 执行日志")
        print("=" * 60)
        
        for log in self.execution_log:
            print(f"\n[{log['time']}] 步骤 {log['step']}")
            print(f"  Agent: {log['agent_name']}")
            print(f"  任务: {log['action']}")
            print(f"  输出: {log['output']}")
        
        # 保存日志
        log_path = workspace / "aios" / "templates" / "workflow_execution_log.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.execution_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 日志已保存: {log_path}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python execute_workflow.py <workflow-name>")
        print("\n可用工作流:")
        print("  - product-development  (产品开发流程)")
        print("  - growth-experiment    (增长实验流程)")
        sys.exit(1)
    
    workflow_name = sys.argv[1]
    
    print("=" * 60)
    print("AI Team Workflow Executor v1.0")
    print("=" * 60)
    
    # 创建执行器
    executor = WorkflowExecutor()
    
    # 执行工作流
    executor.execute_workflow(workflow_name)
    
    print("\n" + "=" * 60)
    print("🎉 工作流执行完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()

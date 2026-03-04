"""
AIOS - Agent Operating System
统一 API 入口

融合：AIOS + Agent + Skills + Code
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import sys

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / 'core'))
sys.path.insert(0, str(Path(__file__).parent))

from core.scheduler_v5 import Scheduler
from vm_controller import VMController
from core.ollama_client import OllamaClient


class AIOS:
    """AIOS 统一 API"""
    
    def __init__(self, workspace: Optional[Path] = None, 
                 use_vm: bool = True, vm_pool_size: int = 3):
        """
        初始化 AIOS
        
        Args:
            workspace: 工作目录
            use_vm: 是否使用 VM
            vm_pool_size: VM 池大小
        """
        if workspace is None:
            workspace = Path(__file__).parent
        
        self.workspace = workspace
        self.use_vm = use_vm
        
        # 初始化核心组件
        self.scheduler = Scheduler(
            max_concurrent=5,
            default_timeout=60,
            workspace=workspace,
            use_vm=use_vm,
            vm_pool_size=vm_pool_size
        )
        
        self.vm_controller = self.scheduler.vm_controller if use_vm else None
        self.ollama_client = OllamaClient()
        
        # Agent 注册表
        self.agents = {}
        
        # Skills 注册表
        self.skills = {}
        
        # 初始化默认 Agents
        self._init_default_agents()
        
        # 初始化默认 Skills
        self._init_default_skills()
    
    def _init_default_agents(self):
        """初始化默认 Agents"""
        self.agents = {
            'coder-agent': {
                'id': 'coder-agent',
                'name': 'Coder Agent',
                'type': 'code_generation',
                'skills': ['code_generation', 'code_review', 'debugging'],
                'model': 'qwen2.5:7b',
                'vm_enabled': True,
                'status': 'idle'
            },
            'analyst-agent': {
                'id': 'analyst-agent',
                'name': 'Analyst Agent',
                'type': 'data_analysis',
                'skills': ['data_analysis', 'visualization'],
                'model': 'qwen2.5:7b',
                'vm_enabled': True,
                'status': 'idle'
            },
            'monitor-agent': {
                'id': 'monitor-agent',
                'name': 'Monitor Agent',
                'type': 'monitoring',
                'skills': ['system_monitoring', 'alerting'],
                'model': 'qwen2.5:7b',
                'vm_enabled': False,
                'status': 'idle'
            }
        }
    
    def _init_default_skills(self):
        """初始化默认 Skills"""
        self.skills = {
            'code_generation': {
                'id': 'code_generation',
                'name': 'Code Generation',
                'description': '生成代码',
                'category': 'coding',
                'keywords': ['写代码', '生成', '实现', 'code', 'generate']
            },
            'data_analysis': {
                'id': 'data_analysis',
                'name': 'Data Analysis',
                'description': '数据分析',
                'category': 'analysis',
                'keywords': ['分析', '统计', 'analysis', 'analyze']
            },
            'system_monitoring': {
                'id': 'system_monitoring',
                'name': 'System Monitoring',
                'description': '系统监控',
                'category': 'monitoring',
                'keywords': ['监控', '检查', 'monitor', 'check']
            }
        }
    
    def execute(self, task_description: str, 
                agent: Optional[str] = None,
                priority: str = 'normal') -> Dict[str, Any]:
        """
        执行任务（自然语言接口）
        
        Args:
            task_description: 任务描述
            agent: 指定 Agent（可选）
            priority: 优先级
        
        Returns:
            执行结果
        """
        # 自动选择 Agent
        if agent is None:
            agent = self._select_agent(task_description)
        
        # 使用 Ollama 生成代码/内容
        result = self.ollama_client.generate(
            model='qwen2.5:7b',
            prompt=task_description
        )
        
        return {
            'task': task_description,
            'agent': agent,
            'priority': priority,
            'response': result.get('response', ''),
            'status': 'completed' if 'response' in result else 'failed'
        }
    
    def submit_task(self, task: Dict[str, Any]) -> str:
        """
        提交结构化任务
        
        Args:
            task: 任务对象
        
        Returns:
            任务 ID
        """
        # 创建执行器
        def executor():
            return self.execute(task['description'])
        
        # 提交到 Scheduler
        scheduler_task = {
            'id': task.get('id', f"task-{int(time.time())}"),
            'func': executor,
            'depends_on': task.get('depends_on', []),
            'timeout': task.get('timeout', 60)
        }
        
        self.scheduler.schedule(scheduler_task)
        return scheduler_task['id']
    
    def _select_agent(self, task_description: str) -> str:
        """自动选择 Agent"""
        # 简单的关键词匹配
        if any(kw in task_description for kw in ['写', '代码', 'code', '实现']):
            return 'coder-agent'
        elif any(kw in task_description for kw in ['分析', 'analysis', '统计']):
            return 'analyst-agent'
        elif any(kw in task_description for kw in ['监控', 'monitor', '检查']):
            return 'monitor-agent'
        else:
            return 'coder-agent'  # 默认
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """列出所有 Agents"""
        return list(self.agents.values())
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有 Skills"""
        return list(self.skills.values())
    
    def get_status(self) -> Dict[str, Any]:
        """获取 AIOS 状态"""
        return {
            'workspace': str(self.workspace),
            'use_vm': self.use_vm,
            'agents': len(self.agents),
            'skills': len(self.skills),
            'scheduler_stats': self.scheduler.stats,
            'vm_pool': len(self.vm_controller.vm_pool) if self.vm_controller else 0
        }
    
    def shutdown(self):
        """关闭 AIOS"""
        self.scheduler.shutdown()


# 便捷函数
def execute(task: str, **kwargs) -> Dict[str, Any]:
    """快速执行任务"""
    aios = AIOS()
    try:
        return aios.execute(task, **kwargs)
    finally:
        aios.shutdown()


if __name__ == '__main__':
    # 测试
    print("\n=== AIOS 统一 API 测试 ===\n")
    
    aios = AIOS(use_vm=False)  # 暂时不用 VM，加快测试
    
    try:
        # 测试 1：代码生成
        print("1. 测试代码生成...")
        result = aios.execute("写一个 Python 函数计算阶乘")
        print(f"   Agent: {result['agent']}")
        print(f"   Status: {result['status']}")
        print(f"   Response: {result['response'][:100]}...")
        print()
        
        # 测试 2：列出 Agents
        print("2. 列出所有 Agents...")
        agents = aios.list_agents()
        for agent in agents:
            print(f"   - {agent['name']} ({agent['type']})")
        print()
        
        # 测试 3：列出 Skills
        print("3. 列出所有 Skills...")
        skills = aios.list_skills()
        for skill in skills:
            print(f"   - {skill['name']} ({skill['category']})")
        print()
        
        # 测试 4：获取状态
        print("4. 获取 AIOS 状态...")
        status = aios.get_status()
        print(f"   Agents: {status['agents']}")
        print(f"   Skills: {status['skills']}")
        print(f"   Stats: {status['scheduler_stats']}")
        print()
        
        print("=== 所有测试通过 ✅ ===\n")
    
    finally:
        aios.shutdown()

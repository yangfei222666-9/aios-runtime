"""
Superpowers Mode - 跳过 Planning，直接执行

灵感来源：Claude Code 取消 Plan 模式，直接用 Superpowers
核心思路：把所有非代码执行的思考工作交给 AI，人类只负责高层设计

使用场景：
1. 简单任务（不需要复杂规划）
2. 快速原型（先跑起来再优化）
3. 探索性任务（不确定最佳路径）

对比：
- Planning Mode: 先规划 → 再执行（适合复杂任务）
- Superpowers Mode: 直接执行（适合简单任务）
"""

import json
import time
from typing import Dict, List, Any, Optional
from pathlib import Path

from aios.sdk.action import ActionModule
from aios.data_collector.collector import DataCollector
from aios.data_collector.schema import Task


class SuperpowersMode:
    """Superpowers 模式 - 跳过规划，直接执行"""
    
    def __init__(self, workspace: str = "C:/Users/A/.openclaw/workspace/aios"):
        self.workspace = Path(workspace)
        self.action_module = ActionModule(agent_id="superpowers")
        self.collector = DataCollector(str(self.workspace / "data"))
        
    def execute(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        max_steps: int = 10,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        直接执行任务（无需规划）
        
        Args:
            task: 任务描述
            context: 上下文信息
            max_steps: 最大执行步数
            timeout: 超时时间（秒）
            
        Returns:
            执行结果
        """
        start_time = time.time()
        
        # 记录任务开始
        task_id = self.collector.create_task(
            title=task,
            type="superpowers",
            agent_id="superpowers"
        )
        
        self.collector.update_task(
            task_id=task_id,
            status="running"
        )
        
        try:
            # 直接执行（无需规划）
            result = self._execute_direct(
                task=task,
                context=context,
                max_steps=max_steps,
                timeout=timeout
            )
            
            # 记录任务完成
            elapsed = time.time() - start_time
            self.collector.update_task(
                task_id=task_id,
                status="success",
                result=result,
                metrics={"elapsed_ms": int(elapsed * 1000)}
            )
            
            return {
                "success": True,
                "task_id": task_id,
                "result": result,
                "elapsed": elapsed,
                "steps": result.get("steps", 0)
            }
            
        except Exception as e:
            # 记录任务失败
            elapsed = time.time() - start_time
            self.collector.update_task(
                task_id=task_id,
                status="failed",
                result={"error": str(e)},
                metrics={"elapsed_ms": int(elapsed * 1000)}
            )
            
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "elapsed": elapsed
            }
    
    def _execute_direct(
        self,
        task: str,
        context: Optional[Dict[str, Any]],
        max_steps: int,
        timeout: int
    ) -> Dict[str, Any]:
        """
        直接执行（核心逻辑）
        
        策略：
        1. 分析任务 → 识别需要的工具
        2. 直接调用工具 → 不生成详细计划
        3. 根据结果决定下一步 → 动态调整
        4. 重复直到完成或超时
        """
        steps = []
        current_context = context or {}
        start_time = time.time()
        
        for step_num in range(1, max_steps + 1):
            # 检查超时
            if time.time() - start_time > timeout:
                raise TimeoutError(f"执行超时（{timeout}秒）")
            
            # 分析当前状态，决定下一步
            next_action = self._decide_next_action(
                task=task,
                context=current_context,
                history=steps
            )
            
            if next_action["type"] == "done":
                # 任务完成
                return {
                    "status": "completed",
                    "steps": step_num - 1,
                    "result": next_action.get("result"),
                    "history": steps
                }
            
            # 执行动作
            action_result = self.action_module.shell(
                command=next_action["params"].get("command", "echo 'test'"),
                timeout=30
            )
            
            # 记录步骤
            steps.append({
                "step": step_num,
                "action": next_action,
                "result": {
                    "success": action_result.success,
                    "output": action_result.output,
                    "error": action_result.error
                }
            })
            
            # 更新上下文
            current_context["last_result"] = action_result.output
        
        # 达到最大步数
        raise RuntimeError(f"达到最大步数（{max_steps}），任务未完成")
    
    def _decide_next_action(
        self,
        task: str,
        context: Dict[str, Any],
        history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        决定下一步动作（简化版 ReAct）
        
        这里是简化实现，实际应该调用 LLM 做决策
        """
        # TODO: 集成 LLM 做决策
        # 现在先返回一个简单的示例
        
        if not history:
            # 第一步：分析任务
            return {
                "type": "action",
                "tool": "analyze",
                "params": {"task": task}
            }
        
        # 后续步骤：根据历史决定
        last_result = history[-1]["result"]
        
        if last_result.get("success"):
            # 上一步成功，任务完成
            return {
                "type": "done",
                "result": last_result
            }
        else:
            # 上一步失败，重试或调整策略
            return {
                "type": "action",
                "tool": "retry",
                "params": {"previous": last_result}
            }


# 便捷函数
def superpower(task: str, **kwargs) -> Dict[str, Any]:
    """
    快速执行任务（Superpowers 模式）
    
    Example:
        result = superpower("创建一个 Flask API")
        result = superpower("分析日志文件", context={"file": "app.log"})
    """
    mode = SuperpowersMode()
    return mode.execute(task, **kwargs)


if __name__ == "__main__":
    # 测试
    result = superpower("测试 Superpowers 模式")
    print(json.dumps(result, indent=2, ensure_ascii=False))

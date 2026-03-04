"""
AIOS Evaluator - 量化评估系统

核心功能：
1. 任务评估 - 成功率、耗时、成本
2. Agent 评估 - 性能、稳定性、效率
3. 系统评估 - 健康度、Evolution Score、错误率
4. 改进评估 - Self-Improving Loop 效果验证

评估维度：
- 质量（Quality）- 任务成功率、错误率
- 性能（Performance）- 响应时间、吞吐量
- 成本（Cost）- Token 使用、API 调用
- 稳定性（Stability）- 失败率、波动性
- 改进效果（Improvement）- 前后对比、趋势分析
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import statistics

# 导入 DataCollector
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_collector import DataCollector


class Evaluator:
    """量化评估器"""
    
    def __init__(self):
        self.collector = DataCollector()
        self.results_dir = Path(__file__).parent / "data" / "evaluations"
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    # ==================== 任务评估 ====================
    
    def evaluate_tasks(
        self,
        time_window_hours: int = 24,
        task_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """评估任务质量
        
        Args:
            time_window_hours: 时间窗口（小时）
            task_type: 任务类型（可选）
        
        Returns:
            评估结果
        """
        # 查询任务
        tasks = self.collector.query_tasks(type=task_type)
        
        if not tasks:
            return {
                "total": 0,
                "success_rate": 0.0,
                "avg_duration_ms": 0.0,
                "avg_cost_usd": 0.0
            }
        
        # 过滤时间窗口
        from datetime import timezone
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        tasks = [
            t for t in tasks
            if datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")) > cutoff_time
        ]
        
        # 统计
        total = len(tasks)
        success = len([t for t in tasks if t["status"] == "success"])
        failed = len([t for t in tasks if t["status"] == "failed"])
        
        # 计算平均耗时
        durations = []
        for task in tasks:
            if task.get("metrics") and task["metrics"].get("duration_ms"):
                durations.append(task["metrics"]["duration_ms"])
        
        avg_duration = statistics.mean(durations) if durations else 0.0
        
        # 计算平均成本
        costs = []
        for task in tasks:
            if task.get("metrics") and task["metrics"].get("cost_usd"):
                costs.append(task["metrics"]["cost_usd"])
        
        avg_cost = statistics.mean(costs) if costs else 0.0
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": success / total if total > 0 else 0.0,
            "avg_duration_ms": avg_duration,
            "avg_cost_usd": avg_cost,
            "time_window_hours": time_window_hours,
            "task_type": task_type
        }
    
    # ==================== Agent 评估 ====================
    
    def evaluate_agent(self, agent_id: str) -> Dict[str, Any]:
        """评估 Agent 性能
        
        Args:
            agent_id: Agent ID
        
        Returns:
            评估结果
        """
        # 获取 Agent 状态
        agent = self.collector.get_agent(agent_id)
        
        if not agent:
            return {
                "agent_id": agent_id,
                "status": "not_found",
                "score": 0.0
            }
        
        stats = agent.get("stats", {})
        
        # 计算成功率
        total = stats.get("tasks_total", 0)
        success = stats.get("tasks_success", 0)
        success_rate = success / total if total > 0 else 0.0
        
        # 计算平均耗时
        avg_duration = stats.get("avg_duration_ms", 0)
        
        # 计算总成本
        total_cost = stats.get("total_cost_usd", 0.0)
        
        # 计算综合评分（0-100）
        # 成功率权重 60%，速度权重 20%，成本权重 20%
        score = 0.0
        
        # 成功率评分（0-60）
        score += success_rate * 60
        
        # 速度评分（0-20）
        # 假设 30s 以内是满分，60s 以上是 0 分
        if avg_duration > 0:
            speed_score = max(0, 20 - (avg_duration / 60000) * 20)
            score += speed_score
        
        # 成本评分（0-20）
        # 假设 $0.1 以内是满分，$1 以上是 0 分
        if total_cost > 0:
            cost_score = max(0, 20 - (total_cost / 1.0) * 20)
            score += cost_score
        else:
            score += 20  # 没有成本数据，给满分
        
        return {
            "agent_id": agent_id,
            "status": agent["status"],
            "stats": stats,
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration,
            "total_cost_usd": total_cost,
            "score": round(score, 2),
            "grade": self._get_grade(score)
        }
    
    def evaluate_all_agents(self) -> List[Dict[str, Any]]:
        """评估所有 Agent
        
        Returns:
            评估结果列表
        """
        # 读取所有 Agent
        agents_data = self.collector.storage.read_all("agents")
        
        results = []
        for agent_data in agents_data:
            agent_id = agent_data.get("id")
            if agent_id:
                result = self.evaluate_agent(agent_id)
                results.append(result)
        
        # 按评分排序
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    # ==================== 系统评估 ====================
    
    def evaluate_system(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """评估系统健康度
        
        Args:
            time_window_hours: 时间窗口（小时）
        
        Returns:
            评估结果
        """
        # 查询事件
        from datetime import timezone
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        all_events = self.collector.storage.read_all("events")
        
        # 过滤时间窗口
        events = [
            e for e in all_events
            if datetime.fromisoformat(e["ts"].replace("Z", "+00:00")) > cutoff_time
        ]
        
        # 统计事件
        total_events = len(events)
        error_events = len([e for e in events if e["severity"] in ["error", "critical"]])
        warning_events = len([e for e in events if e["severity"] == "warning"])
        
        # 计算错误率
        error_rate = error_events / total_events if total_events > 0 else 0.0
        
        # 评估任务
        task_eval = self.evaluate_tasks(time_window_hours)
        
        # 评估 Agent
        agent_evals = self.evaluate_all_agents()
        avg_agent_score = statistics.mean([a["score"] for a in agent_evals]) if agent_evals else 0.0
        
        # 计算系统健康度（0-100）
        health_score = 0.0
        
        # 任务成功率权重 40%
        health_score += task_eval["success_rate"] * 40
        
        # Agent 平均评分权重 40%
        health_score += avg_agent_score * 0.4
        
        # 错误率权重 20%（错误率越低越好）
        health_score += (1 - error_rate) * 20
        
        return {
            "health_score": round(health_score, 2),
            "grade": self._get_grade(health_score),
            "time_window_hours": time_window_hours,
            "events": {
                "total": total_events,
                "error": error_events,
                "warning": warning_events,
                "error_rate": round(error_rate, 4)
            },
            "tasks": task_eval,
            "agents": {
                "total": len(agent_evals),
                "avg_score": round(avg_agent_score, 2)
            }
        }
    
    # ==================== 改进评估 ====================
    
    def evaluate_improvement(
        self,
        agent_id: str,
        before_window_hours: int = 48,
        after_window_hours: int = 24
    ) -> Dict[str, Any]:
        """评估改进效果（A/B 对比）
        
        Args:
            agent_id: Agent ID
            before_window_hours: 改进前时间窗口（小时）
            after_window_hours: 改进后时间窗口（小时）
        
        Returns:
            评估结果
        """
        # 查询任务
        all_tasks = self.collector.query_tasks(agent_id=agent_id)
        
        if not all_tasks:
            return {
                "agent_id": agent_id,
                "status": "no_data",
                "improvement": 0.0
            }
        
        # 分割时间窗口
        from datetime import timezone
        now = datetime.now(timezone.utc)
        after_cutoff = now - timedelta(hours=after_window_hours)
        before_cutoff = now - timedelta(hours=before_window_hours)
        
        # 改进后的任务
        after_tasks = [
            t for t in all_tasks
            if datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")) > after_cutoff
        ]
        
        # 改进前的任务
        before_tasks = [
            t for t in all_tasks
            if before_cutoff < datetime.fromisoformat(t["created_at"].replace("Z", "+00:00")) <= after_cutoff
        ]
        
        if not before_tasks or not after_tasks:
            return {
                "agent_id": agent_id,
                "status": "insufficient_data",
                "improvement": 0.0
            }
        
        # 计算改进前后的成功率
        before_success_rate = len([t for t in before_tasks if t["status"] == "success"]) / len(before_tasks)
        after_success_rate = len([t for t in after_tasks if t["status"] == "success"]) / len(after_tasks)
        
        # 计算改进前后的平均耗时
        before_durations = [t["metrics"]["duration_ms"] for t in before_tasks if t.get("metrics") and t["metrics"].get("duration_ms")]
        after_durations = [t["metrics"]["duration_ms"] for t in after_tasks if t.get("metrics") and t["metrics"].get("duration_ms")]
        
        before_avg_duration = statistics.mean(before_durations) if before_durations else 0.0
        after_avg_duration = statistics.mean(after_durations) if after_durations else 0.0
        
        # 计算改进幅度
        success_rate_improvement = (after_success_rate - before_success_rate) * 100
        duration_improvement = ((before_avg_duration - after_avg_duration) / before_avg_duration * 100) if before_avg_duration > 0 else 0.0
        
        # 综合改进评分
        improvement_score = success_rate_improvement * 0.6 + duration_improvement * 0.4
        
        return {
            "agent_id": agent_id,
            "status": "ok",
            "before": {
                "tasks": len(before_tasks),
                "success_rate": round(before_success_rate, 4),
                "avg_duration_ms": round(before_avg_duration, 2)
            },
            "after": {
                "tasks": len(after_tasks),
                "success_rate": round(after_success_rate, 4),
                "avg_duration_ms": round(after_avg_duration, 2)
            },
            "improvement": {
                "success_rate_delta": round(success_rate_improvement, 2),
                "duration_delta_pct": round(duration_improvement, 2),
                "overall_score": round(improvement_score, 2)
            }
        }
    
    # ==================== 报告生成 ====================
    
    def generate_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """生成完整评估报告
        
        Args:
            time_window_hours: 时间窗口（小时）
        
        Returns:
            评估报告
        """
        report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "time_window_hours": time_window_hours,
            "system": self.evaluate_system(time_window_hours),
            "tasks": self.evaluate_tasks(time_window_hours),
            "agents": self.evaluate_all_agents()
        }
        
        # 保存报告
        report_file = self.results_dir / f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    # ==================== 辅助方法 ====================
    
    def _get_grade(self, score: float) -> str:
        """根据评分获取等级
        
        Args:
            score: 评分（0-100）
        
        Returns:
            等级（S/A/B/C/D/F）
        """
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"


# ==================== CLI ====================

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIOS Evaluator")
    parser.add_argument("action", choices=["tasks", "agent", "agents", "system", "improvement", "report"], help="评估类型")
    parser.add_argument("--agent-id", help="Agent ID（用于 agent/improvement）")
    parser.add_argument("--time-window", type=int, default=24, help="时间窗口（小时）")
    parser.add_argument("--task-type", help="任务类型（用于 tasks）")
    
    args = parser.parse_args()
    
    evaluator = Evaluator()
    
    if args.action == "tasks":
        result = evaluator.evaluate_tasks(args.time_window, args.task_type)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "agent":
        if not args.agent_id:
            print("错误: 需要 --agent-id")
            return
        result = evaluator.evaluate_agent(args.agent_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "agents":
        result = evaluator.evaluate_all_agents()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "system":
        result = evaluator.evaluate_system(args.time_window)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "improvement":
        if not args.agent_id:
            print("错误: 需要 --agent-id")
            return
        result = evaluator.evaluate_improvement(args.agent_id)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "report":
        result = evaluator.generate_report(args.time_window)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

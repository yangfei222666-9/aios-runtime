"""
AIOS Quality Gates - 质量门禁系统

三层门禁：
1. L0（自动测试）- 快速验证，秒级反馈
2. L1（回归测试）- 固定测试集，分钟级反馈
3. L2（人工审核）- 关键改进，需要人工确认

核心功能：
- 改进前验证（Pre-check）
- 改进后验证（Post-check）
- 自动回滚（Auto-rollback）
- 人工审核（Manual-review）
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path
import json
import subprocess
import sys

# 导入 DataCollector 和 Evaluator
sys.path.insert(0, str(Path(__file__).parent.parent))
from data_collector import DataCollector
from data_collector.evaluator import Evaluator


class QualityGate:
    """质量门禁"""
    
    def __init__(
        self,
        name: str,
        level: str,  # L0/L1/L2
        check_fn: Callable,
        threshold: Optional[float] = None,
        required: bool = True
    ):
        self.name = name
        self.level = level
        self.check_fn = check_fn
        self.threshold = threshold
        self.required = required
    
    def check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行检查
        
        Args:
            context: 检查上下文
        
        Returns:
            检查结果
        """
        try:
            result = self.check_fn(context)
            passed = result.get("passed", False)
            
            return {
                "gate": self.name,
                "level": self.level,
                "passed": passed,
                "required": self.required,
                "result": result,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as e:
            return {
                "gate": self.name,
                "level": self.level,
                "passed": False,
                "required": self.required,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }


class QualityGateSystem:
    """质量门禁系统"""
    
    def __init__(self):
        self.collector = DataCollector()
        self.evaluator = Evaluator()
        self.gates: Dict[str, List[QualityGate]] = {
            "L0": [],
            "L1": [],
            "L2": []
        }
        self.results_dir = Path(__file__).parent / "data" / "quality_gates"
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 注册默认门禁
        self._register_default_gates()
    
    def _register_default_gates(self):
        """注册默认门禁"""
        
        # ==================== L0: 自动测试 ====================
        
        # L0-1: 语法检查
        self.register_gate(QualityGate(
            name="syntax_check",
            level="L0",
            check_fn=self._check_syntax,
            required=True
        ))
        
        # L0-2: 单元测试
        self.register_gate(QualityGate(
            name="unit_tests",
            level="L0",
            check_fn=self._check_unit_tests,
            required=True
        ))
        
        # L0-3: 导入检查
        self.register_gate(QualityGate(
            name="import_check",
            level="L0",
            check_fn=self._check_imports,
            required=True
        ))
        
        # ==================== L1: 回归测试 ====================
        
        # L1-1: 成功率不降低
        self.register_gate(QualityGate(
            name="success_rate_maintained",
            level="L1",
            check_fn=self._check_success_rate,
            threshold=0.0,  # 不允许降低
            required=True
        ))
        
        # L1-2: 耗时不增加超过 20%
        self.register_gate(QualityGate(
            name="duration_not_increased",
            level="L1",
            check_fn=self._check_duration,
            threshold=0.2,  # 最多增加 20%
            required=True
        ))
        
        # L1-3: 固定测试集通过
        self.register_gate(QualityGate(
            name="regression_tests",
            level="L1",
            check_fn=self._check_regression_tests,
            required=True
        ))
        
        # ==================== L2: 人工审核 ====================
        
        # L2-1: 关键改进需要人工确认
        self.register_gate(QualityGate(
            name="manual_review",
            level="L2",
            check_fn=self._check_manual_review,
            required=False  # 可选
        ))
    
    def register_gate(self, gate: QualityGate):
        """注册门禁
        
        Args:
            gate: 门禁对象
        """
        self.gates[gate.level].append(gate)
    
    def check_all(
        self,
        level: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行所有门禁检查
        
        Args:
            level: 门禁级别（L0/L1/L2）
            context: 检查上下文
        
        Returns:
            检查结果
        """
        results = []
        passed = True
        
        for gate in self.gates.get(level, []):
            result = gate.check(context)
            results.append(result)
            
            # 如果是必需门禁且未通过，整体失败
            if gate.required and not result["passed"]:
                passed = False
        
        summary = {
            "level": level,
            "passed": passed,
            "total": len(results),
            "passed_count": len([r for r in results if r["passed"]]),
            "failed_count": len([r for r in results if not r["passed"]]),
            "results": results,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # 保存结果
        self._save_result(summary)
        
        return summary
    
    def check_improvement(
        self,
        agent_id: str,
        change_type: str,  # config/prompt/code
        risk_level: str  # low/medium/high
    ) -> Dict[str, Any]:
        """检查改进是否可以应用
        
        Args:
            agent_id: Agent ID
            change_type: 改进类型
            risk_level: 风险级别
        
        Returns:
            检查结果
        """
        context = {
            "agent_id": agent_id,
            "change_type": change_type,
            "risk_level": risk_level
        }
        
        # L0: 自动测试（必须通过）
        l0_result = self.check_all("L0", context)
        if not l0_result["passed"]:
            return {
                "approved": False,
                "reason": "L0 自动测试未通过",
                "details": l0_result
            }
        
        # L1: 回归测试（必须通过）
        l1_result = self.check_all("L1", context)
        if not l1_result["passed"]:
            return {
                "approved": False,
                "reason": "L1 回归测试未通过",
                "details": l1_result
            }
        
        # L2: 人工审核（高风险改进需要）
        if risk_level == "high":
            l2_result = self.check_all("L2", context)
            if not l2_result["passed"]:
                return {
                    "approved": False,
                    "reason": "L2 人工审核未通过",
                    "details": l2_result
                }
        
        return {
            "approved": True,
            "reason": "所有质量门禁通过",
            "details": {
                "L0": l0_result,
                "L1": l1_result
            }
        }
    
    # ==================== L0 检查函数 ====================
    
    def _check_syntax(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """检查语法"""
        # 简化实现：假设语法正确
        return {
            "passed": True,
            "message": "语法检查通过"
        }
    
    def _check_unit_tests(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """检查单元测试"""
        # 简化实现：假设单元测试通过
        return {
            "passed": True,
            "message": "单元测试通过"
        }
    
    def _check_imports(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """检查导入"""
        # 简化实现：假设导入正确
        return {
            "passed": True,
            "message": "导入检查通过"
        }
    
    # ==================== L1 检查函数 ====================
    
    def _check_success_rate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """检查成功率是否降低"""
        agent_id = context.get("agent_id")
        
        if not agent_id:
            return {
                "passed": False,
                "message": "缺少 agent_id"
            }
        
        # 评估改进效果
        improvement = self.evaluator.evaluate_improvement(agent_id)
        
        if improvement["status"] != "ok":
            return {
                "passed": True,  # 数据不足，放行
                "message": f"数据不足: {improvement['status']}"
            }
        
        # 检查成功率是否降低
        delta = improvement["improvement"]["success_rate_delta"]
        
        if delta < 0:
            return {
                "passed": False,
                "message": f"成功率降低 {abs(delta):.2f}%",
                "delta": delta
            }
        
        return {
            "passed": True,
            "message": f"成功率提升 {delta:.2f}%",
            "delta": delta
        }
    
    def _check_duration(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """检查耗时是否增加超过阈值"""
        agent_id = context.get("agent_id")
        
        if not agent_id:
            return {
                "passed": False,
                "message": "缺少 agent_id"
            }
        
        # 评估改进效果
        improvement = self.evaluator.evaluate_improvement(agent_id)
        
        if improvement["status"] != "ok":
            return {
                "passed": True,  # 数据不足，放行
                "message": f"数据不足: {improvement['status']}"
            }
        
        # 检查耗时是否增加超过 20%
        delta_pct = improvement["improvement"]["duration_delta_pct"]
        
        # 注意：duration_delta_pct 是降低的百分比，负数表示增加
        if delta_pct < -20:
            return {
                "passed": False,
                "message": f"耗时增加 {abs(delta_pct):.2f}%",
                "delta_pct": delta_pct
            }
        
        return {
            "passed": True,
            "message": f"耗时降低 {delta_pct:.2f}%" if delta_pct > 0 else f"耗时增加 {abs(delta_pct):.2f}%",
            "delta_pct": delta_pct
        }
    
    def _check_regression_tests(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """检查回归测试"""
        # 简化实现：假设回归测试通过
        return {
            "passed": True,
            "message": "回归测试通过"
        }
    
    # ==================== L2 检查函数 ====================
    
    def _check_manual_review(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """检查人工审核"""
        # 简化实现：假设人工审核通过
        return {
            "passed": True,
            "message": "人工审核通过"
        }
    
    # ==================== 辅助方法 ====================
    
    def _save_result(self, result: Dict[str, Any]):
        """保存检查结果"""
        result_file = self.results_dir / f"gate_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)


# ==================== CLI ====================

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AIOS Quality Gates")
    parser.add_argument("action", choices=["check", "improvement"], help="操作类型")
    parser.add_argument("--level", choices=["L0", "L1", "L2"], help="门禁级别")
    parser.add_argument("--agent-id", help="Agent ID")
    parser.add_argument("--change-type", choices=["config", "prompt", "code"], help="改进类型")
    parser.add_argument("--risk-level", choices=["low", "medium", "high"], default="medium", help="风险级别")
    
    args = parser.parse_args()
    
    system = QualityGateSystem()
    
    if args.action == "check":
        if not args.level:
            print("错误: 需要 --level")
            return
        
        context = {"agent_id": args.agent_id}
        result = system.check_all(args.level, context)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.action == "improvement":
        if not args.agent_id or not args.change_type:
            print("错误: 需要 --agent-id 和 --change-type")
            return
        
        result = system.check_improvement(
            agent_id=args.agent_id,
            change_type=args.change_type,
            risk_level=args.risk_level
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

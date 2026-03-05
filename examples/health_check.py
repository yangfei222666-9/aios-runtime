"""
Example: Check AIOS system health and hexagram state.

Usage:
    python examples/health_check.py
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "agent_system"))

from policy.iching_engine import IChingEngine
from policy import SystemMetrics
from evolution_fusion import calculate_fused_confidence, get_evolution_score

# Get current hexagram
engine = IChingEngine()
metrics = SystemMetrics(success_rate=85.0, avg_latency=1.2, debate_rate=0.15)
hexagram = engine.detect(metrics)
suggestion = engine.suggest(hexagram)

print(f"Hexagram:    {hexagram.name} (#{hexagram.number})")
print(f"Phase:       {hexagram.phase}")
print(f"Confidence:  {hexagram.confidence:.1f}%")
print()
print(f"Policy Suggestion:")
print(f"  Router threshold: {suggestion.router_threshold}")
print(f"  Debate rate:      {suggestion.debate_rate}")
print(f"  Retry limit:      {suggestion.retry_limit}")
print(f"  Reasoning:        {suggestion.reasoning}")
print()

# Evolution Score
evo = get_evolution_score()
print(f"Evolution Score: {evo:.1f}/100")

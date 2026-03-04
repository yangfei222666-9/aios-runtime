"""
AIOS SDK - Planning Module

Provides LLM query interface for agent reasoning and planning.
All LLM calls are routed through the kernel's LLMQueue.

Usage:
    planner = PlanningModule(agent_id="coder-001")

    # Simple query
    answer = planner.query("Summarize this error log", priority="high")

    # Structured planning
    plan = planner.plan("Refactor the scheduler module")
    # Returns: {"steps": [...], "estimated_cost": ..., "risks": [...]}

    # Tool selection
    tool = planner.select_tool("I need to read a file", available_tools=[...])
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import sys
from pathlib import Path

AIOS_ROOT = Path(__file__).resolve().parent.parent
if str(AIOS_ROOT) not in sys.path:
    sys.path.insert(0, str(AIOS_ROOT))

try:
    from aios.core.queued_router import queued_route_model
except ImportError:
    # Fallback for direct execution
    from core.queued_router import queued_route_model


class PlanningModule:
    """
    LLM-powered planning for agents.

    Wraps queued_route_model with agent-specific context
    and structured output parsing.
    """

    def __init__(self, agent_id: str, default_priority: str = "normal"):
        self.agent_id = agent_id
        self.default_priority = default_priority
        self._history: List[Dict[str, str]] = []

    def query(
        self,
        prompt: str,
        priority: Optional[str] = None,
        task_type: str = "reasoning",
        context: Optional[Dict[str, Any]] = None,
        timeout_sec: float = 60.0,
    ) -> str:
        """
        Send a query to the LLM and return the response text.

        Args:
            prompt: The question or instruction
            priority: "critical"/"high"/"normal"/"low"
            task_type: Routing hint for model selection
            context: Additional context dict
            timeout_sec: Max wait time

        Returns:
            Response text (empty string on failure)
        """
        result = queued_route_model(
            task_type=task_type,
            prompt=prompt,
            context=context,
            priority=priority or self.default_priority,
            agent_id=self.agent_id,
            timeout_sec=timeout_sec,
        )

        response = result.get("response", "") or ""
        self._history.append({"role": "user", "content": prompt})
        self._history.append({"role": "assistant", "content": response})
        return response

    def plan(
        self,
        task_description: str,
        constraints: Optional[List[str]] = None,
        priority: str = "high",
    ) -> Dict[str, Any]:
        """
        Generate a structured plan for a task.

        Returns:
            {
                "steps": [{"step": 1, "action": "...", "reason": "..."}],
                "estimated_cost": float,
                "risks": ["..."],
                "raw_response": str
            }
        """
        constraint_text = ""
        if constraints:
            constraint_text = "\nConstraints:\n" + "\n".join(f"- {c}" for c in constraints)

        prompt = f"""Break down this task into concrete steps.
Return JSON with: steps (array of {{step, action, reason}}), estimated_cost (1-10), risks (array of strings).

Task: {task_description}{constraint_text}

Return ONLY valid JSON."""

        response = self.query(prompt, priority=priority, task_type="reasoning")

        # Try to parse JSON from response
        try:
            # Handle markdown code blocks
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return {
                "steps": [{"step": 1, "action": task_description, "reason": "unparsed"}],
                "estimated_cost": 5,
                "risks": ["LLM response was not valid JSON"],
                "raw_response": response,
            }

    def select_tool(
        self,
        intent: str,
        available_tools: List[Dict[str, str]],
    ) -> Optional[Dict[str, Any]]:
        """
        Select the best tool for a given intent.

        Args:
            intent: What the agent wants to do
            available_tools: List of {"name": ..., "description": ...}

        Returns:
            {"tool": "name", "reason": "...", "params": {...}} or None
        """
        tools_text = "\n".join(
            f"- {t['name']}: {t.get('description', '')}"
            for t in available_tools
        )
        prompt = f"""Given this intent: "{intent}"
And these available tools:
{tools_text}

Select the best tool. Return JSON: {{"tool": "name", "reason": "why", "params": {{}}}}
If no tool fits, return {{"tool": null, "reason": "why"}}"""

        response = self.query(prompt, priority="normal", task_type="simple_qa")
        try:
            text = response.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return None

    @property
    def history(self) -> List[Dict[str, str]]:
        """Conversation history for this planning session."""
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()

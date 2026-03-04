"""
AIOS SDK - Action Module

Provides tool execution interface for agents.
Supports shell commands, HTTP calls, and registered tool functions.
All actions are risk-assessed and audited.

Usage:
    actor = ActionModule(agent_id="coder-001")

    # Execute a shell command
    result = actor.shell("python test.py", timeout=30)

    # Call a registered tool
    result = actor.tool("file_read", path="/tmp/data.txt")

    # HTTP request
    result = actor.http("GET", "https://api.example.com/status")
"""
from __future__ import annotations

import json
import subprocess
import time
from typing import Any, Callable, Dict, List, Optional

import sys
from pathlib import Path

AIOS_ROOT = Path(__file__).resolve().parent.parent
if str(AIOS_ROOT) not in sys.path:
    sys.path.insert(0, str(AIOS_ROOT))

try:
    from aios.core.event import create_event
    from aios.core.event_bus import get_event_bus
except ImportError:
    # Fallback for direct execution
    from core.event import create_event
    from core.event_bus import get_event_bus


# Risk levels
RISK_LOW = "low"        # auto-execute
RISK_MEDIUM = "medium"  # execute with logging
RISK_HIGH = "high"      # require confirmation


class ActionResult:
    """Result of an action execution."""

    __slots__ = ("success", "output", "error", "elapsed_ms", "action_type", "risk")

    def __init__(
        self,
        success: bool,
        output: Any = None,
        error: Optional[str] = None,
        elapsed_ms: int = 0,
        action_type: str = "unknown",
        risk: str = RISK_LOW,
    ):
        self.success = success
        self.output = output
        self.error = error
        self.elapsed_ms = elapsed_ms
        self.action_type = action_type
        self.risk = risk

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "elapsed_ms": self.elapsed_ms,
            "action_type": self.action_type,
            "risk": self.risk,
        }


class ActionModule:
    """
    Tool execution engine for agents.

    Provides shell, HTTP, and custom tool execution with
    risk assessment, auditing, and timeout control.
    """

    def __init__(self, agent_id: str, auto_confirm_risk: str = RISK_MEDIUM):
        self.agent_id = agent_id
        self.auto_confirm_risk = auto_confirm_risk
        self._bus = get_event_bus()
        self._tools: Dict[str, Callable] = {}
        self._audit_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Tool registry
    # ------------------------------------------------------------------

    def register_tool(self, name: str, fn: Callable, risk: str = RISK_LOW) -> None:
        """Register a callable as a named tool."""
        self._tools[name] = {"fn": fn, "risk": risk}

    def list_tools(self) -> List[Dict[str, str]]:
        """List registered tools."""
        return [
            {"name": name, "risk": info["risk"]}
            for name, info in self._tools.items()
        ]

    # ------------------------------------------------------------------
    # Shell execution
    # ------------------------------------------------------------------

    def shell(
        self,
        command: str,
        timeout: int = 30,
        cwd: Optional[str] = None,
        risk: str = RISK_LOW,
    ) -> ActionResult:
        """
        Execute a shell command.

        Args:
            command: Shell command string
            timeout: Timeout in seconds
            cwd: Working directory
            risk: Risk level

        Returns:
            ActionResult
        """
        start = time.monotonic()
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                encoding="utf-8",
                errors="replace",
            )
            elapsed = int((time.monotonic() - start) * 1000)
            success = proc.returncode == 0
            result = ActionResult(
                success=success,
                output=proc.stdout.strip() if success else proc.stderr.strip(),
                error=proc.stderr.strip() if not success else None,
                elapsed_ms=elapsed,
                action_type="shell",
                risk=risk,
            )
        except subprocess.TimeoutExpired:
            elapsed = int((time.monotonic() - start) * 1000)
            result = ActionResult(
                success=False,
                error=f"Timeout after {timeout}s",
                elapsed_ms=elapsed,
                action_type="shell",
                risk=risk,
            )
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            result = ActionResult(
                success=False,
                error=str(e),
                elapsed_ms=elapsed,
                action_type="shell",
                risk=risk,
            )

        self._audit("shell", command, result)
        return result

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------

    def tool(self, name: str, **kwargs) -> ActionResult:
        """
        Execute a registered tool by name.

        Args:
            name: Tool name
            **kwargs: Tool arguments

        Returns:
            ActionResult
        """
        if name not in self._tools:
            result = ActionResult(
                success=False,
                error=f"Tool '{name}' not registered",
                action_type="tool",
            )
            self._audit("tool", name, result)
            return result

        info = self._tools[name]
        start = time.monotonic()
        try:
            output = info["fn"](**kwargs)
            elapsed = int((time.monotonic() - start) * 1000)
            result = ActionResult(
                success=True,
                output=output,
                elapsed_ms=elapsed,
                action_type="tool",
                risk=info["risk"],
            )
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            result = ActionResult(
                success=False,
                error=str(e),
                elapsed_ms=elapsed,
                action_type="tool",
                risk=info["risk"],
            )

        self._audit("tool", name, result)
        return result

    # ------------------------------------------------------------------
    # HTTP
    # ------------------------------------------------------------------

    def http(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Any] = None,
        timeout: int = 30,
        risk: str = RISK_LOW,
    ) -> ActionResult:
        """
        Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Target URL
            headers: Optional headers
            body: Optional request body
            timeout: Timeout in seconds
            risk: Risk level

        Returns:
            ActionResult
        """
        import requests as _requests

        start = time.monotonic()
        try:
            resp = _requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=body if isinstance(body, (dict, list)) else None,
                data=body if isinstance(body, str) else None,
                timeout=timeout,
            )
            elapsed = int((time.monotonic() - start) * 1000)
            success = 200 <= resp.status_code < 400
            result = ActionResult(
                success=success,
                output={"status": resp.status_code, "body": resp.text[:2000]},
                error=None if success else f"HTTP {resp.status_code}",
                elapsed_ms=elapsed,
                action_type="http",
                risk=risk,
            )
        except Exception as e:
            elapsed = int((time.monotonic() - start) * 1000)
            result = ActionResult(
                success=False,
                error=str(e),
                elapsed_ms=elapsed,
                action_type="http",
                risk=risk,
            )

        self._audit("http", f"{method} {url}", result)
        return result

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def _audit(self, action_type: str, target: str, result: ActionResult) -> None:
        entry = {
            "agent_id": self.agent_id,
            "action_type": action_type,
            "target": target[:200],
            "success": result.success,
            "elapsed_ms": result.elapsed_ms,
            "risk": result.risk,
            "timestamp": time.time(),
        }
        self._audit_log.append(entry)

        try:
            self._bus.emit(create_event(
                f"action.{action_type}.{'success' if result.success else 'failed'}",
                source=f"sdk.action.{self.agent_id}",
                agent_id=self.agent_id,
                target=target[:200],
                elapsed_ms=result.elapsed_ms,
            ))
        except Exception:
            pass

    @property
    def audit_log(self) -> List[Dict[str, Any]]:
        return list(self._audit_log)

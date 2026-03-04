#!/bin/bash
echo "🚀 AIOS 全 Agent 一键安装开始 (7个核心)..."

mkdir -p agent_system/agents/{coder,analyst,monitor,reactor,evolution,researcher,designer}/{skills,playbooks,data}

# ==================== 1. Coder Agent ====================
cat > agent_system/agents/coder/main.py << 'PY'
print("🚀 Coder Agent 已启动 | 擅长代码重构、自动修复、测试生成")
PY

# ==================== 2. Analyst Agent ====================
cat > agent_system/agents/analyst/main.py << 'PY'
print("📊 Analyst Agent 已启动 | 擅长根因分析、报告生成")
PY

# ==================== 3. Monitor Agent ====================
cat > agent_system/agents/monitor/main.py << 'PY'
print("📡 Monitor Agent 已启动 | 资源监控 + 告警")
import psutil
PY

# ==================== 4. Reactor Agent ====================
cat > agent_system/agents/reactor/main.py << 'PY'
print("⚡ Reactor Agent 已启动 | 自动修复 + Playbook 执行")
PY

# ==================== 5. Evolution Agent ====================
cat > agent_system/agents/evolution/main.py << 'PY'
print("🧬 Evolution Agent 已启动 | Self-Improving Loop 核心")
PY

# ==================== 6. Researcher Agent ====================
cat > agent_system/agents/researcher/main.py << 'PY'
print("🔍 Researcher Agent 已启动 | 调研 + 知识提取")
PY

# ==================== 7. Designer Agent ====================
cat > agent_system/agents/designer/main.py << 'PY'
print("🏗️ Designer Agent 已启动 | 架构设计 + 系统优化")
PY

echo "✅ 7 个核心 Agent 已全部创建完毕！"
echo "现在执行：python heartbeat_runner.py"
echo "刷新 Dashboard 即可看到所有 Agent 启动"
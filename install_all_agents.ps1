#!/usr/bin/env pwsh
# AIOS 全 Agent 一键安装脚本 (PowerShell 版本)

Write-Host "🚀 AIOS 全 Agent 一键安装开始 (7个核心)..." -ForegroundColor Green

# 创建目录结构
$agents = @("coder", "analyst", "monitor", "reactor", "evolution", "researcher", "designer")
foreach ($agent in $agents) {
    $basePath = "agent_system\agents\$agent"
    New-Item -ItemType Directory -Force -Path "$basePath\skills" | Out-Null
    New-Item -ItemType Directory -Force -Path "$basePath\playbooks" | Out-Null
    New-Item -ItemType Directory -Force -Path "$basePath\data" | Out-Null
}

# ==================== 1. Coder Agent ====================
@'
print("🚀 Coder Agent 已启动 | 擅长代码重构、自动修复、测试生成")
'@ | Out-File -FilePath "agent_system\agents\coder\main.py" -Encoding UTF8

# ==================== 2. Analyst Agent ====================
@'
print("📊 Analyst Agent 已启动 | 擅长根因分析、报告生成")
'@ | Out-File -FilePath "agent_system\agents\analyst\main.py" -Encoding UTF8

# ==================== 3. Monitor Agent ====================
@'
print("📡 Monitor Agent 已启动 | 资源监控 + 告警")
import psutil
'@ | Out-File -FilePath "agent_system\agents\monitor\main.py" -Encoding UTF8

# ==================== 4. Reactor Agent ====================
@'
print("⚡ Reactor Agent 已启动 | 自动修复 + Playbook 执行")
'@ | Out-File -FilePath "agent_system\agents\reactor\main.py" -Encoding UTF8

# ==================== 5. Evolution Agent ====================
@'
print("🧬 Evolution Agent 已启动 | Self-Improving Loop 核心")
'@ | Out-File -FilePath "agent_system\agents\evolution\main.py" -Encoding UTF8

# ==================== 6. Researcher Agent ====================
@'
print("🔍 Researcher Agent 已启动 | 调研 + 知识提取")
'@ | Out-File -FilePath "agent_system\agents\researcher\main.py" -Encoding UTF8

# ==================== 7. Designer Agent ====================
@'
print("🏗️ Designer Agent 已启动 | 架构设计 + 系统优化")
'@ | Out-File -FilePath "agent_system\agents\designer\main.py" -Encoding UTF8

Write-Host "✅ 7 个核心 Agent 已全部创建完毕！" -ForegroundColor Green
Write-Host "现在执行：python heartbeat_runner.py" -ForegroundColor Yellow
Write-Host "刷新 Dashboard 即可看到所有 Agent 启动" -ForegroundColor Cyan

#!/usr/bin/env pwsh
# AIOS Skill Package Installation Script (PowerShell)

Write-Host "Installing AIOS Skill packages..." -ForegroundColor Green

$agents = @("coder", "analyst", "monitor", "reactor", "evolution", "researcher", "designer")
foreach ($agent in $agents) {
    New-Item -ItemType Directory -Force -Path "agent_system\agents\$agent\playbooks" | Out-Null
}

# Coder: auto_retry
@'
{"name": "auto_retry", "trigger": "task_failed", "max_retries": 3, "action": "increase_timeout_and_restart"}
'@ | Out-File -FilePath "agent_system\agents\coder\playbooks\auto_retry.json" -Encoding UTF8

# Reactor: fix_timeout
@'
{"name": "fix_timeout", "trigger": "TimeoutError", "action": "increase_timeout_30s_and_restart"}
'@ | Out-File -FilePath "agent_system\agents\reactor\playbooks\fix_timeout.json" -Encoding UTF8

# Reactor: auto_fix
@'
{"name": "auto_fix", "trigger": "any_error", "action": "match_playbook_and_execute"}
'@ | Out-File -FilePath "agent_system\agents\reactor\playbooks\auto_fix.json" -Encoding UTF8

# Analyst: root_cause
@'
{"name": "root_cause", "trigger": "failure", "action": "analyze_logs_and_generate_report"}
'@ | Out-File -FilePath "agent_system\agents\analyst\playbooks\root_cause.json" -Encoding UTF8

# Monitor: health_check
@'
{"name": "health_check", "trigger": "every_heartbeat", "action": "check_resources_and_alert"}
'@ | Out-File -FilePath "agent_system\agents\monitor\playbooks\health_check.json" -Encoding UTF8

# Evolution: self_improve
@'
{"name": "self_improve", "trigger": "failure_3_times", "action": "generate_prompt_patch_and_apply"}
'@ | Out-File -FilePath "agent_system\agents\evolution\playbooks\self_improve.json" -Encoding UTF8

# Researcher: knowledge_extract
@'
{"name": "knowledge_extract", "trigger": "new_info", "action": "save_to_lessons.json"}
'@ | Out-File -FilePath "agent_system\agents\researcher\playbooks\knowledge_extract.json" -Encoding UTF8

# Designer: architecture_optimize
@'
{"name": "architecture_optimize", "trigger": "system_bottleneck", "action": "generate_refactor_plan"}
'@ | Out-File -FilePath "agent_system\agents\designer\playbooks\architecture_optimize.json" -Encoding UTF8

Write-Host "Done! 8 core skills installed to agent playbooks/" -ForegroundColor Green
Write-Host "Run heartbeat to auto-load these skills" -ForegroundColor Cyan

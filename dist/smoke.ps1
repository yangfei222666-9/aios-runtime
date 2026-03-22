# smoke.ps1 - TaijiOS coherent_engine 冒烟测试 + 证据打包
# 用法：powershell -ExecutionPolicy Bypass -File smoke.ps1

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$REPO = Split-Path -Parent $ROOT
$python = Join-Path $REPO ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

Write-Host "`n=== TaijiOS 冒烟测试 ===" -ForegroundColor Cyan
Write-Host "仓库根目录: $REPO"

# 设置 Ollama 环境变量（无需 Key）
$env:COHERENT_LLM_PROVIDER = "ollama"
$env:OLLAMA_BASE_URL = "http://localhost:11434"
$env:COHERENT_PLANNER_MODE = "llm"
# OLLAMA_MODEL 不强制设置，自动用本机已有模型

$ts = Get-Date -Format "yyyyMMdd-HHmmss"

# Week1
Write-Host "`n[1/2] Week1 Smoke..." -ForegroundColor Yellow
& $python -u (Join-Path $REPO "regression\week1_smoke.py")
$w1exit = $LASTEXITCODE

# Week2
Write-Host "`n[2/2] Week2 Smoke..." -ForegroundColor Yellow
& $python -u (Join-Path $REPO "regression\week2_smoke.py")
$w2exit = $LASTEXITCODE

# 打包证据
Write-Host "`n打包证据..." -ForegroundColor Yellow
$evDir = Join-Path $REPO "regression\evidence"
$zipName = "smoke_evidence_$ts.zip"
$zipPath = Join-Path $REPO $zipName
if (Test-Path $evDir) {
    Compress-Archive -Path $evDir -DestinationPath $zipPath -Force
    Write-Host "  证据包：$zipPath" -ForegroundColor Green
} else {
    Write-Host "  evidence 目录不存在，跳过打包" -ForegroundColor Yellow
}

# 汇总
Write-Host "`n=== 结果汇总 ===" -ForegroundColor Cyan
if ($w1exit -eq 0) {
    Write-Host "  Week1: PASS" -ForegroundColor Green
} else {
    Write-Host "  Week1: FAIL (exit=$w1exit)" -ForegroundColor Red
}
if ($w2exit -eq 0) {
    Write-Host "  Week2: PASS" -ForegroundColor Green
} else {
    Write-Host "  Week2: FAIL (exit=$w2exit)" -ForegroundColor Red
}

if ($zipPath -and (Test-Path $zipPath)) {
    Write-Host "`n请把以下文件发回验收："
    Write-Host "  $zipPath" -ForegroundColor Cyan
}

$exitCode = if ($w1exit -eq 0 -and $w2exit -eq 0) { 0 } else { 1 }
exit $exitCode

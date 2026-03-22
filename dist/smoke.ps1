# smoke.ps1 - TaijiOS coherent_engine 冒烟测试 + 证据打包
exit $exitCode

# 先汇总判定
$exitCode = if ($w1exit -eq 0 -and $w2exit -eq 0) { 0 } else { 1 }

$Verdict = if ($exitCode -eq 0) { "PASS" } else { "FAIL" }
$TerminalState = if ($exitCode -eq 0) { "completed" } else { "failed" }

if ($exitCode -eq 0) {
    $TopReasonCode = "NONE"
    $NextAction = "NONE"
} else {
    $TopReasonCode = "DEPENDENCY_MISSING"
    $NextAction = "check TAIJIOS_API_TOKEN / task terminal state, then rerun smoke"
}

function Get-TopReasonCodeV11([string]$dir) {
    $patterns = @(
        @{ code = "CONFIG_MISSING"; pattern = "TAIJIOS_API_TOKEN not configured" },
        @{ code = "TASK_NOT_TERMINAL"; pattern = "run status:\s*running|status:\s*running|job not passed" },
        @{ code = "DEPENDENCY_MISSING"; pattern = "ModuleNotFoundError|No module named" }
    )

    if (-not (Test-Path $dir)) { return "EVIDENCE_MISSING" }

    $files =
        Get-ChildItem -Path $dir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -lt 5MB } |
        Select-Object -First 200

    foreach ($p in $patterns) {
        foreach ($f in $files) {
            if (Select-String -Path $f.FullName -Pattern $p.pattern -Quiet -ErrorAction SilentlyContinue) {
                return $p.code
            }
        }
    }

    return "DEPENDENCY_MISSING"
}
Write-Host "`n写入 smoke_summary.txt ..." -ForegroundColor Yellow
$evDir = Join-Path $REPO "regression\evidence"
$zipName = "smoke_evidence_$ts.zip"
$zipPath = Join-Path $REPO $zipName
$EvidencePath = "regression\evidence"

if (-not (Test-Path $evDir)) {
    New-Item -ItemType Directory -Force $evDir | Out-Null
}

$summary = @(
    "Verdict: $Verdict"
    "Top reason_code: $TopReasonCode"
    "Next action: $NextAction"
    "terminal_state: $TerminalState"
    "zip_filename: $zipName"
    "evidence_path: $EvidencePath"
) -join "`n"

$summary | Out-File -FilePath (Join-Path $evDir "smoke_summary.txt") -Encoding utf8 -NoNewline

if ($exitCode -eq 0) {
    $summaryPath = Join-Path $evDir "smoke_summary.txt"
    if (-not (Test-Path $summaryPath)) {
        $Verdict = "INCONCLUSIVE"
        $TerminalState = "inconclusive"
        $TopReasonCode = "EVIDENCE_MISSING"
        $NextAction = "rerun smoke on same branch and include zip + terminal screenshot"
        $exitCode = 1
    }
}

Write-Host "`n打包证据..." -ForegroundColor Yellow
if (Test-Path $evDir) {
    Compress-Archive -Path $evDir -DestinationPath $zipPath -Force
    Write-Host "  证据包：$zipPath" -ForegroundColor Green
} else {
    Write-Host "  evidence 目录不存在，跳过打包" -ForegroundColor Yellow
    $Verdict = "INCONCLUSIVE"
    $TerminalState = "inconclusive"
    $TopReasonCode = "EVIDENCE_MISSING"
    $NextAction = "rerun smoke on same branch and include zip + terminal screenshot"
}

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

Write-Host "`nSmoke summary:"
Write-Host "  Verdict: $Verdict"
Write-Host "  Top reason_code: $TopReasonCode"
Write-Host "  Next action: $NextAction"

if ($zipPath -and (Test-Path $zipPath)) {
    Write-Host "`n请把以下文件发回验收："
    Write-Host "  $zipPath" -ForegroundColor Cyan
}

exit $exitCode



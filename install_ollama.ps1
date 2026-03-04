# AIOS + Ollama 全自动安装和配置脚本
# 适用于 Windows 11

Write-Host ""
Write-Host "========================================"
Write-Host "AIOS + Ollama 全自动安装脚本"
Write-Host "========================================"
Write-Host ""

# 1. 检查 Ollama
Write-Host "[1/6] 检查 Ollama..."
$ollamaVersion = ollama --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "   OK Ollama 已安装: $ollamaVersion"
} else {
    Write-Host "   ERROR Ollama 未安装，请先安装"
    exit 1
}

# 2. 检查模型
Write-Host ""
Write-Host "[2/6] 检查模型..."
$models = ollama list 2>&1 | Out-String
if ($models -match "qwen2.5:7b") {
    Write-Host "   OK qwen2.5:7b 已下载"
} else {
    Write-Host "   正在下载 qwen2.5:7b..."
    ollama pull qwen2.5:7b
    Write-Host "   OK 模型下载完成"
}

# 3. 测试 API
Write-Host ""
Write-Host "[3/6] 测试 API..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5
    Write-Host "   OK API 连接成功"
} catch {
    Write-Host "   ERROR API 连接失败"
    exit 1
}

# 4. 测试推理
Write-Host ""
Write-Host "[4/6] 测试推理..."
$json = '{"model":"qwen2.5:7b","prompt":"Hello","stream":false}'
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/generate" -Method Post -Body $json -ContentType "application/json" -UseBasicParsing -TimeoutSec 30
    Write-Host "   OK 推理成功"
} catch {
    Write-Host "   ERROR 推理失败"
}

# 5. 测试 AIOS
Write-Host ""
Write-Host "[5/6] 测试 AIOS..."
$aioscorePath = "C:\Users\A\.openclaw\workspace\aios\core"
if (Test-Path $aioscorePath) {
    cd $aioscorePath
    $env:PYTHONIOENCODING = 'utf-8'
    & "C:\Program Files\Python312\python.exe" ollama_client.py
} else {
    Write-Host "   SKIP AIOS 目录不存在"
}

# 完成
Write-Host ""
Write-Host "========================================"
Write-Host "安装和测试完成"
Write-Host "========================================"
Write-Host ""
Write-Host "快速开始:"
Write-Host "  ollama run qwen2.5:7b"
Write-Host ""

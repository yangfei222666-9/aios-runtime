# Perplexity 集成到 AIOS - 使用指南

## ✅ 已完成

1. **Perplexity Search Skill** - 3个脚本（search/ask/research）
2. **Perplexity_Researcher Agent** - Agent 配置文件
3. **AIOS Dispatcher 集成** - 添加了路由规则

## 🚀 如何使用

### 方式 1：通过任务队列（推荐）

**添加搜索任务：**
```python
# 添加到 task_queue.jsonl
{
    "id": "search_001",
    "type": "search",
    "message": "搜索 Perplexity AI 最新融资消息",
    "priority": "normal",
    "enqueued_at": "2026-02-27T14:30:00Z"
}
```

**添加深度研究任务：**
```python
{
    "id": "research_001",
    "type": "deep_research",
    "message": "研究 AIOS 自我改进系统的最佳实践",
    "priority": "high",
    "enqueued_at": "2026-02-27T14:30:00Z"
}
```

**AIOS 会自动：**
1. 检测任务类型（search/deep_research）
2. 路由到 Perplexity Agent
3. 执行搜索/研究
4. 返回结果（带引用来源）

### 方式 2：直接调用 Skill

**基础搜索：**
```bash
cd C:\Users\A\.openclaw\workspace\skills\perplexity-search
node scripts/search.mjs "Perplexity AI 最新消息"
```

**对话式搜索：**
```bash
node scripts/ask.mjs "它和 ChatGPT 有什么区别？" --context "Perplexity 是一个 AI 搜索引擎"
```

**深度研究：**
```bash
node scripts/research.mjs "AIOS 架构设计" --depth 3 --output report.md
```

### 方式 3：通过 OpenClaw 语音命令

**简单搜索：**
```
你: "搜索 Perplexity AI 最新消息"
AIOS: [自动路由到 perplexity-search skill]
```

**深度研究：**
```
你: "研究 AIOS 自我改进系统"
AIOS: [自动路由到 perplexity_researcher agent]
```

## 📋 任务类型映射

| 任务类型 | 路由到 | 用途 |
|---------|--------|------|
| `search` | perplexity-search (Skill) | 快速搜索，返回答案+引用 |
| `deep_research` | perplexity_researcher (Agent) | 深度研究，多轮搜索+报告 |

## 🔧 配置

### API Key 设置

**临时设置（当前会话）：**
```powershell
$env:PERPLEXITY_API_KEY = "pplx-xxxxx"
```

**永久设置（所有会话）：**
```powershell
[System.Environment]::SetEnvironmentVariable("PERPLEXITY_API_KEY", "pplx-xxxxx", "User")
```

### 模型选择

在 `auto_dispatcher_v2.py` 中已配置：
```python
"search": {"model": "perplexity-sonar-pro", "label": "perplexity_search"},
"deep_research": {"model": "perplexity-sonar-pro", "label": "perplexity_researcher"},
```

**可选模型：**
- `sonar` - 快速，适合简单查询
- `sonar-pro` - 最佳质量（默认）
- `sonar-reasoning` - 深度推理

## 📊 监控和日志

**查看任务状态：**
```bash
# 查看任务队列
cat C:\Users\A\.openclaw\workspace\aios\agent_system\task_queue.jsonl

# 查看 Dispatcher 日志
cat C:\Users\A\.openclaw\workspace\aios\agent_system\dispatcher.log
```

**Dashboard 可视化：**
```bash
python aios.py dashboard
# 访问 http://127.0.0.1:8888
```

## 🧪 测试

### 测试 1：基础搜索

**添加任务：**
```bash
cd C:\Users\A\.openclaw\workspace\aios\agent_system
echo '{"id":"test_search_001","type":"search","message":"Perplexity AI 最新融资","priority":"normal","enqueued_at":"2026-02-27T14:30:00Z"}' >> task_queue.jsonl
```

**运行 Dispatcher：**
```bash
python auto_dispatcher_v2.py
```

**预期结果：**
- 任务被路由到 perplexity-search
- 返回答案 + 引用来源
- 记录到 dispatcher.log

### 测试 2：深度研究

**添加任务：**
```bash
echo '{"id":"test_research_001","type":"deep_research","message":"研究 AIOS 架构设计","priority":"high","enqueued_at":"2026-02-27T14:30:00Z"}' >> task_queue.jsonl
```

**运行 Dispatcher：**
```bash
python auto_dispatcher_v2.py
```

**预期结果：**
- 任务被路由到 perplexity_researcher
- 多轮搜索（3 rounds）
- 生成完整报告

## ⚠️ 注意事项

### 1. API Key 必需

**没有 API Key 会报错：**
```
Error: PERPLEXITY_API_KEY environment variable not set
```

**解决：** 设置环境变量（见上方"配置"部分）

### 2. Rate Limits

**免费版限制：**
- 每个会话最多 5 次查询
- 超过后需要等待或升级

**Pro 版：**
- 无限查询
- $17/月

### 3. 成本控制

**预估成本：**
- 基础搜索：~$0.01/次
- 深度研究（3 rounds）：~$0.05/次

**建议：**
- 日常使用：免费版够用
- 频繁使用：升级 Pro

## 🎯 下一步

### 立即可用（无需 API Key）

1. ✅ 任务路由已配置
2. ✅ Agent 配置已创建
3. ✅ Skill 脚本已就绪

### 需要 API Key 才能测试

1. ❌ 获取 Perplexity API Key
2. ❌ 设置环境变量
3. ❌ 运行测试脚本

### 可选优化

1. [ ] 添加缓存（避免重复搜索）
2. [ ] 成本追踪（记录每次搜索的成本）
3. [ ] A/B 测试（对比 Perplexity vs Tavily）
4. [ ] 自动降级（API 失败时切换到 Tavily）

## 📚 相关文档

- **Skill 文档：** `skills/perplexity-search/SKILL.md`
- **集成指南：** `skills/perplexity-search/INTEGRATION.md`
- **快速开始：** `skills/perplexity-search/README.md`
- **完成报告：** `skills/perplexity-search/COMPLETION_REPORT.md`

---

**状态：** ✅ 集成完成，等待 API Key 测试

**作者：** 小九  
**日期：** 2026-02-27

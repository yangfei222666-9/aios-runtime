# AIOS 功能映射文档

**版本：** v3.4  
**生成时间：** 2026-03-06  
**维护者：** 小九 + 珊瑚海

---

## 总览

```
AIOS v3.4 - 自我进化 AI 操作系统
│
├── 核心引擎层（Core Engine）
│   ├── EventBus          事件总线
│   ├── Scheduler         任务调度
│   ├── Task Queue        任务队列
│   ├── Heartbeat v5.0    心跳机制
│   └── Task Router       智能路由
│
├── 决策智慧层（Decision Layer）
│   ├── 64卦决策系统       状态机
│   ├── Evolution Score   置信度融合
│   ├── Adversarial Validation  Bull vs Bear 辩论
│   └── Model Router      快慢思考分离
│
├── Agent 执行层（Agent Layer）
│   ├── Coder Agent       代码生成
│   ├── Analyst Agent     数据分析
│   ├── Monitor Agent     系统监控
│   ├── Researcher Agent  信息研究
│   └── Meta Agent        Agent 自创建
│
├── 自我进化层（Self-Evolving Layer）
│   ├── LowSuccess_Agent  失败重生
│   ├── Self-Improving Loop  自我改进
│   ├── LanceDB 经验库    向量记忆
│   └── Phase 3 Observer  观察统计
│
├── 可观测层（Observability Layer）
│   ├── Dashboard v3.4    实时仪表盘
│   ├── Telegram 推送     通知系统
│   ├── SLO 监控          服务质量
│   └── Pattern Analysis  模式分析
│
└── 生态扩展层（Ecosystem Layer）
    ├── Agent Market      Agent 市场
    ├── Spawn Lock        并发控制
    ├── Web Monitor       网站监控
    └── Site Monitor      站点监控
```

---

## 核心引擎层

### EventBus（事件总线）
| 属性 | 说明 |
|------|------|
| 文件 | `core/event_bus.py` |
| 作用 | 系统神经中枢，所有组件通过事件通信 |
| 延迟 | <10ms |
| 持久化 | `events.jsonl` |

**支持事件类型：**
- `task.submitted` / `task.started` / `task.completed` / `task.failed`
- `agent.degraded` / `system.health_updated`
- `evolution.score_updated` / `hexagram.changed`

---

### Scheduler（任务调度）
| 属性 | 说明 |
|------|------|
| 文件 | `core/scheduler.py`（含 v2/v3/v5 多版本） |
| 作用 | 智能任务调度，优先级 + 依赖 + 资源感知 |
| 并发 | 最多 5 个并行任务 |
| 超时 | 默认 300s，可配置 |

**调度策略：**
```
P0（紧急）→ P1（高）→ P2（普通）→ P3（低）
依赖检查 → 资源评估 → 并发控制 → 超时处理
```

---

### Task Queue（任务队列）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/task_queue.py` |
| 持久化 | `task_queue.jsonl` |
| 重试 | 失败自动重试 3 次（指数退避） |

**任务生命周期：**
```
pending → running → completed
                 ↘ failed → retry（最多3次）→ dead_letter
```

**CLI 操作：**
```bash
python aios.py submit --desc "任务描述" --type code --priority high
python aios.py list --status pending
python aios.py status <task_id>
```

---

### Heartbeat v5.0（心跳机制）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/heartbeat_v5.py` |
| 触发 | 每 30 秒（OpenClaw 主会话） |
| 每次处理 | 最多 5 个任务 |

**执行流程：**
1. 检查任务队列 → 执行待处理任务
2. 每小时整点 → 触发 LowSuccess Regeneration
3. 健康度评估 → 输出 HEARTBEAT_OK / 告警

---

### Task Router（智能路由）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/task_router.py` |
| 关键词 | 80+ 中英文关键词 |
| 路由目标 | 12 个 Agent |
| 匹配策略 | 精确 → 关键词 → 模糊（三层） |

**路由映射：**
| 任务类型 | 目标 Agent |
|----------|-----------|
| code / 代码 / 重构 | coder-dispatcher |
| analyze / 分析 / 统计 | analyst-dispatcher |
| monitor / 监控 / 检查 | monitor-dispatcher |
| research / 搜索 / 学习 | researcher-dispatcher |
| plan / 规划 / 设计 | planner-dispatcher |

---

## 决策智慧层

### 64卦决策系统
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/bigua_strategy.py` |
| 状态数 | 64 种（覆盖所有场景） |
| 历史 | `bigua_history.jsonl` |

**核心卦象：**
| 卦象 | 场景 | 策略 |
|------|------|------|
| 乾卦 | 系统高峰期 | 全力执行，主动出击 |
| 坤卦 | 稳定运行期 | 厚积薄发，静待花开 |
| 大过卦 | 高风险任务 | 谨慎验证，双重检查 |
| 既济卦 | 任务完成 | 总结经验，准备下一步 |
| 未济卦 | 任务未完成 | 分析原因，调整策略 |

---

### Evolution Score（置信度融合）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/evolution_fusion.py` |
| 当前分数 | **99.5 / 100** |
| 更新频率 | 每次事件触发后 |

**计算公式：**
```
fused = base_confidence * 0.65
      + evolution_score * 0.35
      + 稳定期加成（连续7天 >90%）
      + 双高加成（base>90% AND evo>90%）
      + LowSuccess修复加成（+2.0%）
```

**评分等级：**
- 90-100：优秀（绿色）
- 80-90：良好（黄色）
- 70-80：一般（橙色）
- <70：需改进（红色，自动告警）

---

### Adversarial Validation（对抗验证）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/adversarial_validator.py` |
| 触发条件 | 高风险任务（risk_score > 0.7） |
| 效果 | 决策失败率降低 30%+ |

**辩论流程：**
```
高风险任务
    ↓
Bull 辩手（支持论据）
    ↓
Bear 辩手（风险识别）
    ↓
64卦调解（当前卦象智慧）
    ↓
融合方案 + 最终置信度
    ↓
Evolution Score +0.4
```

---

### Model Router（快慢思考分离）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/llm_router.py` |
| 快模型 | claude-haiku（简单任务，<5s） |
| 慢模型 | claude-sonnet / opus（复杂任务） |

**路由规则：**
- 简单查询 → Fast 模型
- 代码生成 → Standard 模型
- 高风险 + 辩论触发 → Slow 模型

---

## Agent 执行层

### 核心 Agent 列表
| Agent | 类型 | 文件 | 职责 |
|-------|------|------|------|
| coder-dispatcher | coder | `agents/coder/` | 代码生成、重构、调试 |
| analyst-dispatcher | analysis | `agents/analyst/` | 数据分析、报告生成 |
| monitor-dispatcher | monitor | `agents/monitor/` | 系统监控、告警 |
| researcher-dispatcher | research | `agents/researcher/` | 信息搜索、学习 |
| Health_Monitor | monitor | `agents/` | 健康度检查 |
| LowSuccess_Agent | recovery | `agent_system/low_success_agent_v3.py` | 失败重生 |

### Agent 统计（截至 2026-03-04）
| Agent | 成功率 | 任务数 |
|-------|--------|--------|
| monitor-dispatcher | 100% | 49 |
| analyst-dispatcher | 92.9% | 28 |
| coder-dispatcher | 75% | 12 |

### Meta Agent（Agent 自创建）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/meta_agent.py` |
| 作用 | 检测能力缺口，自动设计并创建新 Agent |

**流程：**
```
缺口检测（11个缺口，3个高优先级）
    ↓
设计 Agent（从模板或自定义）
    ↓
沙盒测试（配置完整性验证）
    ↓
提交审批 → 批准创建
    ↓
写入 agents.jsonl + agent_configs.json
```

---

## 自我进化层

### LowSuccess_Agent v3.0（失败重生）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/low_success_regeneration.py` |
| 触发 | 每小时整点（Heartbeat 自动） |
| 每次处理 | 最多 5 个失败任务 |
| 重生成功率 | 75%+ |

**完整闭环：**
```
失败任务（lessons.json）
    ↓
LanceDB 推荐历史成功策略
    ↓
生成 feedback + strategy
    ↓
创建 spawn 请求
    ↓
Heartbeat 执行真实 Agent
    ↓
Phase 3 观察记录
    ↓
成功 → 保存到 LanceDB
    ↓
下次同类错误自动应用历史经验
```

---

### Self-Improving Loop v2.0
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/self_improving_loop_v2.py` |
| 测试覆盖 | 17 个测试用例全部通过 |
| 性能开销 | <1% |

**7步闭环：**
1. 观察（Observe）— 收集运行数据
2. 分析（Analyze）— 识别改进机会
3. 设计（Design）— 生成改进方案
4. 验证（Validate）— Quality Gates 三层门禁
5. 执行（Execute）— 应用改进
6. 监控（Monitor）— 观察效果
7. 回滚（Rollback）— 如果无效自动恢复

---

### LanceDB 经验库
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/experience_learner_v3.py` |
| 向量维度 | 384维（sentence-transformers） |
| 缓存 | TTLCache（1小时过期） |
| 坤卦加成 | 成功率>80% 时 confidence=0.98 |

---

### Phase 3 Observer（观察统计）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/phase3_observer.py` |
| 触发 | 每次重生自动记录 |
| 报告 | `reports/lowsuccess_phase3_report.md` |
| 图表 | Mermaid 饼图 + 流程图 |

---

## 可观测层

### Dashboard v3.4
| 属性 | 说明 |
|------|------|
| 文件 | `dashboard/AIOS-Dashboard-v3.4/server.py` |
| 端口 | 8888 |
| 访问 | http://127.0.0.1:8888 |
| 启动 | `python server.py` |

**展示内容：**
- Evolution Score 实时曲线
- Agent 状态矩阵
- 任务队列状态
- SLO 体检（4个指标）
- 64卦当前状态

---

### Telegram 推送
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/telegram_notifier.py` |
| 每日简报 | 自动推送（run_pattern_analysis.py） |
| 每周 SLO | 每周一自动推送（含趋势图） |
| 告警 | Evolution Score < 70 立即推送 |

---

### SLO 监控
| 指标 | 目标 | 当前 |
|------|------|------|
| 任务成功率（TSR） | ≥85% | 80.4% |
| 自动修复率（CR） | ≥90% | 92% |
| 系统可用性 | ≥99% | 99%+ |
| 平均响应时间 | <60s | ~38s |

---

### Pattern Analysis（模式分析）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/run_pattern_analysis.py` |
| 触发 | 每日自动 + 每周一 |
| 输出 | 每日简报 + 周报 + LanceDB 监控 |

---

## 生态扩展层

### Agent Market（Agent 市场）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/agent_market.py` |
| 已发布 | 4 个 Agent |
| 已安装 | 37 个 Agent |

**CLI 操作：**
```bash
python agent_market.py list              # 浏览市场
python agent_market.py search "code"     # 搜索
python agent_market.py export coder      # 导出
python agent_market.py publish ./pkg     # 发布
python agent_market.py install coder     # 安装
```

---

### Spawn Lock（并发控制）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/spawn_lock.py` |
| 作用 | 防止重复 spawn，保证幂等性 |
| 指标 | `spawn_lock_metrics.json` |
| 复盘 | 2026-03-08 11:05 执行 48h 复盘 |

**健康阈值：**
- lock_acquire_latency_ms_avg < 10ms
- idempotent_hit_rate 5-20%
- stale_lock_recovered_total < 5

---

### Web Monitor（网站监控）
| 属性 | 说明 |
|------|------|
| 文件 | `agent_system/web_monitor.py` |
| 配置 | `web_monitor_config.yaml` |
| 告警 | 站点异常自动 Telegram 推送 |

---

## 数据文件索引

| 文件 | 内容 |
|------|------|
| `task_queue.jsonl` | 任务队列（pending/running/completed/failed） |
| `task_executions.jsonl` | 任务执行历史（真实数据源） |
| `lessons.json` | 失败教训库 |
| `experience_library.jsonl` | 成功轨迹库 |
| `spawn_requests.jsonl` | Spawn 请求队列 |
| `spawn_results.jsonl` | Spawn 执行结果 |
| `agents.json` | Agent 注册表 + 统计 |
| `evolution_score.json` | Evolution Score 历史 |
| `bigua_history.jsonl` | 64卦状态历史 |
| `decision_audit.jsonl` | 决策审计链 |
| `heartbeat_stats.json` | 心跳统计 |
| `token_usage.jsonl` | Token 使用记录 |

---

## 快速启动

```bash
# 启动 Dashboard
cd aios/dashboard/AIOS-Dashboard-v3.4
python server.py
# → http://127.0.0.1:8888

# 提交任务
cd aios/agent_system
python aios.py submit --desc "你的任务" --type code --priority high

# 手动触发心跳
$env:PYTHONUTF8=1; python -X utf8 heartbeat_v5.py

# 查看 Agent 状态
python check_agent_status.py

# 运行每日分析
python run_pattern_analysis.py
```

---

## 版本历史

| 版本 | 日期 | 核心变化 |
|------|------|---------|
| v1.0 | 2026-02-24 | 基础框架，真实 Agent 执行验证 |
| v2.0 | 2026-02-25 | Meta Agent，Self-Improving Loop |
| v3.0 | 2026-02-27 | Task Router，Heartbeat v5.0，Kernel 模块 |
| v3.4 | 2026-03-04 | LowSuccess v3.0，Agent 市场，Evolution Score 99.5 |
| v3.4+ | 2026-03-05 | Adversarial Validation，Phase 3 Observer |

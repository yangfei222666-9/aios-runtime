# skill.yaml 完整规范 v1.0

## 必需字段

```yaml
name: doc_agent                           # Skill 名称（必需，小写+下划线）
version: 0.1.0                            # 语义化版本（必需）
description: "Read/Write docs..."         # 描述（必需）
entrypoint: "skills.doc_agent.run:main"   # 入口函数（必需）
```

## 输入/输出 Schema

```yaml
inputs_schema:
  type: object
  properties:
    task:
      type: string
      description: "任务描述"
    format:
      type: string
      enum: ["md", "docx", "pdf"]
  required: ["task"]

outputs_schema:
  type: object
  properties:
    ok: {type: boolean}
    artifact_path: {type: string}
    summary: {type: string}
  required: ["ok"]
```

## 权限/能力声明

```yaml
capabilities:
  - file_read                             # 可读文件
  - file_write                            # 可写文件
  - network_off                           # 禁止网络（默认）
  - execute_shell                         # 可执行 Shell
  - send_notification                     # 可发送通知
  - create_incident                       # 可创建事件

risk_level: low                           # 风险等级（low/medium/high）
auto_approve: true                        # 自动批准（false 需人工确认）
```

## 触发器（可选）

```yaml
triggers:
  - type: on_demand                       # 手动触发（默认）
  - type: schedule                        # 定时触发
    cron: "0 9 * * *"                     # Cron 表达式
    timezone: "Asia/Shanghai"
  - type: webhook                         # Webhook 触发
    path: /health-alert
  - type: event                           # 事件触发
    event_type: system.high_cpu
```

## 运行时配置

```yaml
runtime:
  timeout_sec: 120                        # 超时时间（秒）
  max_concurrency: 2                      # 最大并发数
  retry:
    max_retries: 2                        # 最大重试次数
    backoff_sec: 2                        # 重试间隔（秒）
```

## 路由/标签

```yaml
routing:
  tags: ["docs", "report"]                # 标签（用于发现）
  priority: 0.6                           # 优先级（0-1）
```

## 依赖

```yaml
dependencies:
  - psutil>=5.9.0
  - requests>=2.28.0
```

## 环境变量

```yaml
env:
  ALERT_WEBHOOK: ${ALERT_WEBHOOK}
  SLACK_TOKEN: ${SLACK_TOKEN}
```

## 元数据（可选）

```yaml
icon: "🖥️"                                # 图标
author: "九"                              # 作者
license: MIT                              # 许可证
homepage: https://github.com/...          # 主页
```

## Agent Prompt（可选）

```yaml
default_prompt: |
  你是服务器健康管家，当发现问题时必须先尝试自动修复，再通知我。
  
  工作流程：
  1. 检测异常
  2. 尝试自动修复
  3. 验证修复效果
  4. 通知用户结果
```

## 完整示例

```yaml
name: server_health_agent
version: 1.0.0
description: "实时监控服务器 CPU/内存/磁盘，并能在异常时自动重启服务"
icon: "🖥️"
author: "九"
entrypoint: "skills.server_health.main:run"

inputs_schema:
  type: object
  properties:
    target:
      type: string
      description: "服务器地址"
    metrics:
      type: array
      items: {type: string}
      description: "要监控的指标"
  required: ["target"]

outputs_schema:
  type: object
  properties:
    status: {type: string}
    metrics: {type: object}
    alerts: {type: array}
    actions_taken: {type: array}
  required: ["status"]

capabilities:
  - execute_shell
  - send_notification
  - create_incident

risk_level: medium
auto_approve: false

triggers:
  - type: schedule
    cron: "*/5 * * * *"
    timezone: "Asia/Shanghai"
  - type: webhook
    path: /health-alert

runtime:
  timeout_sec: 60
  max_concurrency: 1
  retry:
    max_retries: 3
    backoff_sec: 5

routing:
  tags: ["monitoring", "health", "server"]
  priority: 0.8

dependencies:
  - psutil>=5.9.0

env:
  ALERT_WEBHOOK: ${ALERT_WEBHOOK}

default_prompt: |
  你是服务器健康管家，当发现问题时必须先尝试自动修复，再通知我。
```

## 字段说明

### name
- 格式：小写字母 + 下划线
- 唯一标识符
- 示例：`doc_agent`, `server_health_agent`

### version
- 语义化版本：`major.minor.patch`
- 示例：`1.0.0`, `0.1.0`

### entrypoint
- 格式：`module.path:function_name`
- 必须是可导入的 Python 函数
- 示例：`skills.doc_agent.run:main`

### capabilities
- `file_read` - 读取文件
- `file_write` - 写入文件
- `network_on` - 允许网络访问
- `network_off` - 禁止网络访问（默认）
- `execute_shell` - 执行 Shell 命令
- `send_notification` - 发送通知
- `create_incident` - 创建事件
- `read_logs` - 读取日志
- `modify_config` - 修改配置

### risk_level
- `low` - 低风险（只读操作）
- `medium` - 中风险（写操作、网络访问）
- `high` - 高风险（Shell 执行、系统修改）

### auto_approve
- `true` - 自动批准执行
- `false` - 需要人工确认（高风险操作）

## 验证规则

1. **必需字段：** name, version, description, entrypoint
2. **版本格式：** 必须符合语义化版本
3. **entrypoint：** 必须可导入
4. **Schema：** 必须符合 JSON Schema 规范
5. **capabilities：** 必须在允许列表中
6. **risk_level：** 必须是 low/medium/high
7. **cron：** 必须是有效的 Cron 表达式

---

**版本：** 1.0  
**最后更新：** 2026-02-26  
**维护者：** 小九 + 珊瑚海

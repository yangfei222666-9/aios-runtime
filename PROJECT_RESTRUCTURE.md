# AIOS 项目重构计划 - 标准开源结构

## 当前问题

1. **根目录混乱** - 100+ 文件堆在根目录
2. **模块不清晰** - aios/core/agent_system 职责重叠
3. **文档分散** - 多个 README/ARCHITECTURE/ROADMAP
4. **测试缺失** - tests/ 目录存在但不完整
5. **配置混乱** - config.yaml/env_config.json/workflows.json 分散

## 目标结构（标准 Python 开源项目）

```
aios/
├── .github/                    # GitHub 配置
│   ├── workflows/              # CI/CD
│   │   ├── test.yml
│   │   ├── lint.yml
│   │   └── release.yml
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── docs/                       # 文档（统一）
│   ├── index.md                # 文档首页
│   ├── getting-started.md      # 快速开始
│   ├── architecture.md         # 架构设计
│   ├── api-reference.md        # API 文档
│   ├── deployment.md           # 部署指南
│   ├── contributing.md         # 贡献指南
│   └── changelog.md            # 变更日志
│
├── src/aios/                   # 源代码（标准 src/ 布局）
│   ├── __init__.py
│   ├── __main__.py             # CLI 入口
│   │
│   ├── core/                   # 核心模块
│   │   ├── __init__.py
│   │   ├── event_bus.py        # 事件总线
│   │   ├── scheduler.py        # 调度器
│   │   ├── executor.py         # 执行器
│   │   └── state_machine.py    # 状态机
│   │
│   ├── agents/                 # Agent 系统
│   │   ├── __init__.py
│   │   ├── base.py             # Agent 基类
│   │   ├── registry.py         # Agent 注册表
│   │   ├── dispatcher.py       # 任务分发
│   │   └── builtin/            # 内置 Agent
│   │       ├── coder.py
│   │       ├── analyst.py
│   │       └── monitor.py
│   │
│   ├── evolution/              # 进化系统
│   │   ├── __init__.py
│   │   ├── hexagram.py         # 64卦系统
│   │   ├── evolution_score.py  # Evolution Score
│   │   ├── fusion.py           # 置信度融合
│   │   └── adversarial.py      # 对抗性验证
│   │
│   ├── learning/               # 学习系统
│   │   ├── __init__.py
│   │   ├── experience.py       # 经验库
│   │   ├── pattern.py          # 模式识别
│   │   └── regeneration.py     # 失败重生
│   │
│   ├── observability/          # 可观测性
│   │   ├── __init__.py
│   │   ├── metrics.py          # 指标收集
│   │   ├── alerts.py           # 告警系统
│   │   └── audit.py            # 审计链
│   │
│   ├── dashboard/              # Web Dashboard
│   │   ├── __init__.py
│   │   ├── server.py           # FastAPI 服务器
│   │   ├── static/             # 静态资源
│   │   └── templates/          # HTML 模板
│   │
│   ├── cli/                    # 命令行工具
│   │   ├── __init__.py
│   │   ├── commands.py         # 命令定义
│   │   └── utils.py            # CLI 工具函数
│   │
│   └── utils/                  # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       ├── config.py
│       └── helpers.py
│
├── tests/                      # 测试（镜像 src/ 结构）
│   ├── __init__.py
│   ├── conftest.py             # pytest 配置
│   ├── unit/                   # 单元测试
│   │   ├── test_event_bus.py
│   │   ├── test_scheduler.py
│   │   └── test_hexagram.py
│   ├── integration/            # 集成测试
│   │   ├── test_agent_flow.py
│   │   └── test_evolution.py
│   └── e2e/                    # 端到端测试
│       └── test_full_cycle.py
│
├── examples/                   # 示例代码
│   ├── basic_usage.py
│   ├── custom_agent.py
│   └── advanced_workflow.py
│
├── scripts/                    # 脚本工具
│   ├── install.sh              # 安装脚本
│   ├── benchmark.py            # 性能测试
│   └── migrate.py              # 数据迁移
│
├── data/                       # 数据文件（运行时）
│   ├── events.jsonl
│   ├── tasks.jsonl
│   ├── agents.json
│   └── .gitkeep
│
├── config/                     # 配置文件
│   ├── default.yaml            # 默认配置
│   ├── production.yaml         # 生产配置
│   └── development.yaml        # 开发配置
│
├── .gitignore
├── .editorconfig
├── LICENSE                     # MIT License
├── README.md                   # 项目首页
├── CONTRIBUTING.md             # 贡献指南
├── CHANGELOG.md                # 变更日志
├── pyproject.toml              # 现代 Python 配置
├── setup.py                    # 向后兼容
└── requirements.txt            # 依赖列表
```

## 重构步骤

### Phase 1: 创建新结构（30分钟）
1. 创建 src/aios/ 目录结构
2. 移动核心模块到对应位置
3. 更新 import 路径

### Phase 2: 整理文档（20分钟）
1. 合并重复文档到 docs/
2. 统一 README.md
3. 清理根目录

### Phase 3: 测试迁移（20分钟）
1. 重组 tests/ 目录
2. 更新测试路径
3. 验证测试通过

### Phase 4: 配置整理（10分钟）
1. 合并配置文件到 config/
2. 更新 setup.py/pyproject.toml
3. 清理临时文件

### Phase 5: 验证（10分钟）
1. 运行完整测试套件
2. 验证 CLI 工具
3. 验证 Dashboard
4. 生成迁移报告

## 核心原则

1. **向后兼容** - 保留旧入口（aios.py → src/aios/__main__.py）
2. **渐进迁移** - 先创建新结构，再逐步迁移
3. **保持运行** - 迁移过程中系统仍可用
4. **完整测试** - 每步验证，确保不破坏功能

## 预期效果

- ✅ 根目录清爽（<20个文件）
- ✅ 模块职责清晰
- ✅ 文档统一规范
- ✅ 符合 Python 开源最佳实践
- ✅ 易于贡献和维护

## 时间估算

**总计：90分钟**
- Phase 1: 30分钟
- Phase 2: 20分钟
- Phase 3: 20分钟
- Phase 4: 10分钟
- Phase 5: 10分钟

## 开始执行？

确认后我立刻开始重构。

# AIOS 改进计划（基于 GitHub 学习）

## 📅 时间线

### 第1周（2026-02-26 ~ 2026-03-04）

**目标：** 实现队列系统和调度算法

#### 任务1：LLM Queue（LLM 请求队列）
- [x] 设计 LLM Queue 接口
- [x] 实现 FIFO 调度算法
- [x] 支持优先级队列
- [x] 编写单元测试
- **负责 Agent：** Architecture_Implementer
- **完成时间：** 2026-02-26

#### 任务2：Memory Queue（内存请求队列）
- [x] 设计 Memory Queue 接口
- [x] 实现 SJF（Shortest Job First）调度
- [x] 实现 RR（Round Robin）调度
- [x] 实现 EDF（Earliest Deadline First）调度
- [x] 编写单元测试
- **负责 Agent：** Architecture_Implementer
- **完成时间：** 2026-02-26

#### 任务3：Storage Queue（存储请求队列）
- [x] 设计 Storage Queue 接口
- [x] 实现 SJF/RR 调度
- [x] 支持批量操作
- [x] 编写单元测试
- **负责 Agent：** Architecture_Implementer
- **完成时间：** 2026-02-26

#### 任务4：Thread Binding（线程绑定）
- [x] 设计线程绑定机制
- [x] 实现线程池管理
- [x] 支持 CPU 亲和性设置
- [x] 编写性能测试
- **负责 Agent：** Performance_Optimizer
- **完成时间：** 2026-02-26

---

### 第2-3周（2026-03-05 ~ 2026-03-18）

**目标：** SDK 模块化和 API 接口

#### 任务5：分离 Kernel 和 SDK
- [x] 设计 Kernel 和 SDK 的接口边界
- [x] 重构现有代码（分离关注点）
- [x] 实现 Exposed Ports（统一 API）
- [x] 编写迁移指南
- **负责 Agent：** Refactor_Planner + Architecture_Implementer
- **完成时间：** 2026-02-26

#### 任务6：SDK 四大模块
- [x] Planning Module（规划模块）
  - LLMQuery 接口
  - ToolQuery 接口
- [x] Action Module（行动模块）
  - ToolQuery 接口
  - 执行器
- [x] Memory Module（记忆模块）
  - MemoryQuery 接口
  - 上下文管理
- [x] Storage Module（存储模块）
  - StorageQuery 接口
  - 持久化管理
- **负责 Agent：** Architecture_Implementer
- **完成时间：** 2026-02-26

#### 任务7：System Call 层
- [x] 设计 AIOS System Call 接口
- [x] 实现系统调用路由
- [x] 支持权限控制
- [x] 编写 API 文档
- **负责 Agent：** Documentation_Writer
- **完成时间：** 2026-02-26

---

### 第4-6周（2026-03-19 ~ 2026-04-08）

**目标：** Context Manager、Memory Manager、Storage Manager

#### 任务8：Context Manager（上下文管理）
- [x] 设计上下文数据结构（AgentContext dataclass）
- [x] 实现上下文切换机制（save/restore/switch）
- [x] 支持上下文持久化（snapshot/load to disk）
- [x] 资源限制追踪和强制执行
- [x] 编写单元测试（8/8 通过）
- **负责 Agent：** Architecture_Implementer
- **完成时间：** 2026-02-27

#### 任务9：Memory Manager（内存管理）
- [x] 设计内存分配策略（per-agent quota + global limit）
- [x] 实现内存回收机制（release/release_all/unregister）
- [x] 支持内存限制和监控（quota enforcement + utilization）
- [x] LRU 驱逐策略（evict_lru with target）
- [x] 编写单元测试（8/8 通过）
- **负责 Agent：** Performance_Optimizer
- **完成时间：** 2026-02-27

#### 任务10：Storage Manager（存储管理）
- [x] 选择存储后端：**aiosqlite**（零依赖、异步、原生 SQL）✅ 已安装
- [x] 设计存储抽象层
- [x] 创建 SQL Schema（schema.sql）
- [x] 实现 Agent 状态持久化
- [x] 实现上下文持久化
- [x] 实现事件存储（替代 events.jsonl）
- [x] 实现任务历史记录
- [x] 支持查询和索引
- [x] 编写单元测试
- **负责 Agent：** Architecture_Implementer
- **完成时间：** 2026-02-26

**技术选型：aiosqlite（原生 SQL）**
- **aiosqlite** - 异步 SQLite 接口
- 零依赖（SQLite 内置）
- 自动管理连接和游标
- 支持参数化查询（?）
- 原生 SQL，更灵活
- 测试覆盖：9/9 ✅

---

### 第7-8周（2026-04-09 ~ 2026-04-22）

**目标：** 性能优化和文档完善

#### 任务11：Benchmark 对比
- [x] 设计性能测试用例
- [x] 运行 Benchmark（Kernel + Storage）
- [x] 生成性能报告（benchmark_report.json）
- [x] 识别优化机会（memory.stats 需优化）
- **负责 Agent：** Benchmark_Runner
- **完成时间：** 2026-02-27

#### 任务12：文档完善
- [x] 统一文档到 README.md
- [x] 撰写快速开始指南
- [x] 编写 API 参考文档
- [x] 制作架构图和流程图
- **负责 Agent：** Documentation_Writer + Tutorial_Creator
- **完成时间：** 2026-02-27

---

### 未来（3-6个月）

**目标：** Computer-use Agent 和学术影响力

#### 任务13：VM Controller + CloudRouter 集成
- [ ] 设计虚拟机控制器（参考 LLM-X-Factors CloudRouter）
- [ ] 实现 Local→Cloud 工作流反转
- [ ] 支持云端 VM 启动（`cloudrouter start ./project`）
- [ ] 支持 GPU 沙箱（`cloudrouter start --gpu B200`）
- [ ] 内置 VNC 桌面、VS Code、Jupyter Lab
- [ ] Agent 可在 VM 上操作浏览器验证
- [ ] 支持并行执行（多个 Agent 同时在不同 VM 上工作）
- [ ] 集成 DataCollector（统一收集所有 VM 的数据）
- [ ] 集成 Evaluator（评估每个 VM 的执行结果）
- [ ] 集成 Quality Gates（确保每个 VM 的改进是安全的）
- [ ] 实现 MCP Server（可选）
- **负责 Agent：** Architecture_Implementer
- **预计耗时：** 1-2个月

**核心价值：**
- **工作流反转：** Agent 思考在本地，干活在云上（Local→Cloud）
- **完全隔离：** 每个 Agent 有自己的 VM，互不干扰
- **并行执行：** 可以同时跑十个 Agent 各干各的
- **可观测性：** VNC 桌面 + DataCollector 事件记录，完整追踪链路

**参考项目：**
- LLM-X-Factors CloudRouter（https://github.com/llm-x-factors/cloudrouter）
- 视频：https://www.bilibili.com/video/BV1xxx（从蓝工到考研 [Agent的] 自主克隆桌面视频）

#### 任务14：学术论文
- [ ] 整理核心创新点
- [ ] 撰写论文草稿
- [ ] 准备实验数据
- [ ] 投稿到顶会（COLM、NAACL、ICLR）
- **负责 Agent：** Paper_Writer
- **预计耗时：** 2-3个月

---

## 🎯 里程碑

- **Week 1-3:** 队列系统 + 调度算法 ✅
- **Week 4-6:** SDK 模块化 + System Call ✅
- **Week 7-9:** Context/Memory/Storage Manager ✅
- **Week 10-12:** 性能优化 + 文档完善 ✅
- **Month 4-6:** Computer-use Agent + 学术论文 ✅

---

## 🚀 我们的优势（保持）

1. ✅ **EventBus** - 事件驱动（他们没有）
2. ✅ **Reactor** - 自动修复（他们没有）
3. ✅ **Self-Improving Loop** - 自我进化（他们没有）
4. ✅ **零依赖** - 可打包可复制（他们依赖很多）
5. ✅ **DataCollector + Evaluator + Quality Gates** - 完整的数据采集、评估、质量门禁闭环（他们没有）

## 🎯 未来方向（CloudRouter 启发）

**工作流反转：Local→Cloud（而非 Cloud→Local）**
- **传统工具：** Agent 思考在云上，干活在本地（Cloud→Local）
- **AIOS + CloudRouter：** Agent 思考在本地，干活在云上（Local→Cloud）

**优势：**
- 干活在云上，你看得到它在想什么
- 可以同时跑十个 Agent 各干各的
- 完全隔离，互不干扰
- 配合 DataCollector/Evaluator/Quality Gates，形成完整闭环

**架构：**
```
AIOS（本地）
  ↓
DataCollector（记录所有任务）
  ↓
Scheduler（决策：哪个 Agent 做什么）
  ↓
CloudRouter（启动云端 VM）
  ↓
Agent 在 VM 上执行任务
  ↓
Evaluator（评估执行结果）
  ↓
Quality Gates（验证改进是否安全）
  ↓
自动回滚（如果失败）
```

---

## 📝 备注

- 每个任务由对应的 Agent 负责
- 每周回顾进度，调整计划
- 优先级：核心功能 > 性能优化 > 文档 > 学术
- 保持我们的优势（EventBus、Reactor、Self-Improving Loop）

---

*创建时间：2026-02-26*  
*最后更新：2026-02-26*

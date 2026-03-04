# AIOS v1.2 Release Notes

## 🎉 重大更新：Planning + Memory 双模块完成

**发布日期：** 2026-02-26  
**版本：** v1.2  
**代码名：** Intelligence Leap（智能飞跃）

---

## 🚀 核心新增

### 1. Planning 模块（智能任务规划）

**功能：**
- ✅ Chain of Thought (CoT) 任务拆解（4种规则）
- ✅ 自动依赖分析
- ✅ 执行策略选择（sequential/parallel/dag）
- ✅ 完整的状态管理

**示例：**
```python
from core.planner import Planner

planner = Planner(workspace)
plan = planner.plan("实现 Memory 模块")
# 自动拆解为：设计 → 实现 → 测试
```

**测试覆盖：** 12/12 ✅

---

### 2. Memory 模块（记忆管理系统）

**功能：**
- ✅ 向量检索（TF-IDF + 余弦相似度）
- ✅ 记忆分层（短期/长期/工作记忆）
- ✅ 自动整理（定期提炼精华）
- ✅ 重要性评分

**示例：**
```python
from core.memory import MemoryManager

manager = MemoryManager(workspace)
manager.store("实现了 Planning 模块", importance=0.9)
results = manager.retrieve("Planning 模块", k=5)
```

**测试覆盖：** 12/12 ✅

---

### 3. Scheduler v3.0（集成 Planning + Memory）

**功能：**
- ✅ 自动任务拆解
- ✅ 记忆检索和上下文注入
- ✅ 任务完成后自动存储到记忆

**示例：**
```python
from core.scheduler import Scheduler

scheduler = Scheduler(workspace=workspace)
plan_id = scheduler.schedule_with_planning(
    "对比 AIOS 和标准 Agent 架构",
    executor=my_executor,
    use_memory=True  # 自动检索相关记忆
)
```

---

## 📊 性能提升

| 维度 | v1.0 | v1.2 | 提升 |
|-----|------|------|-----|
| **Planning 能力** | 3/10 | 7/10 | +4 |
| **Memory 能力** | 4/10 | 7/10 | +3 |
| **总分** | 56/80 | 64/80 | +8 |

---

## 🎯 技术亮点

### Planning 模块
1. **规则驱动的 CoT** - 不依赖 LLM，快速、可控、可解释
2. **自动依赖分析** - 识别子任务之间的依赖关系
3. **灵活的执行策略** - sequential/parallel/dag 自动选择
4. **零侵入集成** - Scheduler 保持向后兼容

### Memory 模块
1. **零依赖** - 纯 Python 实现，不依赖 FAISS/sentence-transformers
2. **TF-IDF Embedding** - 简单高效，适合小规模数据
3. **三层记忆** - 短期/长期/工作记忆分离
4. **自动整理** - 定期提炼精华，更新 MEMORY.md

---

## 📦 安装和使用

### 快速开始

```bash
# 1. 下载并解压
unzip AIOS-v1.2-20260226.zip
cd aios

# 2. 运行 Demo
python aios.py demo

# 3. 查看状态
python aios.py status

# 4. 启动 Dashboard
python aios.py dashboard
# 访问 http://localhost:9091
```

### 系统要求

- Python 3.8+
- 零依赖（纯 Python 实现）
- 可选：GPU（用于本地模型训练）

---

## 📚 文档

- [README.md](README.md) - 快速开始
- [API.md](docs/API.md) - API 文档
- [ROADMAP.md](ROADMAP.md) - 发展路线
- [CHANGELOG.md](CHANGELOG.md) - 完整更新日志

---

## 🔄 从 v1.0 升级

### 兼容性

- ✅ 向后兼容（旧代码无需修改）
- ✅ 新功能可选（use_memory=False 禁用记忆）
- ✅ 配置文件兼容

### 升级步骤

```bash
# 1. 备份旧版本
cp -r aios aios-v1.0-backup

# 2. 解压新版本
unzip AIOS-v1.2-20260226.zip

# 3. 迁移配置（如果有）
cp aios-v1.0-backup/config.json aios/config.json

# 4. 测试
python aios.py demo
```

---

## 🐛 已知问题

1. **PDF 提取** - 某些 PDF 文件提取失败（已知问题，不影响核心功能）
2. **并发写入** - 高并发时可能出现 JSON 写入冲突（已添加重试机制）

---

## 🙏 致谢

感谢所有贡献者和测试者！

特别感谢：
- **珊瑚海** - 核心开发和架构设计
- **小九** - AI 助手和代码实现

---

## 📈 下一步计划

### v1.3（1周内）
- Tool Use 改进（工具注册表 + 动态选择）
- 多模态支持（图像理解 + 图像生成）

### v2.0（1个月内）
- 架构重构（借鉴 EvoMap 的模块化设计）
- 本地模型训练（GPT-2 级别）
- 插件系统

---

## 📄 License

MIT License

---

**完整更新日志：** [CHANGELOG.md](CHANGELOG.md)  
**问题反馈：** [GitHub Issues](https://github.com/yangfei222666-9/aios/issues)  
**讨论区：** [GitHub Discussions](https://github.com/yangfei222666-9/aios/discussions)

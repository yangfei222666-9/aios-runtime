# AIOS 文档结构

**主文档：** README.md（统一入口，包含所有核心内容）

---

## 📚 文档导航

### 🚀 快速开始
- **README.md** - 10 秒快速开始 + 核心功能 + 真实场景演示

### 📖 详细文档
- **ARCHITECTURE.md** - 系统架构设计
- **ROADMAP.md** - 产品路线图
- **CONTRIBUTING.md** - 贡献指南

### 📊 报告文档
- **IMPROVEMENT_REPORT.md** - 改进报告（SDK 导入修复 + Memory 优化 + Demo）
- **TASK_QUEUE_INTEGRATION.md** - 任务队列集成报告
- **OPTIMIZATION_REPORT.md** - 性能优化报告

### 🔧 技术文档
- **docs/API.md** - API 参考（详细）
- **docs/TUTORIAL.md** - 教程（详细）

### 📝 其他文档
- **CHANGELOG.md** - 变更日志
- **SECURITY.md** - 安全政策
- **LICENSE** - 许可证

---

## 🗂️ 文档分类

### 用户文档（给使用者）
1. **README.md** - 主入口（必读）
2. **docs/TUTORIAL.md** - 教程（可选）
3. **CONTRIBUTING.md** - 贡献指南（可选）

### 开发文档（给开发者）
1. **ARCHITECTURE.md** - 架构设计
2. **docs/API.md** - API 参考
3. **ROADMAP.md** - 路线图

### 报告文档（给维护者）
1. **IMPROVEMENT_REPORT.md** - 改进报告
2. **TASK_QUEUE_INTEGRATION.md** - 集成报告
3. **OPTIMIZATION_REPORT.md** - 优化报告

---

## 📋 文档清理建议

### 可以删除的文档（重复或过时）
- `README_OLD.md` - 旧版 README（已备份）
- `README_TEST.md` - 测试文件
- `AIOS_简单介绍.md` - 重复内容（已合并到 README.md）
- `AIOS_详细介绍.md` - 重复内容（已合并到 README.md）
- `QUICKSTART.md` - 重复内容（已合并到 README.md）
- `QUICKSTART_MACOS.md` - 重复内容（已合并到 README.md）

### 可以归档的文档（历史记录）
- `test_report_*.md` - 测试报告（移到 `archive/`）
- `COMPLETION_REPORT_*.md` - 完成报告（移到 `archive/`）
- `PHASE*_REPORT.md` - 阶段报告（移到 `archive/`）
- `*_INJECTION_*.md` - 注入报告（移到 `archive/`）

### 保留的核心文档
- `README.md` - 主文档 ✅
- `ARCHITECTURE.md` - 架构设计 ✅
- `ROADMAP.md` - 路线图 ✅
- `CONTRIBUTING.md` - 贡献指南 ✅
- `CHANGELOG.md` - 变更日志 ✅
- `SECURITY.md` - 安全政策 ✅
- `IMPROVEMENT_REPORT.md` - 改进报告 ✅
- `TASK_QUEUE_INTEGRATION.md` - 集成报告 ✅
- `OPTIMIZATION_REPORT.md` - 优化报告 ✅

---

## 🎯 文档维护原则

1. **单一入口** - README.md 是唯一的快速开始入口
2. **避免重复** - 相同内容不要出现在多个文档中
3. **清晰分类** - 用户文档 / 开发文档 / 报告文档分开
4. **定期清理** - 删除过时文档，归档历史记录
5. **保持更新** - 新功能及时更新到 README.md

---

**最后更新：** 2026-02-27  
**维护者：** 小九 + 珊瑚海

# VM Controller + CloudRouter 设计文档

## 目标

实现 **Local→Cloud 工作流反转**：
- Agent 思考在本地（AIOS）
- Agent 干活在云上（VM）
- 完全隔离，并行执行
- 可观测性（VNC + DataCollector）

## 核心概念（来自 CloudRouter）

### 1. 一条命令，一台机器
```bash
cloudrouter start ./project          # 启动云端 VM + 同步文件
cloudrouter start --gpu B200         # GPU 沙箱
```

### 2. 内置工具
- VNC 桌面（可视化）
- VS Code（代码编辑）
- Jupyter Lab（数据分析）
- 浏览器（验证结果）

### 3. 工作流反转
- **传统工具：** Agent 思考在云上，干活在本地（Cloud→Local）
- **CloudRouter：** Agent 思考在本地，干活在云上（Local→Cloud）

**优势：**
- 干活在云上，你看得到它在想什么
- 可以同时跑十个 Agent 各干各的
- 完全隔离，互不干扰

## AIOS + CloudRouter 架构

```
AIOS（本地）
  ↓
DataCollector（记录所有任务）
  ↓
Scheduler（决策：哪个 Agent 做什么）
  ↓
VM Controller（启动云端 VM）
  ↓
Agent 在 VM 上执行任务
  ↓
Evaluator（评估执行结果）
  ↓
Quality Gates（验证改进是否安全）
  ↓
自动回滚（如果失败）
```

## Phase 1：本地 Docker 模拟（Week 1-2）

**目标：** 先用 Docker 模拟 VM，验证核心概念

### 1.1 VM Controller 基础
- `vm_controller.py` - 核心控制器
- `create_vm(agent_id, config)` - 创建 VM
- `start_vm(vm_id)` - 启动 VM
- `stop_vm(vm_id)` - 停止 VM
- `delete_vm(vm_id)` - 删除 VM
- `list_vms()` - 列出所有 VM
- `get_vm_status(vm_id)` - 查询 VM 状态

### 1.2 Docker 集成
- 使用 Docker Python SDK
- 每个 Agent 一个容器
- 容器内预装：Python + Git + VS Code Server
- 挂载工作目录（双向同步）

### 1.3 执行器
- `execute_in_vm(vm_id, command)` - 在 VM 中执行命令
- `sync_files(vm_id, local_path, remote_path)` - 文件同步
- `get_logs(vm_id)` - 获取执行日志

### 1.4 测试
- 创建 VM → 执行简单任务 → 获取结果 → 删除 VM
- 并行测试：同时启动 3 个 VM，各自执行不同任务

## Phase 2：VNC 桌面（Week 3）

**目标：** 可视化 VM 内部操作

### 2.1 VNC Server
- 容器内启动 VNC Server（TigerVNC 或 x11vnc）
- 暴露 VNC 端口（5900+）
- 支持 noVNC（Web 访问）

### 2.2 桌面环境
- 轻量级桌面（XFCE 或 LXDE）
- 预装浏览器（Firefox）
- 预装终端（xterm）

### 2.3 Dashboard 集成
- AIOS Dashboard 嵌入 noVNC iframe
- 实时查看 Agent 在 VM 中的操作
- 支持多 VM 切换

## Phase 3：CloudRouter 集成（Week 4-6）

**目标：** 从 Docker 迁移到真实云端 VM

### 3.1 云服务商选择
- **AWS EC2** - 成熟稳定，但贵
- **Google Cloud Compute Engine** - 性能好，但复杂
- **DigitalOcean Droplets** - 简单便宜，推荐
- **Vultr** - 便宜，支持按小时计费
- **自建 KVM** - 完全控制，但需要运维

**推荐：DigitalOcean Droplets**
- 按小时计费（$0.007/小时起）
- API 简单（Python SDK）
- 支持快照（快速启动）
- 支持 VNC（Console Access）

### 3.2 VM 镜像
- 基础镜像：Ubuntu 22.04 LTS
- 预装软件：
  - Python 3.12
  - Git
  - Docker
  - VS Code Server
  - VNC Server
  - 浏览器（Firefox）
- 快照保存（避免每次重装）

### 3.3 网络配置
- 每个 VM 独立 IP
- 防火墙规则（只开放必要端口）
- SSH 密钥认证（禁用密码登录）

### 3.4 成本控制
- 按需启动（任务来了才启动）
- 任务完成后自动销毁
- 设置预算上限（每月 $50）
- 监控费用（超过阈值告警）

## Phase 4：并行执行（Week 7）

**目标：** 多个 Agent 同时在不同 VM 上工作

### 4.1 任务队列
- 复用现有 `task_queue.jsonl`
- 每个任务分配一个 VM
- 支持优先级（critical 任务优先分配 VM）

### 4.2 VM 池管理
- 预热池（Pre-warmed Pool）：提前启动 2-3 个 VM
- 动态扩展：任务多时自动增加 VM
- 自动缩减：空闲 5 分钟后销毁 VM

### 4.3 负载均衡
- 根据 VM 负载分配任务
- 避免单个 VM 过载
- 支持任务迁移（VM 故障时）

## Phase 5：DataCollector 集成（Week 8）

**目标：** 统一收集所有 VM 的数据

### 5.1 事件收集
- VM 启动/停止事件
- 任务执行事件
- 命令执行事件
- 文件同步事件

### 5.2 日志收集
- VM 内部日志（stdout/stderr）
- 系统日志（syslog）
- 应用日志（Agent 日志）

### 5.3 指标收集
- CPU/内存/磁盘使用率
- 网络流量
- 任务执行时间
- 成本统计

## Phase 6：Evaluator + Quality Gates（Week 9）

**目标：** 评估 VM 执行结果，确保改进安全

### 6.1 Evaluator 集成
- 评估任务成功率
- 评估执行时间
- 评估成本效益
- 评估代码质量

### 6.2 Quality Gates 集成
- L0：自动测试（VM 内执行单元测试）
- L1：回归测试（对比历史结果）
- L2：人工审核（关键改进需要确认）

### 6.3 自动回滚
- 如果 Quality Gates 失败，自动回滚
- 保留 VM 快照（用于调试）
- 记录失败原因（lessons.json）

## 技术栈

### 本地（AIOS）
- Python 3.12
- Docker Python SDK（Phase 1-2）
- DigitalOcean Python SDK（Phase 3+）
- aiosqlite（数据存储）

### VM（云端）
- Ubuntu 22.04 LTS
- Python 3.12
- Docker
- VNC Server（TigerVNC）
- noVNC（Web 访问）
- VS Code Server
- Firefox

### 网络
- SSH（远程执行）
- VNC（桌面访问）
- HTTP/HTTPS（API 通信）

## 成本估算

### DigitalOcean Droplets
- **Basic Droplet：** $6/月（1 vCPU, 1GB RAM, 25GB SSD）
- **按小时计费：** $0.009/小时
- **预计使用：** 每天 2 小时 × 30 天 = 60 小时/月
- **月成本：** 60 × $0.009 = $0.54/月

### 并行执行（3 个 VM）
- **月成本：** $0.54 × 3 = $1.62/月

### GPU 沙箱（可选）
- **GPU Droplet：** $90/月（1 GPU, 8 vCPU, 16GB RAM）
- **按小时计费：** $0.134/小时
- **预计使用：** 每周 1 小时 × 4 周 = 4 小时/月
- **月成本：** 4 × $0.134 = $0.54/月

**总成本：** ~$2-3/月（不含 GPU），~$3-4/月（含 GPU）

## 风险和挑战

### 1. 网络延迟
- **问题：** 本地 ↔ 云端通信延迟
- **解决：** 选择最近的数据中心（新加坡）

### 2. 成本控制
- **问题：** VM 忘记关闭，费用失控
- **解决：** 自动销毁机制 + 预算告警

### 3. 安全性
- **问题：** VM 被攻击或滥用
- **解决：** 防火墙 + SSH 密钥 + 定期快照

### 4. 数据同步
- **问题：** 本地 ↔ VM 文件同步延迟
- **解决：** rsync + 增量同步

### 5. 调试困难
- **问题：** VM 内部出错，难以调试
- **解决：** VNC 桌面 + 完整日志 + 快照保留

## 参考资料

- **CloudRouter：** https://github.com/llm-x-factors/cloudrouter
- **DigitalOcean API：** https://docs.digitalocean.com/reference/api/
- **Docker Python SDK：** https://docker-py.readthedocs.io/
- **TigerVNC：** https://tigervnc.org/
- **noVNC：** https://novnc.com/

---

**版本：** v1.0  
**创建时间：** 2026-02-27  
**负责人：** 小九 + 珊瑚海

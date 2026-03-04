# AIOS v1.0 快速开始指南 (macOS 版)

## 📋 系统要求

- **macOS 10.15+**（Catalina 或更高）
- **Python 3.8+**（macOS 自带 Python 3）
- **磁盘空间**：至少 10 MB
- **零依赖**：无需安装任何第三方库

---

## 🚀 5分钟快速开始

### 1️⃣ 解压文件

**方法1：图形界面**
- 双击 `AIOS-v1.0-demo.zip`
- macOS 会自动解压到同一文件夹

**方法2：终端**
```bash
unzip AIOS-v1.0-demo.zip
```

### 2️⃣ 打开终端

**快捷方式：**
- `Command + 空格` → 输入 "Terminal" → 回车
- 或者：应用程序 → 实用工具 → 终端

### 3️⃣ 进入目录

```bash
cd ~/Downloads/aios
# 或者你解压到的其他位置
```

**💡 小技巧：** 直接把文件夹拖到终端窗口，会自动填入路径！

### 4️⃣ 运行演示

```bash
python3 aios.py demo
```

**预期输出：**
```
✅ AIOS v1.0 演示
📊 系统状态：健康
🔧 核心组件：EventBus, Scheduler, Reactor
```

---

## 🎯 核心功能

### 查看系统状态

```bash
python3 aios.py status
```

### 启动监控面板

```bash
python3 aios.py dashboard
```

**访问地址：** http://localhost:8080

**在浏览器打开：**
- Safari / Chrome / Firefox 都可以
- 或者按住 `Command` 点击终端里的链接

### 查看版本信息

```bash
python3 aios.py version
```

---

## 🛠️ macOS 特定问题

### Q1: 提示 "python3: command not found"

**检查 Python 版本：**
```bash
python3 --version
```

**如果没有安装 Python 3：**

**方法1：使用 Homebrew（推荐）**
```bash
# 安装 Homebrew（如果还没有）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python 3
brew install python@3.12
```

**方法2：从官网下载**
- 访问 [python.org/downloads](https://www.python.org/downloads/)
- 下载 macOS 安装包
- 双击安装

### Q2: 提示 "权限被拒绝"

**解决方案：**
```bash
# 给 aios.py 添加执行权限
chmod +x aios.py

# 然后可以直接运行
./aios.py demo
```

### Q3: 提示 "无法打开，因为无法验证开发者"

**这是 macOS 的安全机制，解决方法：**

**方法1：右键打开**
- 右键点击 `aios.py`
- 选择"打开方式" → "其他"
- 选择"终端"
- 点击"打开"

**方法2：系统设置**
- 系统偏好设置 → 安全性与隐私
- 点击"仍要打开"

**方法3：命令行（推荐）**
```bash
# 移除隔离属性
xattr -d com.apple.quarantine aios.py
```

### Q4: Dashboard 打不开

**检查端口占用：**
```bash
lsof -i :8080
```

**更换端口：**
```bash
python3 aios.py dashboard --port 8888
```

### Q5: 中文显示乱码

**设置终端编码：**
```bash
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8
```

**永久设置（添加到 ~/.zshrc 或 ~/.bash_profile）：**
```bash
echo 'export LANG=zh_CN.UTF-8' >> ~/.zshrc
echo 'export LC_ALL=zh_CN.UTF-8' >> ~/.zshrc
source ~/.zshrc
```

---

## 🍎 macOS 专属技巧

### 创建桌面快捷方式

**方法1：创建 Shell 脚本**

1. 创建文件 `AIOS.command`：
```bash
#!/bin/bash
cd ~/Downloads/aios
python3 aios.py dashboard
```

2. 添加执行权限：
```bash
chmod +x AIOS.command
```

3. 双击运行！

**方法2：创建 Automator 应用**

1. 打开 Automator
2. 新建"应用程序"
3. 添加"运行 Shell 脚本"
4. 输入：
```bash
cd ~/Downloads/aios && python3 aios.py dashboard
```
5. 保存为"AIOS Dashboard.app"

### 开机自启动

**方法1：登录项**
1. 系统偏好设置 → 用户与群组
2. 登录项 → 点击 "+"
3. 选择你创建的 `AIOS Dashboard.app`

**方法2：launchd（高级）**

创建 `~/Library/LaunchAgents/com.aios.dashboard.plist`：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aios.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/你的用户名/Downloads/aios/aios.py</string>
        <string>dashboard</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

加载：
```bash
launchctl load ~/Library/LaunchAgents/com.aios.dashboard.plist
```

### 使用 iTerm2（推荐）

如果你用 iTerm2 而不是系统自带终端：

**优势：**
- 更好的中文支持
- 分屏功能
- 更多自定义选项

**安装：**
```bash
brew install --cask iterm2
```

### 监控系统资源

**使用 Activity Monitor：**
1. 应用程序 → 实用工具 → 活动监视器
2. 搜索 "python3"
3. 查看 AIOS 的 CPU/内存占用

**命令行：**
```bash
# 查看 Python 进程
ps aux | grep python3

# 实时监控
top -pid $(pgrep -f aios.py)
```

---

## 📚 进阶使用

### 使用虚拟环境（可选）

虽然 AIOS 零依赖，但如果你想隔离环境：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活
source venv/bin/activate

# 运行 AIOS
python aios.py demo

# 退出虚拟环境
deactivate
```

### 自定义配置

编辑 `config.yaml`：

```bash
# 使用 nano（简单）
nano config.yaml

# 使用 vim（高级）
vim config.yaml

# 使用 VSCode（推荐）
code config.yaml
```

### 查看日志

```bash
# 实时日志
tail -f core/data/events.jsonl

# 最近 100 行
tail -n 100 core/data/events.jsonl

# 搜索错误
grep "error" core/data/events.jsonl
```

### 清理数据

```bash
# 清理 7 天前的事件
python3 aios.py cleanup --days 7

# 完全重置（谨慎！）
python3 aios.py reset
```

---

## 🎓 学习资源

### 核心概念

1. **EventBus** - 事件总线，系统心脏
2. **Scheduler** - 决策调度，系统大脑
3. **Reactor** - 自动修复，免疫系统
4. **Agent** - 执行单元，工作者

### 工作流程

```
错误发生 → EventBus → Scheduler → Reactor → 自动修复 → 验证 → 评分上升
```

### 文档位置

- **完整文档**: `README.md`
- **API 参考**: `API.md`
- **架构设计**: `ARCHITECTURE.md`

---

## 💡 使用建议

### 第一次使用

1. 先运行 `python3 aios.py demo` 确认环境正常
2. 再运行 `python3 aios.py status` 查看系统状态
3. 最后启动 `python3 aios.py dashboard` 体验可视化界面

### 日常使用

- **监控模式**: 保持 Dashboard 开启，实时查看系统状态
- **定期检查**: 每天运行 `python3 aios.py status` 查看健康度
- **数据清理**: 每周运行 `python3 aios.py cleanup` 清理旧数据

### 性能优化

- **降低心跳频率**: 修改 `config.yaml` 中的 `scheduler.interval`
- **限制日志大小**: 定期运行 `cleanup` 命令
- **关闭不需要的 Agent**: 编辑 `agent_system/agents.yaml`

---

## 🆘 获取帮助

### 命令行帮助

```bash
python3 aios.py --help
python3 aios.py demo --help
python3 aios.py status --help
```

### 常用快捷键

- `Control + C` - 停止运行
- `Command + K` - 清空终端
- `Command + T` - 新建终端标签页
- `Command + W` - 关闭当前标签页

### 联系方式

- **GitHub**: [你的 GitHub 仓库]
- **Email**: [你的邮箱]
- **Telegram**: @shh7799

---

## 📝 下一步

1. ✅ 完成快速开始
2. 📖 阅读 `README.md` 了解完整功能
3. 🎯 尝试自定义配置
4. 🚀 集成到你的项目中

---

## 🍎 macOS 专属资源

### 推荐工具

- **iTerm2** - 更强大的终端
- **Homebrew** - macOS 包管理器
- **VSCode** - 代码编辑器
- **Dash** - API 文档查看器

### 系统优化

```bash
# 显示隐藏文件
defaults write com.apple.finder AppleShowAllFiles YES
killall Finder

# 禁用 Gatekeeper（谨慎！）
sudo spctl --master-disable

# 查看系统信息
system_profiler SPSoftwareDataType
```

---

**祝你使用愉快！** 🎉🍎

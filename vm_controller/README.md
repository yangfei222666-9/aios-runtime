# VM Controller - 快速开始

## 安装 Docker Desktop

1. **下载：** https://www.docker.com/products/docker-desktop/
2. **安装：** 双击安装程序，勾选 "Use WSL 2 instead of Hyper-V"
3. **重启：** 安装完成后重启电脑
4. **验证：**
   ```bash
   docker --version
   docker run hello-world
   ```

## 快速测试

安装完 Docker 后，运行：

```bash
cd C:\Users\A\.openclaw\workspace\aios\vm_controller
python test_vm_controller.py
```

**预期输出：**
```
=== VM Controller CLI 测试 ===

1. 创建 VM...
   ✅ VM created: 3f2a1b4c5d6e...

2. 启动 VM...
   ✅ VM started

3. 执行命令...
   ✅ Command executed:
      stdout: Hello from VM
      exit_code: 0
      duration: 234ms

4. 查询状态...
   ✅ Status: running

5. 列出所有 VM...
   ✅ Total VMs: 1

6. 停止 VM...
   ✅ VM stopped

7. 删除 VM...
   ✅ VM deleted

=== 所有测试通过 ✅ ===
```

## CLI 使用

```bash
# 创建 VM
python vm_controller.py create my-agent

# 启动 VM
python vm_controller.py start <vm_id>

# 在 VM 中执行命令
python vm_controller.py exec <vm_id> "python3 -c 'print(1+1)'"

# 查询状态
python vm_controller.py status <vm_id>

# 列出所有 VM
python vm_controller.py list

# 获取日志
python vm_controller.py logs <vm_id>

# 停止 VM
python vm_controller.py stop <vm_id>

# 删除 VM
python vm_controller.py delete <vm_id>

# 清理所有 VM
python vm_controller.py cleanup
```

## Python API

```python
from vm_controller import VMController

# 创建控制器
controller = VMController()

# 创建 VM
vm_id = controller.create_vm('my-agent')

# 启动 VM
controller.start_vm(vm_id)

# 执行命令
result = controller.execute_in_vm(vm_id, 'python3 -c "print(1+1)"')
print(result['stdout'])  # 输出: 2

# 停止 VM
controller.stop_vm(vm_id)

# 删除 VM
controller.delete_vm(vm_id)
```

## 并行测试

```python
# 创建 3 个 VM 并行执行任务
vm_ids = []
for i in range(3):
    vm_id = controller.create_vm(f'agent-{i}')
    controller.start_vm(vm_id)
    vm_ids.append(vm_id)

# 并行执行
for i, vm_id in enumerate(vm_ids):
    result = controller.execute_in_vm(vm_id, f'echo "Task {i} done"')
    print(result['stdout'])
```

## 下一步

- ✅ Phase 1: Docker 模拟（今天）
- ⏳ Phase 2: VNC 桌面（下周）
- ⏳ Phase 3: CloudRouter 集成（2-3周后）
- ⏳ Phase 4: 并行执行（4周后）
- ⏳ Phase 5: DataCollector 集成（5周后）
- ⏳ Phase 6: Evaluator + Quality Gates（6周后）

---

**准备好了吗？安装 Docker 后运行测试！** 🚀

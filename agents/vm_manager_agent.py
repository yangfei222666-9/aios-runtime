"""
AIOS VM Manager Agent - VM 生命周期管理
集成 vm-controller-skill，提供 VM 创建/启动/停止/删除/监控能力
"""

import sys
import os
from pathlib import Path

# 添加 skill 路径
SKILL_PATH = Path(__file__).parent.parent.parent / "skills" / "vm-controller-skill"
sys.path.insert(0, str(SKILL_PATH))

from vm_controller import (
    vm_create, vm_start, vm_stop, vm_delete, 
    vm_status, vm_exec, vm_shell, vm_logs,
    check_docker, load_registry
)


class VMManagerAgent:
    """VM 管理 Agent"""
    
    def __init__(self):
        self.name = "VM_Manager"
        self.version = "1.0.0"
        self.capabilities = [
            "create_vm",
            "start_vm", 
            "stop_vm",
            "delete_vm",
            "query_status",
            "exec_command",
            "view_logs",
            "monitor_resources"
        ]
    
    def handle_task(self, task: dict) -> dict:
        """
        处理 VM 管理任务
        
        task 格式:
        {
            "action": "create|start|stop|delete|status|exec|logs",
            "vm_name": "vm名称",
            "image": "镜像名（可选）",
            "cpu": "CPU核数（可选）",
            "memory": "内存大小（可选）",
            "ports": "端口映射（可选）",
            "command": "要执行的命令（exec时）",
            "lines": 日志行数（logs时）
        }
        """
        action = task.get("action")
        vm_name = task.get("vm_name")
        
        try:
            if action == "check":
                success = check_docker()
                return {
                    "success": success,
                    "action": "check",
                    "message": "Docker 已就绪" if success else "Docker 不可用"
                }
            
            elif action == "create":
                success = vm_create(
                    name=vm_name,
                    image=task.get("image", "ubuntu"),
                    cpu=task.get("cpu", "1"),
                    memory=task.get("memory", "512m"),
                    ports=task.get("ports")
                )
                return {
                    "success": success,
                    "action": "create",
                    "vm_name": vm_name,
                    "message": f"VM '{vm_name}' 创建{'成功' if success else '失败'}"
                }
            
            elif action == "start":
                success = vm_start(vm_name)
                return {
                    "success": success,
                    "action": "start",
                    "vm_name": vm_name,
                    "message": f"VM '{vm_name}' 启动{'成功' if success else '失败'}"
                }
            
            elif action == "stop":
                success = vm_stop(vm_name)
                return {
                    "success": success,
                    "action": "stop",
                    "vm_name": vm_name,
                    "message": f"VM '{vm_name}' 停止{'成功' if success else '失败'}"
                }
            
            elif action == "delete":
                force = task.get("force", False)
                success = vm_delete(vm_name, force=force)
                return {
                    "success": success,
                    "action": "delete",
                    "vm_name": vm_name,
                    "message": f"VM '{vm_name}' 删除{'成功' if success else '失败'}"
                }
            
            elif action == "status":
                registry = load_registry()
                if vm_name:
                    vm_info = registry.get(vm_name)
                    return {
                        "success": vm_info is not None,
                        "action": "status",
                        "vm_name": vm_name,
                        "info": vm_info,
                        "message": f"VM '{vm_name}' 信息" if vm_info else f"VM '{vm_name}' 不存在"
                    }
                else:
                    return {
                        "success": True,
                        "action": "status",
                        "vms": registry,
                        "count": len(registry),
                        "message": f"共 {len(registry)} 个 VM"
                    }
            
            elif action == "exec":
                command = task.get("command")
                if not command:
                    return {
                        "success": False,
                        "action": "exec",
                        "message": "缺少 command 参数"
                    }
                success = vm_exec(vm_name, command)
                return {
                    "success": success,
                    "action": "exec",
                    "vm_name": vm_name,
                    "command": command,
                    "message": f"命令执行{'成功' if success else '失败'}"
                }
            
            elif action == "logs":
                lines = task.get("lines", 50)
                success = vm_logs(vm_name, lines)
                return {
                    "success": success,
                    "action": "logs",
                    "vm_name": vm_name,
                    "message": f"日志查看{'成功' if success else '失败'}"
                }
            
            else:
                return {
                    "success": False,
                    "action": action,
                    "message": f"未知操作: {action}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "action": action,
                "error": str(e),
                "message": f"执行失败: {e}"
            }
    
    def get_status(self) -> dict:
        """获取 Agent 状态"""
        registry = load_registry()
        return {
            "agent": self.name,
            "version": self.version,
            "docker_available": check_docker(),
            "vm_count": len(registry),
            "vms": list(registry.keys())
        }


# 测试代码
if __name__ == "__main__":
    agent = VMManagerAgent()
    
    print("🧪 测试 VM Manager Agent\n")
    
    # 1. 检查 Docker
    print("1️⃣ 检查 Docker 状态")
    result = agent.handle_task({"action": "check"})
    print(f"   {result}\n")
    
    # 2. 创建测试 VM
    print("2️⃣ 创建测试 VM")
    result = agent.handle_task({
        "action": "create",
        "vm_name": "aios-test",
        "image": "alpine",
        "memory": "256m"
    })
    print(f"   {result}\n")
    
    # 3. 查看状态
    print("3️⃣ 查看 VM 状态")
    result = agent.handle_task({"action": "status"})
    print(f"   {result}\n")
    
    # 4. 执行命令
    print("4️⃣ 执行命令")
    result = agent.handle_task({
        "action": "exec",
        "vm_name": "aios-test",
        "command": "echo 'Hello from AIOS VM!'"
    })
    print(f"   {result}\n")
    
    # 5. Agent 状态
    print("5️⃣ Agent 状态")
    status = agent.get_status()
    print(f"   {status}\n")
    
    print("✅ 测试完成")

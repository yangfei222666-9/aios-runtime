"""
VM Controller - 虚拟机控制器

Phase 1: 使用 Docker 模拟 VM
"""

import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import os

# Docker 可执行文件路径
DOCKER_EXE = os.environ.get('DOCKER_EXE', 'docker')
if os.name == 'nt' and DOCKER_EXE == 'docker':
    # Windows 默认路径
    default_path = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"
    if os.path.exists(default_path):
        DOCKER_EXE = default_path


class VMController:
    """VM 控制器（Docker 实现）"""
    
    def __init__(self, data_dir: str = "vm_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.vms_file = self.data_dir / "vms.json"
        self.vms = self._load_vms()
    
    def _load_vms(self) -> Dict:
        """加载 VM 列表"""
        if self.vms_file.exists():
            with open(self.vms_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_vms(self):
        """保存 VM 列表"""
        with open(self.vms_file, 'w', encoding='utf-8') as f:
            json.dump(self.vms, f, indent=2, ensure_ascii=False)
    
    def create_vm(self, agent_id: str, config: Optional[Dict] = None) -> str:
        """
        创建 VM
        
        Args:
            agent_id: Agent ID
            config: VM 配置（可选）
                - image: Docker 镜像（默认 python:3.12-slim）
                - memory: 内存限制（默认 512m）
                - cpu: CPU 限制（默认 1.0）
                - workdir: 工作目录（默认 /workspace）
        
        Returns:
            vm_id: VM ID（Docker 容器 ID）
        """
        config = config or {}
        image = config.get('image', 'python:3.12-slim')
        memory = config.get('memory', '512m')
        cpu = config.get('cpu', '1.0')
        workdir = config.get('workdir', '/workspace')
        
        # 容器名称
        container_name = f"aios-vm-{agent_id}-{int(time.time())}"
        
        # 创建容器（不启动）
        cmd = [
            DOCKER_EXE, 'create',
            '--name', container_name,
            '--memory', memory,
            '--cpus', str(cpu),
            '--workdir', workdir,
            image,
            'sleep', 'infinity'  # 保持容器运行
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            vm_id = result.stdout.strip()
            
            # 保存 VM 信息
            self.vms[vm_id] = {
                'agent_id': agent_id,
                'container_name': container_name,
                'image': image,
                'memory': memory,
                'cpu': cpu,
                'workdir': workdir,
                'status': 'created',
                'created_at': datetime.now().isoformat()
            }
            self._save_vms()
            
            return vm_id
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to create VM: {e.stderr}")
    
    def start_vm(self, vm_id: str):
        """启动 VM"""
        if vm_id not in self.vms:
            raise ValueError(f"VM not found: {vm_id}")
        
        try:
            subprocess.run([DOCKER_EXE, 'start', vm_id], check=True, capture_output=True)
            self.vms[vm_id]['status'] = 'running'
            self.vms[vm_id]['started_at'] = datetime.now().isoformat()
            self._save_vms()
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to start VM: {e.stderr}")
    
    def stop_vm(self, vm_id: str):
        """停止 VM"""
        if vm_id not in self.vms:
            raise ValueError(f"VM not found: {vm_id}")
        
        try:
            subprocess.run([DOCKER_EXE, 'stop', vm_id], check=True, capture_output=True)
            self.vms[vm_id]['status'] = 'stopped'
            self.vms[vm_id]['stopped_at'] = datetime.now().isoformat()
            self._save_vms()
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to stop VM: {e.stderr}")
    
    def delete_vm(self, vm_id: str):
        """删除 VM"""
        if vm_id not in self.vms:
            raise ValueError(f"VM not found: {vm_id}")
        
        # 先停止（如果正在运行）
        if self.vms[vm_id]['status'] == 'running':
            self.stop_vm(vm_id)
        
        try:
            subprocess.run([DOCKER_EXE, 'rm', vm_id], check=True, capture_output=True)
            del self.vms[vm_id]
            self._save_vms()
        
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to delete VM: {e.stderr}")
    
    def list_vms(self) -> List[Dict]:
        """列出所有 VM"""
        return [
            {'vm_id': vm_id, **info}
            for vm_id, info in self.vms.items()
        ]
    
    def get_vm_status(self, vm_id: str) -> Dict:
        """查询 VM 状态"""
        if vm_id not in self.vms:
            raise ValueError(f"VM not found: {vm_id}")
        
        # 从 Docker 获取实时状态
        try:
            result = subprocess.run(
                [DOCKER_EXE, 'inspect', vm_id, '--format', '{{.State.Status}}'],
                capture_output=True,
                text=True,
                check=True
            )
            docker_status = result.stdout.strip()
            
            # 更新状态
            self.vms[vm_id]['status'] = docker_status
            self._save_vms()
            
            return {
                'vm_id': vm_id,
                **self.vms[vm_id],
                'docker_status': docker_status
            }
        
        except subprocess.CalledProcessError:
            # 容器可能已被手动删除
            return {
                'vm_id': vm_id,
                **self.vms[vm_id],
                'docker_status': 'not_found'
            }
    
    def execute_in_vm(self, vm_id: str, command: str) -> Dict:
        """
        在 VM 中执行命令
        
        Args:
            vm_id: VM ID
            command: 要执行的命令
        
        Returns:
            {
                'stdout': str,
                'stderr': str,
                'exit_code': int,
                'duration_ms': int
            }
        """
        if vm_id not in self.vms:
            raise ValueError(f"VM not found: {vm_id}")
        
        if self.vms[vm_id]['status'] != 'running':
            raise RuntimeError(f"VM is not running: {vm_id}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [DOCKER_EXE, 'exec', vm_id, 'sh', '-c', command],
                capture_output=True,
                text=True,
                timeout=60  # 60秒超时
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode,
                'duration_ms': duration_ms
            }
        
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                'stdout': '',
                'stderr': 'Command timeout (60s)',
                'exit_code': -1,
                'duration_ms': duration_ms
            }
        
        except subprocess.CalledProcessError as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                'stdout': e.stdout or '',
                'stderr': e.stderr or str(e),
                'exit_code': e.returncode,
                'duration_ms': duration_ms
            }
    
    def get_logs(self, vm_id: str, tail: int = 100) -> str:
        """
        获取 VM 日志
        
        Args:
            vm_id: VM ID
            tail: 最后 N 行（默认 100）
        
        Returns:
            日志内容
        """
        if vm_id not in self.vms:
            raise ValueError(f"VM not found: {vm_id}")
        
        try:
            result = subprocess.run(
                [DOCKER_EXE, 'logs', '--tail', str(tail), vm_id],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        
        except subprocess.CalledProcessError as e:
            return f"Failed to get logs: {e.stderr}"
    
    def cleanup_all(self):
        """清理所有 VM（用于测试）"""
        for vm_id in list(self.vms.keys()):
            try:
                self.delete_vm(vm_id)
            except Exception as e:
                print(f"Failed to delete VM {vm_id}: {e}")


def main():
    """CLI 入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vm_controller.py <command> [args...]")
        print("Commands:")
        print("  create <agent_id>           - 创建 VM")
        print("  start <vm_id>               - 启动 VM")
        print("  stop <vm_id>                - 停止 VM")
        print("  delete <vm_id>              - 删除 VM")
        print("  list                        - 列出所有 VM")
        print("  status <vm_id>              - 查询 VM 状态")
        print("  exec <vm_id> <command>      - 在 VM 中执行命令")
        print("  logs <vm_id>                - 获取 VM 日志")
        print("  cleanup                     - 清理所有 VM")
        sys.exit(1)
    
    controller = VMController()
    command = sys.argv[1]
    
    try:
        if command == 'create':
            agent_id = sys.argv[2]
            vm_id = controller.create_vm(agent_id)
            print(f"VM created: {vm_id}")
        
        elif command == 'start':
            vm_id = sys.argv[2]
            controller.start_vm(vm_id)
            print(f"VM started: {vm_id}")
        
        elif command == 'stop':
            vm_id = sys.argv[2]
            controller.stop_vm(vm_id)
            print(f"VM stopped: {vm_id}")
        
        elif command == 'delete':
            vm_id = sys.argv[2]
            controller.delete_vm(vm_id)
            print(f"VM deleted: {vm_id}")
        
        elif command == 'list':
            vms = controller.list_vms()
            print(json.dumps(vms, indent=2, ensure_ascii=False))
        
        elif command == 'status':
            vm_id = sys.argv[2]
            status = controller.get_vm_status(vm_id)
            print(json.dumps(status, indent=2, ensure_ascii=False))
        
        elif command == 'exec':
            vm_id = sys.argv[2]
            cmd = ' '.join(sys.argv[3:])
            result = controller.execute_in_vm(vm_id, cmd)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        elif command == 'logs':
            vm_id = sys.argv[2]
            logs = controller.get_logs(vm_id)
            print(logs)
        
        elif command == 'cleanup':
            controller.cleanup_all()
            print("All VMs cleaned up")
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

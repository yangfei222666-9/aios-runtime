"""
AIOS Platform Adapter - 跨平台适配层
支持 Windows、macOS、Linux 的自动检测和适配
"""

import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PlatformAdapter:
    """平台适配器 - 自动检测并适配不同操作系统"""
    
    def __init__(self):
        self.system = platform.system()  # Windows, Darwin, Linux
        self.machine = platform.machine()  # x86_64, arm64, etc.
        self.python_version = sys.version_info
        
    def get_platform_info(self) -> Dict[str, str]:
        """获取平台信息"""
        return {
            "system": self.system,
            "machine": self.machine,
            "python_version": f"{self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}",
            "platform": platform.platform(),
        }
    
    def get_shell_command(self) -> str:
        """获取当前平台的 Shell 命令"""
        if self.system == "Windows":
            return "powershell"
        else:
            return "bash"
    
    def get_python_executable(self) -> str:
        """获取 Python 可执行文件路径"""
        return sys.executable
    
    def get_path_separator(self) -> str:
        """获取路径分隔符"""
        return os.pathsep  # Windows: ; | Unix: :
    
    def get_line_ending(self) -> str:
        """获取换行符"""
        if self.system == "Windows":
            return "\r\n"
        else:
            return "\n"
    
    def normalize_path(self, path: str) -> str:
        """规范化路径（自动处理不同平台的路径分隔符）"""
        return str(Path(path).resolve())
    
    def get_home_dir(self) -> str:
        """获取用户主目录"""
        return str(Path.home())
    
    def get_config_dir(self) -> str:
        """获取配置目录"""
        if self.system == "Windows":
            return os.path.join(os.getenv("APPDATA", ""), "aios")
        elif self.system == "Darwin":
            return os.path.join(self.get_home_dir(), "Library", "Application Support", "aios")
        else:  # Linux
            return os.path.join(self.get_home_dir(), ".config", "aios")
    
    def get_data_dir(self) -> str:
        """获取数据目录"""
        if self.system == "Windows":
            return os.path.join(os.getenv("LOCALAPPDATA", ""), "aios")
        elif self.system == "Darwin":
            return os.path.join(self.get_home_dir(), "Library", "Application Support", "aios", "data")
        else:  # Linux
            return os.path.join(self.get_home_dir(), ".local", "share", "aios")
    
    def get_cache_dir(self) -> str:
        """获取缓存目录"""
        if self.system == "Windows":
            return os.path.join(os.getenv("LOCALAPPDATA", ""), "aios", "cache")
        elif self.system == "Darwin":
            return os.path.join(self.get_home_dir(), "Library", "Caches", "aios")
        else:  # Linux
            return os.path.join(self.get_home_dir(), ".cache", "aios")
    
    def get_log_dir(self) -> str:
        """获取日志目录"""
        if self.system == "Windows":
            return os.path.join(os.getenv("LOCALAPPDATA", ""), "aios", "logs")
        elif self.system == "Darwin":
            return os.path.join(self.get_home_dir(), "Library", "Logs", "aios")
        else:  # Linux
            return os.path.join(self.get_home_dir(), ".local", "share", "aios", "logs")
    
    def create_directories(self):
        """创建所有必要的目录"""
        dirs = [
            self.get_config_dir(),
            self.get_data_dir(),
            self.get_cache_dir(),
            self.get_log_dir(),
        ]
        for d in dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
    
    def get_startup_script_path(self) -> str:
        """获取启动脚本路径"""
        if self.system == "Windows":
            return os.path.join(
                os.getenv("APPDATA", ""),
                "Microsoft",
                "Windows",
                "Start Menu",
                "Programs",
                "Startup",
                "aios.bat"
            )
        elif self.system == "Darwin":
            return os.path.join(
                self.get_home_dir(),
                "Library",
                "LaunchAgents",
                "com.aios.agent.plist"
            )
        else:  # Linux
            return os.path.join(
                self.get_home_dir(),
                ".config",
                "autostart",
                "aios.desktop"
            )
    
    def install_startup_script(self, script_content: str) -> bool:
        """安装开机自启动脚本"""
        try:
            script_path = self.get_startup_script_path()
            Path(script_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
            
            # Linux/macOS 需要添加执行权限
            if self.system != "Windows":
                os.chmod(script_path, 0o755)
            
            return True
        except Exception as e:
            print(f"[ERROR] Failed to install startup script: {e}")
            return False
    
    def get_process_list_command(self) -> List[str]:
        """获取进程列表命令"""
        if self.system == "Windows":
            return ["powershell", "-Command", "Get-Process | Select-Object Name, Id, CPU"]
        else:
            return ["ps", "aux"]
    
    def get_kill_process_command(self, pid: int) -> List[str]:
        """获取杀死进程命令"""
        if self.system == "Windows":
            return ["taskkill", "/F", "/PID", str(pid)]
        else:
            return ["kill", "-9", str(pid)]
    
    def run_command(self, command: List[str], timeout: int = 30) -> Tuple[int, str, str]:
        """运行命令（跨平台）"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8" if self.system == "Windows" else None,
                errors="replace" if self.system == "Windows" else None,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout"
        except Exception as e:
            return -1, "", str(e)
    
    def get_system_info(self) -> Dict[str, str]:
        """获取系统信息"""
        info = self.get_platform_info()
        
        # CPU 信息
        if self.system == "Windows":
            code, out, _ = self.run_command(
                ["powershell", "-Command", "(Get-WmiObject Win32_Processor).Name"]
            )
            info["cpu"] = out.strip() if code == 0 else "Unknown"
        else:
            code, out, _ = self.run_command(["uname", "-m"])
            info["cpu"] = out.strip() if code == 0 else "Unknown"
        
        # 内存信息
        if self.system == "Windows":
            code, out, _ = self.run_command(
                ["powershell", "-Command", "(Get-WmiObject Win32_ComputerSystem).TotalPhysicalMemory"]
            )
            if code == 0:
                try:
                    mem_bytes = int(out.strip())
                    info["memory"] = f"{mem_bytes / (1024**3):.1f} GB"
                except:
                    info["memory"] = "Unknown"
        else:
            code, out, _ = self.run_command(["free", "-h"])
            if code == 0:
                lines = out.strip().split("\n")
                if len(lines) > 1:
                    info["memory"] = lines[1].split()[1]
        
        return info


# 全局单例
_adapter = None


def get_adapter() -> PlatformAdapter:
    """获取平台适配器单例"""
    global _adapter
    if _adapter is None:
        _adapter = PlatformAdapter()
    return _adapter


def main():
    """测试平台适配器"""
    adapter = get_adapter()
    
    print("=" * 60)
    print("AIOS Platform Adapter")
    print("=" * 60)
    
    print("\n[Platform Info]")
    for key, value in adapter.get_platform_info().items():
        print(f"  {key}: {value}")
    
    print("\n[System Info]")
    for key, value in adapter.get_system_info().items():
        print(f"  {key}: {value}")
    
    print("\n[Directories]")
    print(f"  Config: {adapter.get_config_dir()}")
    print(f"  Data: {adapter.get_data_dir()}")
    print(f"  Cache: {adapter.get_cache_dir()}")
    print(f"  Log: {adapter.get_log_dir()}")
    
    print("\n[Startup Script]")
    print(f"  Path: {adapter.get_startup_script_path()}")
    
    print("\n[Shell]")
    print(f"  Command: {adapter.get_shell_command()}")
    print(f"  Python: {adapter.get_python_executable()}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

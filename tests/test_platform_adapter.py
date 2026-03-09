"""
AIOS 平台检测和自动适配测试
"""

import unittest
import os
import sys
import platform
from pathlib import Path

# 添加父目录到 sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from platform_adapter import PlatformAdapter, get_adapter


class TestPlatformAdapter(unittest.TestCase):
    """测试平台适配器"""
    
    def setUp(self):
        """初始化测试"""
        self.adapter = get_adapter()
    
    def test_platform_detection(self):
        """测试平台检测"""
        info = self.adapter.get_platform_info()
        
        self.assertIn("system", info)
        self.assertIn("machine", info)
        self.assertIn("python_version", info)
        self.assertIn("platform", info)
        
        # 验证系统类型
        self.assertIn(info["system"], ["Windows", "Darwin", "Linux"])
    
    def test_shell_command(self):
        """测试 Shell 命令"""
        shell = self.adapter.get_shell_command()
        
        if platform.system() == "Windows":
            self.assertEqual(shell, "powershell")
        else:
            self.assertEqual(shell, "bash")
    
    def test_python_executable(self):
        """测试 Python 可执行文件路径"""
        python_exe = self.adapter.get_python_executable()
        
        self.assertTrue(os.path.exists(python_exe))
        self.assertTrue(python_exe.endswith(("python", "python.exe", "python3")))
    
    def test_path_separator(self):
        """测试路径分隔符"""
        sep = self.adapter.get_path_separator()
        
        if platform.system() == "Windows":
            self.assertEqual(sep, ";")
        else:
            self.assertEqual(sep, ":")
    
    def test_line_ending(self):
        """测试换行符"""
        line_ending = self.adapter.get_line_ending()
        
        if platform.system() == "Windows":
            self.assertEqual(line_ending, "\r\n")
        else:
            self.assertEqual(line_ending, "\n")
    
    def test_normalize_path(self):
        """测试路径规范化"""
        # 测试相对路径
        path = self.adapter.normalize_path(".")
        self.assertTrue(os.path.isabs(path))
        
        # 测试绝对路径
        if platform.system() == "Windows":
            test_path = "C:\\Users\\test\\file.txt"
        else:
            test_path = "/home/test/file.txt"
        
        normalized = self.adapter.normalize_path(test_path)
        self.assertTrue(os.path.isabs(normalized))
    
    def test_home_dir(self):
        """测试用户主目录"""
        home = self.adapter.get_home_dir()
        
        self.assertTrue(os.path.exists(home))
        self.assertTrue(os.path.isabs(home))
    
    def test_config_dir(self):
        """测试配置目录"""
        config_dir = self.adapter.get_config_dir()
        
        self.assertTrue(os.path.isabs(config_dir))
        self.assertIn("aios", config_dir.lower())
    
    def test_data_dir(self):
        """测试数据目录"""
        data_dir = self.adapter.get_data_dir()
        
        self.assertTrue(os.path.isabs(data_dir))
        self.assertIn("aios", data_dir.lower())
    
    def test_cache_dir(self):
        """测试缓存目录"""
        cache_dir = self.adapter.get_cache_dir()
        
        self.assertTrue(os.path.isabs(cache_dir))
        self.assertIn("aios", cache_dir.lower())
    
    def test_log_dir(self):
        """测试日志目录"""
        log_dir = self.adapter.get_log_dir()
        
        self.assertTrue(os.path.isabs(log_dir))
        self.assertIn("aios", log_dir.lower())
    
    def test_create_directories(self):
        """测试创建目录"""
        # 创建目录
        self.adapter.create_directories()
        
        # 验证目录存在
        self.assertTrue(os.path.exists(self.adapter.get_config_dir()))
        self.assertTrue(os.path.exists(self.adapter.get_data_dir()))
        self.assertTrue(os.path.exists(self.adapter.get_cache_dir()))
        self.assertTrue(os.path.exists(self.adapter.get_log_dir()))
    
    def test_startup_script_path(self):
        """测试启动脚本路径"""
        script_path = self.adapter.get_startup_script_path()
        
        self.assertTrue(os.path.isabs(script_path))
        
        if platform.system() == "Windows":
            self.assertTrue(script_path.endswith(".bat"))
        elif platform.system() == "Darwin":
            self.assertTrue(script_path.endswith(".plist"))
        else:  # Linux
            self.assertTrue(script_path.endswith(".desktop"))
    
    def test_process_list_command(self):
        """测试进程列表命令"""
        cmd = self.adapter.get_process_list_command()
        
        self.assertIsInstance(cmd, list)
        self.assertGreater(len(cmd), 0)
    
    def test_kill_process_command(self):
        """测试杀死进程命令"""
        cmd = self.adapter.get_kill_process_command(12345)
        
        self.assertIsInstance(cmd, list)
        self.assertGreater(len(cmd), 0)
        self.assertIn("12345", " ".join(cmd))
    
    def test_run_command(self):
        """测试运行命令"""
        # 测试简单命令
        if platform.system() == "Windows":
            cmd = ["powershell", "-Command", "echo test"]
        else:
            cmd = ["echo", "test"]
        
        code, stdout, stderr = self.adapter.run_command(cmd, timeout=5)
        
        self.assertEqual(code, 0)
        self.assertIn("test", stdout.lower())
    
    def test_system_info(self):
        """测试系统信息"""
        info = self.adapter.get_system_info()
        
        self.assertIn("system", info)
        self.assertIn("machine", info)
        self.assertIn("python_version", info)
        self.assertIn("cpu", info)
    
    def test_singleton(self):
        """测试单例模式"""
        adapter1 = get_adapter()
        adapter2 = get_adapter()
        
        self.assertIs(adapter1, adapter2)


class TestPlatformSpecific(unittest.TestCase):
    """测试平台特定功能"""
    
    def setUp(self):
        """初始化测试"""
        self.adapter = get_adapter()
        self.system = platform.system()
    
    def test_windows_specific(self):
        """测试 Windows 特定功能"""
        if self.system != "Windows":
            self.skipTest("Not running on Windows")
        
        # 测试 PowerShell 命令
        cmd = ["powershell", "-Command", "Get-Date"]
        code, stdout, stderr = self.adapter.run_command(cmd)
        self.assertEqual(code, 0)
        
        # 测试路径格式
        config_dir = self.adapter.get_config_dir()
        self.assertIn("AppData", config_dir)
    
    def test_macos_specific(self):
        """测试 macOS 特定功能"""
        if self.system != "Darwin":
            self.skipTest("Not running on macOS")
        
        # 测试 bash 命令
        cmd = ["date"]
        code, stdout, stderr = self.adapter.run_command(cmd)
        self.assertEqual(code, 0)
        
        # 测试路径格式
        config_dir = self.adapter.get_config_dir()
        self.assertIn("Library", config_dir)
    
    def test_linux_specific(self):
        """测试 Linux 特定功能"""
        if self.system != "Linux":
            self.skipTest("Not running on Linux")
        
        # 测试 bash 命令
        cmd = ["date"]
        code, stdout, stderr = self.adapter.run_command(cmd)
        self.assertEqual(code, 0)
        
        # 测试路径格式
        config_dir = self.adapter.get_config_dir()
        self.assertIn(".config", config_dir)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestPlatformSpecific))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

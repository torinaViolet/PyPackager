"""虚拟环境检测器 - 自动检测和管理 Python 虚拟环境"""

import os
import sys
import subprocess
import json
from pathlib import Path


class VenvDetector:
    """检测项目使用的虚拟环境，获取 Python 解释器路径和已安装包信息"""

    def __init__(self):
        self._cached_packages = {}

    def detect_venv(self, project_dir: str) -> dict:
        """
        自动检测项目目录下的虚拟环境
        返回:
            {
                "found": bool,
                "type": "venv" | "conda" | "virtualenv" | "system",
                "path": str,
                "python_path": str,
                "python_version": str,
            }
        """
        project_path = Path(project_dir)
        result = {
            "found": False,
            "type": "system",
            "path": "",
            "python_path": sys.executable,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        }

        # 1. 检查常见虚拟环境目录名
        venv_dir_names = ["venv", ".venv", "env", ".env", "virtualenv"]
        for name in venv_dir_names:
            venv_path = project_path / name
            if venv_path.is_dir():
                python_path = self._find_python_in_venv(str(venv_path))
                if python_path:
                    result.update({
                        "found": True,
                        "type": self._detect_venv_type(str(venv_path)),
                        "path": str(venv_path),
                        "python_path": python_path,
                        "python_version": self._get_python_version(python_path),
                    })
                    return result

        # 2. 检查 conda 环境
        conda_result = self._detect_conda_env(project_dir)
        if conda_result:
            result.update(conda_result)
            return result

        # 3. 检查当前解释器是否在虚拟环境中
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            result.update({
                "found": True,
                "type": "venv",
                "path": sys.prefix,
                "python_path": sys.executable,
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            })

        return result

    def _find_python_in_venv(self, venv_path: str) -> str:
        """在虚拟环境目录中查找 Python 解释器"""
        venv = Path(venv_path)
        if os.name == 'nt':  # Windows
            candidates = [
                venv / "Scripts" / "python.exe",
                venv / "Scripts" / "python3.exe",
            ]
        else:  # Linux/Mac
            candidates = [
                venv / "bin" / "python",
                venv / "bin" / "python3",
            ]

        for candidate in candidates:
            if candidate.is_file():
                return str(candidate)
        return ""

    def _detect_venv_type(self, venv_path: str) -> str:
        """判断虚拟环境的类型"""
        venv = Path(venv_path)
        if (venv / "conda-meta").is_dir():
            return "conda"
        if (venv / "pyvenv.cfg").is_file():
            return "venv"
        return "virtualenv"

    def _detect_conda_env(self, project_dir: str) -> dict | None:
        """检测 conda 环境"""
        project_path = Path(project_dir)
        # 检查 environment.yml
        env_file = project_path / "environment.yml"
        if not env_file.exists():
            env_file = project_path / "environment.yaml"

        if env_file.exists():
            try:
                import yaml
                with open(env_file, 'r') as f:
                    env_config = yaml.safe_load(f)
                env_name = env_config.get('name', '')
                if env_name:
                    conda_path = self._find_conda_env_path(env_name)
                    if conda_path:
                        python_path = self._find_python_in_venv(conda_path)
                        return {
                            "found": True,
                            "type": "conda",
                            "path": conda_path,
                            "python_path": python_path or sys.executable,
                            "python_version": self._get_python_version(python_path or sys.executable),
                        }
            except Exception:
                pass
        return None

    def _find_conda_env_path(self, env_name: str) -> str:
        """通过环境名找到 conda 环境路径"""
        try:
            result = subprocess.run(
                ["conda", "info", "--envs", "--json"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                info = json.loads(result.stdout)
                for env_path in info.get("envs", []):
                    if Path(env_path).name == env_name:
                        return env_path
        except Exception:
            pass
        return ""

    def _get_python_version(self, python_path: str) -> str:
        """获取指定 Python 解释器的版本号"""
        try:
            result = subprocess.run(
                [python_path, "--version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                # 输出格式: "Python 3.11.5"
                version_str = result.stdout.strip().replace("Python ", "")
                return version_str
        except Exception:
            pass
        return "unknown"

    def get_installed_packages(self, python_path: str = None) -> dict:
        """
        获取已安装的包列表
        返回: {"package_name": "version", ...}
        """
        python = python_path or sys.executable

        if python in self._cached_packages:
            return self._cached_packages[python]

        packages = {}
        try:
            result = subprocess.run(
                [python, "-m", "pip", "list", "--format=json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                pip_list = json.loads(result.stdout)
                for pkg in pip_list:
                    packages[pkg["name"].lower()] = pkg["version"]
        except Exception:
            pass

        self._cached_packages[python] = packages
        return packages

    def is_package_installed(self, package_name: str, python_path: str = None) -> bool:
        """检查指定包是否已安装"""
        packages = self.get_installed_packages(python_path)
        return package_name.lower() in packages

    def get_package_version(self, package_name: str, python_path: str = None) -> str:
        """获取指定包的版本号"""
        packages = self.get_installed_packages(python_path)
        return packages.get(package_name.lower(), "")

    def find_all_pythons(self) -> list:
        """查找系统中所有可用的 Python 解释器"""
        pythons = []
        seen = set()

        # 当前解释器
        self._add_python(sys.executable, pythons, seen)

        # 搜索 PATH 中的 Python
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        if os.name == 'nt':
            exe_names = ["python.exe", "python3.exe"]
        else:
            exe_names = ["python", "python3", "python3.10", "python3.11", "python3.12", "python3.13"]

        for d in path_dirs:
            for exe_name in exe_names:
                full_path = os.path.join(d, exe_name)
                if os.path.isfile(full_path):
                    self._add_python(full_path, pythons, seen)

        return pythons

    def _add_python(self, python_path: str, pythons: list, seen: set):
        """添加一个 Python 解释器到列表（去重）"""
        try:
            real_path = os.path.realpath(python_path)
            if real_path in seen:
                return
            seen.add(real_path)
            version = self._get_python_version(python_path)
            pythons.append({
                "path": python_path,
                "real_path": real_path,
                "version": version,
            })
        except Exception:
            pass
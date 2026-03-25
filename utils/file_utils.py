"""
文件操作工具模块
提供文件扫描、路径处理等通用文件操作功能。
"""
import os
import glob
from typing import List, Optional

from utils.constants import PYTHON_EXTENSIONS, DATA_EXTENSIONS


def find_python_files(directory: str) -> List[str]:
    """递归查找目录下所有 Python 文件。"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        # 跳过常见的无关目录
        dirs[:] = [
            d for d in dirs
            if d not in {
                '__pycache__', '.git', '.svn', 'node_modules',
                '.venv', 'venv', 'env', '.env', '.tox',
                'dist', 'build', '.eggs', '*.egg-info',
            }
        ]
        for f in files:
            _, ext = os.path.splitext(f)
            if ext in PYTHON_EXTENSIONS:
                python_files.append(os.path.join(root, f))
    return python_files


def find_data_files(directory: str) -> List[str]:
    """递归查找目录下所有数据/资源文件。"""
    data_files = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [
            d for d in dirs
            if d not in {
                '__pycache__', '.git', '.svn', 'node_modules',
                '.venv', 'venv', 'env', '.env',
            }
        ]
        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in DATA_EXTENSIONS:
                data_files.append(os.path.join(root, f))
    return data_files


def get_relative_path(file_path: str, base_dir: str) -> str:
    """获取相对路径。"""
    return os.path.relpath(file_path, base_dir)


def ensure_dir(path: str) -> None:
    """确保目录存在，不存在则创建。"""
    os.makedirs(path, exist_ok=True)


def get_file_size_mb(file_path: str) -> float:
    """获取文件大小（MB）。"""
    if os.path.exists(file_path):
        return os.path.getsize(file_path) / (1024 * 1024)
    return 0.0


def get_dir_size_mb(dir_path: str) -> float:
    """获取目录总大小（MB）。"""
    total = 0
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                total += os.path.getsize(fp)
    return total / (1024 * 1024)


def find_icon_file(directory: str) -> Optional[str]:
    """在目录中查找图标文件。"""
    from utils.constants import ICON_EXTENSIONS
    for root, dirs, files in os.walk(directory):
        for f in files:
            _, ext = os.path.splitext(f)
            if ext.lower() in ICON_EXTENSIONS:
                return os.path.join(root, f)
    return None


def find_entry_script(directory: str) -> Optional[str]:
    """智能查找可能的入口脚本。"""
    candidates = ['main.py', 'app.py', 'run.py', 'start.py', '__main__.py']
    for name in candidates:
        path = os.path.join(directory, name)
        if os.path.isfile(path):
            return path
    return None


def detect_venv(directory: str) -> Optional[str]:
    """检测项目目录中的虚拟环境。"""
    venv_dirs = ['.venv', 'venv', 'env', '.env']
    for vdir in venv_dirs:
        venv_path = os.path.join(directory, vdir)
        # 检查是否是有效的虚拟环境
        pyvenv_cfg = os.path.join(venv_path, 'pyvenv.cfg')
        if os.path.isfile(pyvenv_cfg):
            return venv_path
    return None

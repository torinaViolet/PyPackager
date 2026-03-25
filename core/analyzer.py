"""
项目分析器模块
使用 AST 解析 Python 源文件，自动发现依赖、隐藏导入和资源引用。
"""
import ast
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional

from utils.file_utils import find_python_files


@dataclass
class AnalysisResult:
    """项目分析结果。"""
    # 发现的所有 import
    all_imports: Set[str] = field(default_factory=set)
    # 标准库模块
    stdlib_imports: Set[str] = field(default_factory=set)
    # 第三方库模块
    third_party_imports: Set[str] = field(default_factory=set)
    # 本地项目模块
    local_imports: Set[str] = field(default_factory=set)
    # 检测到的大型库
    detected_large_libs: Set[str] = field(default_factory=set)
    # 扫描的文件数
    files_scanned: int = 0
    # 检测到的资源文件引用
    resource_references: List[str] = field(default_factory=list)
    # 潜在的入口脚本
    entry_candidates: List[str] = field(default_factory=list)


class ProjectAnalyzer:
    """
    项目分析器。
    扫描项目目录，用 AST 解析所有 Python 文件的 import 语句，
    自动分类依赖为标准库/第三方/本地模块。
    """

    # 已知的大型库列表（附带子模块前缀）
    KNOWN_LARGE_LIBS = {
        'PySide6', 'PySide2', 'PyQt5', 'PyQt6',
        'torch', 'torchvision', 'torchaudio',
        'tensorflow', 'keras',
        'numpy', 'scipy', 'pandas',
        'matplotlib', 'sklearn', 'scikit-learn',
        'cv2', 'PIL', 'Pillow',
    }

    def __init__(self):
        self._stdlib_modules = self._get_stdlib_modules()

    def analyze(self, project_dir: str) -> AnalysisResult:
        """分析整个项目目录。"""
        result = AnalysisResult()

        # 查找所有 Python 文件
        py_files = find_python_files(project_dir)
        result.files_scanned = len(py_files)

        # 分析每个文件
        for py_file in py_files:
            self._analyze_file(py_file, project_dir, result)

        # 分类导入
        self._classify_imports(result, project_dir)

        # 查找入口脚本候选
        result.entry_candidates = self._find_entry_candidates(
            project_dir, py_files
        )

        return result

    def _analyze_file(self, file_path: str, project_dir: str,
                      result: AnalysisResult):
        """分析单个 Python 文件。"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
        except (IOError, OSError):
            return

        try:
            tree = ast.parse(source, filename=file_path)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            # 处理 import xxx
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level = alias.name.split('.')[0]
                    result.all_imports.add(alias.name)
                    result.all_imports.add(top_level)

            # 处理 from xxx import yyy
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # 跳过相对导入（from .xxx / from ..xxx），它们一定是项目内部模块
                    if node.level and node.level > 0:
                        continue
                    top_level = node.module.split('.')[0]
                    result.all_imports.add(node.module)
                    result.all_imports.add(top_level)

            # 检测资源文件引用 (字符串中的文件路径)
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if self._looks_like_file_path(val):
                    abs_path = os.path.join(project_dir, val)
                    if os.path.exists(abs_path):
                        result.resource_references.append(val)

    def _classify_imports(self, result: AnalysisResult, project_dir: str):
        """将导入分类为标准库/第三方/本地模块。"""
        # 递归收集项目中所有本地模块名（包括子目录中的模块）
        local_names = self._collect_local_module_names(project_dir)

        for imp in result.all_imports:
            top_level = imp.split('.')[0]

            if top_level in local_names:
                result.local_imports.add(imp)
            elif top_level in self._stdlib_modules:
                result.stdlib_imports.add(imp)
            else:
                result.third_party_imports.add(imp)

                # 检测大型库
                for lib in self.KNOWN_LARGE_LIBS:
                    if top_level == lib or top_level == lib.lower():
                        result.detected_large_libs.add(lib)

    def _collect_local_module_names(self, project_dir: str) -> Set[str]:
        """
        递归收集项目目录中所有 Python 模块和包的名称。
        包括顶层和子目录中的 .py 文件名（不含扩展名）及含 __init__.py 的包目录名。
        """
        local_names = set()
        skip_dirs = {
            '__pycache__', '.git', '.svn', 'node_modules',
            '.venv', 'venv', 'env', '.env', '.tox',
            'dist', 'build', '.eggs',
        }

        for root, dirs, files in os.walk(project_dir):
            # 跳过无关目录
            dirs[:] = [
                d for d in dirs
                if d not in skip_dirs and not d.endswith('.egg-info')
            ]

            # 添加包目录名（含 __init__.py 的目录）
            for d in dirs:
                pkg_path = os.path.join(root, d)
                if os.path.isfile(os.path.join(pkg_path, '__init__.py')):
                    local_names.add(d)

            # 添加 .py 文件的模块名
            for f in files:
                if f.endswith('.py') and f != '__init__.py':
                    local_names.add(f[:-3])

        return local_names

    def _get_stdlib_modules(self) -> Set[str]:
        """获取当前 Python 版本的标准库模块列表。"""
        stdlib = set()
        # Python 3.10+ 有 sys.stdlib_module_names
        if hasattr(sys, 'stdlib_module_names'):
            stdlib = set(sys.stdlib_module_names)
        else:
            # 回退方案：列举常见标准库
            stdlib = {
                'abc', 'argparse', 'ast', 'asyncio', 'base64',
                'collections', 'concurrent', 'configparser', 'contextlib',
                'copy', 'csv', 'ctypes', 'dataclasses', 'datetime',
                'decimal', 'difflib', 'email', 'encodings', 'enum',
                'errno', 'fcntl', 'fileinput', 'fnmatch', 'functools',
                'gc', 'getpass', 'glob', 'gzip', 'hashlib', 'heapq',
                'html', 'http', 'importlib', 'inspect', 'io',
                'itertools', 'json', 'logging', 'math', 'mimetypes',
                'multiprocessing', 'ntpath', 'operator', 'os',
                'pathlib', 'pickle', 'platform', 'pprint',
                'posixpath', 'queue', 're', 'shutil', 'signal',
                'socket', 'sqlite3', 'ssl', 'stat', 'string',
                'struct', 'subprocess', 'sys', 'tempfile', 'textwrap',
                'threading', 'time', 'tkinter', 'traceback', 'typing',
                'unittest', 'urllib', 'uuid', 'warnings', 'weakref',
                'xml', 'zipfile', 'zipimport',
            }
        return stdlib

    def _looks_like_file_path(self, value: str) -> bool:
        """判断字符串是否像文件路径。"""
        if not value or len(value) > 200 or len(value) < 3:
            return False
        # 包含路径分隔符和扩展名
        has_sep = '/' in value or '\\' in value
        has_ext = '.' in value.split('/')[-1].split('\\')[-1]
        # 排除 URL 和常见非路径字符串
        is_url = value.startswith(('http://', 'https://', 'ftp://'))
        has_space_heavy = value.count(' ') > 3
        return has_sep and has_ext and not is_url and not has_space_heavy

    def _find_entry_candidates(self, project_dir: str,
                               py_files: List[str]) -> List[str]:
        """查找可能的入口脚本。"""
        candidates = []
        # 优先级排序的入口文件名
        priority_names = [
            'main.py', 'app.py', 'run.py', 'start.py',
            '__main__.py', 'launcher.py'
        ]
        for name in priority_names:
            full = os.path.join(project_dir, name)
            if full in py_files or os.path.isfile(full):
                candidates.append(full)

        # 如果没找到，查找含 if __name__ == "__main__" 的文件
        if not candidates:
            for py_file in py_files:
                try:
                    with open(py_file, 'r', encoding='utf-8',
                              errors='ignore') as f:
                        content = f.read()
                    if 'if __name__' in content and '__main__' in content:
                        candidates.append(py_file)
                except (IOError, OSError):
                    pass

        return candidates

    def get_import_details(self, project_dir: str) -> Dict[str, List[str]]:
        """
        获取更详细的导入信息。
        返回: {"模块名": ["使用该模块的文件列表"]}
        """
        import_map = {}
        py_files = find_python_files(project_dir)

        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8',
                          errors='ignore') as f:
                    source = f.read()
                tree = ast.parse(source, filename=py_file)
            except (IOError, SyntaxError):
                continue

            for node in ast.walk(tree):
                modules = []
                if isinstance(node, ast.Import):
                    modules = [a.name for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    modules = [node.module]

                for mod in modules:
                    top = mod.split('.')[0]
                    if top not in import_map:
                        import_map[top] = []
                    rel = os.path.relpath(py_file, project_dir)
                    if rel not in import_map[top]:
                        import_map[top].append(rel)

        return import_map

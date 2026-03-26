"""
构建引擎模块
负责生成 PyInstaller / Nuitka 命令并调用进程执行构建。
"""
import os
import sys
import shutil
import tempfile
from typing import List, Optional, Tuple

from PySide6.QtCore import QObject, Signal

from core.config_manager import ConfigManager
from core.smart_excluder import SmartExcluder, ExclusionPlan
from utils.constants import (
    ENGINE_PYINSTALLER, ENGINE_NUITKA,
    MODE_ONEFILE, MODE_ONEDIR,
    BUILD_IDLE, BUILD_RUNNING, BUILD_SUCCESS, BUILD_FAILED,
)
from utils.process_runner import ProcessRunner


def _is_frozen() -> bool:
    """判断当前是否在 PyInstaller 打包后的环境中运行。"""
    return getattr(sys, 'frozen', False)


def _find_system_python() -> str:
    """
    查找系统中可用的 Python 解释器路径。
    打包后 sys.executable 指向 exe 自身，不能用来调用 PyInstaller/Nuitka，
    需要找到真正的 python.exe。
    """
    import shutil

    # 1. 优先从 PATH 中查找
    for name in ("python", "python3"):
        path = shutil.which(name)
        if path:
            # 确保找到的不是自身
            try:
                real = os.path.realpath(path)
                if real != os.path.realpath(sys.executable):
                    return path
            except Exception:
                return path

    # 2. Windows: 尝试 py launcher
    if sys.platform == "win32":
        py = shutil.which("py")
        if py:
            return py

    # 3. 常见安装路径 (Windows)
    if sys.platform == "win32":
        import glob
        patterns = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python\Python*\python.exe"),
            r"C:\Python*\python.exe",
            os.path.expandvars(r"%USERPROFILE%\AppData\Local\Programs\Python\Python*\python.exe"),
        ]
        for pattern in patterns:
            matches = sorted(glob.glob(pattern), reverse=True)
            if matches:
                return matches[0]

    return ""


class Builder(QObject):
    """
    构建引擎。
    根据配置管理器中的配置，生成打包命令并执行。
    """

    # ─── 信号 ──────────────────────────────────────────
    build_started = Signal()
    build_output = Signal(str)           # 实时构建输出
    build_error = Signal(str)            # 错误输出
    build_finished = Signal(bool, str)   # (是否成功, 消息)
    build_progress = Signal(int)         # 进度 0-100
    command_generated = Signal(str)      # 生成的命令（用于预览）

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self._config = config_manager
        self._runner = ProcessRunner(self)
        self._state = BUILD_IDLE
        self._exclusion_plan: Optional[ExclusionPlan] = None
        self._project_python: str = ""  # 项目虚拟环境的 Python 路径

        # 连接进程信号
        self._runner.output_received.connect(self._on_output)
        self._runner.error_received.connect(self._on_error)
        self._runner.process_finished.connect(self._on_finished)
        self._runner.process_started.connect(self._on_started)
        self._runner.progress_hint.connect(self.build_progress.emit)

    @property
    def state(self) -> str:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state == BUILD_RUNNING

    def set_exclusion_plan(self, plan: ExclusionPlan):
        """设置智能排除方案。"""
        self._exclusion_plan = plan

    def set_project_python(self, python_path: str):
        """
        设置项目虚拟环境的 Python 解释器路径。
        打包环境下优先使用此路径来执行构建命令。
        """
        self._project_python = python_path

    def generate_command(self) -> Tuple[str, List[str]]:
        """
        根据当前配置生成构建命令。
        返回: (程序路径, 参数列表)
        """
        engine = self._config.get("build.engine", ENGINE_PYINSTALLER)

        if engine == ENGINE_PYINSTALLER:
            return self._generate_pyinstaller_cmd()
        elif engine == ENGINE_NUITKA:
            return self._generate_nuitka_cmd()
        else:
            raise ValueError(f"不支持的打包引擎: {engine}")

    def _get_python_executable(self) -> str:
        """
        获取用于构建的 Python 解释器路径。
        优先级:
          1. 项目虚拟环境的 Python（如果已设置且有效）
          2. 开发环境下使用 sys.executable
3. 打包环境下从系统 PATH 查找 python
        """
        # 1. 优先使用项目虚拟环境的 Python
        if self._project_python and os.path.isfile(self._project_python):
            return self._project_python

        # 2. 开发环境下直接使用当前解释器
        if not _is_frozen():
            return sys.executable

        # 3. 打包环境下查找系统 Python
        python = _find_system_python()
        if not python:
            raise ValueError(
                "未找到系统 Python 解释器!\n"
                "PyPackager 打包运行时需要系统安装的 Python 来执行构建。\n"
                "请确保 Python 已安装并添加到 PATH 环境变量中。"
            )
        return python

    def _generate_pyinstaller_cmd(self) -> Tuple[str, List[str]]:
        """生成 PyInstaller 命令。"""
        program = self._get_python_executable()
        args = ["-m", "PyInstaller"]

        script = self._config.get("entry.script", "")
        if not script:
            raise ValueError("未设置入口脚本")

        # 打包模式
        mode = self._config.get("build.mode", MODE_ONEFILE)
        if mode == MODE_ONEFILE:
            args.append("--onefile")
        else:
            args.append("--onedir")

        # 窗口模式
        console = self._config.get("build.console", False)
        if not console:
            args.append("--noconsole")

        # 图标（自动转换非 .ico 格式）
        icon = self._config.get("entry.icon", "")
        if icon and os.path.isfile(icon):
            icon = self._ensure_ico(icon)
            if icon:
                args.extend(["--icon", icon])

        # 名称
        name = self._config.get("project.name", "")
        if name:
            args.extend(["--name", name])

        # 输出目录
        output_dir = self._config.get("entry.output_dir", "./dist")
        args.extend(["--distpath", output_dir])

        # UPX 压缩
        upx = self._config.get("build.upx", False)
        if upx:
            upx_path = self._config.get("build.upx_path", "")
            if upx_path:
                args.extend(["--upx-dir", upx_path])
        else:
            args.append("--noupx")

        # Strip
        if self._config.get("build.strip", False):
            args.append("--strip")

        # Clean
        if self._config.get("build.clean", True):
            args.append("--clean")

        # UAC 管理员权限
        if self._config.get("build.uac_admin", False):
            args.append("--uac-admin")

        # 版本信息
        version = self._config.get("project.version", "")
        if version:
            # PyInstaller 不直接支持版本号参数，需要 version file
            pass

        # ─── 依赖相关 ─────────────────────────────────
        # PyInstaller 6.x / Python 3.12+ 已自动处理的模块
        auto_excluded = {"distutils"}
        seen_excludes = set()
        seen_imports = set()

        # 隐藏导入
        hidden_imports = self._config.get(
            "dependencies.hidden_imports", []
        )
        for imp in hidden_imports:
            if imp not in seen_imports:
                args.extend(["--hidden-import", imp])
                seen_imports.add(imp)

        # 手动排除
        excludes = self._config.get("dependencies.excludes", [])
        for exc in excludes:
            if exc not in seen_excludes and exc not in auto_excluded:
                args.extend(["--exclude-module", exc])
                seen_excludes.add(exc)

        # 智能排除方案（内部已去重，但需与手动排除合并去重）
        if self._exclusion_plan:
            excluder = SmartExcluder()
            smart_args = excluder.plan_to_pyinstaller_args(
                self._exclusion_plan
            )
            # 过滤掉已添加的排除项
            i = 0
            while i < len(smart_args):
                if smart_args[i] == "--exclude-module" and i + 1 < len(smart_args):
                    mod = smart_args[i + 1]
                    if mod not in seen_excludes:
                        args.extend(["--exclude-module", mod])
                        seen_excludes.add(mod)
                    i += 2
                elif smart_args[i] == "--hidden-import" and i + 1 < len(smart_args):
                    mod = smart_args[i + 1]
                    if mod not in seen_imports:
                        args.extend(["--hidden-import", mod])
                        seen_imports.add(mod)
                    i += 2
                else:
                    args.append(smart_args[i])
                    i += 1

        # ─── 资源文件 ─────────────────────────────────
        data_files = self._config.get("resources.data_files", [])
        for df in data_files:
            src = df.get("src", "")
            dst = df.get("dst", ".")
            if src:
                sep = ";" if sys.platform == "win32" else ":"
                args.extend(["--add-data", f"{src}{sep}{dst}"])

        # 额外参数
        extra = self._config.get("build.extra_args", "")
        if extra:
            args.extend(extra.split())

        # 入口脚本（必须是最后一个参数）
        args.append(script)

        return program, args

    def _generate_nuitka_cmd(self) -> Tuple[str, List[str]]:
        """生成 Nuitka 命令。"""
        program = self._get_python_executable()
        args = ["-m", "nuitka"]

        script = self._config.get("entry.script", "")
        if not script:
            raise ValueError("未设置入口脚本")

        mode = self._config.get("build.mode", MODE_ONEFILE)
        if mode == MODE_ONEFILE:
            args.append("--onefile")
        else:
            args.append("--standalone")

        console = self._config.get("build.console", False)
        if not console:
            args.append("--disable-console")

        icon = self._config.get("entry.icon", "")
        if icon and os.path.isfile(icon):
            icon = self._ensure_ico(icon)
            if icon:
                args.extend([f"--windows-icon-from-ico={icon}"])

        output_dir = self._config.get("entry.output_dir", "./dist")
        args.extend([f"--output-dir={output_dir}"])

        name = self._config.get("project.name", "")
        if name:
            args.extend([f"--output-filename={name}"])

        args.append("--assume-yes-for-downloads")
        args.append("--remove-output")

        # 额外参数
        extra = self._config.get("build.extra_args", "")
        if extra:
            args.extend(extra.split())

        args.append(script)
        return program, args

    def get_command_preview(self) -> str:
        """获取构建命令的预览字符串。"""
        try:
            program, args = self.generate_command()
            cmd_parts = [os.path.basename(program)] + args
            return " ".join(cmd_parts)
        except ValueError as e:
            return f"[错误] {e}"

    def start_build(self):
        """开始构建。"""
        if self._state == BUILD_RUNNING:
            self.build_error.emit("构建正在进行中，请等待完成")
            return

        try:
            program, args = self.generate_command()
        except ValueError as e:
            self.build_error.emit(f"配置错误: {e}")
            self.build_finished.emit(False, str(e))
            return

        # 发送命令预览
        cmd_preview = " ".join(
            [os.path.basename(program)] + args
        )
        self.command_generated.emit(cmd_preview)

        # 获取工作目录
        script = self._config.get("entry.script", "")
        working_dir = os.path.dirname(os.path.abspath(script)) if script else None

        self._state = BUILD_RUNNING
        self._runner.start(program, args, working_dir)

    def cancel_build(self):
        """取消构建。"""
        if self._state == BUILD_RUNNING:
            self._runner.stop()
            self._state = BUILD_IDLE
            self.build_finished.emit(False, "构建已取消")

    def _ensure_ico(self, icon_path: str) -> Optional[str]:
        """
        确保图标为 .ico 格式。
        如果是 .png / .jpg / .bmp 等格式，则使用 Pillow 自动转换。
        返回 .ico 文件路径，失败返回 None。
        """
        ext = os.path.splitext(icon_path)[1].lower()
        if ext == ".ico":
            return icon_path

        # 非 .ico 格式，尝试用 Pillow 转换
        try:
            from PIL import Image
        except ImportError:
            self.build_error.emit(
                "图标格式不是 .ico，且未安装 Pillow 库，无法自动转换。\n"
                "请安装: pip install Pillow，或手动转换为 .ico 格式。"
            )
            return None

        try:
            # 在图标同目录生成 .ico 文件
            ico_path = os.path.splitext(icon_path)[0] + ".ico"
            img = Image.open(icon_path)

            # 生成多尺寸图标以保证兼容性
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            # 只保留不超过原图尺寸的尺寸
            valid_sizes = [s for s in sizes if s[0] <= img.width and s[1] <= img.height]
            if not valid_sizes:
                valid_sizes = [(min(img.width, 256), min(img.height, 256))]

            img.save(ico_path, format="ICO", sizes=valid_sizes)
            self.build_output.emit(
                f"📎 已自动将图标转换为 .ico 格式: {ico_path}\n"
            )
            return ico_path
        except Exception as e:
            self.build_error.emit(f"图标转换失败: {e}")
            return None

    def _on_output(self, text: str):
        self.build_output.emit(text)

    def _on_error(self, text: str):
        self.build_error.emit(text)

    def _on_started(self):
        self.build_started.emit()
        self.build_output.emit("🚀 构建已启动...\n")

    def _on_finished(self, exit_code: int, status: str):
        if exit_code == 0:
            self._state = BUILD_SUCCESS
            output_dir = self._config.get("entry.output_dir", "./dist")
            self.build_output.emit(
                f"\n✅ 构建成功！输出目录: {output_dir}\n"
            )
            self.build_finished.emit(True, f"构建成功 ({status})")
            self.build_progress.emit(100)
        else:
            self._state = BUILD_FAILED
            self.build_error.emit(
                f"\n❌ 构建失败 (退出码: {exit_code}, {status})\n"
            )
            self.build_finished.emit(
                False, f"构建失败 (退出码: {exit_code})"
            )

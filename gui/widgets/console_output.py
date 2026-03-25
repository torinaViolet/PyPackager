"""
控制台组件
包含三个标签页：构建日志、系统终端、Python 交互式控制台。
"""
import os
import sys
import io
import locale
import traceback
import contextlib
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QProgressBar, QTabWidget,
    QLineEdit, QPlainTextEdit,
)
from PySide6.QtCore import Slot, Signal, Qt, QProcess, QTimer, QThread, QObject
from PySide6.QtGui import QTextCharFormat, QColor, QFont, QKeyEvent


# ─── 共享的等宽字体 ────────────────────────────────────
def _mono_font(size: int = 11) -> QFont:
    font = QFont("Cascadia Code", size)
    font.setStyleHint(QFont.StyleHint.Monospace)
    return font


# ═══════════════════════════════════════════════════════
#  终端命令输入框（单行, Enter 提交）
# ═══════════════════════════════════════════════════════

class CommandInput(QLineEdit):
    """支持 ↑↓ 历史记录的命令输入框。"""

    command_submitted = Signal(str)
    interrupt_requested = Signal()  # Ctrl+C 中断

    def __init__(self, placeholder: str = "输入命令...", parent=None):
        super().__init__(parent)
        self._history: list[str] = []
        self._history_index: int = -1
        self._current_input: str = ""
        self.setPlaceholderText(placeholder)
        self.setFont(_mono_font())
        self.returnPressed.connect(self._on_submit)

    def _on_submit(self):
        text = self.text()
        if text.strip():
            self._history.append(text)
        self._history_index = len(self._history)
        self._current_input = ""
        self.command_submitted.emit(text)
        self.clear()

    def keyPressEvent(self, event):
        # Ctrl+C: 无选中文本时发送中断信号
        if (event.key() == Qt.Key.Key_C
                and event.modifiers() & Qt.KeyboardModifier.ControlModifier
                and not self.hasSelectedText()):
            self.interrupt_requested.emit()
            return
        if event.key() == Qt.Key.Key_Up:
            if self._history:
                if self._history_index == len(self._history):
                    self._current_input = self.text()
                self._history_index = max(0, self._history_index - 1)
                self.setText(self._history[self._history_index])
            return
        elif event.key() == Qt.Key.Key_Down:
            if self._history:
                self._history_index = min(len(self._history), self._history_index + 1)
                if self._history_index == len(self._history):
                    self.setText(self._current_input)
                else:
                    self.setText(self._history[self._history_index])
            return
        super().keyPressEvent(event)


# ═══════════════════════════════════════════════════════
#  Python 代码输入框（多行, Enter 换行, Ctrl+Enter 提交）
# ═══════════════════════════════════════════════════════

class PythonCodeInput(QPlainTextEdit):
    """多行 Python 代码输入框。Enter 换行，Ctrl+Enter 执行。"""

    code_submitted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history: list[str] = []
        self._history_index: int = -1
        self._current_input: str = ""
        self.setFont(_mono_font())
        self.setPlaceholderText("输入 Python 代码... (Ctrl+Enter 执行)")
        self.setMaximumHeight(100)
        self.setTabStopDistance(self.fontMetrics().horizontalAdvance(' ') * 4)
        self.document().contentsChanged.connect(self._adjust_height)
        self._adjust_height()

    def _adjust_height(self):
        doc_height = self.document().size().toSize().height()
        margins = self.contentsMargins()
        new_height = min(max(doc_height + margins.top() + margins.bottom() + 10, 32), 100)
        self.setFixedHeight(int(new_height))

    def keyPressEvent(self, event: QKeyEvent):
        # Ctrl+Enter → 提交
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._submit()
                return
            # 普通 Enter → 换行
            super().keyPressEvent(event)
            return

        # ↑↓ 历史（仅在单行时生效）
        if event.key() == Qt.Key.Key_Up and self.document().lineCount() <= 1:
            if self._history:
                if self._history_index == len(self._history):
                    self._current_input = self.toPlainText()
                self._history_index = max(0, self._history_index - 1)
                self.setPlainText(self._history[self._history_index])
                cursor = self.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.setTextCursor(cursor)
            return

        if event.key() == Qt.Key.Key_Down and self.document().lineCount() <= 1:
            if self._history:
                self._history_index = min(len(self._history), self._history_index + 1)
                if self._history_index == len(self._history):
                    self.setPlainText(self._current_input)
                else:
                    self.setPlainText(self._history[self._history_index])
                cursor = self.textCursor()
                cursor.movePosition(cursor.MoveOperation.End)
                self.setTextCursor(cursor)
            return

        super().keyPressEvent(event)

    def _submit(self):
        code = self.toPlainText()
        if code.strip():
            self._history.append(code)
        self._history_index = len(self._history)
        self._current_input = ""
        self.code_submitted.emit(code)
        self.clear()


# ═══════════════════════════════════════════════════════
#  Python exec() Worker（子线程执行代码）
# ═══════════════════════════════════════════════════════

class PythonExecWorker(QObject):
    """在子线程中通过 exec() 执行 Python 代码。"""

    output_ready = Signal(str)
    error_ready = Signal(str)
    finished = Signal()

    def __init__(self, namespace: dict, parent=None):
        super().__init__(parent)
        self._namespace = namespace

    @Slot(str)
    def execute(self, code: str):
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_capture), \
                    contextlib.redirect_stderr(stderr_capture):
                # 先尝试 eval（表达式），失败则 exec（语句）
                try:
                    result = eval(compile(code, "<console>", "eval"), self._namespace)
                    if result is not None:
                        print(repr(result))
                except SyntaxError:
                    exec(compile(code, "<console>", "exec"), self._namespace)
        except Exception:
            stderr_capture.write(traceback.format_exc())

        stdout_text = stdout_capture.getvalue()
        stderr_text = stderr_capture.getvalue()
        if stdout_text:
            self.output_ready.emit(stdout_text)
        if stderr_text:
            self.error_ready.emit(stderr_text)
        self.finished.emit()


# ═══════════════════════════════════════════════════════
#  构建日志标签页
# ═══════════════════════════════════════════════════════

class BuildLogTab(QWidget):
    """构建日志 — 保留原有全部功能。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # 日志输出区域
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(_mono_font())
        layout.addWidget(self.text_edit)

    # ── 公开方法 ──

    def append_output(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        for line in text.strip().splitlines():
            color = self._detect_color(line)
            self._append_colored(f"[{ts}] {line}", color)

    def append_error(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        for line in text.strip().splitlines():
            self._append_colored(f"[{ts}] ⚠ {line}", "#f38ba8")

    def append_info(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self._append_colored(f"[{ts}] ℹ {text}", "#89b4fa")

    def append_success(self, text: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self._append_colored(f"[{ts}] ✅ {text}", "#a6e3a1")

    def set_progress(self, value: int):
        self.progress_bar.show()
        self.progress_bar.setValue(min(value, 100))
        if value >= 100:
            self.progress_bar.setFormat("完成!")

    def show_progress(self):
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")

    def hide_progress(self):
        self.progress_bar.hide()

    def clear(self):
        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

    # ── 内部方法 ──

    def _append_colored(self, text: str, color: str):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text + "\n", fmt)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def _detect_color(self, line: str) -> str:
        lower = line.lower()
        if any(w in lower for w in ['error', 'failed', '❌', 'traceback']):
            return "#f38ba8"
        elif any(w in lower for w in ['warning', 'warn', '⚠']):
            return "#f9e2af"
        elif any(w in lower for w in ['success', '✅', 'completed', '完成']):
            return "#a6e3a1"
        elif any(w in lower for w in ['info', 'ℹ', '🚀', '📦']):
            return "#89b4fa"
        return "#cdd6f4"


# ═══════════════════════════════════════════════════════
#  系统终端标签页
# ═══════════════════════════════════════════════════════

class TerminalTab(QWidget):
    """
    系统终端 — 每条命令独立执行。
    不再保持长驻 shell 进程，避免交互式程序（python/node 等）卡死。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process: QProcess | None = None
        self._working_dir: str = os.path.expanduser("~")
        self._venv_path: str = ""  # 虚拟环境路径
        self._encoding: str = self._detect_system_encoding()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # 顶部工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        self.status_label = QLabel("⚪ 就绪")
        self.status_label.setStyleSheet("font-size: 12px; color: #888;")
        toolbar.addWidget(self.status_label)

        self.cwd_label = QLabel("")
        self.cwd_label.setStyleSheet("font-size: 11px; color: #888;")
        toolbar.addWidget(self.cwd_label)

        toolbar.addStretch()

        self.btn_stop = QPushButton("⏹ 停止")
        self.btn_stop.setToolTip("终止当前命令 (Ctrl+C)")
        self.btn_stop.clicked.connect(self._interrupt)
        self.btn_stop.setEnabled(False)
        toolbar.addWidget(self.btn_stop)

        self.btn_clear = QPushButton("🗑️ 清空")
        self.btn_clear.clicked.connect(self._clear_output)
        toolbar.addWidget(self.btn_clear)

        layout.addLayout(toolbar)

        # 输出区域
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(_mono_font())
        layout.addWidget(self.output)

        # 输入区域
        input_row = QHBoxLayout()
        input_row.setSpacing(4)

        self.prompt_label = QLabel(self._make_prompt())
        self.prompt_label.setFont(_mono_font())
        self.prompt_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        input_row.addWidget(self.prompt_label)

        self.cmd_input = CommandInput("输入系统命令...")
        self.cmd_input.command_submitted.connect(self._on_command)
        self.cmd_input.interrupt_requested.connect(self._interrupt)
        input_row.addWidget(self.cmd_input)

        layout.addLayout(input_row)
        self._update_cwd_label()

    # ── 公开方法 ──

    def set_working_dir(self, path: str):
        """设置工作目录。"""
        if os.path.isdir(path):
            self._working_dir = path
            self.prompt_label.setText(self._make_prompt())
            self._update_cwd_label()

    def set_venv_path(self, venv_path: str):
        """设置虚拟环境路径，终端命令将自动使用该环境的 pip/python。"""
        self._venv_path = venv_path
        if venv_path:
            self._append_system(f"🟩 已激活虚拟环境: {venv_path}\n")

    def stop(self):
        """终止当前进程。"""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()
            self._process.waitForFinished(2000)
        self._process = None
        self.btn_stop.setEnabled(False)
        self.status_label.setText("⚪ 就绪")
        self.status_label.setStyleSheet("font-size: 12px; color: #888;")

    # ── 内部方法 ──

    def _on_command(self, text: str):
        """执行一条命令。"""
        stripped = text.strip()
        if not stripped:
            return

        # 如果当前有进程在运行，拒绝新命令
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self._append_system("⚠ 上一个命令仍在运行，请等待完成或点击 停止\n")
            return

        self._append_input(f"{self._make_prompt()} {stripped}")

        # 拦截 cd 命令 — 本地处理
        if stripped.lower() == "cd" or stripped.lower().startswith("cd "):
            self._handle_cd(stripped)
            return

        # 拦截 cls/clear — 清屏
        if stripped.lower() in ("cls", "clear"):
            self._clear_output()
            return

        # 拦截可能导致卡死的交互式程序
        first_word = stripped.split()[0].lower() if stripped.split() else ""
        interactive_cmds = {'python', 'python3', 'py', 'node', 'irb', 'lua',
                           'powershell', 'pwsh', 'bash', 'sh', 'zsh', 'cmd'}
        # 如果只输入了程序名（无参数），提示用户
        parts = stripped.split()
        if first_word in interactive_cmds and len(parts) == 1:
            self._append_system(
                f"⚠ 交互式程序 '{first_word}' 不支持在此终端中运行。\n"
                f"   请使用 🐍Python 标签页，或者添加参数运行脚本 (如: python script.py)\n"
            )
            return

        # 启动子进程执行命令
        self._process = QProcess(self)
        self._process.setWorkingDirectory(self._working_dir)

        from PySide6.QtCore import QProcessEnvironment
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")

        # 如果有虚拟环境，将其 Scripts/bin 目录加到 PATH 最前面
        if self._venv_path:
            if sys.platform == 'win32':
                venv_bin = os.path.join(self._venv_path, "Scripts")
            else:
                venv_bin = os.path.join(self._venv_path, "bin")
            if os.path.isdir(venv_bin):
                current_path = env.value("PATH", "")
                env.insert("PATH", venv_bin + os.pathsep + current_path)
                env.insert("VIRTUAL_ENV", self._venv_path)

        self._process.setProcessEnvironment(env)

        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)

        if sys.platform == 'win32':
            # 整条命令作为一个字符串传给 /C，确保 >、&& 等 shell 操作符被正确解析
            full_cmd = f"chcp 65001 > nul && {stripped}"
            self._process.start("cmd.exe", ["/C", full_cmd])
        else:
            shell = os.environ.get("SHELL", "/bin/bash")
            self._process.start(shell, ["-c", stripped])

        self.btn_stop.setEnabled(True)
        self.status_label.setText("🟢 运行中")
        self.status_label.setStyleSheet("font-size: 12px; color: #a6e3a1;")

    def _handle_cd(self, text: str):
        """处理 cd 命令。"""
        parts = text.strip().split(maxsplit=1)
        if len(parts) == 1:
            # 只输入 cd: 显示当前目录 (Windows 行为) 或切换到 HOME
            if sys.platform == 'win32':
                self._append_output(self._working_dir + "\n")
            else:
                self._working_dir = os.path.expanduser("~")
                self.prompt_label.setText(self._make_prompt())
                self._update_cwd_label()
            return

        target = parts[1].strip().strip('"').strip("'")
        # 处理 ~ 家目录
        if target.startswith("~"):
            target = os.path.expanduser(target)

        new_dir = os.path.normpath(os.path.join(self._working_dir, target))
        if os.path.isdir(new_dir):
            self._working_dir = new_dir
            self.prompt_label.setText(self._make_prompt())
            self._update_cwd_label()
        else:
            self._append_error(f"目录不存在: {new_dir}\n")

    def _interrupt(self):
        """Ctrl+C 中断当前进程。"""
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            self._process.kill()
            self._append_system("^C\n")

    @Slot()
    def _on_stdout(self):
        if self._process:
            data = self._process.readAllStandardOutput()
            text = bytes(data).decode(self._encoding, errors="replace")
            if text.strip():
                self._append_output(text)

    @Slot()
    def _on_stderr(self):
        if self._process:
            data = self._process.readAllStandardError()
            text = bytes(data).decode(self._encoding, errors="replace")
            if text.strip():
                self._append_error(text)

    @Slot(int, QProcess.ExitStatus)
    def _on_finished(self, exit_code, status):
        self.btn_stop.setEnabled(False)
        self.status_label.setText("⚪ 就绪")
        self.status_label.setStyleSheet("font-size: 12px; color: #888;")
        if exit_code != 0:
            self._append_system(f"--- 退出代码: {exit_code} ---\n")

    def _detect_system_encoding(self) -> str:
        """检测系统控制台编码。"""
        if sys.platform == 'win32':
            # cmd.exe /C chcp 65001 后输出应为 UTF-8
            # 但也要兜底处理其他代码页
            return 'utf-8'
        return locale.getpreferredencoding(False) or 'utf-8'

    def _make_prompt(self) -> str:
        try:
            short = os.path.basename(self._working_dir) or self._working_dir
        except Exception:
            short = "~"
        symbol = ">" if sys.platform == "win32" else "$"
        return f"{short} {symbol}"

    def _update_cwd_label(self):
        display = self._working_dir
        if len(display) > 50:
            display = "..." + display[-47:]
        self.cwd_label.setText(f"📂 {display}")

    def _append_output(self, text: str):
        self._append_colored(text, "#cdd6f4")

    def _append_error(self, text: str):
        self._append_colored(text, "#f38ba8")

    def _append_input(self, text: str):
        self._append_colored(text + "\n", "#a6e3a1")

    def _append_system(self, text: str):
        self._append_colored(text, "#89b4fa")

    def _append_colored(self, text: str, color: str):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text, fmt)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def _clear_output(self):
        self.output.clear()


# ═══════════════════════════════════════════════════════
#  Python 交互式控制台标签页
# ═══════════════════════════════════════════════════════

class PythonConsoleTab(QWidget):
    """
    Python 交互式控制台。

    使用内置 exec() 执行代码，不依赖外部 Python 解释器进程。
    - 开发环境 & 打包后都能正常工作
    - 若项目有虚拟环境，使用虚拟环境的 Python 进程执行
    - 输入框: Enter 换行，Ctrl+Enter 执行
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._python_path: str = ""  # 虚拟环境的 Python 路径
        self._use_external: bool = False  # 是否使用外部进程
        self._process: QProcess | None = None  # 外部进程模式
        self._working_dir: str = os.path.expanduser("~")
        # 内置 exec 模式的命名空间
        self._namespace: dict = {"__name__": "__console__", "__builtins__": __builtins__}
        # 子线程执行
        self._worker_thread: QThread | None = None
        self._worker: PythonExecWorker | None = None
        self._is_busy: bool = False
        self._setup_ui()
        self._update_mode_info()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # 顶部工具栏
        toolbar = QHBoxLayout()
        toolbar.setSpacing(6)

        self.status_label = QLabel("🟢 就绪")
        self.status_label.setStyleSheet("font-size: 12px; color: #a6e3a1;")
        toolbar.addWidget(self.status_label)

        self.python_info = QLabel("")
        self.python_info.setStyleSheet("font-size: 11px; color: #888;")
        toolbar.addWidget(self.python_info)

        toolbar.addStretch()

        self.btn_restart = QPushButton("🔄 重置")
        self.btn_restart.setToolTip("重置命名空间 / 重启解释器")
        self.btn_restart.clicked.connect(self.restart)
        toolbar.addWidget(self.btn_restart)

        self.btn_clear = QPushButton("🗑️ 清空")
        self.btn_clear.clicked.connect(self._clear_output)
        toolbar.addWidget(self.btn_clear)

        layout.addLayout(toolbar)

        # 输出区域
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(_mono_font())
        layout.addWidget(self.output)

        # 输入区域
        input_row = QHBoxLayout()
        input_row.setSpacing(4)

        self.prompt_label = QLabel(">>>")
        self.prompt_label.setFont(_mono_font())
        self.prompt_label.setStyleSheet("color: #f9e2af; font-weight: bold;")
        input_row.addWidget(self.prompt_label, 0, Qt.AlignmentFlag.AlignTop)

        self.code_input = PythonCodeInput()
        self.code_input.code_submitted.connect(self._on_code_submit)
        input_row.addWidget(self.code_input)

        layout.addLayout(input_row)

    # ── 公开方法 ──

    def set_python_path(self, python_path: str):
        """设置虚拟环境的 Python 解释器路径。"""
        if python_path and os.path.isfile(python_path):
            self._python_path = python_path
            self._use_external = True
            self._update_mode_info()
            # 如果进程正在运行，重启
            if self._process and self._process.state() == QProcess.ProcessState.Running:
                self.restart()

    def set_working_dir(self, path: str):
        """设置工作目录。"""
        if os.path.isdir(path):
            self._working_dir = path
            # 内置模式：更新 os.chdir 到 namespace
            if not self._use_external:
                try:
                    self._namespace['__working_dir__'] = path
                except Exception:
                    pass

    def stop(self):
        """停止外部 Python 进程（如有）。"""
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.kill()
            self._process.waitForFinished(2000)
        self._process = None
        # 停止 worker 线程
        if self._worker_thread and self._worker_thread.isRunning():
            self._worker_thread.quit()
            self._worker_thread.wait(2000)

    def restart(self):
        """重置命名空间 / 重启外部解释器。"""
        self.stop()
        if self._use_external:
            self._append_system("--- Python 解释器已重启 ---\n")
            self._start_external()
        else:
            self._namespace = {"__name__": "__console__", "__builtins__": __builtins__}
            self._append_system("--- 命名空间已重置 ---\n")
        self.status_label.setText("🟢 就绪")
        self.status_label.setStyleSheet("font-size: 12px; color: #a6e3a1;")

    # ── 代码执行 ──

    def _on_code_submit(self, code: str):
        """用户提交代码。"""
        if not code.strip():
            return

        # 显示输入
        lines = code.split("\n")
        display = "\n".join(
            (">>> " if i == 0 else "... ") + line
            for i, line in enumerate(lines)
        )
        self._append_input(display)

        if self._use_external:
            self._execute_external(code)
        else:
            self._execute_builtin(code)

    def _execute_builtin(self, code: str):
        """使用内置 exec() 在子线程中执行代码。"""
        if self._is_busy:
            self._append_system("⚠ 上一段代码仍在执行...\n")
            return

        self._is_busy = True
        self.status_label.setText("⏳ 执行中")
        self.status_label.setStyleSheet("font-size: 12px; color: #f9e2af;")

        # 创建 worker 线程
        self._worker_thread = QThread()
        self._worker = PythonExecWorker(self._namespace)
        self._worker.moveToThread(self._worker_thread)

        self._worker.output_ready.connect(self._on_exec_output)
        self._worker.error_ready.connect(self._on_exec_error)
        self._worker.finished.connect(self._on_exec_finished)

        # 用 lambda 传递代码
        self._worker_thread.started.connect(lambda: self._worker.execute(code))
        self._worker_thread.start()

    @Slot(str)
    def _on_exec_output(self, text: str):
        self._append_output(text)

    @Slot(str)
    def _on_exec_error(self, text: str):
        self._append_error(text)

    @Slot()
    def _on_exec_finished(self):
        self._is_busy = False
        self.status_label.setText("🟢 就绪")
        self.status_label.setStyleSheet("font-size: 12px; color: #a6e3a1;")
        if self._worker_thread:
            self._worker_thread.quit()
            self._worker_thread.wait(1000)

    # ── 外部进程模式（虚拟环境）──

    def _start_external(self):
        """启动外部 Python 解释器进程。"""
        self.stop()

        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.setWorkingDirectory(self._working_dir)

        from PySide6.QtCore import QProcessEnvironment
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")
        env.insert("PYTHONUNBUFFERED", "1")
        self._process.setProcessEnvironment(env)

        self._process.readyReadStandardOutput.connect(self._on_proc_stdout)
        self._process.readyReadStandardError.connect(self._on_proc_stderr)
        self._process.finished.connect(self._on_proc_finished)

        self._process.start(self._python_path, ["-i", "-u", "-q"])

    def _execute_external(self, code: str):
        """通过外部进程执行代码。"""
        if self._process is None or self._process.state() == QProcess.ProcessState.NotRunning:
            self._start_external()
            QTimer.singleShot(500, lambda: self._write_to_proc(code))
        else:
            self._write_to_proc(code)

    def _write_to_proc(self, code: str):
        if self._process and self._process.state() == QProcess.ProcessState.Running:
            # 逐行发送，确保多行代码正确执行
            self._process.write((code + "\n").encode("utf-8"))

    @Slot()
    def _on_proc_stdout(self):
        if self._process:
            data = self._process.readAllStandardOutput()
            text = bytes(data).decode("utf-8", errors="replace")
            cleaned = self._filter_prompts(text)
            if cleaned.strip():
                self._append_output(cleaned)

    @Slot()
    def _on_proc_stderr(self):
        if self._process:
            data = self._process.readAllStandardError()
            text = bytes(data).decode("utf-8", errors="replace")
            cleaned = self._filter_prompts(text)
            if cleaned.strip():
                if "Traceback" in text or "Error" in text:
                    self._append_error(cleaned)
                else:
                    self._append_output(cleaned)

    @Slot(int, QProcess.ExitStatus)
    def _on_proc_finished(self, exit_code, status):
        self._append_system(f"\n--- Python 进程已退出 (代码: {exit_code}) ---\n")
        self.status_label.setText("⚪ 已停止")
        self.status_label.setStyleSheet("font-size: 12px; color: #888;")

    def _filter_prompts(self, text: str) -> str:
        """过滤 Python 交互提示符。"""
        lines = text.split('\n')
        filtered = []
        for line in lines:
            stripped = line.strip()
            if stripped in ('>>>', '...'):
                continue
            if line.startswith('>>> '):
                line = line[4:]
            elif line.startswith('... '):
                line = line[4:]
            filtered.append(line)
        return '\n'.join(filtered)

    # ── 显示 ──

    def _update_mode_info(self):
        """更新模式信息显示。"""
        if self._use_external:
            path = self._python_path
            is_venv = any(
                name in path
                for name in ['venv', '.venv', 'env', '.env', 'virtualenv']
            )
            tag = "🟩 虚拟环境" if is_venv else "🔵 外部"
            display_path = path
            if len(display_path) > 50:
                display_path = "..." + display_path[-47:]
            self.python_info.setText(f"{tag}  {display_path}")
        else:
            ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            self.python_info.setText(f"🐍 内置解释器  Python {ver}")

    def _append_output(self, text: str):
        self._append_colored(text, "#cdd6f4")

    def _append_error(self, text: str):
        self._append_colored(text, "#f38ba8")

    def _append_input(self, text: str):
        self._append_colored(text + "\n", "#f9e2af")

    def _append_system(self, text: str):
        self._append_colored(text, "#89b4fa")

    def _append_colored(self, text: str, color: str):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text, fmt)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def _clear_output(self):
        self.output.clear()


# ═══════════════════════════════════════════════════════
#  主控制台组件（三标签页）
# ═══════════════════════════════════════════════════════

class ConsoleOutput(QWidget):
    """
    控制台组件 — 整合构建日志、系统终端和 Python 控制台。

    对外保持原有 API 完全兼容（append_output / append_error /
    set_progress 等方法仍然作用于「构建日志」标签页）。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部标题栏
        header = QHBoxLayout()
        header.setContentsMargins(8, 4, 8, 0)
        title = QLabel("📟 控制台")
        title.setProperty("heading", "true")
        header.addWidget(title)
        header.addStretch()

        self.btn_clear = QPushButton("🗑️ 清空当前")
        self.btn_clear.setToolTip("清空当前标签页内容")
        self.btn_clear.clicked.connect(self._on_clear_current)
        header.addWidget(self.btn_clear)

        layout.addLayout(header)

        # 标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)

        # 1) 构建日志
        self._build_log = BuildLogTab()
        self.tab_widget.addTab(self._build_log, "📟 构建日志")

        # 2) 系统终端
        self._terminal = TerminalTab()
        self.tab_widget.addTab(self._terminal, "💻 终端")

        # 3) Python 控制台
        self._python = PythonConsoleTab()
        self.tab_widget.addTab(self._python, "🐍 Python")

        layout.addWidget(self.tab_widget)

    # ═══════════════════════════════════════════════════
    #  向外暴露的配置方法
    # ═══════════════════════════════════════════════════

    def set_project_dir(self, path: str):
        """打开项目后调用：同时更新终端和 Python 的工作目录。"""
        self._terminal.set_working_dir(path)
        self._python.set_working_dir(path)

    def set_python_path(self, python_path: str):
        """设置 Python 控制台使用的解释器路径。"""
        self._python.set_python_path(python_path)

    def set_venv_path(self, venv_path: str):
        """设置虚拟环境路径，终端将自动激活该环境。"""
        self._terminal.set_venv_path(venv_path)

    # ═══════════════════════════════════════════════════
    #  向后兼容：构建日志 API（与旧版完全一致）
    # ═══════════════════════════════════════════════════

    @Slot(str)
    def append_output(self, text: str):
        self._build_log.append_output(text)

    @Slot(str)
    def append_error(self, text: str):
        self._build_log.append_error(text)

    @Slot(str)
    def append_info(self, text: str):
        self._build_log.append_info(text)

    @Slot(str)
    def append_success(self, text: str):
        self._build_log.append_success(text)

    @Slot(int)
    def set_progress(self, value: int):
        self._build_log.set_progress(value)

    def show_progress(self):
        self._build_log.show_progress()

    def hide_progress(self):
        self._build_log.hide_progress()

    @Slot()
    def clear(self):
        """清空构建日志（保持向后兼容）。"""
        self._build_log.clear()

    # ═══════════════════════════════════════════════════
    #  内部
    # ═══════════════════════════════════════════════════

    def _on_clear_current(self):
        """清空当前激活的标签页。"""
        idx = self.tab_widget.currentIndex()
        if idx == 0:
            self._build_log.clear()
        elif idx == 1:
            self._terminal._clear_output()
        elif idx == 2:
            self._python._clear_output()

    def cleanup(self):
        """应用退出时调用，确保子进程被清理。"""
        self._terminal.stop()
        self._python.stop()

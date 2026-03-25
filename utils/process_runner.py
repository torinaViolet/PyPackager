"""
子进程管理模块
使用 QProcess 进行异步子进程管理，完美集成 Qt 信号槽机制。
"""
from PySide6.QtCore import QObject, QProcess, Signal, Slot


class ProcessRunner(QObject):
    """
    异步进程运行器。
    使用 Qt 的 QProcess 来运行外部命令，
    并通过信号实时发送输出和状态变化。
    """

    # ─── 信号定义 ──────────────────────────────────────
    output_received = Signal(str)       # 标准输出
    error_received = Signal(str)        # 标准错误
    process_finished = Signal(int, str) # (退出码, 退出状态描述)
    process_started = Signal()          # 进程已启动
    progress_hint = Signal(int)         # 进度提示 (0-100)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._process = None
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def start(self, program: str, arguments: list[str],
              working_dir: str = None):
        """启动一个外部进程。"""
        if self._is_running:
            return

        self._process = QProcess(self)
        self._process.setProcessChannelMode(
            QProcess.ProcessChannelMode.MergedChannels
        )

        # 连接信号
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_finished)
        self._process.started.connect(self._on_started)
        self._process.errorOccurred.connect(self._on_error)

        if working_dir:
            self._process.setWorkingDirectory(working_dir)

        self._is_running = True
        self._process.start(program, arguments)

    def stop(self):
        """终止正在运行的进程。"""
        if self._process and self._is_running:
            self._process.kill()
            self._process.waitForFinished(3000)
            self._is_running = False

    @Slot()
    def _on_stdout(self):
        """处理标准输出。"""
        if self._process:
            data = self._process.readAllStandardOutput()
            text = bytes(data).decode('utf-8', errors='replace')
            if text.strip():
                self.output_received.emit(text)
                self._parse_progress(text)

    @Slot()
    def _on_stderr(self):
        """处理标准错误。"""
        if self._process:
            data = self._process.readAllStandardError()
            text = bytes(data).decode('utf-8', errors='replace')
            if text.strip():
                self.error_received.emit(text)

    @Slot(int, QProcess.ExitStatus)
    def _on_finished(self, exit_code, exit_status):
        """进程结束回调。"""
        self._is_running = False
        status_str = "正常退出" if exit_status == QProcess.ExitStatus.NormalExit else "异常退出"
        self.process_finished.emit(exit_code, status_str)

    @Slot()
    def _on_started(self):
        """进程启动回调。"""
        self.process_started.emit()

    @Slot(QProcess.ProcessError)
    def _on_error(self, error):
        """进程错误回调。"""
        error_messages = {
            QProcess.ProcessError.FailedToStart: "进程启动失败，请检查程序路径",
            QProcess.ProcessError.Crashed: "进程崩溃",
            QProcess.ProcessError.Timedout: "进程超时",
            QProcess.ProcessError.WriteError: "写入进程失败",
            QProcess.ProcessError.ReadError: "读取进程输出失败",
            QProcess.ProcessError.UnknownError: "未知错误",
        }
        msg = error_messages.get(error, "未知错误")
        self.error_received.emit(f"[进程错误] {msg}")
        self._is_running = False

    def _parse_progress(self, text: str):
        """
        尝试从 PyInstaller 输出中解析构建进度。
        PyInstaller 的输出格式并不提供明确的进度百分比，
        所以我们根据关键阶段来估算。
        """
        text_lower = text.lower()
        progress_keywords = {
            'analyzing': 10,
            'processing module': 20,
            'looking for ctypes': 30,
            'analyzing run-time hooks': 40,
            'looking for dynamic libraries': 50,
            'applying to analysis': 55,
            'checking pyz': 60,
            'building pyz': 65,
            'building pkg': 70,
            'building exe': 80,
            'building collect': 85,
            'copying': 90,
            'building app': 95,
        }
        for keyword, progress in progress_keywords.items():
            if keyword in text_lower:
                self.progress_hint.emit(progress)
                break

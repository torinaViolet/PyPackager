"""
构建日志控制台组件
实时显示构建输出，支持彩色日志和过滤。
"""
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QLabel, QProgressBar,
)
from PySide6.QtCore import Slot
from PySide6.QtGui import QTextCharFormat, QColor, QFont


class ConsoleOutput(QWidget):
    """构建日志控制台。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标题栏
        header = QHBoxLayout()
        title = QLabel("📟 构建控制台")
        title.setProperty("heading", "true")
        header.addWidget(title)
        header.addStretch()

        self.btn_clear = QPushButton("🗑️ 清空")
        self.btn_clear.clicked.connect(self.clear)
        header.addWidget(self.btn_clear)

        layout.addLayout(header)

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
        font = QFont("Cascadia Code", 11)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit)

    @Slot(str)
    def append_output(self, text: str):
        """添加标准输出文本。"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        for line in text.strip().splitlines():
            color = self._detect_color(line)
            self._append_colored(f"[{timestamp}] {line}", color)

    @Slot(str)
    def append_error(self, text: str):
        """添加错误输出文本。"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        for line in text.strip().splitlines():
            self._append_colored(f"[{timestamp}] ⚠ {line}", "#f38ba8")

    @Slot(str)
    def append_info(self, text: str):
        """添加信息文本。"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_colored(f"[{timestamp}] ℹ {text}", "#89b4fa")

    @Slot(str)
    def append_success(self, text: str):
        """添加成功信息。"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self._append_colored(f"[{timestamp}] ✅ {text}", "#a6e3a1")

    @Slot(int)
    def set_progress(self, value: int):
        """设置进度。"""
        self.progress_bar.show()
        self.progress_bar.setValue(min(value, 100))
        if value >= 100:
            self.progress_bar.setFormat("完成!")

    def show_progress(self):
        """显示进度条。"""
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")

    def hide_progress(self):
        """隐藏进度条。"""
        self.progress_bar.hide()

    @Slot()
    def clear(self):
        """清空控制台。"""
        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.hide()

    def _append_colored(self, text: str, color: str):
        """追加带颜色的文本。"""
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color))
        cursor = self.text_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text + "\n", fmt)
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()

    def _detect_color(self, line: str) -> str:
        """根据内容自动检测日志颜色。"""
        lower = line.lower()
        if any(w in lower for w in ['error', 'failed', '❌', 'traceback']):
            return "#f38ba8"   # 红色
        elif any(w in lower for w in ['warning', 'warn', '⚠']):
            return "#f9e2af"   # 黄色
        elif any(w in lower for w in ['success', '✅', 'completed', '完成']):
            return "#a6e3a1"   # 绿色
        elif any(w in lower for w in ['info', 'ℹ', '🚀', '📦']):
            return "#89b4fa"   # 蓝色
        else:
            return "#cdd6f4"   # 默认

"""排除参数预览对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTextEdit, QTabWidget, QWidget, QDialogButtonBox,
    QApplication,
)
from PySide6.QtCore import Qt


class ExcludePreviewDialog(QDialog):
    """预览生成的排除参数"""

    def __init__(self, excludes: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 排除参数预览")
        self.setMinimumSize(600, 450)
        self._excludes = excludes
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel(f"共 {len(self._excludes)} 个排除模块")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)

        # Tab 切换不同格式
        tabs = QTabWidget()

        # --- Tab 1: 命令行参数 ---
        cmd_widget = QWidget()
        cmd_layout = QVBoxLayout(cmd_widget)

        cmd_label = QLabel("PyInstaller 命令行参数:")
        cmd_label.setStyleSheet("font-weight: bold;")
        cmd_layout.addWidget(cmd_label)

        self.cmd_text = QTextEdit()
        self.cmd_text.setReadOnly(True)
        self.cmd_text.setFontFamily("Consolas")

        cmd_lines = []
        for mod in self._excludes:
            cmd_lines.append(f"--exclude-module {mod}")
        self.cmd_text.setPlainText("\n".join(cmd_lines))
        cmd_layout.addWidget(self.cmd_text)

        btn_copy_cmd = QPushButton("📋 复制到剪贴板")
        btn_copy_cmd.clicked.connect(lambda: self._copy_text(self.cmd_text.toPlainText()))
        cmd_layout.addWidget(btn_copy_cmd)

        tabs.addTab(cmd_widget, "命令行参数")

        # --- Tab 2: .spec 文件格式 ---
        spec_widget = QWidget()
        spec_layout = QVBoxLayout(spec_widget)

        spec_label = QLabel(".spec 文件中的 excludes 列表:")
        spec_label.setStyleSheet("font-weight: bold;")
        spec_layout.addWidget(spec_label)

        self.spec_text = QTextEdit()
        self.spec_text.setReadOnly(True)
        self.spec_text.setFontFamily("Consolas")

        spec_lines = ["excludes = ["]
        for mod in self._excludes:
            spec_lines.append(f"    '{mod}',")
        spec_lines.append("]")
        self.spec_text.setPlainText("\n".join(spec_lines))
        spec_layout.addWidget(self.spec_text)

        btn_copy_spec = QPushButton("📋 复制到剪贴板")
        btn_copy_spec.clicked.connect(lambda: self._copy_text(self.spec_text.toPlainText()))
        spec_layout.addWidget(btn_copy_spec)

        tabs.addTab(spec_widget, ".spec 文件格式")

        # --- Tab 3: Nuitka 格式 ---
        nuitka_widget = QWidget()
        nuitka_layout = QVBoxLayout(nuitka_widget)

        nuitka_label = QLabel("Nuitka 命令行参数:")
        nuitka_label.setStyleSheet("font-weight: bold;")
        nuitka_layout.addWidget(nuitka_label)

        self.nuitka_text = QTextEdit()
        self.nuitka_text.setReadOnly(True)
        self.nuitka_text.setFontFamily("Consolas")

        nuitka_lines = []
        for mod in self._excludes:
            nuitka_lines.append(f"--nofollow-import-to={mod}")
        self.nuitka_text.setPlainText("\n".join(nuitka_lines))
        nuitka_layout.addWidget(self.nuitka_text)

        btn_copy_nuitka = QPushButton("📋 复制到剪贴板")
        btn_copy_nuitka.clicked.connect(lambda: self._copy_text(self.nuitka_text.toPlainText()))
        nuitka_layout.addWidget(btn_copy_nuitka)

        tabs.addTab(nuitka_widget, "Nuitka 格式")

        layout.addWidget(tabs)

        # --- 关闭按钮 ---
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)

    def _copy_text(self, text: str):
        """复制文本到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
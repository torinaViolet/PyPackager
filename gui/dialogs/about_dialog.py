"""关于对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QDialogButtonBox,
)
from PySide6.QtCore import Qt


class AboutDialog(QDialog):
    """关于对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 PyPackager")
        self.setFixedSize(420, 320)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo / 标题
        logo = QLabel("🐍📦")
        logo.setStyleSheet("font-size: 48px;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        name = QLabel("PyPackager")
        name.setStyleSheet("font-size: 24px; font-weight: bold;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        version = QLabel("v1.0.0")
        version.setStyleSheet("font-size: 14px; color: #888;")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        desc = QLabel(
            "一个现代化的 Python 项目打包工具\n"
            "支持 PyInstaller / Nuitka 引擎\n"
            "智能依赖分析 | 大型库裁剪 | 可视化配置"
        )
        desc.setStyleSheet("color: #666; font-size: 12px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # 技术栈
        tech = QLabel("基于 PySide6 (Qt6) 构建")
        tech.setStyleSheet("color: #aaa; font-size: 11px;")
        tech.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(tech)

        # 分隔
        layout.addSpacing(10)

        # 链接
        links = QLabel(
            '💻 <a href="https://github.com/pypackager">GitHub</a> | '
            '📖 <a href="https://pypackager.readthedocs.io">文档</a>'
        )
        links.setOpenExternalLinks(True)
        links.setAlignment(Qt.AlignmentFlag.AlignCenter)
        links.setStyleSheet("font-size: 12px;")
        layout.addWidget(links)

        # 关闭按钮
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.close)
        layout.addWidget(buttons)
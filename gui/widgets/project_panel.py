"""
项目基本信息面板
设置项目名称、入口文件、图标、输出目录等基本信息。
"""
import os

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog,
    QGroupBox, QScrollArea,
)
from PySide6.QtCore import Signal, Qt

from core.config_manager import ConfigManager


class ProjectPanel(QWidget):
    """项目基本信息面板。"""

    config_changed = Signal()

    def __init__(self, config: ConfigManager, parent=None):
        super().__init__(parent)
        self._config = config
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(12)

        # ─── 项目信息分组 ─────────────────────────────
        info_group = QGroupBox("📌 项目信息")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(10)

        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("例如: MyAwesomeApp")
        info_layout.addRow("项目名称:", self.edit_name)

        self.edit_version = QLineEdit()
        self.edit_version.setPlaceholderText("例如: 1.0.0")
        self.edit_version.setText("1.0.0")
        info_layout.addRow("版本号:", self.edit_version)

        self.edit_author = QLineEdit()
        self.edit_author.setPlaceholderText("例如: Your Name")
        info_layout.addRow("作者:", self.edit_author)

        self.edit_description = QLineEdit()
        self.edit_description.setPlaceholderText("应用程序简短描述")
        info_layout.addRow("描述:", self.edit_description)

        layout.addWidget(info_group)

        # ─── 文件路径分组 ─────────────────────────────
        path_group = QGroupBox("📂 文件路径")
        path_layout = QFormLayout(path_group)
        path_layout.setSpacing(10)

        # 入口文件
        entry_row = QHBoxLayout()
        self.edit_script = QLineEdit()
        self.edit_script.setPlaceholderText("选择主入口 Python 文件")
        entry_row.addWidget(self.edit_script)
        self.btn_browse_script = QPushButton("📂")
        self.btn_browse_script.setFixedSize(36, 36)
        self.btn_browse_script.setToolTip("浏览文件")
        self.btn_browse_script.setStyleSheet("QPushButton { padding: 0px; font-size: 16px; }")
        entry_row.addWidget(self.btn_browse_script)
        path_layout.addRow("入口文件:", entry_row)

        # 图标
        icon_row = QHBoxLayout()
        self.edit_icon = QLineEdit()
        self.edit_icon.setPlaceholderText("可选: .ico / .icns / .png 文件")
        icon_row.addWidget(self.edit_icon)
        self.btn_browse_icon = QPushButton("📂")
        self.btn_browse_icon.setFixedSize(36, 36)
        self.btn_browse_icon.setStyleSheet("QPushButton { padding: 0px; font-size: 16px; }")
        icon_row.addWidget(self.btn_browse_icon)
        path_layout.addRow("图标文件:", icon_row)

        # 输出目录
        output_row = QHBoxLayout()
        self.edit_output = QLineEdit()
        self.edit_output.setText("./dist")
        output_row.addWidget(self.edit_output)
        self.btn_browse_output = QPushButton("📂")
        self.btn_browse_output.setFixedSize(36, 36)
        self.btn_browse_output.setStyleSheet("QPushButton { padding: 0px; font-size: 16px; }")
        output_row.addWidget(self.btn_browse_output)
        path_layout.addRow("输出目录:", output_row)

        layout.addWidget(path_group)

        # ─── 提示 ─────────────────────────────
        tip_label = QLabel(
            "💡 打包模式、窗口模式等构建相关设置请前往「⚙ 构建选项」面板配置。"
        )
        tip_label.setStyleSheet("color: #888; font-size: 12px; padding: 8px;")
        tip_label.setWordWrap(True)
        layout.addWidget(tip_label)

        layout.addStretch()

        scroll.setWidget(content_widget)
        outer_layout.addWidget(scroll)

    def _connect_signals(self):
        # 文件浏览按钮
        self.btn_browse_script.clicked.connect(self._browse_script)
        self.btn_browse_icon.clicked.connect(self._browse_icon)
        self.btn_browse_output.clicked.connect(self._browse_output)

        # 所有输入变化都通知配置变化
        self.edit_name.textChanged.connect(self._on_changed)
        self.edit_version.textChanged.connect(self._on_changed)
        self.edit_author.textChanged.connect(self._on_changed)
        self.edit_description.textChanged.connect(self._on_changed)
        self.edit_script.textChanged.connect(self._on_changed)
        self.edit_icon.textChanged.connect(self._on_changed)
        self.edit_output.textChanged.connect(self._on_changed)

    def _browse_script(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择入口 Python 文件", "",
            "Python 文件 (*.py *.pyw);;所有文件 (*)"
        )
        if path:
            self.edit_script.setText(path)
            # 自动填充项目名称
            if not self.edit_name.text():
                name = os.path.splitext(os.path.basename(path))[0]
                self.edit_name.setText(name.replace("_", " ").title())

    def _browse_icon(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图标文件", "",
            "图标文件 (*.ico *.icns *.png *.jpg *.jpeg *.bmp *.svg);;ICO 文件 (*.ico);;图片文件 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)"
        )
        if path:
            self.edit_icon.setText(path)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(
            self, "选择输出目录"
        )
        if path:
            self.edit_output.setText(path)

    def _on_changed(self):
        self.save_to_config()
        self.config_changed.emit()

    def save_to_config(self):
        """将面板数据保存到配置管理器。"""
        self._config.set("project.name", self.edit_name.text())
        self._config.set("project.version", self.edit_version.text())
        self._config.set("project.author", self.edit_author.text())
        self._config.set("project.description", self.edit_description.text())
        self._config.set("entry.script", self.edit_script.text())
        self._config.set("entry.icon", self.edit_icon.text())
        self._config.set("entry.output_dir", self.edit_output.text())

    def load_from_config(self):
        """从配置管理器加载数据到面板。"""
        self.edit_name.setText(self._config.get("project.name", ""))
        self.edit_version.setText(self._config.get("project.version", "1.0.0"))
        self.edit_author.setText(self._config.get("project.author", ""))
        self.edit_description.setText(self._config.get("project.description", ""))
        self.edit_script.setText(self._config.get("entry.script", ""))
        self.edit_icon.setText(self._config.get("entry.icon", ""))
        self.edit_output.setText(self._config.get("entry.output_dir", "./dist"))

"""主工具栏"""

from PySide6.QtWidgets import (
    QToolBar, QWidget, QHBoxLayout, QPushButton, QLabel, QSizePolicy,
)
from PySide6.QtCore import Signal, Qt


class MainToolBar(QToolBar):
    """主工具栏"""

    open_project_clicked = Signal()
    save_config_clicked = Signal()
    load_config_clicked = Signal()
    build_clicked = Signal()
    stop_build_clicked = Signal()
    settings_clicked = Signal()
    theme_toggle_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setStyleSheet("""
            QToolBar {
                spacing: 6px;
                padding: 4px 8px;
                border-bottom: 1px solid #ddd;
            }
        """)
        self._setup_ui()

    def _setup_ui(self):
        # 打开项目
        self.btn_open = QPushButton("📂 打开项目")
        self.btn_open.setToolTip("选择项目入口文件")
        self.btn_open.clicked.connect(self.open_project_clicked.emit)
        self.addWidget(self.btn_open)

        self.addSeparator()

        # 保存配置
        self.btn_save = QPushButton("💾 保存配置")
        self.btn_save.setToolTip("保存当前打包配置")
        self.btn_save.clicked.connect(self.save_config_clicked.emit)
        self.addWidget(self.btn_save)

        # 加载配置
        self.btn_load = QPushButton("📂 加载配置")
        self.btn_load.setToolTip("加载已保存的打包配置")
        self.btn_load.clicked.connect(self.load_config_clicked.emit)
        self.addWidget(self.btn_load)

        self.addSeparator()

        # 开始构建
        self.btn_build = QPushButton("🔨 开始构建")
        self.btn_build.setToolTip("开始打包构建")
        self.btn_build.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 6px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.btn_build.clicked.connect(self.build_clicked.emit)
        self.addWidget(self.btn_build)

        # 停止构建
        self.btn_stop = QPushButton("⏹ 停止")
        self.btn_stop.setToolTip("停止当前构建")
        self.btn_stop.setEnabled(False)
        self.btn_stop.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 6px 16px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.btn_stop.clicked.connect(self.stop_build_clicked.emit)
        self.addWidget(self.btn_stop)

        # 弹性空白
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

        # 图标按钮公共样式
        icon_btn_style = """
            QPushButton {
                padding: 0px;
                font-size: 18px;
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
                border-radius: 18px;
            }
        """

        # 主题切换
        self.btn_theme = QPushButton("🌙")
        self.btn_theme.setToolTip("切换亮/暗主题")
        self.btn_theme.setStyleSheet(icon_btn_style)
        self.btn_theme.clicked.connect(self._on_theme_toggle)
        self.addWidget(self.btn_theme)

        # 设置
        self.btn_settings = QPushButton("⚙")
        self.btn_settings.setToolTip("设置")
        self.btn_settings.setStyleSheet(icon_btn_style)
        self.btn_settings.clicked.connect(self.settings_clicked.emit)
        self.addWidget(self.btn_settings)

    def _on_theme_toggle(self):
        """切换主题图标"""
        if self.btn_theme.text() == "🌙":
            self.btn_theme.setText("☀")
        else:
            self.btn_theme.setText("🌙")
        self.theme_toggle_clicked.emit()

    def set_building(self, is_building: bool):
        """设置构建状态 (按钮启用/禁用)"""
        self.btn_build.setEnabled(not is_building)
        self.btn_stop.setEnabled(is_building)
        self.btn_open.setEnabled(not is_building)
        self.btn_save.setEnabled(not is_building)
        self.btn_load.setEnabled(not is_building)
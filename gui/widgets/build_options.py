"""构建选项面板 - 配置打包引擎、模式、优化等选项"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton,
    QLabel, QComboBox, QCheckBox, QLineEdit, QGroupBox, QFileDialog,
    QRadioButton, QButtonGroup, QTextEdit, QScrollArea,
)
from PySide6.QtCore import Signal, Qt


class BuildOptionsPanel(QWidget):
    """构建选项面板"""

    options_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # 使用 QScrollArea 包裹全部内容，防止窗口小时 UI 拥挤
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # --- 标题 ---
        title = QLabel("⚙ 构建选项")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # ═══ 打包引擎 ═══
        engine_group = QGroupBox("打包引擎")
        engine_layout = QHBoxLayout(engine_group)
        self.engine_group = QButtonGroup(self)

        self.radio_pyinstaller = QRadioButton("PyInstaller")
        self.radio_pyinstaller.setChecked(True)
        self.radio_nuitka = QRadioButton("Nuitka")
        self.engine_group.addButton(self.radio_pyinstaller, 0)
        self.engine_group.addButton(self.radio_nuitka, 1)
        engine_layout.addWidget(self.radio_pyinstaller)
        engine_layout.addWidget(self.radio_nuitka)
        engine_layout.addStretch()

        engine_status_label = QLabel()
        engine_status_label.setStyleSheet("color: #888; font-size: 11px;")
        engine_layout.addWidget(engine_status_label)

        # 检测引擎是否安装
        self._check_engine_availability(engine_status_label)

        layout.addWidget(engine_group)

        # ═══ 基本选项 ═══
        basic_group = QGroupBox("基本选项")
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(10)

        # 打包模式
        mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup(self)
        self.radio_onefile = QRadioButton("单文件 (--onefile)")
        self.radio_onefile.setChecked(True)
        self.radio_onedir = QRadioButton("单目录 (--onedir)")
        self.mode_group.addButton(self.radio_onefile, 0)
        self.mode_group.addButton(self.radio_onedir, 1)
        mode_layout.addWidget(self.radio_onefile)
        mode_layout.addWidget(self.radio_onedir)
        mode_layout.addStretch()
        basic_layout.addRow("打包模式:", mode_layout)

        # 窗口模式
        window_layout = QHBoxLayout()
        self.window_group = QButtonGroup(self)
        self.radio_gui = QRadioButton("GUI 窗口 (--noconsole)")
        self.radio_gui.setChecked(True)
        self.radio_console = QRadioButton("控制台 (--console)")
        self.window_group.addButton(self.radio_gui, 0)
        self.window_group.addButton(self.radio_console, 1)
        window_layout.addWidget(self.radio_gui)
        window_layout.addWidget(self.radio_console)
        window_layout.addStretch()
        basic_layout.addRow("窗口模式:", window_layout)

        # 目标平台
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["当前平台 (自动)", "Windows", "Linux", "macOS"])
        self.platform_combo.setCurrentIndex(0)
        basic_layout.addRow("目标平台:", self.platform_combo)

        layout.addWidget(basic_group)

        # ═══ 优化选项 ═══
        opt_group = QGroupBox("优化选项")
        opt_layout = QVBoxLayout(opt_group)
        opt_layout.setSpacing(8)

        # UPX 压缩
        upx_layout = QHBoxLayout()
        self.check_upx = QCheckBox("启用 UPX 压缩")
        upx_layout.addWidget(self.check_upx)
        self.upx_path_input = QLineEdit()
        self.upx_path_input.setPlaceholderText("UPX 可执行文件路径 (留空则自动搜索)")
        self.upx_path_input.setEnabled(False)
        upx_layout.addWidget(self.upx_path_input)
        self.btn_upx_browse = QPushButton("📂")
        self.btn_upx_browse.setFixedSize(36, 36)
        self.btn_upx_browse.setStyleSheet("QPushButton { padding: 0px; font-size: 16px; }")
        self.btn_upx_browse.setEnabled(False)
        self.btn_upx_browse.clicked.connect(self._browse_upx)
        upx_layout.addWidget(self.btn_upx_browse)
        opt_layout.addLayout(upx_layout)

        self.check_upx.toggled.connect(self.upx_path_input.setEnabled)
        self.check_upx.toggled.connect(self.btn_upx_browse.setEnabled)

        # 剥离调试符号
        self.check_strip = QCheckBox("剥离调试符号 (--strip)")
        opt_layout.addWidget(self.check_strip)

        # 排除模块
        exclude_layout = QVBoxLayout()
        self.check_exclude = QCheckBox("排除不需要的模块")
        exclude_layout.addWidget(self.check_exclude)

        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText("输入要排除的模块，用逗号分隔 (如: test, unittest, tkinter)")
        self.exclude_input.setEnabled(False)
        exclude_layout.addWidget(self.exclude_input)
        self.check_exclude.toggled.connect(self.exclude_input.setEnabled)
        opt_layout.addLayout(exclude_layout)

        # 清理构建缓存
        self.check_clean = QCheckBox("构建前清理缓存 (--clean)")
        self.check_clean.setChecked(True)
        opt_layout.addWidget(self.check_clean)

        layout.addWidget(opt_group)

        # ═══ 高级选项 ═══
        adv_group = QGroupBox("高级选项")
        adv_layout = QVBoxLayout(adv_group)
        adv_layout.setSpacing(8)

        self.check_admin = QCheckBox("请求管理员权限 (UAC)")
        adv_layout.addWidget(self.check_admin)

        self.check_version_info = QCheckBox("添加版本信息 (--version-file)")
        adv_layout.addWidget(self.check_version_info)

        self.check_debug = QCheckBox("调试模式 (--debug all)")
        adv_layout.addWidget(self.check_debug)

        # 自定义参数
        custom_label = QLabel("自定义参数:")
        adv_layout.addWidget(custom_label)

        self.custom_args_input = QTextEdit()
        self.custom_args_input.setPlaceholderText(
            "输入额外的命令行参数，每行一个。\n"
            "例如:\n"
            "--add-binary=libfoo.so:.\n"
            "--runtime-hook=my_hook.py"
        )
        self.custom_args_input.setMaximumHeight(100)
        adv_layout.addWidget(self.custom_args_input)

        layout.addWidget(adv_group)

        layout.addStretch()

        scroll.setWidget(content_widget)
        outer_layout.addWidget(scroll)

        # 信号连接
        self.engine_group.buttonToggled.connect(lambda: self.options_changed.emit())
        self.mode_group.buttonToggled.connect(lambda: self.options_changed.emit())
        self.window_group.buttonToggled.connect(lambda: self.options_changed.emit())

    def _check_engine_availability(self, label: QLabel):
        """检测打包引擎是否安装"""
        status_parts = []
        try:
            import PyInstaller
            status_parts.append(f"PyInstaller ✅ v{PyInstaller.__version__}")
        except ImportError:
            status_parts.append("PyInstaller ❌")
            self.radio_pyinstaller.setEnabled(False)

        try:
            import subprocess
            result = subprocess.run(["nuitka", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                ver = result.stdout.strip().split('\n')[0]
                status_parts.append(f"Nuitka ✅ {ver}")
            else:
                status_parts.append("Nuitka ❌")
                self.radio_nuitka.setEnabled(False)
        except Exception:
            status_parts.append("Nuitka ❌")
            self.radio_nuitka.setEnabled(False)

        label.setText(" | ".join(status_parts))

    def _browse_upx(self):
        """浏览选择 UPX 路径"""
        path, _ = QFileDialog.getOpenFileName(
            self, "选择 UPX 可执行文件", "",
            "可执行文件 (*.exe);;所有文件 (*)"
        )
        if path:
            self.upx_path_input.setText(path)

    def get_config(self) -> dict:
        """获取构建选项配置"""
        # 获取排除模块列表
        excludes = []
        if self.check_exclude.isChecked() and self.exclude_input.text().strip():
            excludes = [m.strip() for m in self.exclude_input.text().split(",") if m.strip()]

        # 获取自定义参数
        custom_args = self.custom_args_input.toPlainText().strip()

        return {
            "engine": "pyinstaller" if self.radio_pyinstaller.isChecked() else "nuitka",
            "onefile": self.radio_onefile.isChecked(),
            "console": self.radio_console.isChecked(),
            "upx": self.check_upx.isChecked(),
            "upx_path": self.upx_path_input.text().strip(),
            "strip": self.check_strip.isChecked(),
            "clean": self.check_clean.isChecked(),
            "uac_admin": self.check_admin.isChecked(),
            "version_info": self.check_version_info.isChecked(),
            "debug": self.check_debug.isChecked(),
            "excludes": excludes,
            "extra_args": custom_args,
        }

    def set_config(self, config: dict):
        """从配置恢复面板状态"""
        engine = config.get("engine", "pyinstaller")
        if engine == "nuitka":
            self.radio_nuitka.setChecked(True)
        else:
            self.radio_pyinstaller.setChecked(True)

        if config.get("onefile", True):
            self.radio_onefile.setChecked(True)
        else:
            self.radio_onedir.setChecked(True)

        if config.get("console", False):
            self.radio_console.setChecked(True)
        else:
            self.radio_gui.setChecked(True)

        self.check_upx.setChecked(config.get("upx", False))
        self.upx_path_input.setText(config.get("upx_path", ""))
        self.check_strip.setChecked(config.get("strip", False))
        self.check_clean.setChecked(config.get("clean", True))
        self.check_admin.setChecked(config.get("uac_admin", False))
        self.check_version_info.setChecked(config.get("version_info", False))
        self.check_debug.setChecked(config.get("debug", False))

        excludes = config.get("excludes", [])
        if excludes:
            self.check_exclude.setChecked(True)
            self.exclude_input.setText(", ".join(excludes))

        self.custom_args_input.setPlainText(config.get("extra_args", ""))
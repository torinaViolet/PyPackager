"""主窗口 - 整合所有面板和功能"""

import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QListWidget, QListWidgetItem, QStackedWidget,
    QSplitter, QFileDialog, QMessageBox, QStatusBar,
    QApplication,
)
from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QFont

from gui.widgets.toolbar import MainToolBar
from gui.widgets.project_panel import ProjectPanel
from gui.widgets.dependency_panel import DependencyPanel
from gui.widgets.resource_panel import ResourcePanel
from gui.widgets.build_options import BuildOptionsPanel
from gui.widgets.library_trimmer import LibraryTrimmerPanel
from gui.widgets.console_output import ConsoleOutput

from gui.dialogs.about_dialog import AboutDialog

from core.analyzer import ProjectAnalyzer
from core.builder import Builder
from core.config_manager import ConfigManager
from core.smart_excluder import SmartExcluder
from core.venv_detector import VenvDetector


class MainWindow(QMainWindow):
    """PyPackager 主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐍 PyPackager — Python 打包工具")
        self.setMinimumSize(1100, 750)
        self.resize(1280, 800)

        # 核心组件 — ConfigManager 是中央数据枢纽
        self._config_manager = ConfigManager()
        self._analyzer = ProjectAnalyzer()
        self._builder = Builder(self._config_manager)
        self._smart_excluder = SmartExcluder()
        self._venv_detector = VenvDetector()

        # 状态
        self._project_dir = ""
        self._is_dark_theme = False

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """搭建 UI"""

        # === 工具栏 ===
        self.toolbar = MainToolBar()
        self.addToolBar(self.toolbar)

        # === 中央区域 ===
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 上下分割器（上部: 导航+面板, 下部: 控制台）
        self.main_splitter = QSplitter(Qt.Orientation.Vertical)

        # --- 上部: 导航 + 内容面板 ---
        upper_widget = QWidget()
        upper_layout = QHBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(0)

        # 左侧导航
        self.nav_list = QListWidget()
        self.nav_list.setFixedWidth(180)
        self.nav_list.setFont(QFont("", 12))

        nav_items = [
            "📌 基本信息",
            "📦 依赖管理",
            "📁 资源文件",
            "⚙️ 构建选项",
            "✂️ 库裁剪",
        ]
        for text in nav_items:
            item = QListWidgetItem(text)
            item.setSizeHint(QSize(160, 42))
            self.nav_list.addItem(item)

        self.nav_list.setCurrentRow(0)
        upper_layout.addWidget(self.nav_list)

        # 右侧面板堆叠
        self.panel_stack = QStackedWidget()

        # ProjectPanel 需要 ConfigManager
        self.project_panel = ProjectPanel(self._config_manager)
        self.dependency_panel = DependencyPanel()
        self.resource_panel = ResourcePanel()
        self.build_options_panel = BuildOptionsPanel()
        self.library_trimmer_panel = LibraryTrimmerPanel()

        self.panel_stack.addWidget(self.project_panel)          # 0
        self.panel_stack.addWidget(self.dependency_panel)       # 1
        self.panel_stack.addWidget(self.resource_panel)         # 2
        self.panel_stack.addWidget(self.build_options_panel)    # 3
        self.panel_stack.addWidget(self.library_trimmer_panel)  # 4

        upper_layout.addWidget(self.panel_stack)
        self.main_splitter.addWidget(upper_widget)

        # --- 下部: 构建控制台 ---
        self.console_output = ConsoleOutput()
        self.main_splitter.addWidget(self.console_output)

        # 设置最小高度，防止拖拽时消失
        upper_widget.setMinimumHeight(200)
        self.console_output.setMinimumHeight(120)

        # 禁止折叠，防止拉伸时面板消失
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, False)

        # 设置分割比例
        self.main_splitter.setStretchFactor(0, 3)
        self.main_splitter.setStretchFactor(1, 1)

        # 设置初始大小分配
        self.main_splitter.setSizes([560, 200])

        # 加粗分割手柄，方便拖拽
        self.main_splitter.setHandleWidth(6)
        self.main_splitter.setStyleSheet("""
            QSplitter::handle:vertical {
                background-color: qlineargradient(
                    y1:0, y2:1,
                    stop:0 transparent,
                    stop:0.3 #aaa,
                    stop:0.5 #888,
                    stop:0.7 #aaa,
                    stop:1 transparent
                );
                height: 6px;
                margin: 0px 40px;
                border-radius: 3px;
            }
            QSplitter::handle:vertical:hover {
                background-color: qlineargradient(
                    y1:0, y2:1,
                    stop:0 transparent,
                    stop:0.3 #74c7ec,
                    stop:0.5 #89b4fa,
                    stop:0.7 #74c7ec,
                    stop:1 transparent
                );
            }
        """)

        main_layout.addWidget(self.main_splitter)

        # === 状态栏 ===
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 — 请打开项目或加载配置开始")

    def _connect_signals(self):
        """连接所有信号"""

        # 导航切换
        self.nav_list.currentRowChanged.connect(self.panel_stack.setCurrentIndex)

        # 工具栏
        self.toolbar.open_project_clicked.connect(self._on_open_project)
        self.toolbar.save_config_clicked.connect(self._on_save_config)
        self.toolbar.load_config_clicked.connect(self._on_load_config)
        self.toolbar.build_clicked.connect(self._on_build)
        self.toolbar.stop_build_clicked.connect(self._on_stop_build)
        self.toolbar.theme_toggle_clicked.connect(self._on_toggle_theme)
        self.toolbar.settings_clicked.connect(self._on_settings)

        # 构建引擎信号
        self._builder.build_output.connect(self._on_build_output)
        self._builder.build_error.connect(self._on_build_error)
        self._builder.build_finished.connect(self._on_build_finished)
        self._builder.build_progress.connect(self._on_build_progress)
        self._builder.build_started.connect(self._on_build_started)
        self._builder.command_generated.connect(self._on_command_generated)

        # 依赖面板扫描按钮
        self.dependency_panel.btn_scan.clicked.connect(self._on_scan_dependencies)

        # 库裁剪面板扫描按钮
        self.library_trimmer_panel.btn_scan.clicked.connect(self._on_scan_dependencies)

    # ===== 打开项目 =====
    @Slot()
    def _on_open_project(self):
        """打开项目 (选择入口文件)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择项目入口文件", "",
            "Python 文件 (*.py *.pyw);;所有文件 (*)"
        )
        if not file_path:
            return

        self._project_dir = os.path.dirname(os.path.abspath(file_path))
        self.resource_panel.set_project_dir(self._project_dir)

                # 更新控制台工作目录
        self.console_output.set_project_dir(self._project_dir)

        # 检测虚拟环境，配置 Python 解释器
        venv_info = self._venv_detector.detect_venv(self._project_dir)
        if venv_info.get("found"):
            python_path = venv_info.get("python_path", "")
            venv_path = venv_info.get("path", "")
            venv_type = venv_info.get("type", "venv")
            # 只有检测到虚拟环境时，才使用外部进程模式
            self.console_output.set_python_path(python_path)
            # 终端也激活虚拟环境（pip/python 命令使用项目环境）
            self.console_output.set_venv_path(venv_path)
            # 构建引擎也使用虚拟环境的 Python（PyInstaller/Nuitka 通常安装在虚拟环境中）
            self._builder.set_project_python(python_path)
            self.console_output.append_info(
                f"检测到{venv_type}虚拟环境: {venv_path}"
            )
            self.console_output.append_info(
                f"Python 解释器: {python_path} ({venv_info.get('python_version', '')})"
            )
        else:
            self.console_output.append_info(
                "未检测到虚拟环境，Python 控制台将使用内置解释器"
            )

        # 设置到 ConfigManager
        self._config_manager.set("entry.script", file_path)
        name = os.path.splitext(os.path.basename(file_path))[0]
        if not self._config_manager.get("project.name"):
            self._config_manager.set("project.name", name.replace("_", " ").title())

        # 刷新 ProjectPanel 显示
        self.project_panel.load_from_config()

        self.status_bar.showMessage(f"已打开项目: {self._project_dir}")
        self.console_output.append_info(f"已打开项目: {self._project_dir}")
        self.console_output.append_info(f"入口文件: {file_path}")

        # 自动扫描
        self._on_scan_dependencies()

    # ===== 扫描依赖 =====
    @Slot()
    def _on_scan_dependencies(self):
        """扫描项目依赖"""
        entry_script = self._config_manager.get("entry.script", "")
        if not entry_script or not os.path.isfile(entry_script):
            QMessageBox.warning(self, "警告", "请先设置有效的入口文件。")
            return

        project_dir = os.path.dirname(os.path.abspath(entry_script))
        self.console_output.append_info("开始扫描项目依赖...")
        self.status_bar.showMessage("正在扫描依赖...")

        try:
            # analyzer.analyze 接收目录路径，返回 AnalysisResult 对象
            analysis = self._analyzer.analyze(project_dir)

            self.console_output.append_info(
                f"扫描了 {analysis.files_scanned} 个文件，"
                f"发现 {len(analysis.third_party_imports)} 个第三方依赖"
            )

            # ---- 更新依赖面板 ----
            dep_list = []
            for imp in sorted(analysis.third_party_imports):
                top_level = imp.split('.')[0]
                # 只显示顶层模块，避免重复
                if imp == top_level:
                    dep_list.append({
                        "name": imp,
                        "version": "",
                        "status": "✅ 已安装",
                        "source": "🔍 自动发现",
                    })
            self.dependency_panel.set_dependencies(dep_list)

            # 隐藏导入建议
            from gui.dialogs.hidden_imports import COMMON_HIDDEN_IMPORTS
            suggestions = []
            for lib in analysis.detected_large_libs:
                base = lib.split('.')[0]
                lib_suggestions = COMMON_HIDDEN_IMPORTS.get(base, [])
                suggestions.extend(lib_suggestions)
            self.dependency_panel.set_suggestions(suggestions)

            # ---- 更新库裁剪面板 ----
            try:
                from core.library_profiles import get_profile
                profiles = {}
                for lib_name in analysis.detected_large_libs:
                    profile_cls = get_profile(lib_name)
                    if profile_cls is not None:
                        profiles[lib_name] = profile_cls

                if profiles:
                    used_imports_list = list(analysis.all_imports)
                    self.library_trimmer_panel.set_analysis_results(
                        used_imports_list, profiles
                    )
                    lib_names = ", ".join(profiles.keys())
                    self.console_output.append_info(
                        f"检测到可优化的大型库: {lib_names}"
                    )
                else:
                    self.console_output.append_info("未检测到可优化的大型库")
            except Exception as e:
                self.console_output.append_error(f"库裁剪分析出错: {e}")

            # ---- 检测到的资源文件 ----
            if analysis.resource_references:
                self.console_output.append_info(
                    f"检测到 {len(analysis.resource_references)} 个资源文件引用"
                )

            self.console_output.append_success("依赖扫描完成!")
            self.status_bar.showMessage(
                f"扫描完成 — {len(analysis.third_party_imports)} 个第三方依赖, "
                f"{len(analysis.detected_large_libs)} 个大型库"
            )

        except Exception as e:
            self.console_output.append_error(f"扫描失败: {e}")
            self.status_bar.showMessage("扫描失败")

    # ===== 保存/加载配置 =====
    @Slot()
    def _on_save_config(self):
        """保存打包配置"""
        default_path = (
            os.path.join(self._project_dir, "pypackager.json")
            if self._project_dir else "pypackager.json"
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", default_path,
            "JSON 文件 (*.json)"
        )
        if not file_path:
            return

        # 先把所有面板数据同步到 ConfigManager
        self._sync_panels_to_config()

        if self._config_manager.save(file_path):
            self.console_output.append_success(f"配置已保存: {file_path}")
            self.status_bar.showMessage(f"配置已保存到 {file_path}")
        else:
            QMessageBox.critical(self, "错误", "保存配置失败!")

    @Slot()
    def _on_load_config(self):
        """加载打包配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载配置文件", "",
            "JSON 文件 (*.json);;所有文件 (*)"
        )
        if not file_path:
            return

        if self._config_manager.load(file_path):
            self._load_config_to_panels()
            # 更新项目目录
            script = self._config_manager.get("entry.script", "")
            if script:
                self._project_dir = os.path.dirname(os.path.abspath(script))
                self.resource_panel.set_project_dir(self._project_dir)

            self.console_output.append_success(f"配置已加载: {file_path}")
            self.status_bar.showMessage(f"已加载配置: {file_path}")
        else:
            QMessageBox.critical(self, "错误", "加载配置失败!")

    def _sync_panels_to_config(self):
        """将所有面板数据同步到 ConfigManager"""
        # ① ProjectPanel 已经通过 save_to_config 自动同步了
        #    但手动再调一次确保最新
        self.project_panel.save_to_config()

        # ② 构建选项面板 → ConfigManager
        build_opts = self.build_options_panel.get_config()
        self._config_manager.set("build.engine", build_opts.get("engine", "pyinstaller"))
        self._config_manager.set(
            "build.mode", "onefile" if build_opts.get("onefile", True) else "onedir"
        )
        self._config_manager.set("build.console", build_opts.get("console", False))
        self._config_manager.set("build.upx", build_opts.get("upx", False))
        self._config_manager.set("build.upx_path", build_opts.get("upx_path", ""))
        self._config_manager.set("build.strip", build_opts.get("strip", False))
        self._config_manager.set("build.clean", build_opts.get("clean", True))
        self._config_manager.set("build.uac_admin", build_opts.get("uac_admin", False))
        self._config_manager.set("build.extra_args", build_opts.get("extra_args", ""))

        # ③ 依赖面板 → ConfigManager
        dep_config = self.dependency_panel.get_config()
        self._config_manager.set(
            "dependencies.hidden_imports",
            dep_config.get("hidden_imports", [])
        )

        # 合并排除列表: 构建选项排除 + 库裁剪排除
        build_excludes = build_opts.get("excludes", [])
        library_excludes = self.library_trimmer_panel.get_all_excludes()
        all_excludes = list(set(build_excludes + library_excludes))
        self._config_manager.set("dependencies.excludes", all_excludes)

        # ④ 资源文件面板 → ConfigManager
        res_config = self.resource_panel.get_config()
        self._config_manager.set(
            "resources.data_files",
            res_config.get("data_files", [])
        )

    def _load_config_to_panels(self):
        """将 ConfigManager 数据加载到所有面板"""
        # ① ProjectPanel
        self.project_panel.load_from_config()

        # ② 构建选项面板
        build_config = {
            "engine": self._config_manager.get("build.engine", "pyinstaller"),
            "onefile": self._config_manager.get("build.mode", "onefile") == "onefile",
            "console": self._config_manager.get("build.console", False),
            "upx": self._config_manager.get("build.upx", False),
            "upx_path": self._config_manager.get("build.upx_path", ""),
            "strip": self._config_manager.get("build.strip", False),
            "clean": self._config_manager.get("build.clean", True),
            "uac_admin": self._config_manager.get("build.uac_admin", False),
            "extra_args": self._config_manager.get("build.extra_args", ""),
            "excludes": self._config_manager.get("dependencies.excludes", []),
        }
        self.build_options_panel.set_config(build_config)

        # ③ 依赖面板
        dep_config = {
            "hidden_imports": self._config_manager.get("dependencies.hidden_imports", []),
        }
        self.dependency_panel.set_config(dep_config)

        # ④ 资源文件面板
        res_config = {
            "data_files": self._config_manager.get("resources.data_files", []),
        }
        self.resource_panel.set_config(res_config)

    # ===== 构建 =====
    @Slot()
    def _on_build(self):
        """开始构建"""
        entry_script = self._config_manager.get("entry.script", "")
        if not entry_script or not os.path.isfile(entry_script):
            QMessageBox.warning(self, "警告", "请先设置有效的入口文件!")
            return

        # 同步所有面板到 ConfigManager
        self._sync_panels_to_config()

        self.toolbar.set_building(True)
        self.console_output.clear()
        self.console_output.show_progress()

        self.console_output.append_info("=" * 50)
        self.console_output.append_info("开始构建...")
        self.console_output.append_info("=" * 50)

        self.status_bar.showMessage("正在构建...")

        # 如果有库裁剪方案，设置到 Builder
        try:
            entry_script = self._config_manager.get("entry.script", "")
            project_dir = os.path.dirname(os.path.abspath(entry_script))
            analysis = self._analyzer.analyze(project_dir)

            if analysis.detected_large_libs:
                plan = self._smart_excluder.generate_plan(analysis)
                self._builder.set_exclusion_plan(plan)
                if plan.total_saved_mb > 0:
                    self.console_output.append_info(
                        f"已应用智能排除方案，预计节省 {plan.total_saved_mb:.0f} MB"
                    )
        except Exception as e:
            self.console_output.append_output(f"智能排除分析跳过: {e}")

        # 启动构建
        self._builder.start_build()

    @Slot()
    def _on_stop_build(self):
        """停止构建"""
        self._builder.cancel_build()
        self.toolbar.set_building(False)
        self.console_output.hide_progress()
        self.console_output.append_error("构建已手动停止")
        self.status_bar.showMessage("构建已停止")

    @Slot()
    def _on_build_started(self):
        """构建已启动"""
        pass

    @Slot(str)
    def _on_command_generated(self, cmd: str):
        """显示生成的命令"""
        self.console_output.append_info(f"执行命令: {cmd}")

    @Slot(str)
    def _on_build_output(self, text: str):
        """构建标准输出"""
        self.console_output.append_output(text)

    @Slot(str)
    def _on_build_error(self, text: str):
        """构建错误输出"""
        self.console_output.append_error(text)

    @Slot(bool, str)
    def _on_build_finished(self, success: bool, message: str):
        """构建完成"""
        self.toolbar.set_building(False)
        self.console_output.hide_progress()
        if success:
            self.console_output.set_progress(100)
            self.console_output.append_success(f"构建成功! {message}")
            self.status_bar.showMessage(f"构建成功! {message}")
        else:
            self.console_output.append_error(f"构建失败: {message}")
            self.status_bar.showMessage("构建失败")

    @Slot(int)
    def _on_build_progress(self, percent: int):
        """构建进度"""
        self.console_output.set_progress(percent)
        self.status_bar.showMessage(f"构建中... {percent}%")

    # ===== 主题切换 =====
    @Slot()
    def _on_toggle_theme(self):
        """切换亮/暗主题"""
        from gui.styles.theme import get_stylesheet
        self._is_dark_theme = not self._is_dark_theme
        theme_name = "dark" if self._is_dark_theme else "light"
        app = QApplication.instance()
        app.setStyleSheet(get_stylesheet(theme_name))
        self.console_output.append_info(
            f"已切换到{'暗色' if self._is_dark_theme else '亮色'}主题"
        )

    # ===== 设置 =====
    @Slot()
    def _on_settings(self):
        """打开关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        """窗口关闭时清理子进程。"""
        self.console_output.cleanup()
        super().closeEvent(event)
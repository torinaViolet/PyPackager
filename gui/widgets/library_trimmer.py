"""大型库裁剪面板 - 可视化管理大型库的子模块排除"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QScrollArea, QGroupBox, QCheckBox,
    QProgressBar, QFrame,
)
from PySide6.QtCore import Signal, Qt


class LibraryTrimmerPanel(QWidget):
    """大型库裁剪面板"""

    excludes_changed = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._profiles = {}
        self._library_widgets = {}  # name -> LibraryTrimWidget
        self._used_imports = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- 标题 ---
        title = QLabel("✂️ 大型库裁剪")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("智能分析项目依赖，排除未使用的大型库子模块，大幅减小打包体积。")
        desc.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(desc)

        # --- 工具栏 ---
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_scan = QPushButton("🔍 自动扫描项目")
        toolbar.addWidget(self.btn_scan)

        self.btn_recommend = QPushButton("🎯 一键推荐排除")
        self.btn_recommend.clicked.connect(self._on_recommend_all)
        toolbar.addWidget(self.btn_recommend)

        self.btn_keep_all = QPushButton("↩️ 全部保留")
        self.btn_keep_all.clicked.connect(self._on_keep_all)
        toolbar.addWidget(self.btn_keep_all)

        self.btn_aggressive = QPushButton("⚡ 激进裁剪")
        self.btn_aggressive.setToolTip("排除所有未直接使用的子模块 (可能需要手动调整)")
        self.btn_aggressive.clicked.connect(self._on_aggressive_trim)
        toolbar.addWidget(self.btn_aggressive)

        toolbar.addStretch()

        self.btn_custom = QPushButton("➕ 自定义库配置")
        self.btn_custom.setToolTip("为任意库创建裁剪配置")
        self.btn_custom.clicked.connect(self._on_custom_profile)
        toolbar.addWidget(self.btn_custom)

        layout.addLayout(toolbar)

        # --- 库列表滚动区域 ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.libs_container = QWidget()
        self.libs_layout = QVBoxLayout(self.libs_container)
        self.libs_layout.setSpacing(12)
        self.libs_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 默认提示
        self.placeholder_label = QLabel("请先执行「自动扫描项目」来检测可优化的大型库。")
        self.placeholder_label.setStyleSheet("color: #888; font-size: 14px; padding: 40px;")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.libs_layout.addWidget(self.placeholder_label)

        scroll.setWidget(self.libs_container)
        layout.addWidget(scroll)

        # --- 总体节省统计 ---
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        summary_layout = QHBoxLayout(summary_frame)

        self.total_savings_label = QLabel("📊 预计总节省: 0 MB")
        self.total_savings_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #27ae60;"
        )
        summary_layout.addWidget(self.total_savings_label)
        summary_layout.addStretch()

        self.btn_preview = QPushButton("📋 预览排除参数")
        self.btn_preview.clicked.connect(self._on_preview_excludes)
        summary_layout.addWidget(self.btn_preview)

        layout.addWidget(summary_frame)

    def set_analysis_results(self, used_imports: list, profiles: dict):
        """
        设置分析结果。
        used_imports: 项目使用到的 import 列表
        profiles: {lib_name: profile_class}  (注意是类，不是实例)
        """
        self._used_imports = used_imports
        self._profiles = profiles

        self._clear_library_widgets()

        if not profiles:
            self.placeholder_label.setVisible(True)
            self.placeholder_label.setText("未检测到可优化的大型库。")
            return

        self.placeholder_label.setVisible(False)

        for name, profile_cls in profiles.items():
            widget = LibraryTrimWidget(profile_cls, used_imports)
            widget.exclude_changed.connect(self._on_individual_change)
            self.libs_layout.addWidget(widget)
            self._library_widgets[name] = widget

        self._update_total_savings()

    def _clear_library_widgets(self):
        for widget in self._library_widgets.values():
            widget.deleteLater()
        self._library_widgets.clear()

    def _on_individual_change(self):
        self._update_total_savings()
        self.excludes_changed.emit(self.get_all_excludes())

    def _update_total_savings(self):
        total = sum(w.get_estimated_savings() for w in self._library_widgets.values())
        self.total_savings_label.setText(f"📊 预计总节省: {total:.0f} MB")

    def _on_recommend_all(self):
        for widget in self._library_widgets.values():
            widget.apply_recommended()
        self._update_total_savings()

    def _on_keep_all(self):
        for widget in self._library_widgets.values():
            widget.keep_all()
        self._update_total_savings()

    def _on_aggressive_trim(self):
        for widget in self._library_widgets.values():
            widget.apply_aggressive()
        self._update_total_savings()

    def _on_preview_excludes(self):
        from gui.dialogs.exclude_preview import ExcludePreviewDialog
        excludes = self.get_all_excludes()
        dialog = ExcludePreviewDialog(excludes, parent=self)
        dialog.exec()

    def get_all_excludes(self) -> list:
        excludes = []
        for widget in self._library_widgets.values():
            excludes.extend(widget.get_excludes())
        return excludes

    def get_config(self) -> dict:
        return {"library_excludes": self.get_all_excludes()}

    def set_config(self, config: dict):
        excludes = config.get("library_excludes", [])
        for widget in self._library_widgets.values():
            widget.apply_excludes(excludes)
        self._update_total_savings()

    def _on_custom_profile(self):
        """打开自定义裁剪配置对话框"""
        from gui.dialogs.custom_profile_dialog import CustomProfileDialog
        dialog = CustomProfileDialog(parent=self)
        dialog.profile_created.connect(self._on_profile_created)
        dialog.exec()

    def _on_profile_created(self, filepath: str):
        """自定义 Profile 生成完成"""
        # 提示用户重新扫描
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "提示",
            "自定义裁剪配置已生成并注册。\n"
            "请点击「🔍 自动扫描项目」来刷新裁剪面板。"
        )


class LibraryTrimWidget(QGroupBox):
    """单个库的裁剪控件"""

    exclude_changed = Signal()

    def __init__(self, profile_cls, used_imports: list, parent=None):
        """
        profile_cls: BaseProfile 的子类 (类对象，非实例)
        used_imports: 项目所有 import 列表
        """
        super().__init__(parent)
        self._profile = profile_cls
        self._used_imports = used_imports
        self._module_checkboxes = {}  # module_name -> QCheckBox
        self._data_checkboxes = {}    # data_path -> QCheckBox
        self._setup_ui()

    def _setup_ui(self):
        profile = self._profile

        # 安全获取属性 (profile 可能是类，属性都是类级别的)
        profile_name = getattr(profile, 'name', 'Unknown')
        profile_desc = getattr(profile, 'description', '')
        profile_modules = getattr(profile, 'modules', {})
        profile_excludable_data = getattr(profile, 'excludable_data', [])

        self.setTitle(f"📦 {profile_name}")
        self.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 8px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        # 描述
        if profile_desc:
            desc_label = QLabel(profile_desc)
            desc_label.setStyleSheet(
                "color: #888; font-weight: normal; font-size: 12px;"
            )
            layout.addWidget(desc_label)

        # 子模块列表
        if profile_modules:
            modules_label = QLabel("子模块:")
            modules_label.setStyleSheet(
                "font-weight: bold; font-size: 12px; color: #555;"
            )
            layout.addWidget(modules_label)

            for mod_name, mod_info in profile_modules.items():
                row = QHBoxLayout()

                is_used = self._is_module_used(mod_name)
                is_essential = getattr(mod_info, 'is_essential', False)
                size_mb = getattr(mod_info, 'size_mb', 0)
                mod_desc = getattr(mod_info, 'description', '')

                cb = QCheckBox()
                cb.setChecked(True)  # 默认保留
                if is_essential:
                    cb.setEnabled(False)
                    cb.setChecked(True)
                cb.toggled.connect(self._on_checkbox_changed)
                self._module_checkboxes[mod_name] = cb
                row.addWidget(cb)

                name_label = QLabel(mod_name)
                name_label.setMinimumWidth(200)
                name_label.setStyleSheet("font-weight: normal; font-size: 12px;")
                row.addWidget(name_label)

                size_label = QLabel(f"{size_mb}MB")
                size_label.setMinimumWidth(50)
                size_label.setStyleSheet(
                    "color: #888; font-weight: normal; font-size: 12px;"
                )
                row.addWidget(size_label)

                if is_essential:
                    status_text, color = "🔒 必需", "#95a5a6"
                elif is_used:
                    status_text, color = "📌 已使用", "#27ae60"
                else:
                    status_text, color = "⚪ 未使用", "#e67e22"

                status_label = QLabel(status_text)
                status_label.setStyleSheet(
                    f"color: {color}; font-weight: normal; font-size: 12px;"
                )
                status_label.setMinimumWidth(80)
                row.addWidget(status_label)

                if mod_desc:
                    desc_lbl = QLabel(mod_desc)
                    desc_lbl.setStyleSheet(
                        "color: #aaa; font-weight: normal; font-size: 11px;"
                    )
                    row.addWidget(desc_lbl)

                row.addStretch()
                layout.addLayout(row)

        # 可排除数据文件
        if profile_excludable_data:
            data_label = QLabel("📂 可排除数据文件:")
            data_label.setStyleSheet(
                "font-weight: bold; font-size: 12px; color: #555; margin-top: 8px;"
            )
            layout.addWidget(data_label)

            for data_item in profile_excludable_data:
                row = QHBoxLayout()
                # data_item 可能是 str 或 dict
                if isinstance(data_item, dict):
                    data_path = data_item.get("path", str(data_item))
                else:
                    data_path = str(data_item)
                cb = QCheckBox(data_path)
                cb.setChecked(True)  # 默认保留
                cb.setStyleSheet("font-weight: normal; font-size: 12px;")
                cb.toggled.connect(self._on_checkbox_changed)
                self._data_checkboxes[data_path] = cb
                row.addWidget(cb)
                row.addStretch()
                layout.addLayout(row)

        # 体积预估进度条
        self.savings_bar = QProgressBar()
        self.savings_bar.setMaximum(100)
        self.savings_bar.setValue(0)
        self.savings_bar.setFormat("节省 %v%")
        self.savings_bar.setMaximumHeight(20)
        self.savings_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 4px;
                text-align: center;
                font-weight: normal;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.savings_bar)

        self.savings_label = QLabel("💡 预计节省: 0 MB")
        self.savings_label.setStyleSheet(
            "color: #27ae60; font-weight: bold; font-size: 12px;"
        )
        layout.addWidget(self.savings_label)

    def _on_checkbox_changed(self):
        """复选框变化时更新显示并发信号"""
        self._update_savings_display()
        self.exclude_changed.emit()

    def _is_module_used(self, module_name: str) -> bool:
        """检查模块是否被项目使用"""
        mod_lower = module_name.lower()
        for imp in self._used_imports:
            imp_lower = imp.lower()
            if imp_lower == mod_lower or imp_lower.startswith(mod_lower + "."):
                return True
            if '.' in imp_lower:
                parts = imp_lower.split('.')
                if mod_lower in parts:
                    return True
                # 也检查完整限定名匹配
                # 例: module_name="PySide6.QtWidgets", imp="PySide6.QtWidgets"
                if mod_lower == imp_lower:
                    return True
        return False

    def get_excludes(self) -> list:
        excludes = []
        for mod_name, cb in self._module_checkboxes.items():
            if not cb.isChecked() and cb.isEnabled():
                excludes.append(mod_name)
        return excludes

    def get_estimated_savings(self) -> float:
        savings = 0
        profile_modules = getattr(self._profile, 'modules', {})
        for mod_name, cb in self._module_checkboxes.items():
            if not cb.isChecked() and cb.isEnabled():
                mod_info = profile_modules.get(mod_name)
                if mod_info:
                    savings += getattr(mod_info, 'size_mb', 0)
        return savings

    def _update_savings_display(self):
        savings = self.get_estimated_savings()
        profile_modules = getattr(self._profile, 'modules', {})
        total = sum(
            getattr(m, 'size_mb', 0) for m in profile_modules.values()
        )
        percent = int(savings / total * 100) if total > 0 else 0
        self.savings_bar.setValue(percent)
        self.savings_label.setText(f"💡 预计节省: {savings:.0f} MB ({percent}%)")

    def apply_recommended(self):
        """推荐: 排除未使用的模块"""
        for mod_name, cb in self._module_checkboxes.items():
            if cb.isEnabled():
                cb.setChecked(self._is_module_used(mod_name))
        self._update_savings_display()

    def apply_aggressive(self):
        """激进: 只保留明确使用的，数据文件全排除"""
        for mod_name, cb in self._module_checkboxes.items():
            if cb.isEnabled():
                cb.setChecked(self._is_module_used(mod_name))
        for cb in self._data_checkboxes.values():
            cb.setChecked(False)
        self._update_savings_display()

    def keep_all(self):
        """全部保留"""
        for cb in self._module_checkboxes.values():
            if cb.isEnabled():
                cb.setChecked(True)
        for cb in self._data_checkboxes.values():
            cb.setChecked(True)
        self._update_savings_display()

    def apply_excludes(self, excludes: list):
        """应用指定的排除列表"""
        for mod_name, cb in self._module_checkboxes.items():
            if cb.isEnabled():
                cb.setChecked(mod_name not in excludes)
        self._update_savings_display()
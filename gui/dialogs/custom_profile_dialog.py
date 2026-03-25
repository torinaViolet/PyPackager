"""自定义库裁剪 Profile 对话框"""

import os
import json

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QGroupBox,
    QFormLayout, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSpinBox, QCheckBox,
    QDialogButtonBox, QScrollArea, QWidget,
)
from PySide6.QtCore import Qt, Signal


class CustomProfileDialog(QDialog):
    """自定义库裁剪 Profile 创建/编辑对话框"""

    profile_created = Signal(str)  # 发送生成的 profile 文件路径

    def __init__(self, project_dir: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("📦 自定义库裁剪配置")
        self.setMinimumSize(700, 600)
        self._project_dir = project_dir
        self._modules = []  # [{"name", "size_mb", "description", "is_essential", "dependencies"}]
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        desc = QLabel(
            "为任意 Python 库创建裁剪配置。定义子模块信息后，"
            "扫描时将自动识别并提供裁剪建议。"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(desc)

        # ─── 滚动区域 ─────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(12)

        # ─── 库基本信息 ─────────────────────────────
        info_group = QGroupBox("库基本信息")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(10)

        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("例如: SciPy")
        info_layout.addRow("库显示名:", self.edit_name)

        self.edit_package = QLineEdit()
        self.edit_package.setPlaceholderText("例如: scipy (pip install 时的名称)")
        info_layout.addRow("包名:", self.edit_package)

        self.edit_import = QLineEdit()
        self.edit_import.setPlaceholderText("例如: scipy (import 时的名称)")
        info_layout.addRow("导入名:", self.edit_import)

        self.spin_total_size = QSpinBox()
        self.spin_total_size.setRange(1, 5000)
        self.spin_total_size.setValue(50)
        self.spin_total_size.setSuffix(" MB")
        info_layout.addRow("预估总大小:", self.spin_total_size)

        self.edit_description = QLineEdit()
        self.edit_description.setPlaceholderText("例如: 科学计算库")
        info_layout.addRow("描述:", self.edit_description)

        content_layout.addWidget(info_group)

        # ─── 子模块管理 ─────────────────────────────
        mod_group = QGroupBox("子模块列表")
        mod_layout = QVBoxLayout(mod_group)

        # 工具栏
        mod_toolbar = QHBoxLayout()
        self.btn_add_mod = QPushButton("➕ 添加子模块")
        self.btn_add_mod.clicked.connect(self._on_add_module)
        mod_toolbar.addWidget(self.btn_add_mod)

        self.btn_remove_mod = QPushButton("🗑️ 移除选中")
        self.btn_remove_mod.clicked.connect(self._on_remove_module)
        mod_toolbar.addWidget(self.btn_remove_mod)

        self.btn_auto_detect = QPushButton("🔍 自动检测子模块")
        self.btn_auto_detect.setToolTip("根据导入名自动检测已安装库的子模块")
        self.btn_auto_detect.clicked.connect(self._on_auto_detect)
        mod_toolbar.addWidget(self.btn_auto_detect)

        mod_toolbar.addStretch()
        mod_layout.addLayout(mod_toolbar)

        # 子模块表格
        self.mod_table = QTableWidget()
        self.mod_table.setColumnCount(5)
        self.mod_table.setHorizontalHeaderLabels([
            "子模块名", "大小(MB)", "描述", "必需", "依赖"
        ])
        self.mod_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.mod_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.mod_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.mod_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.mod_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.mod_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.mod_table.setAlternatingRowColors(True)
        self.mod_table.verticalHeader().setVisible(False)
        mod_layout.addWidget(self.mod_table)

        content_layout.addWidget(mod_group)

        # ─── 隐藏导入 ─────────────────────────────
        hidden_group = QGroupBox("常见隐藏导入 (可选)")
        hidden_layout = QVBoxLayout(hidden_group)

        self.edit_hidden_imports = QLineEdit()
        self.edit_hidden_imports.setPlaceholderText(
            "逗号分隔，例如: scipy._lib.messagestream, scipy.special._ufuncs"
        )
        hidden_layout.addWidget(self.edit_hidden_imports)

        content_layout.addWidget(hidden_group)
        content_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

        # ─── 按钮栏 ─────────────────────────────
        btn_layout = QHBoxLayout()

        self.btn_import_json = QPushButton("📂 导入 JSON")
        self.btn_import_json.clicked.connect(self._on_import_json)
        btn_layout.addWidget(self.btn_import_json)

        self.btn_export_json = QPushButton("💾 导出 JSON")
        self.btn_export_json.clicked.connect(self._on_export_json)
        btn_layout.addWidget(self.btn_export_json)

        btn_layout.addStretch()

        self.btn_generate = QPushButton("🚀 生成并注册")
        self.btn_generate.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; "
            "font-weight: bold; border: none; padding: 8px 20px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #219a52; }"
        )
        self.btn_generate.clicked.connect(self._on_generate)
        btn_layout.addWidget(self.btn_generate)

        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)

    def _on_add_module(self):
        """添加子模块行"""
        row = self.mod_table.rowCount()
        self.mod_table.insertRow(row)
        self.mod_table.setItem(row, 0, QTableWidgetItem(""))
        self.mod_table.setItem(row, 1, QTableWidgetItem("5"))
        self.mod_table.setItem(row, 2, QTableWidgetItem(""))

        # 必需列用 checkbox
        chk_item = QTableWidgetItem()
        chk_item.setFlags(chk_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        chk_item.setCheckState(Qt.CheckState.Unchecked)
        self.mod_table.setItem(row, 3, chk_item)

        self.mod_table.setItem(row, 4, QTableWidgetItem(""))

    def _on_remove_module(self):
        """移除选中的子模块"""
        rows = set()
        for item in self.mod_table.selectedItems():
            rows.add(item.row())
        for row in sorted(rows, reverse=True):
            self.mod_table.removeRow(row)

    def _on_auto_detect(self):
        """自动检测已安装库的子模块"""
        import_name = self.edit_import.text().strip()
        if not import_name:
            QMessageBox.warning(self, "警告", "请先填写导入名。")
            return

        try:
            import importlib
            import pkgutil

            mod = importlib.import_module(import_name)
            if not hasattr(mod, '__path__'):
                QMessageBox.information(
                    self, "提示",
                    f"'{import_name}' 不是一个包 (没有子模块)。"
                )
                return

            submodules = []
            for importer, modname, ispkg in pkgutil.iter_modules(mod.__path__):
                # 跳过私有模块和测试
                if modname.startswith('_') or modname in ('test', 'tests', 'testing'):
                    continue
                submodules.append(modname)

            if not submodules:
                QMessageBox.information(self, "提示", "未检测到公开子模块。")
                return

            # 清空并填充表格
            self.mod_table.setRowCount(0)
            for sub in sorted(submodules):
                row = self.mod_table.rowCount()
                self.mod_table.insertRow(row)
                self.mod_table.setItem(row, 0, QTableWidgetItem(sub))
                self.mod_table.setItem(row, 1, QTableWidgetItem("5"))
                self.mod_table.setItem(row, 2, QTableWidgetItem(""))

                chk_item = QTableWidgetItem()
                chk_item.setFlags(chk_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                chk_item.setCheckState(Qt.CheckState.Unchecked)
                self.mod_table.setItem(row, 3, chk_item)

                self.mod_table.setItem(row, 4, QTableWidgetItem(""))

            QMessageBox.information(
                self, "成功",
                f"检测到 {len(submodules)} 个子模块。\n"
                "请手动补充各模块的大小估算、描述和依赖关系。"
            )

        except ImportError:
            QMessageBox.warning(
                self, "警告",
                f"无法导入 '{import_name}'，请确认已安装该库。"
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"检测失败: {e}")

    def _collect_modules(self) -> list:
        """从表格收集模块数据"""
        modules = []
        for row in range(self.mod_table.rowCount()):
            name_item = self.mod_table.item(row, 0)
            size_item = self.mod_table.item(row, 1)
            desc_item = self.mod_table.item(row, 2)
            essential_item = self.mod_table.item(row, 3)
            deps_item = self.mod_table.item(row, 4)

            name = name_item.text().strip() if name_item else ""
            if not name:
                continue

            try:
                size = float(size_item.text()) if size_item else 5.0
            except ValueError:
                size = 5.0

            modules.append({
                "name": name,
                "size_mb": size,
                "description": desc_item.text().strip() if desc_item else "",
                "is_essential": (
                    essential_item.checkState() == Qt.CheckState.Checked
                    if essential_item else False
                ),
                "dependencies": [
                    d.strip() for d in (deps_item.text() if deps_item else "").split(",")
                    if d.strip()
                ],
            })
        return modules

    def _to_dict(self) -> dict:
        """将所有配置导出为字典"""
        hidden = [
            h.strip()
            for h in self.edit_hidden_imports.text().split(",")
            if h.strip()
        ]
        return {
            "name": self.edit_name.text().strip(),
            "package_name": self.edit_package.text().strip(),
            "import_name": self.edit_import.text().strip(),
            "total_size_mb": self.spin_total_size.value(),
            "description": self.edit_description.text().strip(),
            "modules": self._collect_modules(),
            "common_hidden_imports": hidden,
        }

    def _from_dict(self, data: dict):
        """从字典恢复配置"""
        self.edit_name.setText(data.get("name", ""))
        self.edit_package.setText(data.get("package_name", ""))
        self.edit_import.setText(data.get("import_name", ""))
        self.spin_total_size.setValue(data.get("total_size_mb", 50))
        self.edit_description.setText(data.get("description", ""))
        self.edit_hidden_imports.setText(
            ", ".join(data.get("common_hidden_imports", []))
        )

        # 填充子模块表格
        self.mod_table.setRowCount(0)
        for mod in data.get("modules", []):
            row = self.mod_table.rowCount()
            self.mod_table.insertRow(row)
            self.mod_table.setItem(row, 0, QTableWidgetItem(mod.get("name", "")))
            self.mod_table.setItem(row, 1, QTableWidgetItem(str(mod.get("size_mb", 5))))
            self.mod_table.setItem(row, 2, QTableWidgetItem(mod.get("description", "")))

            chk_item = QTableWidgetItem()
            chk_item.setFlags(chk_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            chk_item.setCheckState(
                Qt.CheckState.Checked if mod.get("is_essential") else Qt.CheckState.Unchecked
            )
            self.mod_table.setItem(row, 3, chk_item)

            deps_str = ", ".join(mod.get("dependencies", []))
            self.mod_table.setItem(row, 4, QTableWidgetItem(deps_str))

    def _on_import_json(self):
        """导入 JSON 配置"""
        path, _ = QFileDialog.getOpenFileName(
            self, "导入裁剪配置", "",
            "JSON 文件 (*.json);;所有文件 (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._from_dict(data)
            QMessageBox.information(self, "成功", f"已导入配置: {path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败: {e}")

    def _on_export_json(self):
        """导出 JSON 配置"""
        data = self._to_dict()
        if not data["name"]:
            QMessageBox.warning(self, "警告", "请填写库显示名。")
            return

        default_name = f"{data['import_name'] or 'custom'}_profile.json"
        path, _ = QFileDialog.getSaveFileName(
            self, "导出裁剪配置", default_name,
            "JSON 文件 (*.json)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "成功", f"已导出配置: {path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")

    def _on_generate(self):
        """生成 Profile 类文件并注册"""
        data = self._to_dict()

        # 验证
        if not data["name"]:
            QMessageBox.warning(self, "警告", "请填写库显示名。")
            return
        if not data["import_name"]:
            QMessageBox.warning(self, "警告", "请填写导入名。")
            return
        if not data["modules"]:
            QMessageBox.warning(self, "警告", "请至少添加一个子模块。")
            return

        # 生成 Python 代码
        code = self._generate_profile_code(data)
        safe_name = data["import_name"].replace(".", "_").lower()
        filename = f"{safe_name}_profile.py"
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "core", "library_profiles", filename
        )
        filepath = os.path.normpath(filepath)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)

            # 动态注册到 PROFILE_REGISTRY
            self._register_profile(data, safe_name, filepath)

            QMessageBox.information(
                self, "成功",
                f"已生成并注册裁剪配置!\n\n"
                f"文件: {filepath}\n"
                f"库名: {data['name']}\n"
                f"子模块数: {len(data['modules'])}\n\n"
                f"重新扫描项目即可看到新的裁剪选项。"
            )
            self.profile_created.emit(filepath)
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成失败: {e}")

    def _generate_profile_code(self, data: dict) -> str:
        """生成 Profile 类的 Python 代码"""
        class_name = "".join(
            w.capitalize() for w in data["name"].replace("-", " ").split()
        ) + "Profile"

        lines = [
            f'"""',
            f'{data["name"]} 裁剪配置',
            f'自动生成 — 可手动编辑调整',
            f'"""',
            f'from core.library_profiles.base_profile import BaseProfile, ModuleInfo',
            f'',
            f'',
            f'class {class_name}(BaseProfile):',
            f'    """{data["name"]} 裁剪方案。"""',
            f'',
            f'    name = "{data["name"]}"',
            f'    package_name = "{data["package_name"]}"',
            f'    import_name = "{data["import_name"]}"',
            f'    total_size_mb = {data["total_size_mb"]}',
            f'',
            f'    modules = {{',
        ]

        for mod in data["modules"]:
            deps_str = ", ".join(f'"{d}"' for d in mod.get("dependencies", []))
            lines.append(
                f'        "{mod["name"]}": ModuleInfo('
                f'size_mb={mod["size_mb"]}, '
                f'description="{mod["description"]}", '
                f'dependencies=[{deps_str}], '
                f'is_essential={mod["is_essential"]},'
                f'),'
            )

        lines.append('    }')
        lines.append('')

        # 隐藏导入
        hidden = data.get("common_hidden_imports", [])
        if hidden:
            hidden_str = ", ".join(f'"{h}"' for h in hidden)
            lines.append(f'    common_hidden_imports = [{hidden_str}]')
        else:
            lines.append('    common_hidden_imports = []')

        lines.append('')
        lines.append('    excludable_data = []')
        lines.append('')

        return "\n".join(lines)

    def _register_profile(self, data: dict, safe_name: str, filepath: str):
        """动态注册 profile 到 PROFILE_REGISTRY"""
        import importlib.util

        # 动态加载生成的模块
        spec = importlib.util.spec_from_file_location(
            f"core.library_profiles.{safe_name}_profile", filepath
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 找到 Profile 类
        class_name = "".join(
            w.capitalize() for w in data["name"].replace("-", " ").split()
        ) + "Profile"
        profile_cls = getattr(module, class_name)

        # 注册到 PROFILE_REGISTRY
        from core.library_profiles import PROFILE_REGISTRY
        PROFILE_REGISTRY[data["import_name"]] = profile_cls
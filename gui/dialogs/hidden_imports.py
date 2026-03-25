"""隐藏导入管理对话框"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QLineEdit,
    QMessageBox, QDialogButtonBox, QGroupBox,
)
from PySide6.QtCore import Qt


# 常见库的隐藏导入数据库
COMMON_HIDDEN_IMPORTS = {
    "PIL": [
        "PIL._tkinter_finder",
        "PIL._imagingtk",
    ],
    "sklearn": [
        "sklearn.utils._typedefs",
        "sklearn.utils._heap",
        "sklearn.utils._sorting",
        "sklearn.utils._vector_sentinel",
        "sklearn.neighbors._partition_nodes",
    ],
    "pandas": [
        "pandas._libs.tslibs.timedeltas",
        "pandas._libs.tslibs.nattype",
        "pandas._libs.tslibs.np_datetime",
    ],
    "scipy": [
        "scipy._lib.messagestream",
        "scipy.special._ufuncs_cxx",
        "scipy.linalg.cython_blas",
        "scipy.linalg.cython_lapack",
    ],
    "cryptography": [
        "cryptography.hazmat.primitives.kdf.pbkdf2",
        "cryptography.hazmat.backends.openssl",
    ],
    "sqlalchemy": [
        "sqlalchemy.sql.default_comparator",
        "sqlalchemy.ext.baked",
    ],
    "PySide6": [
        "PySide6.QtSvg",
        "PySide6.QtXml",
    ],
    "PyQt6": [
        "PyQt6.QtSvg",
        "PyQt6.QtXml",
    ],
    "pkg_resources": [
        "pkg_resources.extern",
        "pkg_resources._vendor",
    ],
    "numpy": [
        "numpy.core._methods",
        "numpy.core._dtype_ctypes",
    ],
    "matplotlib": [
        "matplotlib.backends.backend_tkagg",
        "matplotlib.backends.backend_agg",
    ],
}


class HiddenImportsDialog(QDialog):
    """隐藏导入管理对话框"""

    def __init__(self, current_hidden_imports: list = None, detected_libs: list = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("隐藏导入管理")
        self.setMinimumSize(600, 500)
        self._result_imports = list(current_hidden_imports or [])
        self._detected_libs = detected_libs or []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # --- 说明 ---
        desc = QLabel(
            "某些库使用动态导入，PyInstaller 无法自动检测。\n"
            "如果打包后运行出现 ModuleNotFoundError，请在此添加缺失的模块。"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)

        # --- 当前隐藏导入列表 ---
        current_group = QGroupBox("当前隐藏导入列表")
        current_layout = QVBoxLayout(current_group)

        self.imports_list = QListWidget()
        for imp in self._result_imports:
            self.imports_list.addItem(imp)
        current_layout.addWidget(self.imports_list)

        # 手动添加
        add_layout = QHBoxLayout()
        self.add_input = QLineEdit()
        self.add_input.setPlaceholderText("输入模块名，如: sklearn.utils._typedefs")
        self.add_input.returnPressed.connect(self._on_add)
        add_layout.addWidget(self.add_input)

        btn_add = QPushButton("➕ 添加")
        btn_add.clicked.connect(self._on_add)
        add_layout.addWidget(btn_add)

        btn_remove = QPushButton("🗑️ 移除选中")
        btn_remove.clicked.connect(self._on_remove)
        add_layout.addWidget(btn_remove)

        current_layout.addLayout(add_layout)
        layout.addWidget(current_group)

        # --- 常见隐藏导入建议 ---
        suggest_group = QGroupBox("💡 常见隐藏导入 (点击添加)")
        suggest_layout = QVBoxLayout(suggest_group)

        # 根据检测到的库显示建议
        has_suggestions = False
        for lib_name in self._detected_libs:
            base_lib = lib_name.split('.')[0]
            suggestions = COMMON_HIDDEN_IMPORTS.get(base_lib, [])
            if suggestions:
                has_suggestions = True
                lib_label = QLabel(f"📦 {base_lib}:")
                lib_label.setStyleSheet("font-weight: bold; margin-top: 4px;")
                suggest_layout.addWidget(lib_label)

                btn_row = QHBoxLayout()
                for suggestion in suggestions:
                    btn = QPushButton(f"+ {suggestion}")
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #3498db;
                            color: white;
                            border-radius: 10px;
                            padding: 3px 8px;
                            font-size: 11px;
                            border: none;
                        }
                        QPushButton:hover { background-color: #2980b9; }
                    """)
                    btn.clicked.connect(lambda checked, s=suggestion: self._add_import(s))
                    btn_row.addWidget(btn)
                btn_row.addStretch()
                suggest_layout.addLayout(btn_row)

        if not has_suggestions:
            no_suggest = QLabel("未检测到需要隐藏导入的库，或暂无建议。")
            no_suggest.setStyleSheet("color: #888;")
            suggest_layout.addWidget(no_suggest)

        # 显示所有可选的库
        all_btn_layout = QHBoxLayout()
        all_label = QLabel("查看所有库建议:")
        all_label.setStyleSheet("color: #888; font-size: 11px;")
        all_btn_layout.addWidget(all_label)
        for lib_name in sorted(COMMON_HIDDEN_IMPORTS.keys()):
            btn = QPushButton(lib_name)
            btn.setMaximumWidth(100)
            btn.setStyleSheet("font-size: 11px; padding: 2px 6px;")
            btn.clicked.connect(lambda checked, ln=lib_name: self._show_lib_suggestions(ln))
            all_btn_layout.addWidget(btn)
        all_btn_layout.addStretch()
        suggest_layout.addLayout(all_btn_layout)

        layout.addWidget(suggest_group)

        # --- 按钮 ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_add(self):
        """添加手动输入的模块"""
        text = self.add_input.text().strip()
        if text:
            self._add_import(text)
            self.add_input.clear()

    def _add_import(self, module_name: str):
        """添加一个隐藏导入"""
        if module_name not in self._result_imports:
            self._result_imports.append(module_name)
            self.imports_list.addItem(module_name)

    def _on_remove(self):
        """移除选中的隐藏导入"""
        for item in self.imports_list.selectedItems():
            row = self.imports_list.row(item)
            self.imports_list.takeItem(row)
            if item.text() in self._result_imports:
                self._result_imports.remove(item.text())

    def _show_lib_suggestions(self, lib_name: str):
        """显示某个库的所有建议"""
        suggestions = COMMON_HIDDEN_IMPORTS.get(lib_name, [])
        if suggestions:
            for s in suggestions:
                self._add_import(s)

    def get_hidden_imports(self) -> list:
        """获取最终的隐藏导入列表"""
        return list(self._result_imports)
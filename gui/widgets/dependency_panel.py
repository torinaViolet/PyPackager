"""依赖管理面板 - 显示和管理项目依赖"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLabel, QLineEdit, QMessageBox,
    QFrame, QScrollArea,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QColor, QIcon


class DependencyPanel(QWidget):
    """依赖管理面板"""

    dependencies_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dependencies = []  # list of dict: {name, status, type, version}
        self._setup_ui()

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- 标题 ---
        title = QLabel("📦 依赖管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("管理项目依赖库，自动扫描 import 语句或手动添加。")
        desc.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(desc)

        # --- 工具栏 ---
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_scan = QPushButton("🔍 自动扫描")
        self.btn_scan.setToolTip("扫描项目文件，自动发现依赖")
        toolbar.addWidget(self.btn_scan)

        self.btn_add = QPushButton("➕ 手动添加")
        self.btn_add.clicked.connect(self._on_add_dependency)
        toolbar.addWidget(self.btn_add)

        self.btn_remove = QPushButton("🗑️ 移除选中")
        self.btn_remove.clicked.connect(self._on_remove_selected)
        toolbar.addWidget(self.btn_remove)

        toolbar.addStretch()

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索依赖...")
        self.search_input.setMaximumWidth(200)
        self.search_input.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_input)

        layout.addLayout(toolbar)

        # --- 依赖表格 ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["模块名", "版本", "状态", "来源"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # --- 隐藏导入建议区 ---
        suggestion_frame = QFrame()
        suggestion_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        suggestion_layout = QVBoxLayout(suggestion_frame)

        suggestion_title = QLabel("⚠️ 常见隐藏导入建议")
        suggestion_title.setStyleSheet("font-weight: bold; color: #e67e22;")
        suggestion_layout.addWidget(suggestion_title)

        self.suggestion_area = QHBoxLayout()
        suggestion_layout.addLayout(self.suggestion_area)
        self.suggestion_label = QLabel("请先执行自动扫描以获取建议。")
        self.suggestion_label.setStyleSheet("color: #888; font-size: 12px;")
        self.suggestion_area.addWidget(self.suggestion_label)
        self.suggestion_area.addStretch()

        layout.addWidget(suggestion_frame)

                # --- 统计信息 ---
        self.stats_label = QLabel("共 0 个依赖")
        self.stats_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.stats_label)

        scroll.setWidget(content_widget)
        outer_layout.addWidget(scroll)

    def set_dependencies(self, dependencies: list):
        """
        设置依赖列表
        dependencies: [{"name": str, "version": str, "status": str, "source": str}, ...]
        """
        self._dependencies = dependencies
        self._refresh_table()

    def get_dependencies(self) -> list:
        """获取当前依赖列表"""
        return list(self._dependencies)

    def add_dependency(self, name: str, version: str = "", status: str = "✅ 已安装",
                       source: str = "➕ 手动添加"):
        """添加一个依赖"""
        # 检查是否已存在
        for dep in self._dependencies:
            if dep["name"].lower() == name.lower():
                return False

        self._dependencies.append({
            "name": name,
            "version": version,
            "status": status,
            "source": source,
        })
        self._refresh_table()
        self.dependencies_changed.emit()
        return True

    def set_suggestions(self, suggestions: list):
        """设置隐藏导入建议"""
        # 清除旧的建议按钮
        while self.suggestion_area.count():
            item = self.suggestion_area.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not suggestions:
            label = QLabel("未发现需要的隐藏导入。")
            label.setStyleSheet("color: #27ae60;")
            self.suggestion_area.addWidget(label)
        else:
            for suggestion in suggestions[:10]:  # 最多显示10个
                btn = QPushButton(f"+ {suggestion}")
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border-radius: 10px;
                        padding: 4px 10px;
                        font-size: 11px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                btn.clicked.connect(lambda checked, s=suggestion: self._on_add_suggestion(s))
                self.suggestion_area.addWidget(btn)

        self.suggestion_area.addStretch()

    def _refresh_table(self):
        """刷新表格显示"""
        self.table.setRowCount(len(self._dependencies))
        for row, dep in enumerate(self._dependencies):
            self.table.setItem(row, 0, QTableWidgetItem(dep.get("name", "")))
            self.table.setItem(row, 1, QTableWidgetItem(dep.get("version", "")))

            status_item = QTableWidgetItem(dep.get("status", ""))
            status = dep.get("status", "")
            if "已安装" in status:
                status_item.setForeground(QColor("#27ae60"))
            elif "隐藏" in status or "警告" in status:
                status_item.setForeground(QColor("#e67e22"))
            elif "缺失" in status:
                status_item.setForeground(QColor("#e74c3c"))
            self.table.setItem(row, 2, status_item)

            self.table.setItem(row, 3, QTableWidgetItem(dep.get("source", "")))

        self.stats_label.setText(f"共 {len(self._dependencies)} 个依赖")

    def _on_add_dependency(self):
        """手动添加依赖"""
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "添加依赖", "请输入模块名称:")
        if ok and name.strip():
            name = name.strip()
            if not self.add_dependency(name):
                QMessageBox.information(self, "提示", f"依赖 '{name}' 已存在。")

    def _on_remove_selected(self):
        """移除选中的依赖"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            return

        # 从后往前删除，避免索引偏移
        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(self._dependencies):
                self._dependencies.pop(row)

        self._refresh_table()
        self.dependencies_changed.emit()

    def _on_search(self, text: str):
        """过滤搜索"""
        search_text = text.lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            if name_item:
                match = search_text in name_item.text().lower()
                self.table.setRowHidden(row, not match)

    def _on_add_suggestion(self, module_name: str):
        """添加建议的隐藏导入"""
        self.add_dependency(module_name, status="⚠️ 隐藏导入", source="💡 建议添加")

    def get_config(self) -> dict:
        """获取面板配置"""
        hidden_imports = []
        excludes = []
        for dep in self._dependencies:
            if "隐藏" in dep.get("status", ""):
                hidden_imports.append(dep["name"])
        return {
            "hidden_imports": hidden_imports,
            "all_dependencies": self._dependencies,
        }

    def set_config(self, config: dict):
        """从配置恢复面板状态"""
        deps = config.get("all_dependencies", [])
        if deps:
            self._dependencies = deps
            self._refresh_table()
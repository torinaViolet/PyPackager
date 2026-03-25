"""资源文件管理面板 - 添加和管理需要打包的数据文件"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QLabel, QFileDialog, QMessageBox,
    QFrame, QScrollArea,
)
from PySide6.QtCore import Signal, Qt


class ResourcePanel(QWidget):
    """资源文件管理面板"""

    resources_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._resources = []  # list of dict: {"src": str, "dst": str, "is_dir": bool}
        self._project_dir = ""
        self._setup_ui()

    def set_project_dir(self, project_dir: str):
        """设置项目目录，用于计算相对路径"""
        self._project_dir = project_dir

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
        title = QLabel("📁 资源文件管理")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        desc = QLabel("添加需要打包进程序的数据文件和目录（图片、配置文件、数据库等）。")
        desc.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(desc)

        # --- 工具栏 ---
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        self.btn_add_file = QPushButton("📄 添加文件")
        self.btn_add_file.clicked.connect(self._on_add_file)
        toolbar.addWidget(self.btn_add_file)

        self.btn_add_dir = QPushButton("📂 添加目录")
        self.btn_add_dir.clicked.connect(self._on_add_dir)
        toolbar.addWidget(self.btn_add_dir)

        self.btn_remove = QPushButton("🗑️ 移除选中")
        self.btn_remove.clicked.connect(self._on_remove_selected)
        toolbar.addWidget(self.btn_remove)

        self.btn_edit_dst = QPushButton("✏️ 编辑目标路径")
        self.btn_edit_dst.clicked.connect(self._on_edit_dst)
        toolbar.addWidget(self.btn_edit_dst)

        toolbar.addStretch()

        self.btn_gen_helper = QPushButton("🛠 生成 resource_path")
        self.btn_gen_helper.setToolTip("生成资源路径辅助代码，兼容开发和打包环境")
        self.btn_gen_helper.clicked.connect(self._on_gen_helper)
        toolbar.addWidget(self.btn_gen_helper)
        layout.addLayout(toolbar)

        # --- 资源文件表格 ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["类型", "源路径", "打包内目标路径"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # --- 提示区 ---
        tip_frame = QFrame()
        tip_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        tip_layout = QVBoxLayout(tip_frame)

        tip_title = QLabel("💡 提示")
        tip_title.setStyleSheet("font-weight: bold; color: #3498db;")
        tip_layout.addWidget(tip_title)

        tip_text = QLabel(
            "• 打包后的资源文件可通过以下方式访问:\n"
            "  import sys, os\n"
            "  base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))\n"
            "  file_path = os.path.join(base, 'assets', 'logo.png')\n\n"
            "• 「目标路径」指文件在打包程序内部的相对路径"
        )
        tip_text.setStyleSheet("color: #666; font-size: 12px; font-family: Consolas, monospace;")
        tip_text.setWordWrap(True)
        tip_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        tip_layout.addWidget(tip_text)

        layout.addWidget(tip_frame)

                # --- 统计信息 ---
        self.stats_label = QLabel("共 0 个资源文件/目录")
        self.stats_label.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.stats_label)

        scroll.setWidget(content_widget)
        outer_layout.addWidget(scroll)

    def _refresh_table(self):
        """刷新表格"""
        self.table.setRowCount(len(self._resources))
        for row, res in enumerate(self._resources):
            type_str = "📂 目录" if res.get("is_dir") else "📄 文件"
            self.table.setItem(row, 0, QTableWidgetItem(type_str))
            self.table.setItem(row, 1, QTableWidgetItem(res.get("src", "")))
            self.table.setItem(row, 2, QTableWidgetItem(res.get("dst", "")))

        self.stats_label.setText(f"共 {len(self._resources)} 个资源文件/目录")

    def _on_add_file(self):
        """添加资源文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择资源文件",
            self._project_dir or "",
            "所有文件 (*)"
        )
        for f in files:
            self._add_resource(f, is_dir=False)

    def _on_add_dir(self):
        """添加资源目录"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "选择资源目录",
            self._project_dir or "",
        )
        if dir_path:
            self._add_resource(dir_path, is_dir=True)

    def _add_resource(self, src: str, is_dir: bool):
        """添加一个资源项目"""
        import os
        # 检查是否已存在
        for res in self._resources:
            if res["src"] == src:
                return

        # 计算一个默认的目标路径
        if self._project_dir:
            try:
                rel_path = os.path.relpath(src, self._project_dir)
            except ValueError:
                rel_path = os.path.basename(src)
        else:
            rel_path = os.path.basename(src)

        # 目标路径：对于文件取其父目录名，对于目录取目录名
        if is_dir:
            dst = os.path.basename(src)
        else:
            parent = os.path.basename(os.path.dirname(src))
            dst = parent if parent and parent != '.' else '.'

        self._resources.append({
            "src": src,
            "dst": dst,
            "is_dir": is_dir,
        })
        self._refresh_table()
        self.resources_changed.emit()

    def _on_remove_selected(self):
        """移除选中资源"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            return

        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(self._resources):
                self._resources.pop(row)

        self._refresh_table()
        self.resources_changed.emit()

    def _on_edit_dst(self):
        """编辑目标路径"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if len(selected_rows) != 1:
            QMessageBox.information(self, "提示", "请选择一行进行编辑。")
            return

        row = selected_rows.pop()
        from PySide6.QtWidgets import QInputDialog
        current_dst = self._resources[row]["dst"]
        new_dst, ok = QInputDialog.getText(
            self, "编辑目标路径",
            "请输入打包内的目标路径:",
            text=current_dst
        )
        if ok and new_dst.strip():
            self._resources[row]["dst"] = new_dst.strip()
            self._refresh_table()
            self.resources_changed.emit()

    def get_config(self) -> dict:
        """获取面板配置"""
        return {
            "data_files": [
                {"src": r["src"], "dst": r["dst"], "is_dir": r.get("is_dir", False)}
                for r in self._resources
            ]
        }

    def set_config(self, config: dict):
        """从配置恢复面板状态"""
        self._resources = []
        for item in config.get("data_files", []):
            self._resources.append({
                "src": item.get("src", ""),
                "dst": item.get("dst", "."),
                "is_dir": item.get("is_dir", False),
            })
        self._refresh_table()

    def _on_gen_helper(self):
        """打开 resource_path 代码生成器"""
        from gui.dialogs.resource_helper_dialog import ResourceHelperDialog
        dialog = ResourceHelperDialog(self._project_dir, parent=self)
        dialog.exec()
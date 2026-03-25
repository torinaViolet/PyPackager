"""环境选择器对话框 - 选择 Python 解释器和虚拟环境"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QListWidget, QListWidgetItem, QFileDialog,
    QDialogButtonBox, QGroupBox, QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal as QSignal


class PythonScanWorker(QThread):
    """后台扫描 Python 解释器"""
    finished = QSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            from core.venv_detector import VenvDetector
            detector = VenvDetector()
            pythons = detector.find_all_pythons()
            self.finished.emit(pythons)
        except Exception as e:
            self.finished.emit([])


class EnvSelectorDialog(QDialog):
    """Python 环境选择器"""

    def __init__(self, current_python: str = "", project_dir: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("🐍 选择 Python 环境")
        self.setMinimumSize(550, 450)
        self._current_python = current_python
        self._project_dir = project_dir
        self._selected_python = current_python
        self._setup_ui()
        self._start_scan()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # --- 说明 ---
        desc = QLabel(
            "选择用于打包的 Python 解释器。\n"
            "建议使用项目的虚拟环境来确保依赖正确。"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666;")
        layout.addWidget(desc)

        # --- 检测到的虚拟环境 ---
        venv_group = QGroupBox("🔍 检测到的环境")
        venv_layout = QVBoxLayout(venv_group)

        self.env_list = QListWidget()
        self.env_list.itemClicked.connect(self._on_env_selected)
        venv_layout.addWidget(self.env_list)

        self.scan_progress = QProgressBar()
        self.scan_progress.setRange(0, 0)  # 无限进度
        self.scan_progress.setMaximumHeight(3)
        venv_layout.addWidget(self.scan_progress)

        layout.addWidget(venv_group)

        # --- 手动选择 ---
        manual_group = QGroupBox("手动指定")
        manual_layout = QHBoxLayout(manual_group)

        self.btn_browse = QPushButton("📂 浏览选择 Python 解释器...")
        self.btn_browse.clicked.connect(self._on_browse)
        manual_layout.addWidget(self.btn_browse)

        layout.addWidget(manual_group)

        # --- 当前选择 ---
        self.selected_label = QLabel(f"当前选择: {self._selected_python or '未选择'}")
        self.selected_label.setStyleSheet("font-weight: bold; color: #2980b9;")
        layout.addWidget(self.selected_label)

        # --- 按钮 ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _start_scan(self):
        """开始后台扫描"""
        self.scan_worker = PythonScanWorker()
        self.scan_worker.finished.connect(self._on_scan_finished)
        self.scan_worker.start()

    def _on_scan_finished(self, pythons: list):
        """扫描完成"""
        self.scan_progress.setRange(0, 1)
        self.scan_progress.setValue(1)
        self.scan_progress.setVisible(False)

        # 如果有项目目录，先检测项目虚拟环境
        if self._project_dir:
            try:
                from core.venv_detector import VenvDetector
                detector = VenvDetector()
                venv_info = detector.detect_venv(self._project_dir)
                if venv_info.get("found"):
                    item = QListWidgetItem(
                        f"⭐ 项目虚拟环境 ({venv_info['type']}) - "
                        f"Python {venv_info['python_version']}\n"
                        f"   {venv_info['python_path']}"
                    )
                    item.setData(Qt.ItemDataRole.UserRole, venv_info['python_path'])
                    self.env_list.addItem(item)
            except Exception:
                pass

        # 添加所有找到的 Python
        for py_info in pythons:
            path = py_info.get("path", "")
            version = py_info.get("version", "unknown")
            item = QListWidgetItem(
                f"🐍 Python {version}\n"
                f"   {path}"
            )
            item.setData(Qt.ItemDataRole.UserRole, path)
            # 标记当前选中
            if path == self._current_python:
                item.setText(item.text() + "  ✅ (当前)")
            self.env_list.addItem(item)

        if self.env_list.count() == 0:
            item = QListWidgetItem("未检测到 Python 环境，请手动选择。")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.env_list.addItem(item)

    def _on_env_selected(self, item: QListWidgetItem):
        """选中一个环境"""
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self._selected_python = path
            self.selected_label.setText(f"当前选择: {path}")

    def _on_browse(self):
        """手动浏览 Python 解释器"""
        if __import__('os').name == 'nt':
            filter_str = "Python (python.exe);;所有文件 (*)"
        else:
            filter_str = "所有文件 (*)"

        path, _ = QFileDialog.getOpenFileName(
            self, "选择 Python 解释器", "", filter_str
        )
        if path:
            self._selected_python = path
            self.selected_label.setText(f"当前选择: {path}")

    def get_selected_python(self) -> str:
        """获取选中的 Python 路径"""
        return self._selected_python
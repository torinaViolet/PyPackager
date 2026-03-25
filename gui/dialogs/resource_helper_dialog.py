"""resource_path 辅助代码生成器对话框"""

import os

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QGroupBox,
    QFormLayout, QFileDialog, QApplication, QMessageBox,
    QComboBox,
)
from PySide6.QtCore import Qt


# 模板代码
TEMPLATE_STANDARD = '''\
"""
资源路径辅助模块
自动兼容开发环境和 PyInstaller 打包后环境。

用法:
    from {module_path} import resource_path

    logo = resource_path("assets/logo.png")
    config = resource_path("data/config.json")
"""
import sys
import os


def resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径。
    兼容开发环境和 PyInstaller 打包后的环境 (onefile / onedir)。

    Args:
        relative_path: 资源文件相对于项目根目录的路径

    Returns:
        资源文件的绝对路径
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后环境
        base_path = sys._MEIPASS
    else:
        # 开发环境: 以本文件所在目录为基准向上回到项目根目录
        base_path = os.path.dirname(os.path.abspath(__file__))
{parent_nav}
    return os.path.join(base_path, relative_path)
'''

TEMPLATE_CLASS = '''\
"""
资源管理器模块
提供资源路径解析、存在性检查等功能。
兼容开发环境和 PyInstaller 打包后环境。

用法:
    from {module_path} import ResourceManager

    res = ResourceManager()
    logo_path = res.get("assets/logo.png")
    if res.exists("data/config.json"):
        ...
"""
import sys
import os


class ResourceManager:
    """资源文件管理器，兼容开发环境和打包后环境。"""

    def __init__(self):
        if hasattr(sys, '_MEIPASS'):
            self._base = sys._MEIPASS
        else:
            self._base = os.path.dirname(os.path.abspath(__file__))
{parent_nav}

    def get(self, relative_path: str) -> str:
        """获取资源文件的绝对路径。"""
        return os.path.join(self._base, relative_path)

    def exists(self, relative_path: str) -> bool:
        """检查资源文件是否存在。"""
        full_path = self.get(relative_path)
        return os.path.exists(full_path)

    def read_text(self, relative_path: str, encoding: str = "utf-8") -> str:
        """读取文本资源文件。"""
        with open(self.get(relative_path), "r", encoding=encoding) as f:
            return f.read()

    def read_bytes(self, relative_path: str) -> bytes:
        """读取二进制资源文件。"""
        with open(self.get(relative_path), "rb") as f:
            return f.read()

    @property
    def base_path(self) -> str:
        """获取资源基础路径。"""
        return self._base
'''


class ResourceHelperDialog(QDialog):
    """resource_path 辅助代码生成器"""

    def __init__(self, project_dir: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("📦 资源路径辅助代码生成器")
        self.setMinimumSize(650, 550)
        self._project_dir = project_dir
        self._setup_ui()
        self._connect_signals()
        self._generate_preview()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 说明
        desc = QLabel(
            "生成 resource_path 辅助模块，让资源文件在开发环境和打包后都能正确访问。"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(desc)

        # ─── 配置分组 ─────────────────────────────
        config_group = QGroupBox("生成配置")
        config_layout = QFormLayout(config_group)
        config_layout.setSpacing(10)

        # 模板风格
        self.combo_style = QComboBox()
        self.combo_style.addItems(["简单函数 (resource_path)", "类封装 (ResourceManager)"])
        config_layout.addRow("代码风格:", self.combo_style)

        # 生成位置
        path_row = QHBoxLayout()
        self.edit_output_path = QLineEdit()
        self.edit_output_path.setPlaceholderText("例如: utils/resource_helper.py")
        if self._project_dir:
            self.edit_output_path.setText("utils/resource_helper.py")
        path_row.addWidget(self.edit_output_path)
        self.btn_browse = QPushButton("📂")
        self.btn_browse.setFixedSize(36, 36)
        self.btn_browse.setStyleSheet("QPushButton { padding: 0px; font-size: 16px; }")
        self.btn_browse.clicked.connect(self._browse_output)
        path_row.addWidget(self.btn_browse)
        config_layout.addRow("生成位置:", path_row)

        layout.addWidget(config_group)

        # ─── 代码预览 ─────────────────────────────
        preview_group = QGroupBox("代码预览")
        preview_layout = QVBoxLayout(preview_group)

        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setStyleSheet(
            "font-family: 'Cascadia Code', 'Consolas', monospace; font-size: 12px;"
        )
        preview_layout.addWidget(self.code_preview)

        layout.addWidget(preview_group)

        # ─── 按钮栏 ─────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_copy = QPushButton("📋 复制代码")
        self.btn_copy.clicked.connect(self._copy_code)
        btn_layout.addWidget(self.btn_copy)

        self.btn_save = QPushButton("💾 保存到文件")
        self.btn_save.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; "
            "font-weight: bold; border: none; padding: 8px 20px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #219a52; }"
        )
        self.btn_save.clicked.connect(self._save_file)
        btn_layout.addWidget(self.btn_save)

        self.btn_close = QPushButton("关闭")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

    def _connect_signals(self):
        self.combo_style.currentIndexChanged.connect(self._generate_preview)
        self.edit_output_path.textChanged.connect(self._generate_preview)

    def _browse_output(self):
        """选择生成位置"""
        path, _ = QFileDialog.getSaveFileName(
            self, "选择生成位置",
            os.path.join(self._project_dir, self.edit_output_path.text()) if self._project_dir else "",
            "Python 文件 (*.py)"
        )
        if path and self._project_dir:
            try:
                rel = os.path.relpath(path, self._project_dir)
                self.edit_output_path.setText(rel.replace("\\", "/"))
            except ValueError:
                self.edit_output_path.setText(path)
        elif path:
            self.edit_output_path.setText(path)

    def _calculate_depth(self) -> int:
        """计算生成文件相对于项目根的深度"""
        rel_path = self.edit_output_path.text().strip().replace("\\", "/")
        if not rel_path:
            return 0
        parts = rel_path.split("/")
        # 减去文件名本身，剩下的是目录层数
        return max(0, len(parts) - 1)

    def _generate_preview(self):
        """生成代码预览"""
        rel_path = self.edit_output_path.text().strip().replace("\\", "/")
        depth = self._calculate_depth()

        # 生成回溯父目录的代码
        if depth == 0:
            parent_nav = ""
        else:
            lines = []
            for _ in range(depth):
                lines.append("            base_path = os.path.dirname(base_path)")
            parent_nav = "\n".join(lines) + "\n"

        # 计算 import 路径
        if rel_path:
            module_path = rel_path.replace("/", ".").replace("\\", ".")
            if module_path.endswith(".py"):
                module_path = module_path[:-3]
        else:
            module_path = "resource_helper"

        style = self.combo_style.currentIndex()
        if style == 0:
            code = TEMPLATE_STANDARD.format(
                module_path=module_path,
                parent_nav=parent_nav,
            )
        else:
            code = TEMPLATE_CLASS.format(
                module_path=module_path,
                parent_nav=parent_nav,
            )

        self.code_preview.setPlainText(code)

    def _copy_code(self):
        """复制代码到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.code_preview.toPlainText())
        QMessageBox.information(self, "提示", "代码已复制到剪贴板！")

    def _save_file(self):
        """保存到文件"""
        rel_path = self.edit_output_path.text().strip()
        if not rel_path:
            QMessageBox.warning(self, "警告", "请设置生成位置。")
            return

        if self._project_dir:
            full_path = os.path.join(self._project_dir, rel_path)
        else:
            full_path = rel_path

        # 确保目录存在
        dir_path = os.path.dirname(full_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # 检查是否已存在
        if os.path.exists(full_path):
            reply = QMessageBox.question(
                self, "确认",
                f"文件 {rel_path} 已存在，是否覆盖？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(self.code_preview.toPlainText())
            QMessageBox.information(
                self, "成功",
                f"已生成: {full_path}\n\n"
                f"使用方式:\n"
                f"  from {rel_path.replace('/', '.').replace('.py', '')} import resource_path"
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")
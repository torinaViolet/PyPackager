"""
主题管理模块
提供亮色和暗色主题样式表。
"""

# ─── 颜色定义 ──────────────────────────────────────────
COLORS = {
    "dark": {
        "bg": "#1e1e2e",
        "bg_alt": "#2a2a3d",
        "bg_card": "#313147",
        "fg": "#cdd6f4",
        "fg_dim": "#a6adc8",
        "accent": "#89b4fa",
        "accent_hover": "#74c7ec",
        "success": "#a6e3a1",
        "warning": "#f9e2af",
        "error": "#f38ba8",
        "border": "#45475a",
        "input_bg": "#313244",
        "scrollbar": "#585b70",
        "selection": "#45475a",
    },
    "light": {
        "bg": "#eff1f5",
        "bg_alt": "#e6e9ef",
        "bg_card": "#ffffff",
        "fg": "#4c4f69",
        "fg_dim": "#6c6f85",
        "accent": "#1e66f5",
        "accent_hover": "#2a7ae4",
        "success": "#40a02b",
        "warning": "#df8e1d",
        "error": "#d20f39",
        "border": "#ccd0da",
        "input_bg": "#ffffff",
        "scrollbar": "#bcc0cc",
        "selection": "#dce0e8",
    },
}


def get_stylesheet(theme: str = "dark") -> str:
    """获取完整的应用样式表。"""
    c = COLORS.get(theme, COLORS["dark"])

    return f"""
    /* ─── 全局 ────────────────────────────── */
    QMainWindow, QDialog {{
        background-color: {c['bg']};
        color: {c['fg']};
    }}

    QWidget {{
        color: {c['fg']};
        font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
        font-size: 13px;
    }}

    /* ─── 标签 ────────────────────────────── */
    QLabel {{
        color: {c['fg']};
        padding: 2px;
    }}

    QLabel[heading="true"] {{
        font-size: 16px;
        font-weight: bold;
        color: {c['accent']};
        padding: 8px 0;
    }}

    /* ─── 输入框 ──────────────────────────── */
    QLineEdit, QSpinBox, QDoubleSpinBox {{
        background-color: {c['input_bg']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 10px;
        selection-background-color: {c['accent']};
    }}

    QLineEdit:focus, QSpinBox:focus {{
        border: 1px solid {c['accent']};
    }}

    QTextEdit, QPlainTextEdit {{
        background-color: {c['input_bg']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px;
        font-family: "Cascadia Code", "Consolas", monospace;
        font-size: 12px;
    }}

    /* ─── 按钮 ────────────────────────────── */
    QPushButton {{
        background-color: {c['bg_card']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 7px 18px;
        font-weight: 500;
    }}

    QPushButton:hover {{
        background-color: {c['accent']};
        color: {c['bg']};
        border-color: {c['accent']};
    }}

    QPushButton:pressed {{
        background-color: {c['accent_hover']};
    }}

    QPushButton:disabled {{
        background-color: {c['bg_alt']};
        color: {c['fg_dim']};
        border-color: {c['border']};
    }}

    QPushButton[primary="true"] {{
        background-color: {c['accent']};
        color: {c['bg']};
        border: none;
        font-weight: bold;
    }}

    QPushButton[primary="true"]:hover {{
        background-color: {c['accent_hover']};
    }}

    QPushButton[danger="true"] {{
        background-color: {c['error']};
        color: #ffffff;
        border: none;
    }}

    /* ─── 复选框 / 单选框 ──────────────────── */
    QCheckBox, QRadioButton {{
        color: {c['fg']};
        spacing: 8px;
        padding: 4px;
    }}

    QCheckBox::indicator, QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {c['border']};
        border-radius: 4px;
        background-color: {c['input_bg']};
    }}

    QRadioButton::indicator {{
        border-radius: 10px;
    }}

    QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
        background-color: {c['accent']};
        border-color: {c['accent']};
    }}

    /* ─── 下拉框 ──────────────────────────── */
    QComboBox {{
        background-color: {c['input_bg']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 6px 10px;
    }}

    QComboBox:hover {{
        border-color: {c['accent']};
    }}

    QComboBox::drop-down {{
        border: none;
        padding-right: 8px;
    }}

    QComboBox QAbstractItemView {{
        background-color: {c['bg_card']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        selection-background-color: {c['accent']};
        selection-color: {c['bg']};
    }}

    /* ─── 表格 ────────────────────────────── */
    QTableWidget, QTreeWidget, QListWidget {{
        background-color: {c['input_bg']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        gridline-color: {c['border']};
        alternate-background-color: {c['bg_alt']};
    }}

    QTableWidget::item:selected,
    QTreeWidget::item:selected,
    QListWidget::item:selected {{
        background-color: {c['accent']};
        color: {c['bg']};
    }}

    QHeaderView::section {{
        background-color: {c['bg_alt']};
        color: {c['fg']};
        padding: 6px;
        border: none;
        border-bottom: 1px solid {c['border']};
        font-weight: bold;
    }}

    /* ─── 进度条 ──────────────────────────── */
    QProgressBar {{
        background-color: {c['bg_alt']};
        border: none;
        border-radius: 8px;
        height: 16px;
        text-align: center;
        color: {c['fg']};
        font-size: 11px;
    }}

    QProgressBar::chunk {{
        background-color: {c['accent']};
        border-radius: 8px;
    }}

    /* ─── 分组框 ──────────────────────────── */
    QGroupBox {{
        background-color: {c['bg_card']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        margin-top: 12px;
        padding-top: 20px;
        font-weight: bold;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: {c['accent']};
    }}

    /* ─── 选项卡 ──────────────────────────── */
    QTabWidget::pane {{
        border: 1px solid {c['border']};
        border-radius: 8px;
        background-color: {c['bg_card']};
    }}

    QTabBar::tab {{
        background-color: {c['bg_alt']};
        color: {c['fg_dim']};
        padding: 8px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
    }}

    QTabBar::tab:selected {{
        background-color: {c['bg_card']};
        color: {c['accent']};
        font-weight: bold;
    }}

    QTabBar::tab:hover {{
        background-color: {c['bg_card']};
        color: {c['fg']};
    }}

    /* ─── 分割线 ──────────────────────────── */
    QSplitter::handle {{
        background-color: {c['border']};
        height: 2px;
        margin: 2px;
    }}

    /* ─── 滚动条 ──────────────────────────── */
    QScrollBar:vertical {{
        background: transparent;
        width: 10px;
        margin: 0;
    }}

    QScrollBar::handle:vertical {{
        background: {c['scrollbar']};
        border-radius: 5px;
        min-height: 30px;
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    QScrollBar:horizontal {{
        background: transparent;
        height: 10px;
    }}

    QScrollBar::handle:horizontal {{
        background: {c['scrollbar']};
        border-radius: 5px;
        min-width: 30px;
    }}

    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0;
    }}

    /* ─── 工具提示 ─────────────────────────── */
    QToolTip {{
        background-color: {c['bg_card']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        border-radius: 4px;
        padding: 4px 8px;
    }}

    /* ─── 菜单栏 ──────────────────────────── */
    QMenuBar {{
        background-color: {c['bg']};
        color: {c['fg']};
        padding: 2px;
    }}

    QMenuBar::item:selected {{
        background-color: {c['accent']};
        color: {c['bg']};
        border-radius: 4px;
    }}

    QMenu {{
        background-color: {c['bg_card']};
        color: {c['fg']};
        border: 1px solid {c['border']};
        border-radius: 6px;
        padding: 4px;
    }}

    QMenu::item:selected {{
        background-color: {c['accent']};
        color: {c['bg']};
        border-radius: 4px;
    }}

    /* ─── 状态栏 ──────────────────────────── */
    QStatusBar {{
        background-color: {c['bg_alt']};
        color: {c['fg_dim']};
        border-top: 1px solid {c['border']};
    }}
    """

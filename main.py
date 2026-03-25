"""
PyPackager — Python 项目可视化打包工具
入口文件
"""

import sys
import os

# 确保项目根目录在 Python 路径中
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


def main():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QFont

    # 高 DPI 支持
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setApplicationName("PyPackager")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("PyPackager")

    # 设置默认字体
    font = QFont("Microsoft YaHei UI", 10)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    # 应用默认亮色主题
    try:
        from gui.styles.theme import get_stylesheet
        app.setStyleSheet(get_stylesheet("light"))
    except Exception as e:
        print(f"主题加载失败: {e}")

    # 创建并显示主窗口
    from gui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
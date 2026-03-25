"""
PyQt6 裁剪配置
"""
from core.library_profiles.base_profile import BaseProfile, ModuleInfo


class PyQt6Profile(BaseProfile):
    """PyQt6 裁剪方案，结构与 PySide6 类似。"""

    name = "PyQt6"
    package_name = "PyQt6"
    import_name = "PyQt6"
    total_size_mb = 180.0

    modules = {
        "QtCore": ModuleInfo(
            size_mb=5, description="核心非GUI功能",
            dependencies=[], is_essential=True,
        ),
        "QtGui": ModuleInfo(
            size_mb=6, description="基础GUI功能",
            dependencies=["QtCore"],
        ),
        "QtWidgets": ModuleInfo(
            size_mb=8, description="桌面UI控件",
            dependencies=["QtCore", "QtGui"],
        ),
        "QtNetwork": ModuleInfo(
            size_mb=3, description="网络功能",
            dependencies=["QtCore"],
        ),
        "QtWebEngineWidgets": ModuleInfo(
            size_mb=80, description="内嵌浏览器引擎",
            dependencies=["QtCore", "QtGui", "QtWidgets", "QtNetwork",
                          "QtWebEngineCore"],
        ),
        "QtWebEngineCore": ModuleInfo(
            size_mb=5, description="WebEngine核心",
            dependencies=["QtCore", "QtNetwork"],
        ),
        "QtQml": ModuleInfo(
            size_mb=5, description="QML声明式UI引擎",
            dependencies=["QtCore", "QtNetwork"],
        ),
        "QtQuick": ModuleInfo(
            size_mb=8, description="Qt Quick UI框架",
            dependencies=["QtCore", "QtGui", "QtQml"],
        ),
        "Qt3DCore": ModuleInfo(
            size_mb=4, description="3D渲染核心",
            dependencies=["QtCore", "QtGui"],
        ),
        "QtMultimedia": ModuleInfo(
            size_mb=8, description="音视频",
            dependencies=["QtCore", "QtGui", "QtNetwork"],
        ),
        "QtBluetooth": ModuleInfo(
            size_mb=2, description="蓝牙通信",
            dependencies=["QtCore"],
        ),
        "QtSvg": ModuleInfo(
            size_mb=1, description="SVG支持",
            dependencies=["QtCore", "QtGui"],
        ),
        "QtCharts": ModuleInfo(
            size_mb=3, description="图表",
            dependencies=["QtCore", "QtGui", "QtWidgets"],
        ),
        "QtOpenGL": ModuleInfo(
            size_mb=2, description="OpenGL",
            dependencies=["QtCore", "QtGui"],
        ),
        "QtSql": ModuleInfo(
            size_mb=2, description="SQL数据库",
            dependencies=["QtCore"],
        ),
        "QtXml": ModuleInfo(
            size_mb=1, description="XML处理",
            dependencies=["QtCore"],
        ),
        "QtTest": ModuleInfo(
            size_mb=2, description="单元测试",
            dependencies=["QtCore"],
        ),
        "QtPrintSupport": ModuleInfo(
            size_mb=2, description="打印支持",
            dependencies=["QtCore", "QtGui", "QtWidgets"],
        ),
        "QtDesigner": ModuleInfo(
            size_mb=5, description="Designer集成",
            dependencies=["QtCore", "QtGui", "QtWidgets"],
        ),
    }

    common_hidden_imports = [
        "PyQt6.QtSvg",
        "PyQt6.QtXml",
        "PyQt6.QtPrintSupport",
    ]

    excludable_data = [
        {"path": "PyQt6/Qt6/translations", "size_mb": 15, "desc": "翻译文件"},
        {"path": "PyQt6/Qt6/qml", "size_mb": 20, "desc": "QML文件"},
    ]

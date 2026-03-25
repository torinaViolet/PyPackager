"""
PySide6 裁剪配置
详细定义 PySide6 各子模块的大小、依赖关系和裁剪建议。
"""
from core.library_profiles.base_profile import BaseProfile, ModuleInfo


class PySide6Profile(BaseProfile):
    """PySide6 裁剪方案。"""

    name = "PySide6"
    package_name = "PySide6"
    import_name = "PySide6"
    total_size_mb = 200.0

    modules = {
        "QtCore": ModuleInfo(
            size_mb=5, description="核心非GUI功能 (信号槽/事件循环/线程/定时器)",
            dependencies=[], is_essential=True,
        ),
        "QtGui": ModuleInfo(
            size_mb=6, description="基础GUI功能 (颜色/字体/图片/绘图)",
            dependencies=["QtCore"],
        ),
        "QtWidgets": ModuleInfo(
            size_mb=8, description="桌面UI控件 (按钮/表格/布局/对话框)",
            dependencies=["QtCore", "QtGui"],
        ),
        "QtNetwork": ModuleInfo(
            size_mb=3, description="网络功能 (HTTP/TCP/UDP/SSL)",
            dependencies=["QtCore"],
        ),
        "QtWebEngineWidgets": ModuleInfo(
            size_mb=80, description="内嵌浏览器引擎 (基于Chromium)",
            dependencies=["QtCore", "QtGui", "QtWidgets", "QtNetwork",
                          "QtWebEngineCore"],
        ),
        "QtWebEngineCore": ModuleInfo(
            size_mb=5, description="WebEngine核心",
            dependencies=["QtCore", "QtNetwork"],
        ),
        "QtWebChannel": ModuleInfo(
            size_mb=1, description="Web通道通信",
            dependencies=["QtCore"],
        ),
        "QtQml": ModuleInfo(
            size_mb=5, description="QML声明式UI引擎",
            dependencies=["QtCore", "QtNetwork"],
        ),
        "QtQuick": ModuleInfo(
            size_mb=8, description="Qt Quick UI框架",
            dependencies=["QtCore", "QtGui", "QtQml"],
        ),
        "QtQuickWidgets": ModuleInfo(
            size_mb=1, description="Quick与Widgets混合",
            dependencies=["QtCore", "QtGui", "QtWidgets", "QtQuick"],
        ),
        "Qt3DCore": ModuleInfo(
            size_mb=4, description="3D渲染核心",
            dependencies=["QtCore", "QtGui"],
        ),
        "Qt3DRender": ModuleInfo(
            size_mb=5, description="3D渲染引擎",
            dependencies=["QtCore", "QtGui", "Qt3DCore"],
        ),
        "Qt3DExtras": ModuleInfo(
            size_mb=2, description="3D扩展组件",
            dependencies=["QtCore", "QtGui", "Qt3DCore", "Qt3DRender"],
        ),
        "QtMultimedia": ModuleInfo(
            size_mb=8, description="音视频播放/录制",
            dependencies=["QtCore", "QtGui", "QtNetwork"],
        ),
        "QtMultimediaWidgets": ModuleInfo(
            size_mb=1, description="多媒体控件",
            dependencies=["QtCore", "QtGui", "QtWidgets", "QtMultimedia"],
        ),
        "QtBluetooth": ModuleInfo(
            size_mb=2, description="蓝牙通信",
            dependencies=["QtCore"],
        ),
        "QtNfc": ModuleInfo(
            size_mb=1, description="NFC近场通信",
            dependencies=["QtCore"],
        ),
        "QtSensors": ModuleInfo(
            size_mb=1, description="传感器",
            dependencies=["QtCore"],
        ),
        "QtSerialPort": ModuleInfo(
            size_mb=1, description="串口通信",
            dependencies=["QtCore"],
        ),
        "QtSvg": ModuleInfo(
            size_mb=1, description="SVG图形支持",
            dependencies=["QtCore", "QtGui"],
        ),
        "QtSvgWidgets": ModuleInfo(
            size_mb=1, description="SVG控件",
            dependencies=["QtCore", "QtGui", "QtWidgets", "QtSvg"],
        ),
        "QtCharts": ModuleInfo(
            size_mb=3, description="图表组件",
            dependencies=["QtCore", "QtGui", "QtWidgets"],
        ),
        "QtDataVisualization": ModuleInfo(
            size_mb=3, description="3D数据可视化",
            dependencies=["QtCore", "QtGui"],
        ),
        "QtOpenGL": ModuleInfo(
            size_mb=2, description="OpenGL集成",
            dependencies=["QtCore", "QtGui"],
        ),
        "QtOpenGLWidgets": ModuleInfo(
            size_mb=1, description="OpenGL控件",
            dependencies=["QtCore", "QtGui", "QtWidgets", "QtOpenGL"],
        ),
        "QtPositioning": ModuleInfo(
            size_mb=2, description="地理定位",
            dependencies=["QtCore"],
        ),
        "QtRemoteObjects": ModuleInfo(
            size_mb=2, description="远程对象",
            dependencies=["QtCore", "QtNetwork"],
        ),
        "QtStateMachine": ModuleInfo(
            size_mb=1, description="状态机",
            dependencies=["QtCore"],
        ),
        "QtTest": ModuleInfo(
            size_mb=2, description="单元测试框架",
            dependencies=["QtCore"],
        ),
        "QtXml": ModuleInfo(
            size_mb=1, description="XML处理",
            dependencies=["QtCore"],
        ),
        "QtConcurrent": ModuleInfo(
            size_mb=1, description="并发框架",
            dependencies=["QtCore"],
        ),
        "QtDBus": ModuleInfo(
            size_mb=2, description="D-Bus通信(Linux)",
            dependencies=["QtCore"],
        ),
        "QtDesigner": ModuleInfo(
            size_mb=5, description="Designer设计器集成",
            dependencies=["QtCore", "QtGui", "QtWidgets"],
        ),
        "QtHelp": ModuleInfo(
            size_mb=2, description="帮助系统",
            dependencies=["QtCore", "QtGui", "QtWidgets"],
        ),
        "QtPrintSupport": ModuleInfo(
            size_mb=2, description="打印支持",
            dependencies=["QtCore", "QtGui", "QtWidgets"],
        ),
        "QtPdf": ModuleInfo(
            size_mb=10, description="PDF渲染",
            dependencies=["QtCore", "QtGui"],
        ),
        "QtPdfWidgets": ModuleInfo(
            size_mb=1, description="PDF控件",
            dependencies=["QtCore", "QtGui", "QtWidgets", "QtPdf"],
        ),
    }

    common_hidden_imports = [
        "PySide6.QtSvg",
        "PySide6.QtXml",
        "PySide6.QtPrintSupport",
    ]

    excludable_data = [
        {"path": "PySide6/translations", "size_mb": 15, "desc": "翻译文件"},
        {"path": "PySide6/Qt/qml", "size_mb": 20, "desc": "QML文件 (不用QML可排除)"},
        {"path": "PySide6/opengl32sw.dll", "size_mb": 8, "desc": "软件OpenGL渲染 (一般不需要)"},
        {"path": "PySide6/Qt/plugins/multimedia", "size_mb": 5, "desc": "多媒体插件"},
        {"path": "PySide6/Qt/plugins/sqldrivers", "size_mb": 3, "desc": "SQL驱动 (不用数据库可排除)"},
    ]

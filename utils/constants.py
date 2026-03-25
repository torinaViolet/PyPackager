"""
常量定义模块
定义应用程序中使用的所有常量。
"""
import os
import sys

# ─── 应用信息 ──────────────────────────────────────────
APP_NAME = "PyPackager"
APP_VERSION = "1.0.0"
APP_AUTHOR = "PyPackager Team"
APP_DESCRIPTION = "一个可视化的 Python 项目打包工具"

# ─── 路径常量 ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
DEFAULT_CONFIG_PATH = os.path.join(ASSETS_DIR, "default_config.json")

# ─── 打包引擎 ──────────────────────────────────────────
ENGINE_PYINSTALLER = "pyinstaller"
ENGINE_NUITKA = "nuitka"
SUPPORTED_ENGINES = [ENGINE_PYINSTALLER, ENGINE_NUITKA]

# ─── 构建模式 ──────────────────────────────────────────
MODE_ONEFILE = "onefile"
MODE_ONEDIR = "onedir"

# ─── 裁剪策略 ──────────────────────────────────────────
TRIM_RECOMMENDED = "recommended"  # 推荐模式: 只排除确定未使用的
TRIM_AGGRESSIVE = "aggressive"    # 激进模式: 排除未使用+可能未使用的
TRIM_MANUAL = "manual"            # 手动模式: 用户自选

# ─── 文件过滤 ──────────────────────────────────────────
PYTHON_EXTENSIONS = {".py", ".pyw"}
ICON_EXTENSIONS = {".ico", ".icns", ".png"}
DATA_EXTENSIONS = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".txt", ".csv", ".xml", ".html", ".css", ".js",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".bmp",
    ".ttf", ".otf", ".woff", ".woff2",
    ".mp3", ".wav", ".ogg",
    ".mp4", ".avi", ".mkv",
    ".db", ".sqlite", ".sqlite3",
}

# ─── 日志级别 ──────────────────────────────────────────
LOG_INFO = "INFO"
LOG_WARNING = "WARNING"
LOG_ERROR = "ERROR"
LOG_SUCCESS = "SUCCESS"
LOG_DEBUG = "DEBUG"

# ─── 默认排除的模块 ─────────────────────────────────────
DEFAULT_EXCLUDES = [
    "tkinter",
    "test",
    "unittest",
    "setuptools",
    "pip",
    "ensurepip",
    "venv",
    "lib2to3",
    "idlelib",
    "turtledemo",
    # 注意: distutils 已在 Python 3.12 中移除，
    # PyInstaller 6.x 会自动处理，不需要手动排除
]

# ─── 配置文件版本 ───────────────────────────────────────
CONFIG_VERSION = "1.0"

# ─── 构建状态 ──────────────────────────────────────────
BUILD_IDLE = "idle"
BUILD_RUNNING = "running"
BUILD_SUCCESS = "success"
BUILD_FAILED = "failed"
BUILD_CANCELLED = "cancelled"

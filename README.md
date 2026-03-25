<div align="center">

# 🐍 PyPackager

**Python 项目可视化打包工具**

*告别命令行，一键打包你的 Python 项目*

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://python.org)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-lightgrey)]()

<img src="preview/主界面.png" width="800" alt="PyPackager 主界面">

</div>

---

## ✨ 功能特色

### 🎯 核心功能
- **可视化配置** — 所有打包选项一目了然，告别复杂的命令行参数
- **双引擎支持** — 同时支持 PyInstaller 和 Nuitka 打包引擎
- **智能依赖扫描** — 自动分析项目 import 语句，精确识别第三方依赖（自动过滤标准库和项目内部模块）
- **多功能控制台** — 集成构建日志、系统终端和 Python 交互式控制台三合一

### ✂️ 大型库裁剪
- **智能裁剪** — 自动分析项目使用了哪些子模块，推荐排除未使用部分
- **内置 6 大库配置** — PySide6、PyQt6、PyTorch、NumPy、Pandas、Matplotlib
- **自定义配置** — 可视化创建任意库的裁剪配置，支持自动检测子模块
- **体积预估** — 实时显示预计节省的空间

### 📦 资源管理
- **资源文件管理** — 拖拽式添加需要打包的数据文件和目录
- **resource_path 生成器** — 一键生成资源路径辅助代码，兼容开发和打包环境
- **图标自动转换** — 自动将 PNG/JPG 等格式转换为 ICO

### 📟 集成控制台
- **构建日志** — 彩色日志输出，构建进度实时可见
- **系统终端** — 内置终端，支持执行系统命令，自动激活项目虚拟环境
- **Python 控制台** — 交互式 Python 解释器，支持多行代码输入（Enter 换行，Ctrl+Enter 执行）
- **智能环境检测** — 自动检测项目虚拟环境，终端和 Python 控制台无缝切换
- **双模式解释器** — 有虚拟环境时使用项目 Python，无虚拟环境时使用内置 exec() 引擎（打包后也能正常使用）

### 🎨 用户体验
- **亮/暗主题切换** — 支持明亮和暗色两种主题
- **配置保存/加载** — 打包配置可保存为 JSON，随时恢复
- **隐藏导入建议** — 自动推荐常见的隐藏导入列表

---

## 📸 界面预览

<table>
  <tr>
    <td align="center"><b>📦 依赖管理</b></td>
    <td align="center"><b>⚙ 构建选项</b></td>
  </tr>
  <tr>
    <td><img src="preview/依赖管理.png" width="400" alt="依赖管理"></td>
    <td><img src="preview/构建选项.png" width="400" alt="构建选项"></td>
  </tr>
  <tr>
    <td align="center"><b>📁 资源文件</b></td>
    <td align="center"><b>✂️ 库裁剪</b></td>
  </tr>
  <tr>
    <td><img src="preview/资源文件.png" width="400" alt="资源文件"></td>
    <td><img src="preview/库裁剪.png" width="400" alt="库裁剪"></td>
  </tr>
  <tr>
    <td align="center"><b>🛠 资源路径生成器</b></td>
    <td align="center"><b>⚙ 自定义裁剪配置</b></td>
  </tr>
  <tr>
    <td><img src="preview/资源文件函数.png" width="400" alt="资源路径生成器"></td>
    <td><img src="preview/自定义配置.png" width="400" alt="自定义裁剪配置"></td>
  </tr>
</table>

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Windows / Linux / macOS

### 安装

```bash
# 克隆项目
git clone https://github.com/torinaViolet/PyPackager.git
cd PyPackager

# 创建虚拟环境 (推荐)
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 运行

```bash
python main.py
```

### 可选依赖

```bash
# Nuitka 打包引擎 (可选)
pip install nuitka
```

---

## 📖 使用指南

### 基本打包流程

1. **打开项目** — 点击「📂 打开项目」选择 Python 入口文件
2. **配置信息** — 在「📌 基本信息」填写项目名称、图标等
3. **检查依赖** — 切换到「📦 依赖管理」查看自动扫描结果
4. **设置选项** — 在「⚙ 构建选项」配置打包模式、引擎等
5. **开始构建** — 点击「🔨 开始构建」，在控制台查看实时输出

<details>
<summary>📷 查看操作截图</summary>

| 依赖管理面板 | 构建选项面板 |
|:---:|:---:|
| <img src="preview/依赖管理.png" width="380"> | <img src="preview/构建选项.png" width="380"> |

</details>

### 大型库裁剪

如果你的项目使用了 PySide6、PyTorch 等大型库：

1. 切换到「✂️ 库裁剪」面板
2. 点击「🔍 自动扫描项目」
3. 查看检测到的大型库及其子模块
4. 点击「🎯 一键推荐排除」自动选择未使用的模块
5. 检查结果，按需调整后开始构建

> 💡 以 PySide6 为例，完整打包约 200MB，裁剪后可降至 20-40MB

<details>
<summary>📷 查看操作截图</summary>

<img src="preview/库裁剪.png" width="700" alt="库裁剪面板">

</details>

### 自定义库裁剪配置

针对未内置的库，你可以在「✂️ 库裁剪」面板点击「➕ 自定义库配置」：

1. 填写库名和导入名
2. 点击「🔍 自动检测子模块」自动发现子模块
3. 手动补充各模块的大小估算和依赖关系
4. 点击「🚀 生成并注册」
5. 配置可导出为 JSON，方便分享和复用

<details>
<summary>📷 查看操作截图</summary>

<img src="preview/自定义配置.png" width="700" alt="自定义裁剪配置">

</details>

### 资源文件打包

如果你的程序需要打包图片、配置文件等资源：

1. 切换到「📁 资源文件」面板
2. 添加需要打包的文件或目录
3. 点击「🛠 生成 resource_path」生成兼容代码
4. 在项目中使用生成的辅助函数访问资源

```python
from utils.resource_helper import resource_path

# 开发环境和打包后都能正确访问
logo = resource_path("assets/logo.png")
config = resource_path("data/config.json")
```

<details>
<summary>📷 查看操作截图</summary>

| 资源文件面板 | resource_path 生成器 |
|:---:|:---:|
| <img src="preview/资源文件.png" width="380"> | <img src="preview/资源文件函数.png" width="380"> |

</details>

---

## 📁 项目结构

```
PyPackager/
├── main.py                          # 程序入口
├── requirements.txt                 # 依赖列表
├── LICENSE                          # MIT 许可证
│
├── core/                            # 核心逻辑层
│   ├── analyzer.py                  # 项目依赖分析器
│   ├── builder.py                   # 构建引擎 (PyInstaller/Nuitka)
│   ├── config_manager.py            # 配置管理器
│   ├── smart_excluder.py            # 智能排除引擎
│   ├── venv_detector.py             # 虚拟环境检测
│   └── library_profiles/            # 大型库裁剪配置
│       ├── base_profile.py          # Profile 基类
│       ├── pyside6.py               # PySide6 裁剪配置
│       ├── pyqt6.py                 # PyQt6 裁剪配置
│       ├── torch_profile.py         # PyTorch 裁剪配置
│       ├── numpy_profile.py         # NumPy 裁剪配置
│       ├── pandas_profile.py        # Pandas 裁剪配置
│       └── matplotlib_profile.py    # Matplotlib 裁剪配置
│
├── gui/                             # GUI 界面层
│   ├── main_window.py               # 主窗口
│   ├── widgets/                     # UI 组件
│   │   ├── toolbar.py               # 工具栏
│   │   ├── project_panel.py         # 基本信息面板
│   │   ├── dependency_panel.py      # 依赖管理面板
│   │   ├── resource_panel.py        # 资源文件面板
│   │   ├── build_options.py         # 构建选项面板
│   │   ├── library_trimmer.py       # 库裁剪面板
│   │   └── console_output.py        # 多功能控制台 (构建日志/终端/Python)
│   ├── dialogs/                     # 对话框
│   │   ├── about_dialog.py          # 关于对话框
│   │   ├── env_selector.py          # 环境选择器
│   │   ├── exclude_preview.py       # 排除预览
│   │   ├── hidden_imports.py        # 隐藏导入管理
│   │   ├── resource_helper_dialog.py # resource_path 生成器
│   │   └── custom_profile_dialog.py # 自定义裁剪配置
│   └── styles/
│       └── theme.py                 # 主题样式 (亮色/暗色)
│
└── utils/                           # 工具层
    ├── constants.py                 # 常量定义
    ├── file_utils.py                # 文件工具
    └── process_runner.py            # 进程运行器
```

---

## 🔧 技术栈

| 组件 | 技术 |
|---|---|
| GUI 框架 | PySide6 (Qt for Python) |
| 打包引擎 | PyInstaller / Nuitka |
| 图标转换 | Pillow |
| 集成终端 | QProcess + 内置 exec() |
| 语言 | Python 3.10+ |

---

## 🤝 贡献

欢迎贡献代码！你可以：

1. **Fork** 本仓库
2. 创建功能分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 提交 **Pull Request**

### 贡献方向

- 🆕 添加更多库的裁剪 Profile（如 TensorFlow、OpenCV 等）
- 🌍 国际化 / 多语言支持
- 🎨 更多主题风格
- 📝 完善文档和教程
- 🐛 Bug 修复和性能优化

---

## 📋 更新日志

### v1.1.0
- ✨ **多功能控制台** — 新增系统终端和 Python 交互式控制台标签页
- ✨ **虚拟环境自动激活** — 打开项目后终端自动激活虚拟环境，pip/python 命令直接使用项目环境
- ✨ **内置 Python 解释器** — 无虚拟环境时使用内置 exec() 引擎，打包后也能正常执行 Python 代码
- ✨ **多行代码输入** — Python 控制台支持 Enter 换行、Ctrl+Enter 执行，支持命令历史
- ✨ **终端 Ctrl+C 中断** — 支持 Ctrl+C 和停止按钮终止运行中的命令
- 🐛 **修复依赖扫描** — 修复项目内部模块（如 base_profile）被误识别为第三方依赖的问题
- 🐛 **修复终端乱码** — 修复 Windows 终端 UTF-8 编码问题
- 🐛 **修复交互式程序卡死** — 终端拦截 python/node 等交互式命令，避免进程卡死

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

<div align="center">

**如果觉得有用，请给个 ⭐ Star 支持一下！**

Made with ❤️ by PyPackager Team

</div>
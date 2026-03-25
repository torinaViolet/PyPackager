"""
Matplotlib 裁剪配置
"""
from core.library_profiles.base_profile import BaseProfile, ModuleInfo


class MatplotlibProfile(BaseProfile):
    """Matplotlib 裁剪方案。"""

    name = "Matplotlib"
    package_name = "matplotlib"
    import_name = "matplotlib"
    total_size_mb = 50.0

    modules = {
        "pyplot": ModuleInfo(
            size_mb=5, description="常用绑图接口",
            dependencies=["figure", "axes"], is_essential=True,
        ),
        "figure": ModuleInfo(
            size_mb=3, description="图形对象",
            dependencies=[],
        ),
        "axes": ModuleInfo(
            size_mb=5, description="坐标轴",
            dependencies=[],
        ),
        "backends": ModuleInfo(
            size_mb=10, description="渲染后端",
            dependencies=[],
        ),
        "animation": ModuleInfo(
            size_mb=3, description="动画",
            dependencies=["pyplot"],
        ),
        "widgets": ModuleInfo(
            size_mb=2, description="交互控件",
            dependencies=["pyplot"],
        ),
        "mplot3d": ModuleInfo(
            size_mb=5, description="3D绘图",
            dependencies=["axes"],
        ),
        "tests": ModuleInfo(
            size_mb=10, description="测试文件",
            dependencies=[],
        ),
    }

    common_hidden_imports = [
        "matplotlib.backends.backend_agg",
        "matplotlib.backends.backend_svg",
    ]

    excludable_data = [
        {"path": "matplotlib/mpl-data/sample_data", "size_mb": 5, "desc": "示例数据"},
        {"path": "matplotlib/mpl-data/fonts", "size_mb": 5, "desc": "字体文件(可精简)"},
        {"path": "matplotlib/tests", "size_mb": 10, "desc": "测试文件"},
    ]

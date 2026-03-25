"""
Pandas 裁剪配置
"""
from core.library_profiles.base_profile import BaseProfile, ModuleInfo


class PandasProfile(BaseProfile):
    """Pandas 裁剪方案。"""

    name = "Pandas"
    package_name = "pandas"
    import_name = "pandas"
    total_size_mb = 60.0

    modules = {
        "core": ModuleInfo(
            size_mb=15, description="核心DataFrame/Series",
            dependencies=[], is_essential=True,
        ),
        "io": ModuleInfo(
            size_mb=10, description="IO读写(CSV/Excel/SQL等)",
            dependencies=["core"],
        ),
        "plotting": ModuleInfo(
            size_mb=5, description="绘图集成",
            dependencies=["core"],
        ),
        "tseries": ModuleInfo(
            size_mb=5, description="时间序列",
            dependencies=["core"],
        ),
        "sparse": ModuleInfo(
            size_mb=3, description="稀疏数据",
            dependencies=["core"],
        ),
        "api": ModuleInfo(
            size_mb=2, description="API兼容层",
            dependencies=["core"],
        ),
        "tests": ModuleInfo(
            size_mb=15, description="测试文件",
            dependencies=[],
        ),
    }

    common_hidden_imports = [
        "pandas._libs.tslibs.timedeltas",
        "pandas._libs.tslibs.nattype",
        "pandas._libs.tslibs.np_datetime",
        "pandas._libs.skiplist",
    ]

    excludable_data = [
        {"path": "pandas/tests", "size_mb": 15, "desc": "测试文件"},
    ]

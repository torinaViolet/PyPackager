"""
NumPy 裁剪配置
"""
from core.library_profiles.base_profile import BaseProfile, ModuleInfo


class NumpyProfile(BaseProfile):
    """NumPy 裁剪方案。"""

    name = "NumPy"
    package_name = "numpy"
    import_name = "numpy"
    total_size_mb = 60.0

    modules = {
        "core": ModuleInfo(
            size_mb=15, description="核心数组操作",
            dependencies=[], is_essential=True,
        ),
        "linalg": ModuleInfo(
            size_mb=10, description="线性代数",
            dependencies=["core"],
        ),
        "fft": ModuleInfo(
            size_mb=5, description="FFT变换",
            dependencies=["core"],
        ),
        "random": ModuleInfo(
            size_mb=5, description="随机数",
            dependencies=["core"],
        ),
        "polynomial": ModuleInfo(
            size_mb=3, description="多项式",
            dependencies=["core"],
        ),
        "ma": ModuleInfo(
            size_mb=3, description="掩码数组",
            dependencies=["core"],
        ),
        "testing": ModuleInfo(
            size_mb=3, description="测试工具",
            dependencies=["core"],
        ),
        "f2py": ModuleInfo(
            size_mb=5, description="Fortran接口",
            dependencies=["core"],
        ),
        "distutils": ModuleInfo(
            size_mb=3, description="构建工具",
            dependencies=[],
        ),
    }

    common_hidden_imports = [
        "numpy.core._methods",
        "numpy.core._dtype_ctypes",
    ]

    excludable_data = [
        {"path": "numpy/tests", "size_mb": 5, "desc": "测试文件"},
        {"path": "numpy/f2py", "size_mb": 5, "desc": "Fortran绑定(一般不需要)"},
    ]

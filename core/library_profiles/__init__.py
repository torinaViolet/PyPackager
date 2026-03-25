"""
大型库裁剪配置模块
自动注册所有库配置文件。
"""
from typing import Dict, Optional, Type

from core.library_profiles.base_profile import BaseProfile
from core.library_profiles.pyside6 import PySide6Profile
from core.library_profiles.pyqt6 import PyQt6Profile
from core.library_profiles.torch_profile import TorchProfile
from core.library_profiles.matplotlib_profile import MatplotlibProfile
from core.library_profiles.numpy_profile import NumpyProfile
from core.library_profiles.pandas_profile import PandasProfile


# 注册表: import名 -> Profile类
PROFILE_REGISTRY: Dict[str, Type[BaseProfile]] = {
    "PySide6": PySide6Profile,
    "PyQt6": PyQt6Profile,
    "torch": TorchProfile,
    "matplotlib": MatplotlibProfile,
    "numpy": NumpyProfile,
    "pandas": PandasProfile,
}


def get_profile(lib_name: str) -> Optional[Type[BaseProfile]]:
    """根据库名获取对应的裁剪配置。"""
    return PROFILE_REGISTRY.get(lib_name)


def get_all_profile_names() -> list:
    """获取所有已注册的库名。"""
    return list(PROFILE_REGISTRY.keys())

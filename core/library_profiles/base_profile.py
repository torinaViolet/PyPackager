"""
大型库裁剪 - 基类
定义库裁剪配置的通用接口和数据结构。
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional


@dataclass
class ModuleInfo:
    """子模块信息。"""
    size_mb: float = 0.0
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    is_essential: bool = False  # 是否为基础必需模块


class BaseProfile:
    """
    大型库裁剪配置基类。
    每个大型库都应该继承此类并填充自己的子模块信息。
    """

    name: str = ""                          # 库名
    package_name: str = ""                  # pip 包名
    import_name: str = ""                   # import 时的名称
    total_size_mb: float = 0.0              # 完整大小估算

    # 子模块注册表
    modules: Dict[str, ModuleInfo] = {}

    # 常见的隐藏导入
    common_hidden_imports: List[str] = []

    # 可以安全排除的数据文件/目录
    excludable_data: List[dict] = []  # [{"path": ..., "size_mb": ..., "desc": ...}]

    @classmethod
    def get_essential_modules(cls) -> List[str]:
        """获取基础必需模块列表。"""
        return [
            name for name, info in cls.modules.items()
            if info.is_essential
        ]

    @classmethod
    def get_all_module_names(cls) -> List[str]:
        """获取所有子模块名称。"""
        return list(cls.modules.keys())

    @classmethod
    def get_module_with_deps(cls, module_name: str) -> Set[str]:
        """
        获取某个模块及其所有依赖（递归）。
        保证如果用户使用了某个模块，它的所有依赖也会被保留。
        """
        result = set()
        if module_name not in cls.modules:
            return result

        result.add(module_name)
        for dep in cls.modules[module_name].dependencies:
            result.update(cls.get_module_with_deps(dep))
        return result

    @classmethod
    def calculate_excludable(
        cls,
        used_imports: Set[str]
    ) -> dict:
        """
        根据已使用的导入，计算可排除的模块和预计节省的空间。

        Args:
            used_imports: 项目中实际使用的导入集合

        Returns:
            {
                "keep": [保留的模块],
                "exclude": [可排除的模块],
                "saved_mb": 节省的空间(MB),
                "total_mb": 总大小(MB),
            }
        """
        # 找出实际使用的子模块
        used_submodules = set()
        prefix = cls.import_name or cls.package_name

        for imp in used_imports:
            parts = imp.split('.')
            if parts[0] == prefix and len(parts) > 1:
                used_submodules.add(parts[1])

        # 展开依赖：保留使用的模块 + 它们的依赖
        keep = set()
        for mod in used_submodules:
            keep.update(cls.get_module_with_deps(mod))

        # 必需模块总是保留
        for mod in cls.get_essential_modules():
            keep.update(cls.get_module_with_deps(mod))

        # 计算可排除的
        all_mods = set(cls.modules.keys())
        exclude = all_mods - keep

        # 计算空间
        saved = sum(
            cls.modules[m].size_mb for m in exclude
            if m in cls.modules
        )
        total = sum(info.size_mb for info in cls.modules.values())

        return {
            "keep": sorted(keep),
            "exclude": sorted(exclude),
            "saved_mb": saved,
            "total_mb": total,
        }

    @classmethod
    def get_exclude_args(cls, excluded_modules: List[str]) -> List[str]:
        """
        生成 PyInstaller 排除参数。
        返回: ["--exclude-module", "PySide6.QtWebEngine", ...]
        """
        prefix = cls.import_name or cls.package_name
        args = []
        for mod in excluded_modules:
            args.extend(["--exclude-module", f"{prefix}.{mod}"])
        return args

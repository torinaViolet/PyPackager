"""
智能排除引擎
基于项目分析结果和大型库配置，自动生成最优的排除列表。
"""
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Type

from core.analyzer import AnalysisResult
from core.library_profiles.base_profile import BaseProfile
from core.library_profiles import PROFILE_REGISTRY, get_profile
from utils.constants import TRIM_RECOMMENDED, TRIM_AGGRESSIVE, DEFAULT_EXCLUDES


@dataclass
class LibraryTrimResult:
    """单个库的裁剪结果。"""
    lib_name: str
    profile_name: str
    total_mb: float
    saved_mb: float
    keep_modules: List[str] = field(default_factory=list)
    exclude_modules: List[str] = field(default_factory=list)
    exclude_data: List[dict] = field(default_factory=list)
    hidden_imports: List[str] = field(default_factory=list)


@dataclass
class ExclusionPlan:
    """完整的排除方案。"""
    library_trims: List[LibraryTrimResult] = field(default_factory=list)
    global_excludes: List[str] = field(default_factory=list)
    all_hidden_imports: List[str] = field(default_factory=list)
    total_saved_mb: float = 0.0


class SmartExcluder:
    """
    智能排除引擎。
    根据项目分析结果，结合大型库的裁剪配置，
    自动生成最优排除方案。
    """

    def __init__(self):
        pass

    def generate_plan(
        self,
        analysis: AnalysisResult,
        strategy: str = TRIM_RECOMMENDED,
    ) -> ExclusionPlan:
        """
        生成排除方案。

        Args:
            analysis: 项目分析结果
            strategy: 裁剪策略 (recommended / aggressive / manual)

        Returns:
            ExclusionPlan: 排除方案
        """
        plan = ExclusionPlan()

        # 添加全局默认排除
        plan.global_excludes = list(DEFAULT_EXCLUDES)

        # 对每个检测到的大型库生成裁剪方案
        for lib_name in analysis.detected_large_libs:
            profile_cls = get_profile(lib_name)
            if profile_cls is None:
                continue

            trim_result = self._trim_library(
                profile_cls, analysis.all_imports, strategy
            )
            if trim_result:
                plan.library_trims.append(trim_result)
                plan.all_hidden_imports.extend(trim_result.hidden_imports)
                plan.total_saved_mb += trim_result.saved_mb

        # 去重
        plan.all_hidden_imports = list(set(plan.all_hidden_imports))

        return plan

    def _trim_library(
        self,
        profile_cls: Type[BaseProfile],
        used_imports: Set[str],
        strategy: str,
    ) -> Optional[LibraryTrimResult]:
        """对单个库执行裁剪分析。"""
        calc = profile_cls.calculate_excludable(used_imports)

        if not calc["exclude"]:
            return None

        result = LibraryTrimResult(
            lib_name=profile_cls.import_name or profile_cls.package_name,
            profile_name=profile_cls.name,
            total_mb=calc["total_mb"],
            saved_mb=calc["saved_mb"],
            keep_modules=calc["keep"],
            exclude_modules=calc["exclude"],
            hidden_imports=list(profile_cls.common_hidden_imports),
        )

        # 激进模式：额外排除数据文件
        if strategy == TRIM_AGGRESSIVE:
            result.exclude_data = list(profile_cls.excludable_data)
            result.saved_mb += sum(
                d.get("size_mb", 0) for d in profile_cls.excludable_data
            )

        return result

    def plan_to_pyinstaller_args(self, plan: ExclusionPlan) -> List[str]:
        """
        将排除方案转化为 PyInstaller 命令行参数。
        """
        args = []
        seen_excludes = set()

        # PyInstaller 6.x / Python 3.12+ 已自动处理的模块，不再手动排除
        auto_excluded = {"distutils"}

        # 全局排除
        for mod in plan.global_excludes:
            if mod not in seen_excludes and mod not in auto_excluded:
                args.extend(["--exclude-module", mod])
                seen_excludes.add(mod)

        # 库裁剪排除
        for trim in plan.library_trims:
            profile_cls = get_profile(trim.lib_name)
            if profile_cls:
                for mod in trim.exclude_modules:
                    if mod not in seen_excludes and mod not in auto_excluded:
                        args.extend(["--exclude-module", mod])
                        seen_excludes.add(mod)

        # 隐藏导入
        seen_imports = set()
        for imp in plan.all_hidden_imports:
            if imp not in seen_imports:
                args.extend(["--hidden-import", imp])
                seen_imports.add(imp)

        return args

    def plan_to_summary(self, plan: ExclusionPlan) -> str:
        """将排除方案转化为可读文本摘要。"""
        lines = ["═" * 50]
        lines.append("📋 智能排除方案摘要")
        lines.append("═" * 50)

        if plan.library_trims:
            lines.append("\n🔧 大型库裁剪:")
            for trim in plan.library_trims:
                pct = (
                    (trim.saved_mb / trim.total_mb * 100)
                    if trim.total_mb > 0 else 0
                )
                lines.append(
                    f"  📦 {trim.profile_name}: "
                    f"节省 {trim.saved_mb:.0f}MB ({pct:.0f}%)"
                )
                lines.append(
                    f"     保留: {', '.join(trim.keep_modules)}"
                )
                lines.append(
                    f"     排除: {', '.join(trim.exclude_modules)}"
                )

        if plan.global_excludes:
            lines.append(f"\n🚫 全局排除: {len(plan.global_excludes)} 个模块")

        if plan.all_hidden_imports:
            lines.append(
                f"\n🔍 隐藏导入: {len(plan.all_hidden_imports)} 个"
            )

        lines.append(f"\n💡 预计总节省: {plan.total_saved_mb:.0f} MB")
        lines.append("═" * 50)

        return "\n".join(lines)

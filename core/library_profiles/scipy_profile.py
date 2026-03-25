"""SciPy 库裁剪配置"""

from .base_profile import BaseProfile, ModuleInfo


class ScipyProfile(BaseProfile):
    name = "scipy"
    package_name = "scipy"
    description = "科学计算库"

    modules = {
        "scipy.optimize": ModuleInfo(
            size_mb=8,
            description="优化算法 (最小化/曲线拟合/求根)",
            dependencies=[],
        ),
        "scipy.linalg": ModuleInfo(
            size_mb=12,
            description="线性代数 (矩阵分解/求解)",
            dependencies=[],
        ),
        "scipy.sparse": ModuleInfo(
            size_mb=8,
            description="稀疏矩阵运算",
            dependencies=[],
        ),
        "scipy.signal": ModuleInfo(
            size_mb=6,
            description="信号处理 (滤波/卷积/频谱)",
            dependencies=[],
        ),
        "scipy.interpolate": ModuleInfo(
            size_mb=5,
            description="插值方法 (样条/网格)",
            dependencies=[],
        ),
        "scipy.integrate": ModuleInfo(
            size_mb=4,
            description="数值积分与常微分方程",
            dependencies=[],
        ),
        "scipy.stats": ModuleInfo(
            size_mb=10,
            description="统计分布与检验",
            dependencies=[],
        ),
        "scipy.spatial": ModuleInfo(
            size_mb=5,
            description="空间数据结构与算法 (KD树/凸包)",
            dependencies=[],
        ),
        "scipy.ndimage": ModuleInfo(
            size_mb=4,
            description="多维图像处理",
            dependencies=[],
        ),
        "scipy.fft": ModuleInfo(
            size_mb=6,
            description="快速傅里叶变换",
            dependencies=[],
        ),
        "scipy.io": ModuleInfo(
            size_mb=3,
            description="数据输入输出 (MATLAB/.wav)",
            dependencies=[],
        ),
        "scipy.cluster": ModuleInfo(
            size_mb=2,
            description="聚类算法",
            dependencies=[],
        ),
        "scipy.special": ModuleInfo(
            size_mb=8,
            description="特殊数学函数 (贝塞尔/伽马)",
            dependencies=[],
        ),
    }

    common_hidden_imports = [
        "scipy._lib.messagestream",
        "scipy.special._ufuncs_cxx",
        "scipy.linalg.cython_blas",
        "scipy.linalg.cython_lapack",
        "scipy.sparse.csgraph._validation",
    ]

    excludable_data = [
        "scipy/.dylibs/",
    ]
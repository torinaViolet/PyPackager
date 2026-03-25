"""
PyTorch 裁剪配置
"""
from core.library_profiles.base_profile import BaseProfile, ModuleInfo


class TorchProfile(BaseProfile):
    """PyTorch 裁剪方案。"""

    name = "PyTorch"
    package_name = "torch"
    import_name = "torch"
    total_size_mb = 800.0

    modules = {
        "nn": ModuleInfo(
            size_mb=20, description="神经网络模块",
            dependencies=["autograd"], is_essential=True,
        ),
        "autograd": ModuleInfo(
            size_mb=10, description="自动求导",
            dependencies=[], is_essential=True,
        ),
        "optim": ModuleInfo(
            size_mb=5, description="优化器",
            dependencies=["nn"],
        ),
        "cuda": ModuleInfo(
            size_mb=300, description="CUDA GPU支持",
            dependencies=[],
        ),
        "distributed": ModuleInfo(
            size_mb=50, description="分布式训练",
            dependencies=["nn"],
        ),
        "jit": ModuleInfo(
            size_mb=30, description="JIT编译器",
            dependencies=["nn"],
        ),
        "onnx": ModuleInfo(
            size_mb=20, description="ONNX导出",
            dependencies=["nn", "jit"],
        ),
        "quantization": ModuleInfo(
            size_mb=15, description="量化",
            dependencies=["nn"],
        ),
        "utils": ModuleInfo(
            size_mb=5, description="工具函数",
            dependencies=[],
        ),
    }

    common_hidden_imports = [
        "torch._C",
        "torch.nn.modules",
    ]

    excludable_data = [
        {"path": "torch/lib/cudnn*", "size_mb": 200, "desc": "cuDNN库(CPU推理可排除)"},
        {"path": "torch/lib/cublas*", "size_mb": 100, "desc": "cuBLAS(CPU推理可排除)"},
    ]

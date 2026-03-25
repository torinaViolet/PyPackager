"""TensorFlow 库裁剪配置"""

from .base_profile import BaseProfile, ModuleInfo


class TensorflowProfile(BaseProfile):
    name = "tensorflow"
    package_name = "tensorflow"
    description = "深度学习框架"

    modules = {
        "tensorflow.keras": ModuleInfo(
            size_mb=20,
            description="高级深度学习 API (模型/层/训练)",
            dependencies=["tensorflow.python"],
        ),
        "tensorflow.python": ModuleInfo(
            size_mb=150,
            description="TF 核心 Python 绑定",
            dependencies=[],
            is_essential=True,
        ),
        "tensorflow.lite": ModuleInfo(
            size_mb=30,
            description="移动端/边缘设备推理引擎",
            dependencies=[],
        ),
        "tensorflow.estimator": ModuleInfo(
            size_mb=10,
            description="Estimator API (旧版高级API)",
            dependencies=["tensorflow.python"],
        ),
        "tensorflow.summary": ModuleInfo(
            size_mb=5,
            description="TensorBoard 日志摘要",
            dependencies=["tensorflow.python"],
        ),
        "tensorflow.saved_model": ModuleInfo(
            size_mb=5,
            description="模型保存与加载",
            dependencies=["tensorflow.python"],
        ),
        "tensorflow.data": ModuleInfo(
            size_mb=8,
            description="数据管道 (tf.data.Dataset)",
            dependencies=["tensorflow.python"],
        ),
        "tensorflow.distribute": ModuleInfo(
            size_mb=10,
            description="分布式训练策略",
            dependencies=["tensorflow.python"],
        ),
        "tensorflow.tpu": ModuleInfo(
            size_mb=8,
            description="TPU 支持",
            dependencies=["tensorflow.python", "tensorflow.distribute"],
        ),
        "tensorflow.debugging": ModuleInfo(
            size_mb=3,
            description="调试工具",
            dependencies=["tensorflow.python"],
        ),
    }

    common_hidden_imports = [
        "tensorflow.python.ops.gen_math_ops",
        "tensorflow.python.ops.gen_array_ops",
        "tensorflow.python.ops.gen_nn_ops",
        "tensorflow.python.eager.context",
        "tensorflow.python.platform.self_check",
        "google.protobuf",
        "h5py",
        "absl",
    ]

    excludable_data = [
        "tensorflow/include/",
        "tensorflow/lite/",
        "tensorflow/python/debug/",
    ]
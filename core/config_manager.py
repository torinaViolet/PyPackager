"""
配置管理模块
负责打包配置的创建、保存、加载和验证。
"""
import json
import os
from typing import Any, Optional

from utils.constants import CONFIG_VERSION, MODE_ONEFILE, ENGINE_PYINSTALLER


def create_default_config() -> dict:
    """创建默认配置字典。"""
    return {
        "config_version": CONFIG_VERSION,
        "project": {
            "name": "",
            "version": "1.0.0",
            "author": "",
            "description": "",
        },
        "entry": {
            "script": "",
            "icon": "",
            "output_dir": "./dist",
        },
        "build": {
            "engine": ENGINE_PYINSTALLER,
            "mode": MODE_ONEFILE,
            "console": False,
            "upx": False,
            "upx_path": "",
            "strip": False,
            "uac_admin": False,
            "clean": True,
            "extra_args": "",
        },
        "dependencies": {
            "hidden_imports": [],
            "excludes": [],
        },
        "resources": {
            "data_files": [],   # [{"src": "...", "dst": "..."}]
        },
        "trimming": {
            "enabled": True,
            "strategy": "recommended",
            "excluded_modules": [],
            "excluded_data": [],
        },
    }


class ConfigManager:
    """配置管理器，负责配置文件的 CRUD 操作。"""

    def __init__(self):
        self._config = create_default_config()
        self._file_path = None
        self._is_modified = False

    @property
    def config(self) -> dict:
        return self._config

    @property
    def file_path(self) -> Optional[str]:
        return self._file_path

    @property
    def is_modified(self) -> bool:
        return self._is_modified

    def get(self, key_path: str, default=None) -> Any:
        """
        用路径格式获取配置值。
        例如: get("build.engine") -> "pyinstaller"
        """
        keys = key_path.split(".")
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    def set(self, key_path: str, value: Any):
        """
        用路径格式设置配置值。
        例如: set("build.engine", "nuitka")
        """
        keys = key_path.split(".")
        config = self._config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
        self._is_modified = True

    def reset(self):
        """重置为默认配置。"""
        self._config = create_default_config()
        self._file_path = None
        self._is_modified = False

    def save(self, file_path: str = None) -> bool:
        """保存配置到 JSON 文件。"""
        path = file_path or self._file_path
        if not path:
            return False
        try:
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            self._file_path = path
            self._is_modified = False
            return True
        except (IOError, OSError) as e:
            print(f"保存配置失败: {e}")
            return False

    def load(self, file_path: str) -> bool:
        """从 JSON 文件加载配置。"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            # 用默认值补全缺失的字段
            default = create_default_config()
            self._config = self._merge_config(default, loaded)
            self._file_path = file_path
            self._is_modified = False
            return True
        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"加载配置失败: {e}")
            return False

    def _merge_config(self, default: dict, loaded: dict) -> dict:
        """递归合并配置，loaded 覆盖 default。"""
        result = default.copy()
        for key, value in loaded.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def update_from_dict(self, data: dict):
        """从字典批量更新配置。"""
        self._config = self._merge_config(self._config, data)
        self._is_modified = True

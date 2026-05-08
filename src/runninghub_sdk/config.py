"""
配置管理模块

从 .env 文件加载配置
"""

import os
from pathlib import Path


def load_env_file(env_path: Path = None) -> None:
    """
    加载 .env 文件到环境变量

    Args:
        env_path: .env 文件路径，默认为项目根目录
    """
    if env_path is None:
        # 查找 .env 文件
        current_dir = Path(__file__).parent
        env_path = current_dir / ".env"

        if not env_path.exists():
            # 尝试上级目录
            env_path = current_dir.parent / ".env"

    if not env_path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith("#"):
                continue

            # 解析 KEY=VALUE
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                # 移除引号
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                # 设置环境变量（不覆盖已存在的）
                if key and value and key not in os.environ:
                    os.environ[key] = value


def get_api_key() -> str:
    """
    获取 API Key

    优先级:
    1. 环境变量 RUNNINGHUB_API_KEY
    2. .env 文件中的配置

    Returns:
        API Key 字符串

    Raises:
        ValueError: 未配置 API Key
    """
    # 尝试从环境变量获取
    api_key = os.environ.get("RUNNINGHUB_API_KEY", "")

    if not api_key:
        # 尝试加载 .env 文件
        load_env_file()
        api_key = os.environ.get("RUNNINGHUB_API_KEY", "")

    if not api_key or api_key == "your-api-key-here":
        raise ValueError(
            "未配置 API Key!\n"
            "请在 .env 文件中设置 RUNNINGHUB_API_KEY，\n"
            "或设置环境变量 RUNNINGHUB_API_KEY"
        )

    return api_key


def get_base_url() -> str:
    """获取 API 基础 URL"""
    load_env_file()
    return os.environ.get("RUNNINGHUB_BASE_URL", "https://www.runninghub.cn")


def get_timeout() -> float:
    """获取请求超时时间"""
    load_env_file()
    return float(os.environ.get("RUNNINGHUB_TIMEOUT", "60"))
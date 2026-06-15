"""辅助函数模块"""

import hashlib
import json
import os
import time
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

T = TypeVar("T")


def calculate_md5(file_content: bytes) -> str:
    """
    计算文件内容的MD5值

    Args:
        file_content: 文件二进制内容

    Returns:
        MD5十六进制字符串
    """
    return hashlib.md5(file_content).hexdigest()


def calculate_md5_from_file(file_path: str) -> str:
    """
    计算文件的MD5值

    Args:
        file_path: 文件路径

    Returns:
        MD5十六进制字符串
    """
    with open(file_path, "rb") as f:
        return calculate_md5(f.read())


def sleep(seconds: float) -> None:
    """
    同步睡眠

    Args:
        seconds: 睡眠秒数
    """
    time.sleep(seconds)


async def async_sleep(seconds: float) -> None:
    """
    异步睡眠

    Args:
        seconds: 睡眠秒数
    """
    import asyncio
    await asyncio.sleep(seconds)


def retry_with_timeout(
    func: Callable[[], T],
    timeout: float,
    interval: float = 1.0,
    on_retry: Optional[Callable[[int, float], None]] = None
) -> T:
    """
    带超时的重试函数

    Args:
        func: 要执行的函数
        timeout: 超时时间（秒）
        interval: 重试间隔（秒）
        on_retry: 重试回调函数

    Returns:
        函数返回值

    Raises:
        TimeoutError: 超时
    """
    start_time = time.time()
    retry_count = 0

    while True:
        try:
            return func()
        except Exception:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(f"操作超时（{timeout}秒）")

            retry_count += 1
            if on_retry:
                on_retry(retry_count, elapsed)

            time.sleep(interval)


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        格式化的字符串，如 "1.5 MB"
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def bootstrap_env(script_dir: Optional[Union[str, Path]] = None) -> None:
    """
    加载 .env 文件到环境变量

    按优先级搜索：指定的脚本目录 > 当前工作目录

    Args:
        script_dir: 脚本所在目录路径（可选）。建议传入 Path(__file__).resolve().parent
    """
    from ..config import load_env_file

    search_dirs: List[Path] = []
    if script_dir:
        search_dirs.append(Path(script_dir))
    search_dirs.append(Path.cwd())

    for d in search_dirs:
        env_path = d / ".env"
        if env_path.exists():
            load_env_file(env_path)
            return


def get_env(name: str, default: str = "") -> str:
    """
    安全读取环境变量

    Args:
        name: 环境变量名称
        default: 默认值（可选）

    Returns:
        环境变量值，不存在时返回默认值
    """
    return os.getenv(name, "").strip() or default


def get_required_env(name: str) -> str:
    """
    强制读取环境变量，不存在时抛 ValueError

    Args:
        name: 环境变量名称

    Returns:
        环境变量值

    Raises:
        ValueError: 环境变量未设置
    """
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def to_dict(obj: Any) -> Any:
    """
    递归将 dataclass/enum 实例转为纯 dict，便于 JSON 序列化

    支持嵌套的 dataclass、enum、list、dict 组合。
    Enum 转为 .value，其他非容器类型原样返回。

    Args:
        obj: 任意对象

    Returns:
        JSON-friendly 的纯 dict/list/基本类型
    """
    # dataclass
    if hasattr(obj, '__dataclass_fields__'):
        return {k: to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    # enum
    if isinstance(obj, Enum):
        return obj.value
    # list / tuple
    if isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    # dict
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    return obj


def print_task_request_json(
    payload: Dict[str, Any],
    endpoint: Optional[str] = None,
) -> None:
    """
    以格式化 JSON 打印任务提交数据，便于调试。

    Args:
        payload: 提交任务时的请求体
        endpoint: 可选的接口路径
    """
    if endpoint:
        print(f"endpoint: {endpoint}")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
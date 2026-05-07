"""辅助函数模块"""

import hashlib
import time
from typing import Callable, TypeVar, Optional

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
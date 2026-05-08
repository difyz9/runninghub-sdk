"""
RunningHub ComfyUI SDK

一个轻量级的Python SDK，用于调用RunningHub的ComfyUI API。

示例:
    from runninghub_sdk import RunningHubClient, modify_nodes

    # 同步使用
    client = RunningHubClient(api_key="your-api-key")
    task = client.run("workflow-id")
    outputs = client.wait_for_completion(task.task_id)

    # 异步使用
    async with RunningHubClient(api_key="your-api-key") as client:
        task = await client.async_run("workflow-id")
        outputs = await client.async_wait_for_completion(task.task_id)

    # 使用节点修改器
    modifier = (
        modify_nodes()
        .text("6", "a beautiful sunset")
        .seed("3", 12345)
        .steps("3", 25)
    )
    task = client.run_with_modifier("workflow-id", modifier)
"""

__version__ = "1.0.0"

# 主类
from .client import RunningHubClient, create_client

# 类型导出
from .typedefs import (
    # 任务类型
    TaskStatus,
    NodeInput,
    CreateTaskRequest,
    CreateTaskResponse,
    TaskOutput,
    V2QueryResult,
    TaskFailedReason,
    WaitForCompletionOptions,
    # 上传类型
    UploadResponseData,
    LoraUploadResponse,
)

# 异常类导出 (包含 ErrorCode 和 ERROR_MESSAGES)
from .exceptions import (
    RunningHubError,
    TaskError,
    UploadError,
    TimeoutError,
    NetworkError,
    ValidationError,
    ErrorCode,
    ERROR_MESSAGES,
)

# 工具类导出
from .models import NodeModifier, modify_nodes

# 配置模块导出
from .config import get_api_key, get_base_url, get_timeout, load_env_file

__all__ = [
    # 版本
    "__version__",
    # 主类
    "RunningHubClient",
    "create_client",
    # 任务类型
    "TaskStatus",
    "NodeInput",
    "CreateTaskRequest",
    "CreateTaskResponse",
    "TaskOutput",
    "V2QueryResult",
    "TaskFailedReason",
    "WaitForCompletionOptions",
    # 上传类型
    "UploadResponseData",
    "LoraUploadResponse",
    # 错误类型
    "ErrorCode",
    "ERROR_MESSAGES",
    # 异常类
    "RunningHubError",
    "TaskError",
    "UploadError",
    "TimeoutError",
    "NetworkError",
    "ValidationError",
    # 工具类
    "NodeModifier",
    "modify_nodes",
    # 配置
    "get_api_key",
    "get_base_url",
    "get_timeout",
    "load_env_file",
]
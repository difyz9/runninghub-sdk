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

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("runninghub-sdk")
except PackageNotFoundError:
    __version__ = "0+unknown"

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
    ModelPricePreview,
    TaskFailedReason,
    TaskUsage,
    TaskUsageRecord,
    WaitForCompletionOptions,
    # 上传类型
    UploadResponseData,
    LoraUploadResponse,
    # 账户与 webhook 类型
    AccountStatus,
    ApiType,
    ApiKeyInfo,
    ApiKeyType,
    ApiKeyStatus,
    QueueStatus,
    WebhookDetail,
    WebhookCallbackStatus,
    # AI App 类型
    AiAppRunRequest,
    AiAppRunResponse,
    AiAppApiCallDemo,
    AiAppNodeInfo,
    AiAppStatisticsInfo,
    AiAppCover,
    AiAppTag,
    PublicModelListRequest,
    PublicModelListResponse,
    PublicModelRecord,
    PublicModelVersion,
    PublicModelPosterInfo,
    PublicModelOwner,
    PublicModelTag,
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
from .utils import print_task_request_json

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
    "ModelPricePreview",
    "TaskFailedReason",
    "TaskUsage",
    "TaskUsageRecord",
    "WaitForCompletionOptions",
    # 上传类型
    "UploadResponseData",
    "LoraUploadResponse",
    # 账户与 webhook 类型
    "AccountStatus",
    "ApiType",
    "ApiKeyInfo",
    "ApiKeyType",
    "ApiKeyStatus",
    "QueueStatus",
    "WebhookDetail",
    "WebhookCallbackStatus",
    # AI App 类型
    "AiAppRunRequest",
    "AiAppRunResponse",
    "AiAppApiCallDemo",
    "AiAppNodeInfo",
    "AiAppStatisticsInfo",
    "AiAppCover",
    "AiAppTag",
    "PublicModelListRequest",
    "PublicModelListResponse",
    "PublicModelRecord",
    "PublicModelVersion",
    "PublicModelPosterInfo",
    "PublicModelOwner",
    "PublicModelTag",
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
    "print_task_request_json",
    # 配置
    "get_api_key",
    "get_base_url",
    "get_timeout",
    "load_env_file",
]
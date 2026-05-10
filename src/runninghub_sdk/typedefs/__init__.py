"""类型定义模块"""

from .task import (
    TaskStatus,
    NodeInput,
    CreateTaskRequest,
    CreateTaskResponse,
    TaskOutput,
    V2QueryResult,
    ModelPricePreview,
    TaskFailedReason,
    WaitForCompletionOptions,
)
from .upload import (
    UploadResponseData,
    LoraUploadResponse,
)
from .account import (
    AccountStatus,
    ApiType,
    ApiKeyInfo,
    ApiKeyType,
    ApiKeyStatus,
    QueueStatus,
    WebhookDetail,
    WebhookCallbackStatus,
)
from .ai_app import (
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

# ErrorCode 和 ERROR_MESSAGES 在 exceptions.py 中定义，这里不重复导出

__all__ = [
    # 任务类型
    "TaskStatus",
    "NodeInput",
    "CreateTaskRequest",
    "CreateTaskResponse",
    "TaskOutput",
    "V2QueryResult",
    "ModelPricePreview",
    "TaskFailedReason",
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
]
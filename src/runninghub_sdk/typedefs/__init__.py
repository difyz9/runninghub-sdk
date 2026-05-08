"""类型定义模块"""

from .task import (
    TaskStatus,
    NodeInput,
    CreateTaskRequest,
    CreateTaskResponse,
    TaskOutput,
    V2QueryResult,
    TaskFailedReason,
    WaitForCompletionOptions,
)
from .upload import (
    UploadResponseData,
    LoraUploadResponse,
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
    "TaskFailedReason",
    "WaitForCompletionOptions",
    # 上传类型
    "UploadResponseData",
    "LoraUploadResponse",
]
"""RunningHub SDK 异常类定义"""

from typing import Optional


class ErrorCode:
    """API错误码"""
    SUCCESS = 0
    TASK_IS_RUNNING = 804
    TASK_STATUS_ERROR = 805
    TASK_NOT_FOUND = 807
    FILE_SIZE_EXCEEDED = 809
    TASK_IS_QUEUED = 813
    PERSONAL_QUEUE_COUNT_LIMIT = 814
    API_KEY_INVALID = 401
    UNKNOWN = -1


ERROR_MESSAGES = {
    ErrorCode.SUCCESS: "成功",
    ErrorCode.TASK_IS_RUNNING: "任务正在运行中",
    ErrorCode.TASK_STATUS_ERROR: "任务状态错误",
    ErrorCode.TASK_NOT_FOUND: "任务不存在",
    ErrorCode.FILE_SIZE_EXCEEDED: "文件大小超出限制(30MB)",
    ErrorCode.TASK_IS_QUEUED: "任务正在排队中",
    ErrorCode.PERSONAL_QUEUE_COUNT_LIMIT: "个人队列数量已达上限",
    ErrorCode.API_KEY_INVALID: "API Key无效",
    ErrorCode.UNKNOWN: "未知错误",
}


class RunningHubError(Exception):
    """RunningHub SDK 基础异常类"""

    def __init__(
        self,
        code: int = ErrorCode.UNKNOWN,
        message: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        self.code = code
        self.message = message or ERROR_MESSAGES.get(code, "未知错误")
        self.original_error = original_error
        super().__init__(self.message)

    @classmethod
    def from_api_response(cls, code: int, msg: str) -> "RunningHubError":
        """从API响应创建异常"""
        return cls(code=code, message=msg)

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class TaskError(RunningHubError):
    """任务相关错误"""

    def __init__(
        self,
        code: int = ErrorCode.UNKNOWN,
        message: Optional[str] = None,
        task_id: Optional[str] = None,
        failed_reason: Optional[dict] = None
    ):
        super().__init__(code=code, message=message)
        self.task_id = task_id
        self.failed_reason = failed_reason

    def __str__(self) -> str:
        base = super().__str__()
        if self.task_id:
            base = f"{base} (task_id: {self.task_id})"
        if self.failed_reason:
            node_name = self.failed_reason.get("node_name", "unknown")
            exc_msg = self.failed_reason.get("exception_message", "")
            base = f"{base}\n节点: {node_name}\n错误: {exc_msg}"
        return base


class UploadError(RunningHubError):
    """上传相关错误"""

    def __init__(
        self,
        code: int = ErrorCode.UNKNOWN,
        message: Optional[str] = None,
        file_name: Optional[str] = None
    ):
        super().__init__(code=code, message=message)
        self.file_name = file_name


class TimeoutError(RunningHubError):
    """超时错误"""

    def __init__(
        self,
        message: str = "操作超时",
        task_id: Optional[str] = None,
        timeout: Optional[float] = None
    ):
        super().__init__(code=ErrorCode.UNKNOWN, message=message)
        self.task_id = task_id
        self.timeout = timeout

    def __str__(self) -> str:
        base = self.message
        if self.timeout:
            base = f"{base} (超时时间: {self.timeout}秒)"
        if self.task_id:
            base = f"{base} (task_id: {self.task_id})"
        return base


class NetworkError(RunningHubError):
    """网络错误"""

    def __init__(
        self,
        message: str = "网络请求失败",
        original_error: Optional[Exception] = None
    ):
        super().__init__(
            code=ErrorCode.UNKNOWN,
            message=message,
            original_error=original_error
        )


class ValidationError(RunningHubError):
    """参数验证错误"""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(code=ErrorCode.UNKNOWN, message=message)
        self.field = field

    def __str__(self) -> str:
        if self.field:
            return f"参数验证错误 [{self.field}]: {self.message}"
        return f"参数验证错误: {self.message}"
"""账户、队列与 webhook 相关类型定义"""

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, Dict, Optional


class ApiType(str, Enum):
    """账户 API 类型"""

    NORMAL = "NORMAL"
    SHARED = "SHARED"
    EXCLUSIVE = "EXCLUSIVE"


class ApiKeyType(str, Enum):
    """API Key 队列类型"""

    NORMAL = "NORMAL"
    SHARED = "SHARED"
    EXCLUSIVE = "EXCLUSIVE"


class ApiKeyStatus(IntEnum):
    """API Key 状态

    文档仅展示了 `1` 的启用状态，这里补充常见的 `0/1` 常量，
    同时保留原始 `status` 字段以兼容未来扩展值。
    """

    DISABLED = 0
    ENABLED = 1


class WebhookCallbackStatus(str, Enum):
    """Webhook 回调状态"""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RETRYING = "RETRYING"


def _parse_enum(enum_cls: Any, value: Any) -> Optional[Any]:
    """安全解析枚举，遇到未知值时返回 None。"""
    try:
        return enum_cls(value)
    except (ValueError, TypeError):
        return None


@dataclass
class AccountStatus:
    """账户信息"""

    remain_coins: str
    current_task_counts: str
    remain_money: Optional[str]
    currency: Optional[str]
    api_type: str

    @property
    def api_type_enum(self) -> Optional[ApiType]:
        """账户 API 类型枚举；未知值返回 None。"""
        return _parse_enum(ApiType, self.api_type)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AccountStatus":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            remain_coins=str(data.get("remainCoins", "0")),
            current_task_counts=str(data.get("currentTaskCounts", "0")),
            remain_money=(
                str(data["remainMoney"]) if data.get("remainMoney") is not None else None
            ),
            currency=data.get("currency"),
            api_type=data.get("apiType", ""),
        )


@dataclass
class ApiKeyInfo:
    """API Key 信息"""

    key: str
    api_key_name: Optional[str]
    status: int
    quota_limit: Optional[float]
    quota_used: float
    visible: bool
    expire_at: Optional[str]
    expire_in_minute: Optional[int]
    created_at: str

    @property
    def status_enum(self) -> Optional[ApiKeyStatus]:
        """API Key 状态枚举；未知值返回 None。"""
        return _parse_enum(ApiKeyStatus, self.status)

    @property
    def is_enabled(self) -> bool:
        """API Key 是否处于启用状态。"""
        return self.status_enum == ApiKeyStatus.ENABLED

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ApiKeyInfo":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            key=data.get("key", ""),
            api_key_name=data.get("apiKeyName"),
            status=int(data.get("status", 0) or 0),
            quota_limit=(
                float(data["quotaLimit"]) if data.get("quotaLimit") is not None else None
            ),
            quota_used=float(data.get("quotaUsed", 0) or 0),
            visible=bool(data.get("visible", False)),
            expire_at=data.get("expireAt"),
            expire_in_minute=(
                int(data["expireInMinute"])
                if data.get("expireInMinute") is not None else None
            ),
            created_at=data.get("createdAt", ""),
        )


@dataclass
class QueueStatus:
    """指定 API Key 的队列状态"""

    api_key_type: str
    concurrent_limit: int
    running_count: str
    queued_count: str
    total_current_tasks: str

    @property
    def api_key_type_enum(self) -> Optional[ApiKeyType]:
        """队列 API Key 类型枚举；未知值返回 None。"""
        return _parse_enum(ApiKeyType, self.api_key_type)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "QueueStatus":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            api_key_type=data.get("apiKeyType", ""),
            concurrent_limit=int(data.get("concurrentLimit", 0) or 0),
            running_count=str(data.get("runningCount", "0")),
            queued_count=str(data.get("queuedCount", "0")),
            total_current_tasks=str(data.get("totalCurrentTasks", "0")),
        )


@dataclass
class WebhookDetail:
    """Webhook 事件详情"""

    id: str
    user_api_key: str
    task_id: str
    webhook_url: str
    event_data: str
    callback_status: str
    callback_response: str
    retry_count: int
    create_time: str
    update_time: str

    @property
    def callback_status_enum(self) -> Optional[WebhookCallbackStatus]:
        """Webhook 回调状态枚举；未知值返回 None。"""
        return _parse_enum(WebhookCallbackStatus, self.callback_status)

    @property
    def is_callback_success(self) -> bool:
        """Webhook 回调是否成功。"""
        return self.callback_status_enum == WebhookCallbackStatus.SUCCESS

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "WebhookDetail":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            user_api_key=data.get("userApiKey", ""),
            task_id=str(data.get("taskId", "")),
            webhook_url=data.get("webhookUrl", ""),
            event_data=data.get("eventData", ""),
            callback_status=data.get("callbackStatus", ""),
            callback_response=data.get("callbackResponse", ""),
            retry_count=int(data.get("retryCount", 0) or 0),
            create_time=data.get("createTime", ""),
            update_time=data.get("updateTime", ""),
        )
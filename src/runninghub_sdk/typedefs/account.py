"""账户、队列与 webhook 相关类型定义"""

import json
import time
from dataclasses import dataclass
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any, Dict, Optional, Union


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


@dataclass
class RunningHubToken:
    """手机号密码登录返回的 token 信息

    支持本地缓存和自动过期检测：
        token = RunningHubToken.from_dict(login_response)

        # 缓存到本地文件
        token.save("token.json", username="138xxxxxxxx")

        # 从缓存恢复
        token, username = RunningHubToken.load("token.json")
        if token.is_expired:
            print("token 已过期，请重新登录")
    """

    access_token: str
    refresh_token: str
    expire_in: int
    identify: Optional[str] = None
    first_login: Optional[bool] = None

    @property
    def expires_at_ms(self) -> int:
        """过期时间戳（毫秒）"""
        return int(time.time() * 1000) + self.expire_in

    @property
    def is_expired(self) -> bool:
        """判断 token 是否已过期"""
        return self.expires_at_ms <= int(time.time() * 1000)

    def save(self, path: Union[str, Path], username: str = "") -> Path:
        """
        将 token 缓存到本地 JSON 文件

        Args:
            path: 缓存文件路径
            username: 关联的手机号/用户名（用于自动重新登录）

        Returns:
            写入的文件路径
        """
        save_path = Path(path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "username": username,
            "token": {
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expire_in": self.expire_in,
                "expires_at_ms": self.expires_at_ms,
                "identify": self.identify,
                "first_login": self.first_login,
            },
        }
        save_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return save_path

    @classmethod
    def load(cls, path: Union[str, Path]) -> "RunningHubToken":
        """
        从本地 JSON 文件读取缓存 token

        Args:
            path: 缓存文件路径

        Returns:
            RunningHubToken 实例

        Raises:
            FileNotFoundError: 缓存文件不存在
            ValueError: 缓存文件格式无效
        """
        load_path = Path(path)
        data = json.loads(load_path.read_text(encoding="utf-8"))

        # 支持两种格式：带外层的 {username, token} 和纯 token dict
        token_data = data.get("token", data)
        return cls(
            access_token=token_data.get("access_token", ""),
            refresh_token=token_data.get("refresh_token", ""),
            expire_in=int(token_data.get("expire_in", 0) or 0),
            identify=token_data.get("identify"),
            first_login=token_data.get("first_login"),
        )

    @classmethod
    def load_with_username(
        cls, path: Union[str, Path]
    ) -> "RunningHubToken":
        """
        从本地 JSON 文件读取缓存 token，同时返回 username

        Args:
            path: 缓存文件路径

        Returns:
            (RunningHubToken, username) 元组
        """
        load_path = Path(path)
        data = json.loads(load_path.read_text(encoding="utf-8"))
        username = data.get("username", "")
        return cls.load(path), username

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "RunningHubToken":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            access_token=data.get("access_token", ""),
            refresh_token=data.get("refresh_token", ""),
            expire_in=int(data.get("expire_in", 0) or 0),
            identify=data.get("identify"),
            first_login=data.get("firstLogin"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为可序列化字典"""
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expire_in": self.expire_in,
            "expires_at_ms": self.expires_at_ms,
            "identify": self.identify,
            "first_login": self.first_login,
        }
"""账户、队列与 webhook 相关类型定义"""

import json
import time
from dataclasses import dataclass
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


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


# ==================== 用户信息 /uc/getUserInfo ====================


@dataclass
class UserInfoRequest:
    """获取用户信息请求参数"""

    user_id: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 请求格式"""
        return {"userId": self.user_id}


@dataclass
class MemberInfo:
    """会员信息"""

    user_type: str = ""
    member_code: str = ""
    member_name: str = ""
    member_expired_time: str = ""
    member_remaining_days: str = ""
    member_remaining_months: str = ""
    lowest_price: Optional[str] = None
    currency: Optional[str] = None
    pay_channel: str = ""
    member_unit: str = ""
    buy_type: int = 0
    watermark_settings_is_popup: bool = False
    expired: bool = False
    popup: bool = False

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "MemberInfo":
        if data is None:
            data = {}
        return cls(
            user_type=str(data.get("userType", "")),
            member_code=data.get("memberCode", ""),
            member_name=data.get("memberName", ""),
            member_expired_time=data.get("memberExpiredTime", ""),
            member_remaining_days=str(data.get("memberRemainingDays", "")),
            member_remaining_months=str(data.get("memberRemainingMonths", "")),
            lowest_price=str(data["lowestPrice"]) if data.get("lowestPrice") is not None else None,
            currency=data.get("currency"),
            pay_channel=data.get("payChannel", ""),
            member_unit=data.get("memberUnit", ""),
            buy_type=int(data.get("buyType", 0) or 0),
            watermark_settings_is_popup=bool(data.get("watermarkSettingsIsPopup", False)),
            expired=bool(data.get("expired", False)),
            popup=bool(data.get("popup", False)),
        )


@dataclass
class WalletInfo:
    """钱包信息"""

    currency_symbol: str = ""
    currency: str = ""
    balance: float = 0.0
    has_recharged: bool = False

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "WalletInfo":
        if data is None:
            data = {}
        return cls(
            currency_symbol=data.get("currencySymbol", ""),
            currency=data.get("currency", ""),
            balance=float(data.get("balance", 0) or 0),
            has_recharged=bool(data.get("hasRecharged", False)),
        )


@dataclass
class UserConfig:
    """用户配置"""

    sku_standard_model_task_count_max: int = 100
    user_preference_package_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "UserConfig":
        if data is None:
            data = {}
        return cls(
            sku_standard_model_task_count_max=int(data.get("skuStandardModelTaskCountMax", 100) or 100),
            user_preference_package_id=data.get("userPreferencePackageId"),
        )


@dataclass
class ProductPackage:
    """产品套餐"""

    id: str = ""
    rights_id: str = ""
    package_name: str = ""
    package_desc: Optional[str] = None
    rights_desc: str = ""
    is_default: bool = False
    seq: str = ""
    coin_value: int = 0
    wallet_value: float = 0.0
    currency: str = ""
    unit_desc: str = ""
    package_code: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ProductPackage":
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            rights_id=str(data.get("rightsId", "")),
            package_name=data.get("packageName", ""),
            package_desc=data.get("packageDesc"),
            rights_desc=data.get("rightsDesc", ""),
            is_default=bool(data.get("isDefault", False)),
            seq=data.get("seq", ""),
            coin_value=int(data.get("coinValue", 0) or 0),
            wallet_value=float(data.get("walletValue", 0) or 0),
            currency=data.get("currency", ""),
            unit_desc=data.get("unitDesc", ""),
            package_code=data.get("packageCode", ""),
        )


@dataclass
class UserInfoResponse:
    """用户信息响应（uc/getUserInfo）"""

    id: str = ""
    mobile: str = ""
    email: Optional[str] = None
    pwd_flag: bool = False
    head_icon: str = ""
    nick_name: str = ""
    home_page: Optional[str] = None
    member_info: Optional[MemberInfo] = None
    virtual_coin: str = "0"
    virtual_coin_daily: str = "0"
    total_coin: str = "0"
    introduce: Optional[str] = None
    profile: Optional[str] = None
    instance_state: int = -1
    instance_subscribed_type: int = 0
    instance_expire_time_str: str = ""
    instance_expire_time_ts: str = "0"
    balance_use_up_time_str: str = ""
    balance_use_up_time_ts: Optional[str] = None
    power_value: str = "0"
    api_key: str = ""
    ip: str = ""
    country: str = ""
    region: Optional[str] = None
    channel: str = ""
    user_flag: str = ""
    login_coin_triggered: bool = False
    type: str = ""
    role: str = ""
    wx_open_id: Optional[str] = None
    wx_union_id: Optional[str] = None
    wx_nick_name: Optional[str] = None
    wx_head_img_url: Optional[str] = None
    invite_code: str = ""
    invite_config: Optional[str] = None
    invite_code_used: bool = False
    used_invite_code: Optional[str] = None
    like_count: str = "0"
    collect_count: str = "0"
    follow_count: str = "0"
    fan_count: str = "0"
    is_kol: bool = False
    watermark_text: str = ""
    default_watermark_text: str = ""
    watermark_removal_type: int = 0
    notice_has_unread: bool = False
    web_task_max_count_limit: int = 0
    instance_count: Optional[Any] = None
    multiplier: float = 1.0
    multiplier_corp_api: float = 1.0
    show_kontext: bool = False
    wallet_info: Optional[WalletInfo] = None
    bank_dialog_vo: Optional[Any] = None
    user_config: Optional[UserConfig] = None
    product_packages: Optional[List[ProductPackage]] = None
    user_preference_package_id: Optional[str] = None
    show_package_update_popup: bool = False
    package_effective_date: str = ""
    current_package_id: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "UserInfoResponse":
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            mobile=data.get("mobile", ""),
            email=data.get("email"),
            pwd_flag=bool(data.get("pwdFlag", False)),
            head_icon=data.get("headIcon", ""),
            nick_name=data.get("nickName", ""),
            home_page=data.get("homePage"),
            member_info=MemberInfo.from_dict(data.get("memberInfo")),
            virtual_coin=str(data.get("virtualCoin", "0")),
            virtual_coin_daily=str(data.get("virtualCoinDaily", "0")),
            total_coin=str(data.get("totalCoin", "0")),
            introduce=data.get("introduce"),
            profile=data.get("profile"),
            instance_state=int(data.get("instanceState", -1) or -1),
            instance_subscribed_type=int(data.get("instanceSubscribedType", 0) or 0),
            instance_expire_time_str=data.get("instanceExpireTimeStr", ""),
            instance_expire_time_ts=str(data.get("instanceExpireTimeTs", "0")),
            balance_use_up_time_str=data.get("balanceUseUpTimeStr", ""),
            balance_use_up_time_ts=str(data["balanceUseUpTimeTs"]) if data.get("balanceUseUpTimeTs") is not None else None,
            power_value=str(data.get("powerValue", "0")),
            api_key=data.get("apiKey", ""),
            ip=data.get("ip", ""),
            country=data.get("country", ""),
            region=data.get("region"),
            channel=data.get("channel", ""),
            user_flag=data.get("userFlag", ""),
            login_coin_triggered=bool(data.get("loginCoinTriggered", False)),
            type=str(data.get("type", "")),
            role=data.get("role", ""),
            wx_open_id=data.get("wxOpenId"),
            wx_union_id=data.get("wxUnionId"),
            wx_nick_name=data.get("wxNickName"),
            wx_head_img_url=data.get("wxHeadImgUrl"),
            invite_code=data.get("inviteCode", ""),
            invite_config=str(data["inviteConfig"]) if data.get("inviteConfig") is not None else None,
            invite_code_used=bool(data.get("inviteCodeUsed", False)),
            used_invite_code=data.get("usedInviteCode"),
            like_count=str(data.get("likeCount", "0")),
            collect_count=str(data.get("collectCount", "0")),
            follow_count=str(data.get("followCount", "0")),
            fan_count=str(data.get("fanCount", "0")),
            is_kol=bool(data.get("isKOL", False)),
            watermark_text=data.get("watermarkText", ""),
            default_watermark_text=data.get("defaultWatermarkText", ""),
            watermark_removal_type=int(data.get("watermarkRemovalType", 0) or 0),
            notice_has_unread=bool(data.get("noticeHasUnread", False)),
            web_task_max_count_limit=int(data.get("webTaskMaxCountLimit", 0) or 0),
            instance_count=data.get("instanceCount"),
            multiplier=float(data.get("multiplier", 1.0) or 1.0),
            multiplier_corp_api=float(data.get("multiplierCorpApi", 1.0) or 1.0),
            show_kontext=bool(data.get("showKontext", False)),
            wallet_info=WalletInfo.from_dict(data.get("walletInfo")),
            bank_dialog_vo=data.get("bankDialogVo"),
            user_config=UserConfig.from_dict(data.get("userConfig")),
            product_packages=[ProductPackage.from_dict(item) for item in data.get("productPackages", [])],
            user_preference_package_id=data.get("userPreferencePackageId"),
            show_package_update_popup=bool(data.get("showPackageUpdatePopup", False)),
            package_effective_date=data.get("packageEffectiveDate", ""),
            current_package_id=data.get("currentPackageId", ""),
        )


# ==================== API Key 查询 /uc/apiKey/get ====================


@dataclass
class UserApiKeyRequest:
    """查询用户 API Key 请求参数"""

    user_id: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 请求格式"""
        return {"userId": self.user_id}


@dataclass
class SharedApiInfo:
    """共享 API 信息"""

    description: Optional[str] = None
    currency: str = ""
    concurrent_limit: int = 0
    billing_rate: float = 0.0
    billing_48_rate: float = 0.0
    api_key: str = ""
    quick_create_cost_money: float = 0.0

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "SharedApiInfo":
        if data is None:
            data = {}
        return cls(
            description=data.get("description"),
            currency=data.get("currency", ""),
            concurrent_limit=int(data.get("concurrentLimit", 0) or 0),
            billing_rate=float(data.get("billingRate", 0) or 0),
            billing_48_rate=float(data.get("billing48Rate", 0) or 0),
            api_key=data.get("apiKey", ""),
            quick_create_cost_money=float(data.get("quickCreateCostMoney", 0) or 0),
        )


@dataclass
class ExclusiveApiInfo:
    """专属 API 信息"""

    enabled: bool = False
    description: Optional[str] = None
    api_key: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "ExclusiveApiInfo":
        if data is None:
            data = {}
        return cls(
            enabled=bool(data.get("enabled", False)),
            description=data.get("description"),
            api_key=data.get("apiKey"),
        )


@dataclass
class BalanceInfo:
    """余额信息"""

    currency_symbol: Optional[str] = None
    currency: str = ""
    balance: float = 0.0

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "BalanceInfo":
        if data is None:
            data = {}
        return cls(
            currency_symbol=data.get("currencySymbol"),
            currency=data.get("currency", ""),
            balance=float(data.get("balance", 0) or 0),
        )


@dataclass
class UserApiKeyResponse:
    """用户 API Key 信息响应（uc/apiKey/get）"""

    shared_api: Optional[SharedApiInfo] = None
    normal_api_key: str = ""
    exclusive_api: Optional[ExclusiveApiInfo] = None
    balance_info: Optional[BalanceInfo] = None
    monthly_cost: float = 0.0
    current_month_period: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "UserApiKeyResponse":
        if data is None:
            data = {}
        return cls(
            shared_api=SharedApiInfo.from_dict(data.get("sharedApi")),
            normal_api_key=data.get("normalApiKey", ""),
            exclusive_api=ExclusiveApiInfo.from_dict(data.get("exclusiveApi")),
            balance_info=BalanceInfo.from_dict(data.get("balanceInfo")),
            monthly_cost=float(data.get("monthlyCost", 0) or 0),
            current_month_period=data.get("currentMonthPeriod", ""),
        )
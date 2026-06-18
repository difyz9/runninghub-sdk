"""账单用量明细类型定义（/api/billing/usage/wideDetails）"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BillingUsageWideDetailRequest:
    """账单用量明细请求参数"""

    start_date_time: str = ""
    end_date_time: str = ""
    size: int = 10
    include_stats: bool = True
    include_child_tasks: bool = True
    cursor: Optional[str] = None
    task_status: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "startDateTime": self.start_date_time,
            "endDateTime": self.end_date_time,
            "size": self.size,
            "includeStats": self.include_stats,
            "includeChildTasks": self.include_child_tasks,
        }
        if self.cursor is not None:
            d["cursor"] = self.cursor
        if self.task_status is not None:
            d["taskStatus"] = self.task_status
        return d


@dataclass
class BillingUsageWideDetailRecord:
    """账单用量明细记录"""

    pk: str = ""
    task_id: str = ""
    user_id: str = ""
    user_name: str = ""
    team_id: Optional[str] = None
    team_name: Optional[str] = None
    task_name: str = ""
    sku_id: Optional[str] = None
    sku_name_cn: Optional[str] = None
    sku_name_en: Optional[str] = None
    fast_template_code: Optional[str] = None
    real_instance_type: str = ""
    sku_name: Optional[str] = None
    task_category_code: str = ""
    task_category: str = ""
    task_category_display: str = ""
    original_task_category: Optional[str] = None
    task_status: str = ""
    workflow_id: Optional[str] = None
    webapp_id: Optional[str] = None
    api_key: Optional[str] = None
    app_code: Optional[str] = None
    vibex_app_id: Optional[str] = None
    workflow_name: str = ""
    del_flag: bool = False
    error_type: str = ""
    create_time: str = ""
    last_update_time: str = ""
    task_start_time: str = ""
    currency: Optional[str] = None
    api_key_type: int = 0
    api_key_name: Optional[str] = None
    purchased_wallet_amount: float = 0.0
    member_gift_wallet_amount: float = 0.0
    gift_wallet_amount: float = 0.0
    shared_api_wallet_amount: float = 0.0
    third_party_wallet_amount: float = 0.0
    money_amount: float = 0.0
    original_money_amount: Optional[float] = None
    money_discount: Optional[float] = None
    money_discount_amount: Optional[float] = None
    money_duration: str = "0"
    coin_amount: float = 0.0
    coin_used_duration: str = "0"
    task_relation: str = "NORMAL"
    parent_task_id: Optional[str] = None
    call_channel: str = "NORMAL"
    call_type: str = ""
    call_type_display: str = ""
    task_resource_type: str = ""
    canvas_id: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "BillingUsageWideDetailRecord":
        if data is None:
            data = {}
        return cls(
            pk=data.get("pk", ""),
            task_id=str(data.get("taskId", "")),
            user_id=str(data.get("userId", "")),
            user_name=data.get("userName", ""),
            team_id=str(data.get("teamId")) if data.get("teamId") is not None else None,
            team_name=data.get("teamName"),
            task_name=data.get("taskName", ""),
            sku_id=data.get("skuId"),
            sku_name_cn=data.get("skuNameCn"),
            sku_name_en=data.get("skuNameEn"),
            fast_template_code=data.get("fastTemplateCode"),
            real_instance_type=data.get("realInstanceType", ""),
            sku_name=data.get("skuName"),
            task_category_code=data.get("taskCategoryCode", ""),
            task_category=data.get("taskCategory", ""),
            task_category_display=data.get("taskCategoryDisplay", ""),
            original_task_category=data.get("originalTaskCategory"),
            task_status=data.get("taskStatus", ""),
            workflow_id=str(data.get("workflowId")) if data.get("workflowId") is not None else None,
            webapp_id=str(data.get("webappId")) if data.get("webappId") is not None else None,
            api_key=data.get("apiKey"),
            app_code=data.get("appCode"),
            vibex_app_id=data.get("vibexAppId"),
            workflow_name=data.get("workflowName", ""),
            del_flag=bool(data.get("delFlag", False)),
            error_type=data.get("errorType", ""),
            create_time=data.get("createTime", ""),
            last_update_time=data.get("lastUpdateTime", ""),
            task_start_time=data.get("taskStartTime", ""),
            currency=data.get("currency"),
            api_key_type=int(data.get("apiKeyType", 0) or 0),
            api_key_name=data.get("apiKeyName"),
            purchased_wallet_amount=float(data.get("purchasedWalletAmount", 0) or 0),
            member_gift_wallet_amount=float(data.get("memberGiftWalletAmount", 0) or 0),
            gift_wallet_amount=float(data.get("giftWalletAmount", 0) or 0),
            shared_api_wallet_amount=float(data.get("sharedApiWalletAmount", 0) or 0),
            third_party_wallet_amount=float(data.get("thirdPartyWalletAmount", 0) or 0),
            money_amount=float(data.get("moneyAmount", 0) or 0),
            original_money_amount=float(data["originalMoneyAmount"]) if data.get("originalMoneyAmount") is not None else None,
            money_discount=float(data["moneyDiscount"]) if data.get("moneyDiscount") is not None else None,
            money_discount_amount=float(data["moneyDiscountAmount"]) if data.get("moneyDiscountAmount") is not None else None,
            money_duration=str(data.get("moneyDuration", "0")),
            coin_amount=float(data.get("coinAmount", 0) or 0),
            coin_used_duration=str(data.get("coinUsedDuration", "0")),
            task_relation=data.get("taskRelation", "NORMAL"),
            parent_task_id=str(data.get("parentTaskId")) if data.get("parentTaskId") is not None else None,
            call_channel=data.get("callChannel", "NORMAL"),
            call_type=data.get("callType", ""),
            call_type_display=data.get("callTypeDisplay", ""),
            task_resource_type=data.get("taskResourceType", ""),
            canvas_id=data.get("canvasId"),
        )


@dataclass
class BillingUsageWideDetailResponse:
    """账单用量明细响应数据"""

    records: List[BillingUsageWideDetailRecord] = field(default_factory=list)
    size: str = "0"
    next_cursor: Optional[str] = None
    prev_cursor: Optional[str] = None
    has_next: bool = False
    has_previous: bool = False
    currency: str = ""
    total: str = "0"
    duration: str = "0"
    coin_num: float = 0.0
    amount: float = 0.0

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "BillingUsageWideDetailResponse":
        if data is None:
            data = {}
        return cls(
            records=[BillingUsageWideDetailRecord.from_dict(item) for item in (data.get("records") or [])],
            size=str(data.get("size", "0")),
            next_cursor=data.get("nextCursor"),
            prev_cursor=data.get("prevCursor"),
            has_next=bool(data.get("hasNext", False)),
            has_previous=bool(data.get("hasPrevious", False)),
            currency=data.get("currency", ""),
            total=str(data.get("total", "0")),
            duration=str(data.get("duration", "0")),
            coin_num=float(data.get("coinNum", 0) or 0),
            amount=float(data.get("amount", 0) or 0),
        )

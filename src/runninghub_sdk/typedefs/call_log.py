"""任务调用日志详情类型定义（/api/openapi/my/call/log/detail）"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CallLogDetailRequest:
    """调用日志详情请求参数"""

    task_id: str
    user_id: str

    def to_dict(self) -> Dict[str, str]:
        """转换为 API 请求格式"""
        return {"taskId": self.task_id, "userId": self.user_id}


@dataclass
class CallLogBasicInfo:
    """调用日志基本信息"""

    api_name: str = ""
    api_type: str = ""
    api_key_type: str = ""
    task_status: str = ""
    task_id: str = ""
    call_time: str = ""
    duration: str = ""
    amount: Optional[str] = None
    coin_num: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CallLogBasicInfo":
        if data is None:
            data = {}
        return cls(
            api_name=data.get("apiName", ""),
            api_type=data.get("apiType", ""),
            api_key_type=str(data.get("apiKeyType", "")),
            task_status=data.get("taskStatus", ""),
            task_id=str(data.get("taskId", "")),
            call_time=data.get("callTime", ""),
            duration=data.get("duration", ""),
            amount=str(data.get("amount")) if data.get("amount") is not None else None,
            coin_num=data.get("coinNum", ""),
        )


@dataclass
class CallLogOutputItem:
    """调用日志输出文件项"""

    output_name: str = ""
    output_type: str = ""
    file_url: str = ""
    file_preview_url: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CallLogOutputItem":
        if data is None:
            data = {}
        return cls(
            output_name=data.get("outputName", ""),
            output_type=data.get("outputType", ""),
            file_url=data.get("fileUrl", ""),
            file_preview_url=data.get("filePreviewUrl", ""),
        )


@dataclass
class CallLogCostInfo:
    """调用日志费用信息"""

    amount: Optional[str] = None
    coin_num: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CallLogCostInfo":
        if data is None:
            data = {}
        return cls(
            amount=str(data.get("amount")) if data.get("amount") is not None else None,
            coin_num=data.get("coinNum", ""),
        )


@dataclass
class CallLogRequestInfo:
    """调用日志请求参数信息"""

    api_request_params: Any = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CallLogRequestInfo":
        if data is None:
            data = {}
        raw = data.get("apiRequestParams", "")
        # 自动将 JSON 字符串解析为 dict，to_dict() 时直接输出结构化对象
        if isinstance(raw, str) and raw.strip():
            import json
            try:
                raw = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                pass
        return cls(api_request_params=raw)

    def get_request_params_parsed(self) -> Dict[str, Any]:
        """获取解析后的请求参数字典"""
        if isinstance(self.api_request_params, dict):
            return self.api_request_params
        import json
        try:
            return json.loads(self.api_request_params)
        except (json.JSONDecodeError, TypeError):
            return {}


@dataclass
class CallLogResultItem:
    """调用日志结果项"""

    url: str = ""
    node_id: str = ""
    output_type: str = ""
    text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CallLogResultItem":
        if data is None:
            data = {}
        return cls(
            url=data.get("url", ""),
            node_id=str(data.get("nodeId", "")),
            output_type=data.get("outputType", ""),
            text=data.get("text"),
        )


@dataclass
class CallLogUsage:
    """调用日志用量信息"""

    consume_money: Optional[str] = None
    consume_coins: str = ""
    task_cost_time: str = ""
    third_party_consume_money: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CallLogUsage":
        if data is None:
            data = {}
        return cls(
            consume_money=str(data.get("consumeMoney")) if data.get("consumeMoney") is not None else None,
            consume_coins=data.get("consumeCoins", ""),
            task_cost_time=data.get("taskCostTime", ""),
            third_party_consume_money=str(data.get("thirdPartyConsumeMoney")) if data.get("thirdPartyConsumeMoney") is not None else None,
        )


@dataclass
class CallLogTaskUsageRecord:
    """调用日志任务用量记录"""

    task_id: str = ""
    parent_task_id: Optional[str] = None
    task_status: str = ""
    usage: Optional[CallLogUsage] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CallLogTaskUsageRecord":
        if data is None:
            data = {}
        return cls(
            task_id=str(data.get("taskId", "")),
            parent_task_id=str(data.get("parentTaskId")) if data.get("parentTaskId") is not None else None,
            task_status=data.get("taskStatus", ""),
            usage=CallLogUsage.from_dict(data.get("usage")),
        )


@dataclass
class CallLogResponseInfo:
    """调用日志响应信息"""

    task_id: str = ""
    status: str = ""
    error_code: str = ""
    error_message: str = ""
    results: List[CallLogResultItem] = field(default_factory=list)
    client_id: str = ""
    prompt_tips: str = ""
    failed_reason: Dict[str, Any] = field(default_factory=dict)
    usage: Optional[CallLogUsage] = None
    parent_task_id: Optional[str] = None
    task_usage_list: List[CallLogTaskUsageRecord] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CallLogResponseInfo":
        if data is None:
            data = {}
        return cls(
            task_id=str(data.get("taskId", "")),
            status=data.get("status", ""),
            error_code=data.get("errorCode", ""),
            error_message=data.get("errorMessage", ""),
            results=[CallLogResultItem.from_dict(item) for item in (data.get("results") or [])],
            client_id=data.get("clientId", ""),
            prompt_tips=data.get("promptTips", ""),
            failed_reason=data.get("failedReason") or {},
            usage=CallLogUsage.from_dict(data.get("usage")),
            parent_task_id=str(data.get("parentTaskId")) if data.get("parentTaskId") is not None else None,
            task_usage_list=[CallLogTaskUsageRecord.from_dict(item) for item in (data.get("taskUsageList") or [])],
        )


@dataclass
class CallLogDetailResponse:
    """调用日志详情响应数据"""

    basic_info: Optional[CallLogBasicInfo] = None
    outputs: List[CallLogOutputItem] = field(default_factory=list)
    cost_info: Optional[CallLogCostInfo] = None
    request_info: Optional[CallLogRequestInfo] = None
    response_info: Optional[CallLogResponseInfo] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CallLogDetailResponse":
        if data is None:
            data = {}
        return cls(
            basic_info=CallLogBasicInfo.from_dict(data.get("basicInfo")),
            outputs=[CallLogOutputItem.from_dict(item) for item in (data.get("list") or [])],
            cost_info=CallLogCostInfo.from_dict(data.get("costInfo")),
            request_info=CallLogRequestInfo.from_dict(data.get("requestInfo")),
            response_info=CallLogResponseInfo.from_dict(data.get("responseInfo")),
        )

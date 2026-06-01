"""任务相关类型定义"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any, Callable


class TaskStatus(str, Enum):
    """任务状态枚举"""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass
class NodeInput:
    """节点输入信息"""
    node_id: str
    field_name: str
    field_value: Union[str, int, bool, float]

    def to_dict(self) -> Dict[str, Any]:
        """转换为API请求格式"""
        return {
            "nodeId": self.node_id,
            "fieldName": self.field_name,
            "fieldValue": self.field_value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NodeInput":
        """从字典创建"""
        return cls(
            node_id=data["nodeId"],
            field_name=data["fieldName"],
            field_value=data["fieldValue"],
        )


@dataclass
class CreateTaskRequest:
    """创建任务请求参数"""
    workflow_id: str
    node_info_list: Optional[List[NodeInput]] = None
    add_metadata: bool = True
    webhook_url: Optional[str] = None
    workflow: Optional[str] = None
    instance_type: Optional[str] = None
    use_personal_queue: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为API请求格式"""
        data: Dict[str, Any] = {
            "workflowId": self.workflow_id,
            "addMetadata": self.add_metadata,
            "usePersonalQueue": self.use_personal_queue,
        }
        if self.node_info_list:
            data["nodeInfoList"] = [n.to_dict() for n in self.node_info_list]
        if self.webhook_url:
            data["webhookUrl"] = self.webhook_url
        if self.workflow:
            data["workflow"] = self.workflow
        if self.instance_type:
            data["instanceType"] = self.instance_type
        return data


@dataclass
class CreateTaskResponse:
    """创建任务响应"""
    task_id: str
    task_status: TaskStatus
    client_id: str
    prompt_tips: str
    net_wss_url: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CreateTaskResponse":
        """从API响应创建"""
        return cls(
            task_id=data["taskId"],
            task_status=TaskStatus(data["taskStatus"]),
            client_id=data["clientId"],
            prompt_tips=data.get("promptTips", ""),
            net_wss_url=data.get("netWssUrl"),
        )


@dataclass
class TaskOutput:
    """任务输出结果"""
    file_url: str
    file_type: str
    task_cost_time: str
    node_id: str
    third_party_consume_money: Optional[str] = None
    consume_money: Optional[str] = None
    consume_coins: str = "0"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskOutput":
        """从API响应创建"""
        return cls(
            file_url=data["fileUrl"],
            file_type=data["fileType"],
            task_cost_time=str(data.get("taskCostTime", "")),
            node_id=data.get("nodeId", ""),
            third_party_consume_money=data.get("thirdPartyConsumeMoney"),
            consume_money=data.get("consumeMoney"),
            consume_coins=str(data.get("consumeCoins", "0")),
        )


@dataclass
class TaskFailedReason:
    """任务失败原因"""
    current_outputs: str
    exception_type: str
    node_name: str
    current_inputs: str
    traceback: str
    node_id: str
    exception_message: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskFailedReason":
        """从API响应创建"""
        return cls(
            current_outputs=data.get("current_outputs", ""),
            exception_type=data.get("exception_type", ""),
            node_name=data.get("node_name", ""),
            current_inputs=data.get("current_inputs", ""),
            traceback=data.get("traceback", ""),
            node_id=data.get("node_id", ""),
            exception_message=data.get("exception_message", ""),
        )


@dataclass
class V2QueryResult:
    """V2查询结果"""
    task_id: str
    status: Optional[TaskStatus]
    error_code: str
    error_message: str
    results: Optional[List[Dict[str, Any]]]
    client_id: str
    prompt_tips: str
    failed_reason: Optional[TaskFailedReason] = None
    usage: Optional["TaskUsage"] = None
    parent_task_id: Optional[str] = None
    task_usage_list: List["TaskUsageRecord"] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "V2QueryResult":
        """从API响应创建"""
        raw_status = data.get("status", "")
        usage_data = data.get("usage")
        task_usage_list_data = data.get("taskUsageList") or []

        return cls(
            task_id=data.get("taskId", ""),
            status=TaskStatus(raw_status) if raw_status else None,
            error_code=data.get("errorCode", ""),
            error_message=data.get("errorMessage", ""),
            results=data.get("results"),
            client_id=data.get("clientId", ""),
            prompt_tips=data.get("promptTips", ""),
            failed_reason=(
                TaskFailedReason.from_dict(data["failedReason"])
                if isinstance(data.get("failedReason"), dict)
                else None
            ),
            usage=(TaskUsage.from_dict(usage_data) if isinstance(usage_data, dict) else None),
            parent_task_id=data.get("parentTaskId"),
            task_usage_list=[
                TaskUsageRecord.from_dict(item)
                for item in task_usage_list_data
                if isinstance(item, dict)
            ],
        )


@dataclass
class TaskUsage:
    """任务计费信息"""

    consume_money: Optional[str] = None
    consume_coins: Optional[str] = None
    task_cost_time: str = ""
    third_party_consume_money: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskUsage":
        """从API响应创建"""
        return cls(
            consume_money=(
                str(data["consumeMoney"])
                if data.get("consumeMoney") is not None
                else None
            ),
            consume_coins=(
                str(data["consumeCoins"])
                if data.get("consumeCoins") is not None
                else None
            ),
            task_cost_time=str(data.get("taskCostTime", "")),
            third_party_consume_money=(
                str(data["thirdPartyConsumeMoney"])
                if data.get("thirdPartyConsumeMoney") is not None
                else None
            ),
        )


@dataclass
class TaskUsageRecord:
    """任务与子任务计费记录"""

    task_id: str
    parent_task_id: Optional[str]
    task_status: str
    usage: Optional[TaskUsage] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskUsageRecord":
        """从API响应创建"""
        usage_data = data.get("usage")
        return cls(
            task_id=data.get("taskId", ""),
            parent_task_id=data.get("parentTaskId"),
            task_status=str(data.get("taskStatus", "")),
            usage=(TaskUsage.from_dict(usage_data) if isinstance(usage_data, dict) else None),
        )


@dataclass
class ModelPricePreview:
    """模型 API 价格预估结果"""

    error_code: str
    error_message: str
    estimated_price: float
    currency: str
    price_text: str
    price_text_en: Optional[str]
    free_limit: bool
    free_limit_count: Optional[int]
    remaining_free_limit_count: Optional[int]
    is_free_this_call: bool

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelPricePreview":
        """从 API 响应创建"""
        return cls(
            error_code=data.get("errorCode", ""),
            error_message=data.get("errorMessage", ""),
            estimated_price=float(data.get("estimatedPrice", 0) or 0),
            currency=data.get("currency", ""),
            price_text=data.get("priceText", ""),
            price_text_en=data.get("priceTextEn"),
            free_limit=bool(data.get("freeLimit", False)),
            free_limit_count=(
                int(data["freeLimitCount"])
                if data.get("freeLimitCount") is not None else None
            ),
            remaining_free_limit_count=(
                int(data["remainingFreeLimitCount"])
                if data.get("remainingFreeLimitCount") is not None else None
            ),
            is_free_this_call=bool(data.get("isFreeThisCall", False)),
        )


@dataclass
class WaitForCompletionOptions:
    """等待完成选项"""
    poll_interval: float = 2.0  # 轮询间隔(秒)
    timeout: float = 600.0  # 总超时时间(秒)，默认10分钟
    on_status_change: Optional[Callable[[TaskStatus], None]] = None
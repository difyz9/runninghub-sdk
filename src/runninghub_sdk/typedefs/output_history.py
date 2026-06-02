"""Output history 相关类型定义"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class OutputHistoryV2Request:
    """输出历史查询请求

    用于调用 /api/output/v2/history 接口查询任务输出历史，
    支持按状态、任务类型、是否包含输出等条件过滤和分页。
    """

    size: int = 30
    current: int = 1
    status: Optional[List[str]] = None
    task_type: Optional[List[str]] = None
    has_output: bool = True
    fast_creation: Optional[str] = None
    from_id: str = ""
    task_name: str = ""
    reload_data: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 请求格式"""
        data: Dict[str, Any] = {
            "size": self.size,
            "current": self.current,
            "hasOutput": self.has_output,
            "reloadData": self.reload_data,
        }
        if self.status:
            data["status"] = self.status
        if self.task_type:
            data["taskType"] = self.task_type
        if self.fast_creation is not None:
            data["fastCreation"] = self.fast_creation
        if self.from_id:
            data["fromId"] = self.from_id
        if self.task_name:
            data["taskName"] = self.task_name
        return data


@dataclass
class OutputHistoryV2Response:
    """输出历史查询响应（分页）"""

    records: List[Dict[str, Any]]
    size: int
    current: int
    total: int = 0
    pages: int = 0
    has_next: bool = False
    has_previous: bool = False

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "OutputHistoryV2Response":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            records=data.get("records", []),
            size=int(data.get("size", 0) or 0),
            current=int(data.get("current", 0) or 0),
            total=int(data.get("total", 0) or 0),
            pages=int(data.get("pages", 0) or 0),
            has_next=bool(data.get("hasNext", False)),
            has_previous=bool(data.get("hasPrevious", False)),
        )

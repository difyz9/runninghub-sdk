"""工作流相关类型定义"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowCopyResponse:
    """工作流复制/获取详情响应

    调用 /api/workflow/copy 接口后返回的数据结构。
    workflowContent 为 JSON 字符串，可通过 get_workflow_content_parsed() 解析为字典。
    """

    id: str
    name: str
    workflowContent: str  # JSON 字符串
    desc: Optional[str] = None
    systemWorkflow: Optional[bool] = None
    publishTime: Optional[str] = None
    timestamp: Optional[str] = None
    md5: Optional[str] = None
    imageSize: Optional[str] = None
    preview: Optional[str] = None
    owner: Optional[Any] = None
    nodeCount: Optional[int] = None
    statisticsInfo: Optional[Any] = None
    labels: Optional[Any] = None
    tags: Optional[Any] = None
    covers: Optional[Any] = None
    chineseCovers: Optional[Any] = None
    englishCovers: Optional[Any] = None
    primitiveNodes: Optional[Any] = None
    customNodes: Optional[Any] = None
    usedModels: Optional[Any] = None
    liked: Optional[bool] = None
    likeCount: Optional[int] = None
    collect: Optional[bool] = None
    collectCount: Optional[int] = None
    webappId: Optional[str] = None
    status: Optional[int] = None
    workflowState: Optional[int] = None
    webappState: Optional[int] = None
    publishAccess: Optional[Any] = None
    canModifyPublishType: Optional[bool] = None
    canModifyPublishScope: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowCopyResponse":
        """从字典创建"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            workflowContent=data.get("workflowContent", ""),
            desc=data.get("desc"),
            systemWorkflow=data.get("systemWorkflow"),
            publishTime=data.get("publishTime"),
            timestamp=data.get("timestamp"),
            md5=data.get("md5"),
            imageSize=data.get("imageSize"),
            preview=data.get("preview"),
            owner=data.get("owner"),
            nodeCount=data.get("nodeCount"),
            statisticsInfo=data.get("statisticsInfo"),
            labels=data.get("labels"),
            tags=data.get("tags"),
            covers=data.get("covers"),
            chineseCovers=data.get("chineseCovers"),
            englishCovers=data.get("englishCovers"),
            primitiveNodes=data.get("primitiveNodes"),
            customNodes=data.get("customNodes"),
            usedModels=data.get("usedModels"),
            liked=data.get("liked"),
            likeCount=data.get("likeCount"),
            collect=data.get("collect"),
            collectCount=data.get("collectCount"),
            webappId=data.get("webappId"),
            status=data.get("status"),
            workflowState=data.get("workflowState"),
            webappState=data.get("webappState"),
            publishAccess=data.get("publishAccess"),
            canModifyPublishType=data.get("canModifyPublishType"),
            canModifyPublishScope=data.get("canModifyPublishScope"),
        )

    def get_workflow_content_parsed(self) -> Dict[str, Any]:
        """将 workflowContent JSON 字符串解析为字典"""
        if self.workflowContent:
            return json.loads(self.workflowContent)
        return {}

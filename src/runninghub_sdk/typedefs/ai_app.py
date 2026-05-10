"""AI App 相关类型定义"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from .task import CreateTaskResponse, NodeInput


@dataclass
class AiAppRunRequest:
    """发起 AI App 任务请求参数"""

    webapp_id: Union[int, str]
    node_info_list: Optional[List[NodeInput]] = None
    webhook_url: Optional[str] = None
    instance_type: Optional[str] = None
    access_password: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 请求格式"""
        data: Dict[str, Any] = {
            "webappId": self.webapp_id,
        }
        if self.node_info_list:
            data["nodeInfoList"] = [n.to_dict() for n in self.node_info_list]
        if self.webhook_url:
            data["webhookUrl"] = self.webhook_url
        if self.instance_type:
            data["instanceType"] = self.instance_type
        if self.access_password:
            data["accessPassword"] = self.access_password
        return data


@dataclass
class AiAppNodeInfo:
    """AI App 可调用节点信息"""

    node_id: str
    node_name: str = ""
    field_name: str = ""
    field_value: str = ""
    field_data: str = ""
    field_type: str = ""
    description: str = ""
    description_en: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AiAppNodeInfo":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            node_id=str(data.get("nodeId", "")),
            node_name=data.get("nodeName", ""),
            field_name=data.get("fieldName", ""),
            field_value=str(data.get("fieldValue", "")),
            field_data=str(data.get("fieldData", "")),
            field_type=data.get("fieldType", ""),
            description=data.get("description", ""),
            description_en=data.get("descriptionEn", ""),
        )


@dataclass
class AiAppCover:
    """AI App 封面信息"""

    id: str
    obj_name: str = ""
    url: str = ""
    thumbnail_uri: str = ""
    image_width: str = ""
    image_height: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AiAppCover":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            obj_name=data.get("objName", ""),
            url=data.get("url", ""),
            thumbnail_uri=data.get("thumbnailUri", ""),
            image_width=str(data.get("imageWidth", "")),
            image_height=str(data.get("imageHeight", "")),
        )


@dataclass
class AiAppTag:
    """AI App 标签"""

    id: str
    name: str = ""
    name_en: str = ""
    labels: Optional[Any] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AiAppTag":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            name_en=data.get("nameEn", ""),
            labels=data.get("labels"),
        )


@dataclass
class AiAppStatisticsInfo:
    """AI App 统计信息"""

    like_count: str = "0"
    download_count: str = "0"
    use_count: str = "0"
    pv: str = "0"
    collect_count: str = "0"

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AiAppStatisticsInfo":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            like_count=str(data.get("likeCount", "0")),
            download_count=str(data.get("downloadCount", "0")),
            use_count=str(data.get("useCount", "0")),
            pv=str(data.get("pv", "0")),
            collect_count=str(data.get("collectCount", "0")),
        )


@dataclass
class AiAppApiCallDemo:
    """AI App API 调用示例信息"""

    curl: str
    access_encrypted: bool
    webapp_name: str
    statistics_info: AiAppStatisticsInfo
    node_info_list: List[AiAppNodeInfo]
    covers: List[AiAppCover]
    tags: List[AiAppTag]

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AiAppApiCallDemo":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            curl=data.get("curl", ""),
            access_encrypted=bool(data.get("accessEncrypted", False)),
            webapp_name=data.get("webappName", ""),
            statistics_info=AiAppStatisticsInfo.from_dict(data.get("statisticsInfo")),
            node_info_list=[
                AiAppNodeInfo.from_dict(item)
                for item in data.get("nodeInfoList", [])
            ],
            covers=[AiAppCover.from_dict(item) for item in data.get("covers", [])],
            tags=[AiAppTag.from_dict(item) for item in data.get("tags", [])],
        )


AiAppRunResponse = CreateTaskResponse


@dataclass
class PublicModelListRequest:
    """公共模型列表查询参数"""

    resource_type: str = "UNET"
    resource_name: str = ""
    base_models: Optional[List[str]] = None
    tags: Optional[List[int]] = None
    current: int = 1
    size: int = 10

    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 请求格式"""
        data: Dict[str, Any] = {
            "resourceType": self.resource_type,
            "current": self.current,
            "size": self.size,
        }
        if self.resource_name:
            data["resourceName"] = self.resource_name
        if self.base_models:
            data["baseModels"] = self.base_models
        if self.tags:
            data["tags"] = self.tags
        return data


@dataclass
class PublicModelOwner:
    """公共模型作者信息"""

    name: str = ""
    avatar: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PublicModelOwner":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            name=data.get("name", ""),
            avatar=data.get("avatar", ""),
        )


@dataclass
class PublicModelTag:
    """公共模型标签"""

    id: int = 0
    name: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PublicModelTag":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            id=int(data.get("id", 0) or 0),
            name=data.get("name", ""),
        )


@dataclass
class PublicModelPosterInfo:
    """公共模型版本预览图信息"""

    poster_url: str = ""
    thumbnail_url: str = ""
    image_width: int = 0
    image_height: int = 0

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PublicModelPosterInfo":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            poster_url=data.get("posterUrl", ""),
            thumbnail_url=data.get("thumbnailUrl", ""),
            image_width=int(data.get("imageWidth", 0) or 0),
            image_height=int(data.get("imageHeight", 0) or 0),
        )


@dataclass
class PublicModelVersion:
    """公共模型版本信息"""

    id: str = ""
    version: str = ""
    version_resource_name: str = ""
    base_model: str = ""
    base_model_subtype: str = ""
    trigger_words: str = ""
    desc: str = ""
    poster_infos: Optional[List[PublicModelPosterInfo]] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PublicModelVersion":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            version=data.get("version", ""),
            version_resource_name=data.get("versionResourceName", ""),
            base_model=data.get("baseModel", ""),
            base_model_subtype=data.get("baseModelSubtype", ""),
            trigger_words=data.get("triggerWords", ""),
            desc=data.get("desc", ""),
            poster_infos=[
                PublicModelPosterInfo.from_dict(item)
                for item in data.get("posterInfos", [])
            ],
        )


@dataclass
class PublicModelRecord:
    """公共模型记录"""

    id: str = ""
    resource_name: str = ""
    resource_type: str = ""
    create_time: str = ""
    desc: str = ""
    node_model_name: str = ""
    poster_url: str = ""
    thumbnail_url: str = ""
    owner: Optional[PublicModelOwner] = None
    tags: Optional[List[PublicModelTag]] = None
    versions: Optional[List[PublicModelVersion]] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PublicModelRecord":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            resource_name=data.get("resourceName", ""),
            resource_type=data.get("resourceType", ""),
            create_time=data.get("createTime", ""),
            desc=data.get("desc", ""),
            node_model_name=data.get("nodeModelName", ""),
            poster_url=data.get("posterUrl", ""),
            thumbnail_url=data.get("thumbnailUrl", ""),
            owner=PublicModelOwner.from_dict(data.get("owner")),
            tags=[PublicModelTag.from_dict(item) for item in data.get("tags", [])],
            versions=[
                PublicModelVersion.from_dict(item)
                for item in data.get("versions", [])
            ],
        )


@dataclass
class PublicModelListResponse:
    """公共模型列表响应"""

    records: List[PublicModelRecord]
    size: int
    current: int
    total: int
    pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PublicModelListResponse":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            records=[PublicModelRecord.from_dict(item) for item in data.get("records", [])],
            size=int(data.get("size", 0) or 0),
            current=int(data.get("current", 0) or 0),
            total=int(data.get("total", 0) or 0),
            pages=int(data.get("pages", 0) or 0),
            has_next=bool(data.get("hasNext", False)),
            has_previous=bool(data.get("hasPrevious", False)),
        )
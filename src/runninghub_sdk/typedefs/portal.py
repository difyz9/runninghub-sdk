"""Portal/Webapp 相关类型定义"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AccessAuthResponse:
    """access/auth 接口响应

    获取用户 access token，用于访问需要用户级别认证的接口。
    """

    access_key: str
    expire_in: str

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "AccessAuthResponse":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            access_key=data.get("accessKey", ""),
            expire_in=str(data.get("expire_in", "0")),
        )


@dataclass
class PortalTemplateListRequest:
    """门户模板列表查询参数"""

    size: int = 30
    current: int = 1
    tags: Optional[List[str]] = None
    search: str = ""
    sort: str = "RECOMMEND"

    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 请求格式"""
        data: Dict[str, Any] = {
            "size": self.size,
            "current": self.current,
            "sort": self.sort,
        }
        if self.tags:
            data["tags"] = self.tags
        if self.search:
            data["search"] = self.search
        return data


@dataclass
class WebappListRequest:
    """Webapp 列表查询参数"""

    size: int = 30
    current: int = 1
    tags: Optional[List[str]] = None
    search: str = ""
    sort: str = "RECOMMEND"

    def to_dict(self) -> Dict[str, Any]:
        """转换为 API 请求格式"""
        data: Dict[str, Any] = {
            "size": self.size,
            "current": self.current,
            "sort": self.sort,
        }
        if self.tags:
            data["tags"] = self.tags
        if self.search:
            data["search"] = self.search
        return data


@dataclass
class PortalTemplateOwner:
    """模板所属者信息"""

    id: str = ""
    avatar: str = ""
    name: str = ""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PortalTemplateOwner":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            avatar=data.get("avatar", ""),
            name=data.get("name", ""),
        )


@dataclass
class PortalTemplateCover:
    """模板封面信息"""

    id: str = ""
    obj_name: str = ""
    url: str = ""
    thumbnail_uri: str = ""
    image_width: Optional[str] = None
    image_height: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PortalTemplateCover":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            obj_name=data.get("objName", ""),
            url=data.get("url", ""),
            thumbnail_uri=data.get("thumbnailUri", ""),
            image_width=str(data.get("imageWidth")) if data.get("imageWidth") is not None else None,
            image_height=str(data.get("imageHeight")) if data.get("imageHeight") is not None else None,
        )


@dataclass
class PortalTemplateTag:
    """模板标签"""

    id: str = ""
    name: str = ""
    name_en: str = ""
    labels: Optional[Any] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PortalTemplateTag":
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
class PortalTemplateStatisticsInfo:
    """模板统计信息"""

    like_count: str = "0"
    download_count: str = "0"
    use_count: str = "0"
    pv: str = "0"
    collect_count: str = "0"

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PortalTemplateStatisticsInfo":
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
class PortalTemplateRecord:
    """单条模板记录"""

    id: str = ""
    name: str = ""
    desc: str = ""
    system_workflow: bool = False
    publish_time: str = ""
    timestamp: str = ""
    preview: Optional[str] = None
    owner: Optional[PortalTemplateOwner] = None
    statistics_info: Optional[PortalTemplateStatisticsInfo] = None
    node_count: Optional[Any] = None
    liked: int = 0
    covers: Optional[List[PortalTemplateCover]] = None
    tags: Optional[List[PortalTemplateTag]] = None
    labels: str = ""
    seq: str = ""
    home_show: Optional[Any] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PortalTemplateRecord":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            desc=data.get("desc", ""),
            system_workflow=bool(data.get("systemWorkflow", False)),
            publish_time=data.get("publishTime", ""),
            timestamp=data.get("timestamp", ""),
            preview=data.get("preview"),
            owner=PortalTemplateOwner.from_dict(data.get("owner")),
            statistics_info=PortalTemplateStatisticsInfo.from_dict(data.get("statisticsInfo")),
            node_count=data.get("nodeCount"),
            liked=int(data.get("liked", 0) or 0),
            covers=[PortalTemplateCover.from_dict(item) for item in data.get("covers", [])],
            tags=[PortalTemplateTag.from_dict(item) for item in data.get("tags", [])],
            labels=data.get("labels", ""),
            seq=data.get("seq", ""),
            home_show=data.get("homeShow"),
        )


@dataclass
class PortalTemplateListResponse:
    """门户模板列表响应（分页）"""

    records: List[PortalTemplateRecord]
    size: int
    current: int
    total: int
    pages: int
    has_next: bool
    has_previous: bool
    next_cursor: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PortalTemplateListResponse":
        """从 API 响应创建"""
        if data is None:
            data = {}
        return cls(
            records=[PortalTemplateRecord.from_dict(item) for item in data.get("records", [])],
            size=int(data.get("size", 0) or 0),
            current=int(data.get("current", 0) or 0),
            total=int(data.get("total", 0) or 0),
            pages=int(data.get("pages", 0) or 0),
            has_next=bool(data.get("hasNext", False)),
            has_previous=bool(data.get("hasPrevious", False)),
            next_cursor=data.get("nextCursor"),
        )


@dataclass
class WebappListResponse:
    """Webapp 列表响应（通用分页结构）"""

    records: List[Dict[str, Any]]
    size: int
    current: int
    total: int = 0
    pages: int = 0
    has_next: bool = False
    has_previous: bool = False

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "WebappListResponse":
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

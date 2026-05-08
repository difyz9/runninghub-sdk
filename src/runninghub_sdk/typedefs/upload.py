"""上传相关类型定义"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class UploadResponseData:
    """文件上传响应数据"""
    type: str
    download_url: str
    file_name: str
    size: str

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "UploadResponseData":
        """从API响应创建"""
        if data is None:
            data = {}
        return cls(
            type=data.get("type", ""),
            download_url=data.get("download_url", ""),
            file_name=data.get("fileName", ""),
            size=str(data.get("size", "0")),
        )


@dataclass
class LoraUploadResponse:
    """LoRA上传响应"""
    file_name: str
    url: str

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "LoraUploadResponse":
        """从API响应创建"""
        if data is None:
            data = {}
        return cls(
            file_name=data.get("fileName", ""),
            url=data.get("url", ""),
        )

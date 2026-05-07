"""节点修改器 - 支持链式调用构建nodeInfoList"""

from typing import List, Union, Optional
from ..typedefs import NodeInput


class NodeModifier:
    """
    节点修改器 - 支持链式调用构建nodeInfoList

    示例:
        modifier = (
            NodeModifier()
            .text("6", "a beautiful sunset")
            .seed("3", 98765)
            .steps("3", 25)
        )
        node_list = modifier.to_list()
    """

    def __init__(self):
        self._modifications: List[NodeInput] = []

    def set(
        self,
        node_id: str,
        field_name: str,
        field_value: Union[str, int, bool, float]
    ) -> "NodeModifier":
        """
        修改指定节点的字段

        Args:
            node_id: 节点ID
            field_name: 字段名
            field_value: 字段值

        Returns:
            self，支持链式调用
        """
        self._modifications.append(
            NodeInput(
                node_id=node_id,
                field_name=field_name,
                field_value=field_value
            )
        )
        return self

    def text(self, node_id: str, text: str) -> "NodeModifier":
        """
        修改文本内容（如提示词）

        Args:
            node_id: 节点ID（通常是CLIPTextEncode节点）
            text: 文本内容

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "text", text)

    def negative_text(self, node_id: str, text: str) -> "NodeModifier":
        """
        修改负面提示词

        Args:
            node_id: 节点ID
            text: 负面提示词内容

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "text", text)

    def seed(self, node_id: str, seed: int) -> "NodeModifier":
        """
        修改种子值

        Args:
            node_id: 节点ID（通常是KSampler节点）
            seed: 种子值

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "seed", seed)

    def steps(self, node_id: str, steps: int) -> "NodeModifier":
        """
        修改采样步数

        Args:
            node_id: 节点ID（通常是KSampler节点）
            steps: 步数

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "steps", steps)

    def cfg(self, node_id: str, cfg: float) -> "NodeModifier":
        """
        修改CFG值

        Args:
            node_id: 节点ID（通常是KSampler节点）
            cfg: CFG值

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "cfg", cfg)

    def size(
        self,
        node_id: str,
        width: int,
        height: int,
        batch_size: Optional[int] = None
    ) -> "NodeModifier":
        """
        修改图片尺寸

        Args:
            node_id: 节点ID（通常是EmptyLatentImage节点）
            width: 宽度
            height: 高度
            batch_size: 批次大小（可选）

        Returns:
            self，支持链式调用
        """
        self.set(node_id, "width", width)
        self.set(node_id, "height", height)
        if batch_size is not None:
            self.set(node_id, "batch_size", batch_size)
        return self

    def sampler(self, node_id: str, sampler_name: str) -> "NodeModifier":
        """
        修改采样器

        Args:
            node_id: 节点ID（通常是KSampler节点）
            sampler_name: 采样器名称，如 "dpmpp_2m", "euler", "euler_ancestral"

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "sampler_name", sampler_name)

    def scheduler(self, node_id: str, scheduler: str) -> "NodeModifier":
        """
        修改调度器

        Args:
            node_id: 节点ID（通常是KSampler节点）
            scheduler: 调度器名称，如 "karras", "normal", "simple"

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "scheduler", scheduler)

    def denoise(self, node_id: str, denoise: float) -> "NodeModifier":
        """
        修改去噪强度

        Args:
            node_id: 节点ID（通常是KSampler节点）
            denoise: 去噪强度 (0.0-1.0)

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "denoise", denoise)

    def image(self, node_id: str, file_name: str) -> "NodeModifier":
        """
        修改图片（用于LoadImage节点）

        Args:
            node_id: 节点ID（通常是LoadImage节点）
            file_name: 上传后的文件名

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "image", file_name)

    def video(self, node_id: str, file_name: str) -> "NodeModifier":
        """
        修改视频（用于LoadVideo节点）

        Args:
            node_id: 节点ID
            file_name: 上传后的文件名

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "video", file_name)

    def audio(self, node_id: str, file_name: str) -> "NodeModifier":
        """
        修改音频（用于LoadAudio节点）

        Args:
            node_id: 节点ID
            file_name: 上传后的文件名

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "audio", file_name)

    def lora(self, node_id: str, lora_file_name: str) -> "NodeModifier":
        """
        修改LoRA文件（用于RHLoraLoader节点）

        Args:
            node_id: 节点ID
            lora_file_name: 上传后的LoRA文件名

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "lora_name", lora_file_name)

    def lora_strength(self, node_id: str, strength: float) -> "NodeModifier":
        """
        修改LoRA强度

        Args:
            node_id: 节点ID
            strength: 强度值

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "strength_model", strength)

    def checkpoint(self, node_id: str, ckpt_name: str) -> "NodeModifier":
        """
        修改模型检查点

        Args:
            node_id: 节点ID（通常是CheckpointLoaderSimple节点）
            ckpt_name: 模型名称

        Returns:
            self，支持链式调用
        """
        return self.set(node_id, "ckpt_name", ckpt_name)

    def add_many(self, modifications: List[NodeInput]) -> "NodeModifier":
        """
        批量添加修改

        Args:
            modifications: NodeInput列表

        Returns:
            self，支持链式调用
        """
        self._modifications.extend(modifications)
        return self

    def clear(self) -> "NodeModifier":
        """
        清空所有修改

        Returns:
            self，支持链式调用
        """
        self._modifications.clear()
        return self

    def to_list(self) -> List[NodeInput]:
        """
        获取修改列表

        Returns:
            NodeInput列表
        """
        return list(self._modifications)

    def to_dict_list(self) -> List[dict]:
        """
        获取修改列表（字典格式）

        Returns:
            字典列表，可直接用于API请求
        """
        return [m.to_dict() for m in self._modifications]

    def __len__(self) -> int:
        """返回修改数量"""
        return len(self._modifications)

    def __repr__(self) -> str:
        return f"NodeModifier(modifications={len(self)})"


def modify_nodes() -> NodeModifier:
    """
    创建节点修改器的快捷函数

    Returns:
        NodeModifier实例

    示例:
        modifier = modify_nodes().text("6", "hello").seed("3", 123)
    """
    return NodeModifier()
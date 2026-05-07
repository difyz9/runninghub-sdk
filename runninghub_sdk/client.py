"""RunningHub ComfyUI SDK 主客户端类"""

import asyncio
import json
from typing import Optional, List, Dict, Any, Union, Callable, BinaryIO

import httpx

from .typedefs import (
    TaskStatus,
    NodeInput,
    CreateTaskRequest,
    CreateTaskResponse,
    TaskOutput,
    V2QueryResult,
    TaskFailedReason,
    WaitForCompletionOptions,
    UploadResponseData,
    LoraUploadResponse,
)
from .models import NodeModifier, modify_nodes
from .utils import calculate_md5, async_sleep, sleep
from .exceptions import (
    RunningHubError,
    TaskError,
    UploadError,
    TimeoutError,
    NetworkError,
    ValidationError,
    ErrorCode,
)


class RunningHubClient:
    """
    RunningHub ComfyUI SDK 客户端

    支持同步和异步两种模式，使用httpx实现。

    示例:
        # 同步使用
        client = RunningHubClient(api_key="your-api-key")
        task = client.run("workflow-id")
        outputs = client.wait_for_completion(task.task_id)

        # 异步使用
        async with RunningHubClient(api_key="your-api-key") as client:
            task = await client.async_run("workflow-id")
            outputs = await client.async_wait_for_completion(task.task_id)
    """

    BASE_URL = "https://www.runninghub.cn"
    DEFAULT_TIMEOUT = 60.0
    DEFAULT_POLL_INTERVAL = 2.0
    DEFAULT_WAIT_TIMEOUT = 600.0

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        初始化客户端

        Args:
            api_key: API密钥
            base_url: API基础URL（可选）
            timeout: 请求超时时间（秒）
        """
        if not api_key:
            raise ValidationError("API Key不能为空", field="api_key")

        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout

        # httpx客户端（延迟初始化）
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

    # ==================== 客户端管理 ====================

    @property
    def sync_client(self) -> httpx.Client:
        """获取同步HTTP客户端"""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._get_headers(),
            )
        return self._sync_client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """获取异步HTTP客户端"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=self._get_headers(),
            )
        return self._async_client

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Host": "www.runninghub.cn",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def close(self) -> None:
        """关闭同步客户端"""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    async def aclose(self) -> None:
        """关闭异步客户端"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def __enter__(self) -> "RunningHubClient":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    async def __aenter__(self) -> "RunningHubClient":
        return self

    async def __aexit__(self, *args) -> None:
        await self.aclose()

    # ==================== 同步API方法 ====================

    def run(
        self,
        workflow_id: str,
        node_info_list: Optional[List[Union[NodeInput, Dict[str, Any]]]] = None,
        **options
    ) -> CreateTaskResponse:
        """
        发起ComfyUI任务

        Args:
            workflow_id: 工作流ID
            node_info_list: 节点参数修改列表
            **options: 其他选项
                - add_metadata: 是否写入元信息
                - webhook_url: 回调URL
                - instance_type: 实例类型
                - use_personal_queue: 是否使用个人队列

        Returns:
            CreateTaskResponse
        """
        request = self._build_create_request(workflow_id, node_info_list, options)
        response = self._post("/task/openapi/create", request.to_dict())
        return CreateTaskResponse.from_dict(response)

    def run_with_modifier(
        self,
        workflow_id: str,
        modifier: NodeModifier,
        **options
    ) -> CreateTaskResponse:
        """
        使用节点修改器发起任务

        Args:
            workflow_id: 工作流ID
            modifier: 节点修改器
            **options: 其他选项

        Returns:
            CreateTaskResponse
        """
        return self.run(workflow_id, modifier.to_list(), **options)

    def get_status(self, task_id: str) -> TaskStatus:
        """
        查询任务状态

        Args:
            task_id: 任务ID

        Returns:
            TaskStatus
        """
        response = self._post("/task/openapi/status", {"taskId": task_id})
        return TaskStatus(response)

    def get_outputs(self, task_id: str) -> List[TaskOutput]:
        """
        查询任务生成结果

        Args:
            task_id: 任务ID

        Returns:
            TaskOutput列表
        """
        response = self._post("/task/openapi/outputs", {"taskId": task_id})
        if isinstance(response, list):
            return [TaskOutput.from_dict(item) for item in response]
        # 处理错误响应中的失败原因
        if isinstance(response, dict) and "failedReason" in response:
            failed_reason = TaskFailedReason.from_dict(response["failedReason"])
            raise TaskError(
                code=ErrorCode.TASK_STATUS_ERROR,
                message=failed_reason.exception_message,
                task_id=task_id,
                failed_reason=response["failedReason"],
            )
        return []

    def query_v2(self, task_id: str) -> V2QueryResult:
        """
        V2查询接口

        Args:
            task_id: 任务ID

        Returns:
            V2QueryResult
        """
        response = self._post("/openapi/v2/query", {"taskId": task_id})
        return V2QueryResult.from_dict(response)

    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_WAIT_TIMEOUT,
        on_status_change: Optional[Callable[[TaskStatus], None]] = None,
    ) -> List[TaskOutput]:
        """
        等待任务完成

        Args:
            task_id: 任务ID
            poll_interval: 轮询间隔（秒）
            timeout: 超时时间（秒）
            on_status_change: 状态变更回调

        Returns:
            TaskOutput列表

        Raises:
            TimeoutError: 超时
            TaskError: 任务失败
        """
        import time
        start_time = time.time()

        while True:
            status = self.get_status(task_id)

            if on_status_change:
                on_status_change(status)

            if status == TaskStatus.SUCCESS:
                return self.get_outputs(task_id)

            if status == TaskStatus.FAILED:
                try:
                    outputs = self.get_outputs(task_id)
                except TaskError:
                    raise
                raise TaskError(
                    code=ErrorCode.TASK_STATUS_ERROR,
                    message="任务执行失败",
                    task_id=task_id,
                )

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    message=f"等待任务完成超时（{timeout}秒）",
                    task_id=task_id,
                    timeout=timeout,
                )

            sleep(poll_interval)

    def cancel(self, task_id: str) -> None:
        """
        取消任务

        Args:
            task_id: 任务ID
        """
        self._post("/task/openapi/cancel", {"taskId": task_id})

    # ==================== 同步上传方法 ====================

    def upload_file(
        self,
        file: Union[BinaryIO, bytes, str],
        filename: Optional[str] = None
    ) -> UploadResponseData:
        """
        上传文件

        Args:
            file: 文件对象、字节数据或文件路径
            filename: 文件名（可选，用于指定上传文件名）

        Returns:
            UploadResponseData
        """
        if isinstance(file, str):
            # 文件路径
            import os
            actual_filename = filename or os.path.basename(file)
            with open(file, "rb") as f:
                file_content = f.read()
        elif isinstance(file, bytes):
            file_content = file
            actual_filename = filename or "upload.bin"
        else:
            # BinaryIO
            file_content = file.read()
            actual_filename = filename or getattr(file, 'name', 'upload.bin')

        # 使用正确的文件名格式
        files = {"file": (actual_filename, file_content)}
        response = self._upload("/openapi/v2/media/upload/binary", files)
        return UploadResponseData.from_dict(response)

    def upload_image(self, file: Union[BinaryIO, bytes, str]) -> Dict[str, str]:
        """
        上传图片（便捷方法）

        Args:
            file: 文件对象、字节数据或文件路径

        Returns:
            {"fileName": "...", "downloadUrl": "..."}
        """
        result = self.upload_file(file)
        return {
            "fileName": result.file_name,
            "downloadUrl": result.download_url,
        }

    def get_lora_upload_url(self, lora_name: str, md5_hex: str) -> LoraUploadResponse:
        """
        获取LoRA上传URL

        Args:
            lora_name: LoRA名称
            md5_hex: MD5值

        Returns:
            LoraUploadResponse
        """
        response = self._post("/api/openapi/getLoraUploadUrl", {
            "loraName": lora_name,
            "md5Hex": md5_hex,
        })
        return LoraUploadResponse.from_dict(response)

    def upload_lora(
        self,
        lora_name: str,
        file: Union[BinaryIO, bytes, str]
    ) -> str:
        """
        上传LoRA文件

        Args:
            lora_name: LoRA名称
            file: 文件对象、字节数据或文件路径

        Returns:
            fileName
        """
        # 读取文件内容
        if isinstance(file, str):
            with open(file, "rb") as f:
                file_content = f.read()
        elif isinstance(file, bytes):
            file_content = file
        else:
            file_content = file.read()

        # 计算MD5
        md5_hex = calculate_md5(file_content)

        # 获取上传URL
        lora_response = self.get_lora_upload_url(lora_name, md5_hex)

        # PUT上传
        put_response = httpx.put(
            lora_response.url,
            content=file_content,
            headers={"Content-Type": "application/octet-stream"},
            timeout=self.timeout * 3,
        )
        put_response.raise_for_status()

        return lora_response.file_name

    # ==================== 同步工作流方法 ====================

    def get_workflow_json(self, workflow_id: str) -> str:
        """
        获取工作流JSON字符串

        Args:
            workflow_id: 工作流ID

        Returns:
            JSON字符串
        """
        response = self._post("/api/openapi/getJsonApiFormat", {
            "workflowId": workflow_id,
        })
        return response.get("prompt", "")

    def get_workflow_json_parsed(self, workflow_id: str) -> Dict[str, Any]:
        """
        获取工作流JSON对象

        Args:
            workflow_id: 工作流ID

        Returns:
            解析后的字典
        """
        prompt_str = self.get_workflow_json(workflow_id)
        return json.loads(prompt_str)

    # ==================== 异步API方法 ====================

    async def async_run(
        self,
        workflow_id: str,
        node_info_list: Optional[List[Union[NodeInput, Dict[str, Any]]]] = None,
        **options
    ) -> CreateTaskResponse:
        """异步发起ComfyUI任务"""
        request = self._build_create_request(workflow_id, node_info_list, options)
        response = await self._async_post("/task/openapi/create", request.to_dict())
        return CreateTaskResponse.from_dict(response)

    async def async_run_with_modifier(
        self,
        workflow_id: str,
        modifier: NodeModifier,
        **options
    ) -> CreateTaskResponse:
        """异步使用节点修改器发起任务"""
        return await self.async_run(workflow_id, modifier.to_list(), **options)

    async def async_get_status(self, task_id: str) -> TaskStatus:
        """异步查询任务状态"""
        response = await self._async_post("/task/openapi/status", {"taskId": task_id})
        return TaskStatus(response)

    async def async_get_outputs(self, task_id: str) -> List[TaskOutput]:
        """异步查询任务结果"""
        response = await self._async_post("/task/openapi/outputs", {"taskId": task_id})
        if isinstance(response, list):
            return [TaskOutput.from_dict(item) for item in response]
        if isinstance(response, dict) and "failedReason" in response:
            failed_reason = TaskFailedReason.from_dict(response["failedReason"])
            raise TaskError(
                code=ErrorCode.TASK_STATUS_ERROR,
                message=failed_reason.exception_message,
                task_id=task_id,
                failed_reason=response["failedReason"],
            )
        return []

    async def async_wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_WAIT_TIMEOUT,
        on_status_change: Optional[Callable[[TaskStatus], None]] = None,
    ) -> List[TaskOutput]:
        """异步等待任务完成"""
        import time
        start_time = time.time()

        while True:
            status = await self.async_get_status(task_id)

            if on_status_change:
                on_status_change(status)

            if status == TaskStatus.SUCCESS:
                return await self.async_get_outputs(task_id)

            if status == TaskStatus.FAILED:
                try:
                    outputs = await self.async_get_outputs(task_id)
                except TaskError:
                    raise
                raise TaskError(
                    code=ErrorCode.TASK_STATUS_ERROR,
                    message="任务执行失败",
                    task_id=task_id,
                )

            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError(
                    message=f"等待任务完成超时（{timeout}秒）",
                    task_id=task_id,
                    timeout=timeout,
                )

            await async_sleep(poll_interval)

    async def async_cancel(self, task_id: str) -> None:
        """异步取消任务"""
        await self._async_post("/task/openapi/cancel", {"taskId": task_id})

    async def async_upload_file(
        self,
        file: Union[BinaryIO, bytes, str]
    ) -> UploadResponseData:
        """异步上传文件"""
        if isinstance(file, str):
            with open(file, "rb") as f:
                file_content = f.read()
        elif isinstance(file, bytes):
            file_content = file
        else:
            file_content = file.read()

        files = {"file": ("file", file_content)}
        response = await self._async_upload("/openapi/v2/media/upload/binary", files)
        return UploadResponseData.from_dict(response)

    async def async_upload_image(
        self,
        file: Union[BinaryIO, bytes, str]
    ) -> Dict[str, str]:
        """异步上传图片"""
        result = await self.async_upload_file(file)
        return {
            "fileName": result.file_name,
            "downloadUrl": result.download_url,
        }

    async def async_upload_lora(
        self,
        lora_name: str,
        file: Union[BinaryIO, bytes, str]
    ) -> str:
        """异步上传LoRA文件"""
        if isinstance(file, str):
            with open(file, "rb") as f:
                file_content = f.read()
        elif isinstance(file, bytes):
            file_content = file
        else:
            file_content = file.read()

        md5_hex = calculate_md5(file_content)
        response = await self._async_post("/api/openapi/getLoraUploadUrl", {
            "loraName": lora_name,
            "md5Hex": md5_hex,
        })
        lora_response = LoraUploadResponse.from_dict(response)

        async with httpx.AsyncClient() as client:
            put_response = await client.put(
                lora_response.url,
                content=file_content,
                headers={"Content-Type": "application/octet-stream"},
                timeout=self.timeout * 3,
            )
            put_response.raise_for_status()

        return lora_response.file_name

    async def async_get_workflow_json(self, workflow_id: str) -> str:
        """异步获取工作流JSON"""
        response = await self._async_post("/api/openapi/getJsonApiFormat", {
            "workflowId": workflow_id,
        })
        return response.get("prompt", "")

    async def async_get_workflow_json_parsed(
        self,
        workflow_id: str
    ) -> Dict[str, Any]:
        """异步获取工作流JSON对象"""
        prompt_str = await self.async_get_workflow_json(workflow_id)
        return json.loads(prompt_str)

    # ==================== 辅助方法 ====================

    def create_modifier(self) -> NodeModifier:
        """创建节点修改器"""
        return modify_nodes()

    def _build_create_request(
        self,
        workflow_id: str,
        node_info_list: Optional[List[Union[NodeInput, Dict[str, Any]]]],
        options: Dict[str, Any],
    ) -> CreateTaskRequest:
        """构建创建任务请求"""
        parsed_node_list = None
        if node_info_list:
            parsed_node_list = []
            for item in node_info_list:
                if isinstance(item, NodeInput):
                    parsed_node_list.append(item)
                elif isinstance(item, dict):
                    parsed_node_list.append(NodeInput.from_dict(item))

        return CreateTaskRequest(
            workflow_id=workflow_id,
            node_info_list=parsed_node_list,
            add_metadata=options.get("add_metadata", True),
            webhook_url=options.get("webhook_url"),
            instance_type=options.get("instance_type"),
            use_personal_queue=options.get("use_personal_queue", False),
        )

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """同步POST请求"""
        # 添加apiKey到请求体
        data = {**data, "apiKey": self.api_key}
        try:
            response = self.sync_client.post(endpoint, json=data)
            response.raise_for_status()
            result = response.json()
            return self._handle_response(result)
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP错误: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}", e)

    async def _async_post(self, endpoint: str, data: Dict[str, Any]) -> Any:
        """异步POST请求"""
        data = {**data, "apiKey": self.api_key}
        try:
            response = await self.async_client.post(endpoint, json=data)
            response.raise_for_status()
            result = response.json()
            return self._handle_response(result)
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP错误: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}", e)

    def _upload(self, endpoint: str, files: Dict[str, tuple]) -> Any:
        """同步上传文件"""
        try:
            # 上传使用独立的 httpx 客户端，不带默认 headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }
            # 使用独立客户端发送请求，避免默认 Content-Type
            with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                response = client.post(
                    endpoint,
                    files=files,
                    headers=headers,
                )
                response.raise_for_status()
                result = response.json()
                # 打印完整响应以便调试
                print(f"上传API原始响应: {result}")
                return self._handle_upload_response(result)
        except httpx.HTTPStatusError as e:
            raise UploadError(
                code=ErrorCode.UNKNOWN,
                message=f"上传失败: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            raise NetworkError(f"上传请求失败: {str(e)}", e)

    def _handle_upload_response(self, result: Dict[str, Any]) -> Any:
        """处理上传API响应（可能有不同的格式）"""
        # 检查是否有 code 字段
        code = result.get("code", 0)
        if code != 0:
            # 上传接口可能使用 message 或 msg
            error_msg = result.get("message") or result.get("msg") or "未知错误"
            raise RunningHubError.from_api_response(code, error_msg)
        
        # 尝试获取 data 字段
        data = result.get("data")
        if data is None:
            # 如果没有 data 字段，直接返回整个响应（排除 code、msg 和 message）
            data = {k: v for k, v in result.items() if k not in ("code", "msg", "message")}
            if not data:
                # 如果还是空，返回原始响应
                return result
        return data

    async def _async_upload(self, endpoint: str, files: Dict[str, tuple]) -> Any:
        """异步上传文件"""
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = await self.async_client.post(
                endpoint,
                files=files,
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()
            return self._handle_response(result)
        except httpx.HTTPStatusError as e:
            raise UploadError(
                code=ErrorCode.UNKNOWN,
                message=f"上传失败: {e.response.status_code}",
            )
        except httpx.RequestError as e:
            raise NetworkError(f"上传请求失败: {str(e)}", e)

    def _handle_response(self, result: Dict[str, Any]) -> Any:
        """处理API响应"""
        code = result.get("code", 0)
        if code != 0:
            raise RunningHubError.from_api_response(code, result.get("msg", "未知错误"))
        return result.get("data")


def create_client(api_key: str, **kwargs) -> RunningHubClient:
    """
    创建客户端实例的快捷函数

    Args:
        api_key: API密钥
        **kwargs: 其他参数

    Returns:
        RunningHubClient实例
    """
    return RunningHubClient(api_key=api_key, **kwargs)

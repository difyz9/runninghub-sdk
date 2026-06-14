"""RunningHub ComfyUI SDK 主客户端类"""

import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Callable, BinaryIO, Tuple
from urllib.parse import urlparse, unquote

import httpx

from .typedefs import (
    TaskStatus,
    NodeInput,
    CreateTaskRequest,
    CreateTaskResponse,
    AccountStatus,
    ApiKeyInfo,
    QueueStatus,
    WebhookDetail,
    AiAppRunRequest,
    AiAppApiCallDemo,
    PublicModelListRequest,
    PublicModelListResponse,
    TaskOutput,
    V2QueryResult,
    ModelPricePreview,
    TaskFailedReason,
    WaitForCompletionOptions,
    UploadResponseData,
    LoraUploadResponse,
    AccessAuthResponse,
    PortalTemplateListRequest,
    PortalTemplateListResponse,
    WebappListRequest,
    WebappListResponse,
    OutputHistoryV2Request,
    OutputHistoryV2Response,
    WorkflowCopyResponse,
    RunningHubToken,
    UserInfoRequest,
    UserInfoResponse,
    UserApiKeyRequest,
    UserApiKeyResponse,
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

    @classmethod
    def login(
        cls,
        username: str,
        password: str,
        *,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: Optional[str] = None,
    ) -> "RunningHubToken":
        """
        使用手机号和密码登录 RunningHub，获取 access token

        登录成功后返回的 access_token 可用作 api_key 初始化客户端。

        Args:
            username: 手机号
            password: 明文密码（SDK 会自动进行 MD5 加密）
            base_url: API 基础 URL（可选）
            timeout: 请求超时时间（秒）
            user_agent: 自定义 User-Agent（可选）

        Returns:
            RunningHubToken: 包含 access_token、refresh_token 等

        示例:
            token = RunningHubClient.login("138xxxxxxxx", "your_password")
            client = RunningHubClient(api_key=token.access_token)
        """
        import hashlib

        payload = {
            "mobile": username,
            "password": hashlib.md5(password.encode("utf-8")).hexdigest(),
            "channel": None,
            "inviteCode": None,
            "serviceAgreement": True,
        }
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": base_url,
            "Referer": f"{base_url}/",
            "User-Language": "zh_CN",
            "User-Agent": (
                user_agent
                or (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
                )
            ),
        }

        try:
            with httpx.Client(base_url=base_url, timeout=timeout) as client:
                response = client.post("/uc/pwdLogin", json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"登录请求失败: HTTP {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"登录网络错误: {str(e)}", e)

        code = result.get("code", 0)
        if code != 0:
            raise RunningHubError(
                code=code,
                message=result.get("msg") or result.get("message") or "登录失败",
            )

        data = result.get("data") or {}
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")
        if not access_token or not refresh_token:
            raise RunningHubError(
                code=code,
                message="登录成功但缺少 token 字段",
            )

        return RunningHubToken(
            access_token=access_token,
            refresh_token=refresh_token,
            expire_in=int(data.get("expire_in", 0) or 0),
            identify=data.get("identify"),
            first_login=data.get("firstLogin"),
        )

    @classmethod
    def from_login(
        cls,
        username: str,
        password: str,
        *,
        token_cache: Optional[Union[str, Path]] = None,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        user_agent: Optional[str] = None,
    ) -> "RunningHubClient":
        """
        使用手机号和密码一键登录，直接返回可用的客户端实例

        流程：登录 → 获取 token →（可选缓存到本地）→ 创建客户端

        Args:
            username: 手机号
            password: 明文密码
            token_cache: 可选，token 缓存文件路径。
                        指定后登录成功会自动将 token 保存到本地 JSON 文件，
                        后续可通过 from_token_cache() 快速恢复。
            base_url: API 基础 URL（可选）
            timeout: 请求超时时间（秒）
            user_agent: 自定义 User-Agent（可选）

        Returns:
            RunningHubClient 实例（已配置好 api_key）

        示例:
            # 首次使用
            client = RunningHubClient.from_login(
                "138xxxxxxxx", "your_password",
                token_cache="token.json",
            )

            # 后续使用（直接从缓存恢复）
            client = RunningHubClient.from_token_cache("token.json")
        """
        token = cls.login(
            username=username,
            password=password,
            base_url=base_url,
            timeout=timeout,
            user_agent=user_agent,
        )
        if token_cache:
            token.save(token_cache, username=username)

        return cls(api_key=token.access_token, base_url=base_url, timeout=timeout)

    @classmethod
    def from_token_cache(
        cls,
        cache_path: Union[str, Path],
        *,
        password: Optional[str] = None,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> "RunningHubClient":
        """
        从本地缓存恢复客户端

        如果 token 未过期，直接使用缓存的 token；
        如果已过期且提供了密码，自动重新登录并更新缓存；
        如果已过期且没有密码，抛出 RunningHubError。

        Args:
            cache_path: 缓存文件路径（由 from_login 的 token_cache 参数生成）
            password: 密码（可选，token 过期时用于自动重新登录）
            base_url: API 基础 URL（可选）
            timeout: 请求超时时间（秒）

        Returns:
            RunningHubClient 实例

        Raises:
            FileNotFoundError: 缓存文件不存在
            RunningHubError: token 过期且未提供密码
        """
        from .typedefs import RunningHubToken as Token

        load_path = Path(cache_path)
        if not load_path.exists():
            raise FileNotFoundError(f"Token 缓存文件不存在: {load_path}")

        try:
            token, cached_username = Token.load_with_username(load_path)
        except Exception as exc:
            raise ValueError(f"缓存文件格式无效: {exc}") from exc

        if token.is_expired:
            if not password or not cached_username:
                raise RunningHubError(
                    code=ErrorCode.API_KEY_INVALID,
                    message=(
                        f"Token 已过期（{load_path}）。"
                        f"请提供 password 参数自动重新登录，"
                        f"或重新调用 from_login()。"
                    ),
                )
            # 自动重新登录并更新缓存
            new_token = cls.login(
                username=cached_username,
                password=password,
                base_url=base_url,
                timeout=timeout,
            )
            new_token.save(load_path, username=cached_username)
            return cls(api_key=new_token.access_token, base_url=base_url, timeout=timeout)

        return cls(api_key=token.access_token, base_url=base_url, timeout=timeout)

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

    def run_ai_app(
        self,
        webapp_id: Union[int, str],
        node_info_list: Optional[List[Union[NodeInput, Dict[str, Any]]]] = None,
        **options
    ) -> CreateTaskResponse:
        """
        发起 AI App 任务

        Args:
            webapp_id: AI App ID
            node_info_list: 节点参数修改列表
            **options: 其他选项
                - webhook_url: 回调 URL
                - instance_type: 实例类型
                - access_password: 访问密码

        Returns:
            CreateTaskResponse
        """
        request = self._build_ai_app_run_request(webapp_id, node_info_list, options)
        response = self._post("/task/openapi/ai-app/run", request.to_dict())
        return CreateTaskResponse.from_dict(response)

    def run_ai_app_with_modifier(
        self,
        webapp_id: Union[int, str],
        modifier: NodeModifier,
        **options
    ) -> CreateTaskResponse:
        """
        使用节点修改器发起 AI App 任务

        Args:
            webapp_id: AI App ID
            modifier: 节点修改器
            **options: 其他选项

        Returns:
            CreateTaskResponse
        """
        return self.run_ai_app(webapp_id, modifier.to_list(), **options)

    def get_ai_app_api_demo(self, webapp_id: Union[int, str]) -> AiAppApiCallDemo:
        """
        获取 AI App API 调用示例和可修改节点信息

        Args:
            webapp_id: AI App ID

        Returns:
            AiAppApiCallDemo
        """
        response = self._get(
            "/api/webapp/apiCallDemo",
            {"webappId": str(webapp_id), "apiKey": self.api_key},
        )
        return AiAppApiCallDemo.from_dict(response)

    def list_public_models(
        self,
        resource_type: str = "UNET",
        resource_name: str = "",
        base_models: Optional[List[str]] = None,
        tags: Optional[List[int]] = None,
        current: int = 1,
        size: int = 10,
    ) -> PublicModelListResponse:
        """
        获取公共模型列表

        Args:
            resource_type: 模型类型，如 UNET、CHECKPOINT、LORA、GGUF
            resource_name: 模型名称关键词搜索
            base_models: 基础模型过滤列表
            tags: 标签 ID 列表过滤
            current: 当前页码，从 1 开始
            size: 每页条数，最大 50

        Returns:
            PublicModelListResponse
        """
        request = PublicModelListRequest(
            resource_type=resource_type,
            resource_name=resource_name,
            base_models=base_models,
            tags=tags,
            current=current,
            size=size,
        )
        response = self._post(
            "/openapi/v2/resource/list",
            request.to_dict(),
            include_api_key=False,
        )
        return PublicModelListResponse.from_dict(response)

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

    def get_account_status(self) -> AccountStatus:
        """获取账户信息"""
        response = self._post("/uc/openapi/accountStatus", {})
        return AccountStatus.from_dict(response)

    def list_api_keys(self) -> List[ApiKeyInfo]:
        """查询 API Key 列表"""
        response = self._get("/openapi/v2/api-key/list", {})
        if isinstance(response, list):
            return [ApiKeyInfo.from_dict(item) for item in response]
        return []

    def get_queue_status(self) -> QueueStatus:
        """查询当前 API Key 的队列状态"""
        response = self._get("/openapi/v2/queue/status", {})
        return QueueStatus.from_dict(response)

    def validate_api_key(self) -> bool:
        """通过 `/openapi/v2/queue/status` 验证当前 API Key 是否有效。"""
        try:
            self.get_queue_status()
            return True
        except RunningHubError as exc:
            if exc.code in (
                ErrorCode.API_KEY_INVALID,
                ErrorCode.API_KEY_USER_NOT_FOUND,
            ):
                return False
            raise

    def get_webhook_detail(self, task_id: str) -> WebhookDetail:
        """根据 task_id 获取 webhook 事件详情"""
        response = self._post("/task/openapi/getWebhookDetail", {"taskId": task_id})
        return WebhookDetail.from_dict(response)

    def retry_webhook(self, webhook_id: str, webhook_url: str) -> None:
        """重新发送指定 webhook 事件"""
        self._post(
            "/task/openapi/retryWebhook",
            {"webhookId": webhook_id, "webhookUrl": webhook_url},
        )

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

    def download_file(
        self,
        url: str,
        output_path: Union[str, Path],
        overwrite: bool = True,
    ) -> Path:
        """下载任意 URL 到本地文件。"""
        path = Path(output_path)
        if path.exists() and not overwrite:
            raise ValidationError("目标文件已存在", field="output_path")

        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with httpx.stream("GET", url, timeout=self.timeout * 3) as response:
                response.raise_for_status()
                with open(path, "wb") as file_obj:
                    for chunk in response.iter_bytes():
                        file_obj.write(chunk)
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"下载失败: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"下载请求失败: {str(e)}", e)

        return path

    def download_outputs(
        self,
        outputs: List[TaskOutput],
        output_dir: Union[str, Path],
        overwrite: bool = True,
    ) -> List[Path]:
        """下载任务输出列表到本地目录。"""
        base_dir = Path(output_dir)
        downloaded_paths: List[Path] = []

        for index, output in enumerate(outputs, start=1):
            filename = self._build_output_filename(output, index)
            file_path = base_dir / filename
            downloaded_paths.append(
                self.download_file(output.file_url, file_path, overwrite=overwrite)
            )

        return downloaded_paths

    def download_task_outputs(
        self,
        task_id: str,
        output_dir: Union[str, Path],
        overwrite: bool = True,
    ) -> List[Path]:
        """根据 task_id 查询并下载全部输出到本地目录。"""
        outputs = self.get_outputs(task_id)
        return self.download_outputs(outputs, output_dir, overwrite=overwrite)

    def download_history_outputs(
        self,
        records: List[Dict[str, Any]],
        output_dir: Union[str, Path],
        *,
        concurrency: int = 5,
        overwrite: bool = False,
        retries: int = 1,
    ) -> Dict[str, List[str]]:
        """
        并发下载历史记录中的输出文件

        解析历史记录（来自 query_output_history_v2 的 records）中的
        fileUrl 和 outputName，并发下载到本地目录。

        Args:
            records: 历史记录列表，每条记录应包含 fileUrl 和 outputName
            output_dir: 输出目录
            concurrency: 并发下载数，默认 5
            overwrite: 是否覆盖已存在的文件，默认 False
            retries: 下载失败重试次数，默认 1

        Returns:
            {"downloaded": [文件名列表], "skipped": [已跳过], "failed": [失败]}
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        tasks = self._extract_download_tasks(records, output_path)

        if not tasks:
            return {"downloaded": [], "skipped": [], "failed": []}

        downloaded: List[str] = []
        skipped: List[str] = []
        failed: List[str] = []

        def _download_one(url: str, filepath: Path) -> Tuple[str, str]:
            if filepath.exists() and not overwrite:
                return "skipped", filepath.name
            for attempt in range(retries + 1):
                try:
                    resp = httpx.get(url, follow_redirects=True, timeout=self.timeout)
                    resp.raise_for_status()
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    filepath.write_bytes(resp.content)
                    return "downloaded", filepath.name
                except Exception:
                    if filepath.exists():
                        filepath.unlink(missing_ok=True)
                    if attempt >= retries:
                        return "failed", filepath.name
            return "failed", filepath.name

        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            future_map = {
                executor.submit(_download_one, url, fp): fp.name
                for url, fp in tasks
            }
            for future in as_completed(future_map):
                status, name = future.result()
                if status == "downloaded":
                    downloaded.append(name)
                elif status == "skipped":
                    skipped.append(name)
                else:
                    failed.append(name)

        return {
            "downloaded": downloaded,
            "skipped": skipped,
            "failed": failed,
        }

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

    def run_model_api(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> V2QueryResult:
        """
        调用标准模型 API

        Args:
            endpoint: 标准模型接口路径，可以传完整路径如
                /openapi/v2/rhart-image/f-2-dev/text-to-image
                或相对路径如 rhart-image/f-2-dev/text-to-image
            payload: 接口请求体

        Returns:
            V2QueryResult
        """
        normalized_endpoint = self._normalize_model_endpoint(endpoint)
        response = self._post(normalized_endpoint, payload, include_api_key=False)
        return V2QueryResult.from_dict(response)

    def preview_model_price(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> ModelPricePreview:
        """
        预估标准模型 API 调用价格

        Args:
            endpoint: 原始标准模型接口路径
            payload: 与实际调用相同的请求体

        Returns:
            ModelPricePreview
        """
        normalized_endpoint = self._normalize_model_endpoint(endpoint)
        preview_endpoint = self._normalize_price_preview_endpoint(normalized_endpoint)
        response = self._post(preview_endpoint, payload, include_api_key=False)
        return ModelPricePreview.from_dict(response)

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

    def wait_for_query_v2_completion(
        self,
        task_id: str,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_WAIT_TIMEOUT,
        on_status_change: Optional[Callable[[TaskStatus], None]] = None,
    ) -> V2QueryResult:
        """
        基于 /openapi/v2/query 等待任务完成

        适合标准模型 API 等直接返回 V2 结构的接口。
        """
        import time
        start_time = time.time()

        while True:
            result = self.query_v2(task_id)

            if result.error_code and result.error_code != "0" and not result.task_id:
                raise TaskError(
                    code=ErrorCode.TASK_STATUS_ERROR,
                    message=result.error_message or "任务执行失败",
                    task_id=task_id,
                )

            if on_status_change and result.status is not None:
                on_status_change(result.status)

            if result.status == TaskStatus.SUCCESS:
                return result

            if result.status == TaskStatus.FAILED:
                raise TaskError(
                    code=ErrorCode.TASK_STATUS_ERROR,
                    message=result.error_message or "任务执行失败",
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
        file: Union[BinaryIO, bytes, str, os.PathLike[str]],
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
        if isinstance(file, (str, os.PathLike)):
            # 文件路径
            file_path = Path(file)
            actual_filename = filename or file_path.name
            with open(file_path, "rb") as f:
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

    def upload_image(self, file: Union[BinaryIO, bytes, str, os.PathLike[str]]) -> Dict[str, str]:
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

    def copy_workflow(
        self,
        workflow_id: str,
        copy_mode: int = 1,
    ) -> WorkflowCopyResponse:
        """
        获取工作流详情（通过复制接口）

        POST /api/workflow/copy
        返回工作流的 id、name、workflowContent（JSON 字符串）等完整信息。
        可通过 response.get_workflow_content_parsed() 将 workflowContent 解析为字典。

        Args:
            workflow_id: 工作流ID
            copy_mode: 复制模式，默认为 1

        Returns:
            WorkflowCopyResponse: 包含工作流完整信息
        """
        response = self._post("/api/workflow/copy", {
            "workflowId": workflow_id,
            "copyMode": copy_mode,
        })
        return WorkflowCopyResponse.from_dict(response)

    # ==================== 同步 Portal/Webapp 方法 ====================

    def get_access_token(self) -> AccessAuthResponse:
        """
        获取用户 access token

        调用 /api/instance/access/auth 接口，通过 API Key 获取
        一个有时效性的用户访问令牌（JWT 格式），用于访问需要
        用户级别认证的接口。

        Returns:
            AccessAuthResponse: 包含 accessKey 和过期时间
        """
        response = self._post("/api/instance/access/auth", {})
        return AccessAuthResponse.from_dict(response)

    def list_webapps(
        self,
        request: Optional[WebappListRequest] = None,
    ) -> WebappListResponse:
        """
        获取 Webapp 列表

        Args:
            request: WebappListRequest 查询参数（可选）

        Returns:
            WebappListResponse: 分页 Webapp 列表
        """
        req = request or WebappListRequest()
        response = self._post("/api/webapp/list", req.to_dict())
        return WebappListResponse.from_dict(response)

    def list_portal_templates(
        self,
        request: Optional[PortalTemplateListRequest] = None,
    ) -> PortalTemplateListResponse:
        """
        获取工作流模板列表

        调用 /api/portal/template/list 接口，查询 RunningHub 市场中的
        工作流模板，支持关键词搜索、标签过滤和分页。

        Args:
            request: PortalTemplateListRequest 查询参数（可选）

        Returns:
            PortalTemplateListResponse: 分页模板列表，包含完整的记录信息
        """
        req = request or PortalTemplateListRequest()
        response = self._post("/api/portal/template/list", req.to_dict())
        return PortalTemplateListResponse.from_dict(response)

    def query_output_history_v2(
        self,
        request: Optional[OutputHistoryV2Request] = None,
        access_token: Optional[str] = None,
    ) -> OutputHistoryV2Response:
        """
        查询输出历史（V2）

        调用 /api/output/v2/history 接口，使用用户级别的 Bearer token
        查询任务输出历史记录，支持按状态、任务类型、是否包含输出等条件过滤。

        Args:
            request: OutputHistoryV2Request 查询参数（可选）
            access_token: 用户 Bearer token（可选）。
                         不传则使用 api_key 作为 token。

        Returns:
            OutputHistoryV2Response: 分页输出历史记录
        """
        req = request or OutputHistoryV2Request()
        payload = req.to_dict()
        token = access_token or self.api_key

        try:
            response = self.sync_client.post(
                "/api/output/v2/history",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            result = response.json()
            return OutputHistoryV2Response.from_dict(self._handle_response(result))
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP错误: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}", e)

    def get_user_info(
        self,
        user_id: str,
        *,
        access_token: Optional[str] = None,
    ) -> UserInfoResponse:
        """
        获取用户信息

        调用 /uc/getUserInfo 接口，使用用户级别的 Bearer token
        查询用户详细信息（会员、钱包、套餐等）。

        Args:
            user_id: 用户 ID（可从 RunningHubToken.identify 获取）
            access_token: 用户 Bearer token（可选）。
                         不传则使用 api_key 作为 token。

        Returns:
            UserInfoResponse: 用户详细信息
        """
        request = UserInfoRequest(user_id=user_id)
        token = access_token or self.api_key

        try:
            response = self.sync_client.post(
                "/uc/getUserInfo",
                json=request.to_dict(),
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            result = response.json()
            return UserInfoResponse.from_dict(self._handle_response(result))
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP错误: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}", e)

    def get_user_api_key(
        self,
        user_id: str,
        *,
        access_token: Optional[str] = None,
    ) -> UserApiKeyResponse:
        """
        获取用户 API Key 信息

        调用 /uc/apiKey/get 接口，使用用户级别的 Bearer token
        查询共享 API、专属 API、余额等信息。

        Args:
            user_id: 用户 ID
            access_token: 用户 Bearer token（可选）。
                         不传则使用 api_key 作为 token。

        Returns:
            UserApiKeyResponse: API Key 信息
        """
        request = UserApiKeyRequest(user_id=user_id)
        token = access_token or self.api_key

        try:
            response = self.sync_client.post(
                "/uc/apiKey/get",
                json=request.to_dict(),
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            result = response.json()
            return UserApiKeyResponse.from_dict(self._handle_response(result))
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP错误: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}", e)

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

    async def async_run_ai_app(
        self,
        webapp_id: Union[int, str],
        node_info_list: Optional[List[Union[NodeInput, Dict[str, Any]]]] = None,
        **options
    ) -> CreateTaskResponse:
        """异步发起 AI App 任务"""
        request = self._build_ai_app_run_request(webapp_id, node_info_list, options)
        response = await self._async_post("/task/openapi/ai-app/run", request.to_dict())
        return CreateTaskResponse.from_dict(response)

    async def async_run_model_api(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> V2QueryResult:
        """异步调用标准模型 API"""
        normalized_endpoint = self._normalize_model_endpoint(endpoint)
        response = await self._async_post(
            normalized_endpoint,
            payload,
            include_api_key=False,
        )
        return V2QueryResult.from_dict(response)

    async def async_preview_model_price(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> ModelPricePreview:
        """异步预估标准模型 API 调用价格"""
        normalized_endpoint = self._normalize_model_endpoint(endpoint)
        preview_endpoint = self._normalize_price_preview_endpoint(normalized_endpoint)
        response = await self._async_post(
            preview_endpoint,
            payload,
            include_api_key=False,
        )
        return ModelPricePreview.from_dict(response)

    async def async_run_ai_app_with_modifier(
        self,
        webapp_id: Union[int, str],
        modifier: NodeModifier,
        **options
    ) -> CreateTaskResponse:
        """异步使用节点修改器发起 AI App 任务"""
        return await self.async_run_ai_app(webapp_id, modifier.to_list(), **options)

    async def async_get_ai_app_api_demo(
        self,
        webapp_id: Union[int, str],
    ) -> AiAppApiCallDemo:
        """异步获取 AI App API 调用示例和可修改节点信息"""
        response = await self._async_get(
            "/api/webapp/apiCallDemo",
            {"webappId": str(webapp_id), "apiKey": self.api_key},
        )
        return AiAppApiCallDemo.from_dict(response)

    async def async_list_public_models(
        self,
        resource_type: str = "UNET",
        resource_name: str = "",
        base_models: Optional[List[str]] = None,
        tags: Optional[List[int]] = None,
        current: int = 1,
        size: int = 10,
    ) -> PublicModelListResponse:
        """异步获取公共模型列表"""
        request = PublicModelListRequest(
            resource_type=resource_type,
            resource_name=resource_name,
            base_models=base_models,
            tags=tags,
            current=current,
            size=size,
        )
        response = await self._async_post(
            "/openapi/v2/resource/list",
            request.to_dict(),
            include_api_key=False,
        )
        return PublicModelListResponse.from_dict(response)

    async def async_get_status(self, task_id: str) -> TaskStatus:
        """异步查询任务状态"""
        response = await self._async_post("/task/openapi/status", {"taskId": task_id})
        return TaskStatus(response)

    async def async_get_account_status(self) -> AccountStatus:
        """异步获取账户信息"""
        response = await self._async_post("/uc/openapi/accountStatus", {})
        return AccountStatus.from_dict(response)

    async def async_list_api_keys(self) -> List[ApiKeyInfo]:
        """异步查询 API Key 列表"""
        response = await self._async_get("/openapi/v2/api-key/list", {})
        if isinstance(response, list):
            return [ApiKeyInfo.from_dict(item) for item in response]
        return []

    async def async_get_queue_status(self) -> QueueStatus:
        """异步查询当前 API Key 的队列状态"""
        response = await self._async_get("/openapi/v2/queue/status", {})
        return QueueStatus.from_dict(response)

    async def async_validate_api_key(self) -> bool:
        """异步通过 `/openapi/v2/queue/status` 验证当前 API Key 是否有效。"""
        try:
            await self.async_get_queue_status()
            return True
        except RunningHubError as exc:
            if exc.code in (
                ErrorCode.API_KEY_INVALID,
                ErrorCode.API_KEY_USER_NOT_FOUND,
            ):
                return False
            raise

    async def async_get_webhook_detail(self, task_id: str) -> WebhookDetail:
        """异步根据 task_id 获取 webhook 事件详情"""
        response = await self._async_post(
            "/task/openapi/getWebhookDetail",
            {"taskId": task_id},
        )
        return WebhookDetail.from_dict(response)

    async def async_retry_webhook(self, webhook_id: str, webhook_url: str) -> None:
        """异步重新发送指定 webhook 事件"""
        await self._async_post(
            "/task/openapi/retryWebhook",
            {"webhookId": webhook_id, "webhookUrl": webhook_url},
        )

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

    async def async_download_file(
        self,
        url: str,
        output_path: Union[str, Path],
        overwrite: bool = True,
    ) -> Path:
        """异步下载任意 URL 到本地文件。"""
        path = Path(output_path)
        if path.exists() and not overwrite:
            raise ValidationError("目标文件已存在", field="output_path")

        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with httpx.AsyncClient(timeout=self.timeout * 3) as client:
                async with client.stream("GET", url) as response:
                    response.raise_for_status()
                    with open(path, "wb") as file_obj:
                        async for chunk in response.aiter_bytes():
                            file_obj.write(chunk)
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"下载失败: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"下载请求失败: {str(e)}", e)

        return path

    async def async_download_outputs(
        self,
        outputs: List[TaskOutput],
        output_dir: Union[str, Path],
        overwrite: bool = True,
    ) -> List[Path]:
        """异步下载任务输出列表到本地目录。"""
        base_dir = Path(output_dir)
        downloaded_paths: List[Path] = []

        for index, output in enumerate(outputs, start=1):
            filename = self._build_output_filename(output, index)
            file_path = base_dir / filename
            downloaded_paths.append(
                await self.async_download_file(output.file_url, file_path, overwrite=overwrite)
            )

        return downloaded_paths

    async def async_download_task_outputs(
        self,
        task_id: str,
        output_dir: Union[str, Path],
        overwrite: bool = True,
    ) -> List[Path]:
        """异步根据 task_id 查询并下载全部输出到本地目录。"""
        outputs = await self.async_get_outputs(task_id)
        return await self.async_download_outputs(outputs, output_dir, overwrite=overwrite)

    async def async_download_history_outputs(
        self,
        records: List[Dict[str, Any]],
        output_dir: Union[str, Path],
        *,
        concurrency: int = 5,
        overwrite: bool = False,
        retries: int = 1,
    ) -> Dict[str, List[str]]:
        """
        异步并发下载历史记录中的输出文件

        Args:
            records: 历史记录列表，应包含 fileUrl 和 outputName
            output_dir: 输出目录
            concurrency: 并发下载数，默认 5
            overwrite: 是否覆盖已存在的文件，默认 False
            retries: 下载失败重试次数，默认 1

        Returns:
            {"downloaded": [文件名列表], "skipped": [已跳过], "failed": [失败]}
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        tasks = self._extract_download_tasks(records, output_path)

        if not tasks:
            return {"downloaded": [], "skipped": [], "failed": []}

        semaphore = asyncio.Semaphore(concurrency)
        downloaded: List[str] = []
        skipped: List[str] = []
        failed: List[str] = []

        async with httpx.AsyncClient(timeout=self.timeout) as client:

            async def _download_one(url: str, filepath: Path) -> Tuple[str, str]:
                if filepath.exists() and not overwrite:
                    return "skipped", filepath.name
                async with semaphore:
                    for attempt in range(retries + 1):
                        try:
                            resp = await client.get(url, follow_redirects=True)
                            resp.raise_for_status()
                            filepath.parent.mkdir(parents=True, exist_ok=True)
                            filepath.write_bytes(resp.content)
                            return "downloaded", filepath.name
                        except Exception:
                            if filepath.exists():
                                filepath.unlink(missing_ok=True)
                            if attempt >= retries:
                                return "failed", filepath.name
                    return "failed", filepath.name

            jobs = [_download_one(url, fp) for url, fp in tasks]
            results = await asyncio.gather(*jobs)

        for status, name in results:
            if status == "downloaded":
                downloaded.append(name)
            elif status == "skipped":
                skipped.append(name)
            else:
                failed.append(name)

        return {
            "downloaded": downloaded,
            "skipped": skipped,
            "failed": failed,
        }

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
        return []

    async def async_wait_for_query_v2_completion(
        self,
        task_id: str,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        timeout: float = DEFAULT_WAIT_TIMEOUT,
        on_status_change: Optional[Callable[[TaskStatus], None]] = None,
    ) -> V2QueryResult:
        """异步基于 /openapi/v2/query 等待任务完成"""
        import time
        start_time = time.time()

        while True:
            result = await self.async_query_v2(task_id)

            if result.error_code and result.error_code != "0" and not result.task_id:
                raise TaskError(
                    code=ErrorCode.TASK_STATUS_ERROR,
                    message=result.error_message or "任务执行失败",
                    task_id=task_id,
                )

            if on_status_change and result.status is not None:
                on_status_change(result.status)

            if result.status == TaskStatus.SUCCESS:
                return result

            if result.status == TaskStatus.FAILED:
                raise TaskError(
                    code=ErrorCode.TASK_STATUS_ERROR,
                    message=result.error_message or "任务执行失败",
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

    # ==================== 异步 Portal/Webapp 方法 ====================

    async def async_get_access_token(self) -> AccessAuthResponse:
        """
        异步获取用户 access token

        Returns:
            AccessAuthResponse: 包含 accessKey 和过期时间
        """
        response = await self._async_post("/api/instance/access/auth", {})
        return AccessAuthResponse.from_dict(response)

    async def async_list_webapps(
        self,
        request: Optional[WebappListRequest] = None,
    ) -> WebappListResponse:
        """
        异步获取 Webapp 列表

        Args:
            request: WebappListRequest 查询参数（可选）

        Returns:
            WebappListResponse: 分页 Webapp 列表
        """
        req = request or WebappListRequest()
        response = await self._async_post("/api/webapp/list", req.to_dict())
        return WebappListResponse.from_dict(response)

    async def async_list_portal_templates(
        self,
        request: Optional[PortalTemplateListRequest] = None,
    ) -> PortalTemplateListResponse:
        """
        异步获取工作流模板列表

        Args:
            request: PortalTemplateListRequest 查询参数（可选）

        Returns:
            PortalTemplateListResponse: 分页模板列表
        """
        req = request or PortalTemplateListRequest()
        response = await self._async_post("/api/portal/template/list", req.to_dict())
        return PortalTemplateListResponse.from_dict(response)

    async def async_query_output_history_v2(
        self,
        request: Optional[OutputHistoryV2Request] = None,
        access_token: Optional[str] = None,
    ) -> OutputHistoryV2Response:
        """
        异步查询输出历史（V2）

        Args:
            request: OutputHistoryV2Request 查询参数（可选）
            access_token: 用户 Bearer token（可选）。不传则使用 api_key。

        Returns:
            OutputHistoryV2Response: 分页输出历史记录
        """
        req = request or OutputHistoryV2Request()
        payload = req.to_dict()
        token = access_token or self.api_key

        try:
            response = await self.async_client.post(
                "/api/output/v2/history",
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            result = response.json()
            return OutputHistoryV2Response.from_dict(self._handle_response(result))
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP错误: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}", e)

    async def async_get_user_info(
        self,
        user_id: str,
        *,
        access_token: Optional[str] = None,
    ) -> UserInfoResponse:
        """
        异步获取用户信息

        Args:
            user_id: 用户 ID
            access_token: 用户 Bearer token（可选）

        Returns:
            UserInfoResponse: 用户详细信息
        """
        request = UserInfoRequest(user_id=user_id)
        token = access_token or self.api_key

        try:
            response = await self.async_client.post(
                "/uc/getUserInfo",
                json=request.to_dict(),
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            result = response.json()
            return UserInfoResponse.from_dict(self._handle_response(result))
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP错误: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}", e)

    async def async_get_user_api_key(
        self,
        user_id: str,
        *,
        access_token: Optional[str] = None,
    ) -> UserApiKeyResponse:
        """
        异步获取用户 API Key 信息

        Args:
            user_id: 用户 ID
            access_token: 用户 Bearer token（可选）

        Returns:
            UserApiKeyResponse: API Key 信息
        """
        request = UserApiKeyRequest(user_id=user_id)
        token = access_token or self.api_key

        try:
            response = await self.async_client.post(
                "/uc/apiKey/get",
                json=request.to_dict(),
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            result = response.json()
            return UserApiKeyResponse.from_dict(self._handle_response(result))
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP错误: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}", e)

    async def async_upload_file(
        self,
        file: Union[BinaryIO, bytes, str, os.PathLike[str]]
    ) -> UploadResponseData:
        """异步上传文件"""
        if isinstance(file, (str, os.PathLike)):
            file_path = Path(file)
            actual_filename = file_path.name
            with open(file_path, "rb") as f:
                file_content = f.read()
        elif isinstance(file, bytes):
            file_content = file
            actual_filename = "upload.bin"
        else:
            file_content = file.read()
            actual_filename = getattr(file, 'name', 'upload.bin')

        files = {"file": (actual_filename, file_content)}
        response = await self._async_upload("/openapi/v2/media/upload/binary", files)
        return UploadResponseData.from_dict(response)

    async def async_upload_image(
        self,
        file: Union[BinaryIO, bytes, str, os.PathLike[str]]
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

    async def async_copy_workflow(
        self,
        workflow_id: str,
        copy_mode: int = 1,
    ) -> WorkflowCopyResponse:
        """异步获取工作流详情"""
        response = await self._async_post("/api/workflow/copy", {
            "workflowId": workflow_id,
            "copyMode": copy_mode,
        })
        return WorkflowCopyResponse.from_dict(response)

    async def async_query_v2(self, task_id: str) -> V2QueryResult:
        """异步 V2 查询接口"""
        response = await self._async_post("/openapi/v2/query", {"taskId": task_id})
        return V2QueryResult.from_dict(response)

    # ==================== 辅助方法 ====================

    def create_modifier(self) -> NodeModifier:
        """创建节点修改器"""
        return modify_nodes()

    def _normalize_model_endpoint(self, endpoint: str) -> str:
        """标准化标准模型 API 路径"""
        normalized = endpoint.strip()
        if not normalized:
            raise ValidationError("标准模型 API 路径不能为空", field="endpoint")

        if normalized.startswith("https://") or normalized.startswith("http://"):
            prefix = self.base_url.rstrip("/")
            if normalized.startswith(prefix):
                normalized = normalized[len(prefix):]
            else:
                raise ValidationError(
                    "endpoint 必须属于当前 RunningHub base_url",
                    field="endpoint",
                )

        if not normalized.startswith("/"):
            normalized = f"/{normalized}"

        if not normalized.startswith("/openapi/v2/"):
            normalized = f"/openapi/v2/{normalized.lstrip('/')}"

        return normalized

    def _build_output_filename(self, output: TaskOutput, index: int) -> str:
        """根据输出 URL 和类型构建本地文件名。"""
        parsed = urlparse(output.file_url)
        candidate = Path(unquote(parsed.path)).name
        if candidate:
            return candidate

        suffix = f".{output.file_type}" if output.file_type else ""
        return f"output_{index:03d}_node_{output.node_id}{suffix}"

    def _sanitize_filename(self, name: str) -> str:
        """清理文件名，移除非法字符"""
        illegal_chars = '<>:"/\\|?*\0'
        safe = "".join("_" if ch in illegal_chars else ch for ch in name).strip()
        return safe or "unnamed_file"

    def _filename_from_url(self, url: str) -> str:
        """从下载 URL 中提取文件名"""
        parsed = urlparse(url)
        raw_name = Path(unquote(parsed.path)).name
        return self._sanitize_filename(raw_name or "unnamed_file")

    def _extract_download_tasks(
        self,
        records: List[Dict[str, Any]],
        output_dir: Path,
    ) -> List[Tuple[str, Path]]:
        """从历史记录中提取下载任务列表，并进行文件名去重"""
        tasks: List[Tuple[str, str]] = []
        for row in records:
            file_url = str(row.get("fileUrl") or "").strip()
            if not file_url:
                continue
            output_name = str(row.get("outputName") or "").strip()
            if not output_name:
                output_name = self._filename_from_url(file_url)
            output_name = self._sanitize_filename(output_name)
            if output_name:
                tasks.append((file_url, output_name))

        # 文件名去重
        seen: Dict[str, int] = {}
        unique_tasks: List[Tuple[str, Path]] = []
        for url, name in tasks:
            base = Path(name).stem
            ext = Path(name).suffix
            count = seen.get(name, 0)
            unique_name = name if count == 0 else f"{base}_{count}{ext}"
            seen[name] = count + 1
            unique_tasks.append((url, output_dir / unique_name))

        return unique_tasks

    def _normalize_price_preview_endpoint(self, endpoint: str) -> str:
        """根据模型接口路径生成价格预估路径"""
        if not endpoint.startswith("/openapi/v2/"):
            raise ValidationError("无效的标准模型 API 路径", field="endpoint")
        suffix = endpoint[len("/openapi/v2/"):]
        return f"/openapi/v2/price-preview/{suffix}"

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

    def _build_ai_app_run_request(
        self,
        webapp_id: Union[int, str],
        node_info_list: Optional[List[Union[NodeInput, Dict[str, Any]]]],
        options: Dict[str, Any],
    ) -> AiAppRunRequest:
        """构建 AI App 运行请求"""
        parsed_node_list = None
        if node_info_list:
            parsed_node_list = []
            for item in node_info_list:
                if isinstance(item, NodeInput):
                    parsed_node_list.append(item)
                elif isinstance(item, dict):
                    parsed_node_list.append(NodeInput.from_dict(item))

        return AiAppRunRequest(
            webapp_id=webapp_id,
            node_info_list=parsed_node_list,
            webhook_url=options.get("webhook_url"),
            instance_type=options.get("instance_type"),
            access_password=options.get("access_password"),
        )

    def _get(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """同步 GET 请求"""
        try:
            response = self.sync_client.get(endpoint, params=params)
            response.raise_for_status()
            result = response.json()
            return self._handle_response(result)
        except httpx.HTTPStatusError as e:
            raise NetworkError(f"HTTP错误: {e.response.status_code}", e)
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}", e)

    def _post(
        self,
        endpoint: str,
        data: Dict[str, Any],
        include_api_key: bool = True,
    ) -> Any:
        """同步POST请求"""
        if include_api_key:
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

    async def _async_post(
        self,
        endpoint: str,
        data: Dict[str, Any],
        include_api_key: bool = True,
    ) -> Any:
        """异步POST请求"""
        if include_api_key:
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

    async def _async_get(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """异步 GET 请求"""
        try:
            response = await self.async_client.get(endpoint, params=params)
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
        if "code" not in result:
            return result

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

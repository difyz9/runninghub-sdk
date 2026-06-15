# RunningHub ComfyUI SDK

`runninghub-sdk` 是一个面向 RunningHub ComfyUI OpenAPI 的 Python SDK，支持任务创建、状态轮询、结果查询、文件上传，以及用链式 NodeModifier 修改工作流节点参数。

同时支持 RunningHub AI App 接口、门户模板与应用浏览、用户信息查询、输出历史查询与并发下载等能力。


## 认证方式

SDK 支持两种认证方式，使用前请先确认你的场景需要哪一种：

| 方式 | 获取途径 | 适用接口 | 示例 |
|------|---------|---------|------|
| **API Key** 🔑 | RunningHub 后台获取 | 任务创建/查询/取消、文件上传、工作流 JSON、AI App 运行、标准模型 API、公共模型列表、账户信息、队列状态、Webhook 调试 | `RunningHubClient(api_key="...")` |
| **用户 Token** 🪪 | 手机号+密码登录获取 | 门户模板列表、Webapp 列表、用户信息、用户 API Key 信息、输出历史查询、输出文件下载、Access Token 获取、调用日志详情 | `RunningHubClient.from_login("138...", "pswd")` 或 `RunningHubClient.from_env()` |

> **说明**：API Key 是 RunningHub 平台为开发者分配的固定密钥，适合后端集成。用户 Token 是模拟浏览器登录行为获取的临时凭证（有时效性），适合需要操作用户级数据的场景。SDK 统一了这两种方式——从 `login()` 返回的 `access_token` 可以直接作为 `api_key` 传入 `RunningHubClient`。


## 特性

- 🔑 **API Key** 与 🪪 **用户 Token** 双认证，覆盖全部 RunningHub 接口
- 📦 `from_env()` 方法一键从 `.env` 加载认证，无需手动处理登录逻辑
- 🧰 内置 `bootstrap_env()`、`get_env()`、`to_dict()` 等开箱即用的工具函数
- 手机号密码登录，自动缓存 Token，过期自动检测，JWT 自动解码获取 user_id
- 同时支持同步和异步调用
- 基于 `httpx`，接口简单，依赖精简
- 提供完整类型注解，适合 IDE 自动补全
- 支持 `NodeModifier` 链式修改工作流节点输入
- 支持图片、视频、音频、LoRA 等文件上传
- 支持自动轮询等待任务完成
- 支持输出历史并发下载
- 提供一站式门户模板与 Webapp 浏览能力

## 安装

```bash
pip install runninghub-sdk
```

如果你是在本仓库中本地开发：

```bash
pip install -e .
```

## 快速开始

### 方式一：API Key（推荐，适合后端集成）

```python
from runninghub_sdk import RunningHubClient, modify_nodes

# 直接用 API Key 初始化
with RunningHubClient(api_key="your-api-key") as client:
    modifier = (
        modify_nodes()
        .text("6", "a cinematic sunset over the sea")
        .seed("3", 12345)
        .steps("3", 25)
    )

    task = client.run_with_modifier("workflow-id", modifier)
    outputs = client.wait_for_completion(task.task_id)

    for output in outputs:
        print(output.file_url)
```

### 方式二：手机号+密码登录（适合操作用户数据）

```python
from runninghub_sdk import RunningHubClient

# 登录 → 自动缓存 token → 返回可用的客户端
client = RunningHubClient.from_login(
    "138xxxxxxxx",
    "your_password",
    token_cache="./token.json",
)

# 调用需要用户 token 的接口
templates = client.list_portal_templates()
user = client.get_user_info(user_id="your-user-id")

# 也支持所有 API Key 接口（自动复用 access_token）
task = client.run("workflow-id")
```

### 方式三：从环境变量一键创建（推荐在示例脚本中使用）

在项目根目录创建 `.env` 文件：

```env
RUNNINGHUB_USERNAME=138xxxxxxxx
RUNNINGHUB_PASSWORD=your_password
```

然后在代码中直接使用 `from_env()`：

```python
from runninghub_sdk import RunningHubClient, bootstrap_env

# 加载 .env 并自动创建客户端（自动登录、自动提取 user_id）
bootstrap_env()                         # 从脚本目录 / cwd 加载 .env
client = RunningHubClient.from_env()    # 自动选择可用的认证方式

# 直接调用任意接口
detail = client.get_call_log_detail(
    task_id="2066351966031925250",
    user_id="2013415890368073729",
)
```

认证优先级：显式参数 > 环境变量 `RUNNINGHUB_USERNAME` + `RUNNINGHUB_PASSWORD`（自动 login） > `RUNNINGHUB_TOKEN` > `RUNNINGHUB_API_KEY`。

### 异步调用

```python
import asyncio
from runninghub_sdk import RunningHubClient, modify_nodes

async def main() -> None:
    async with RunningHubClient(api_key="your-api-key") as client:
        modifier = modify_nodes().text("6", "a beautiful landscape")
        task = await client.async_run_with_modifier("workflow-id", modifier)
        outputs = await client.async_wait_for_completion(task.task_id)
        for output in outputs:
            print(output.file_url)

asyncio.run(main())
```

## 核心能力

### 认证方式速查

| 认证方式 | 适用场景 | 初始化方法 |
|---------|---------|-----------|
| 🔑 API Key | 任务、AI App、模型 API、上传、账户队列 | `RunningHubClient(api_key=...)` |
| 🪪 用户 Token | 门户模板、用户信息、输出历史、调用日志、登录 | `RunningHubClient.from_login(...)` |
| 📦 环境变量 | 示例脚本、快速开发、CI/CD 环境 | `RunningHubClient.from_env()` |

### 登录与 Token 管理

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `login()` (classmethod) | — | — | 手机号密码登录，返回 `RunningHubToken`（含 `user_id` 属性自动解码 JWT） |
| `from_login()` (classmethod) | — | — | 一键登录 → 缓存 token → 返回客户端 |
| `from_token_cache()` (classmethod) | — | — | 从本地缓存恢复客户端，过期自动提示 |
| `from_env()` (classmethod) | — | — | 从参数或环境变量自动选择认证方式创建客户端 |
| `get_access_token()` | `async_get_access_token()` | 🪪 | 获取用户级 access token（JWT） |

### 用户信息接口

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `get_user_info()` | `async_get_user_info()` | 🪪 | 获取用户信息（会员、钱包、套餐等） |
| `get_user_api_key()` | `async_get_user_api_key()` | 🪪 | 获取用户 API Key 详情（共享/专属/普通） |

### 门户应用与模板

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `list_portal_templates()` | `async_list_portal_templates()` | 🪪 | 获取门户模板列表，支持关键词搜索、分页 |
| `list_webapps()` | `async_list_webapps()` | 🪪 | 获取 Webapp 列表，支持标签过滤 |
| `get_ai_app_api_demo()` | `async_get_ai_app_api_demo()` | 🔑 | 获取 AI App 调用示例、节点信息、封面和标签 |
| `run_ai_app()` | `async_run_ai_app()` | 🔑 | 发起 AI App 任务 |
| `run_ai_app_with_modifier()` | `async_run_ai_app_with_modifier()` | 🔑 | 使用修改器发起 AI App 任务 |
| `list_public_models()` | `async_list_public_models()` | 🔑 | 获取公共模型列表，支持类型/名称/基础模型/标签筛选 |

### 任务接口

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `run()` | `async_run()` | 🔑 | 发起 ComfyUI 任务 |
| `run_with_modifier()` | `async_run_with_modifier()` | 🔑 | 使用 NodeModifier 发起任务 |
| `get_status()` | `async_get_status()` | 🔑 | 查询任务状态 |
| `get_outputs()` | `async_get_outputs()` | 🔑 | 查询任务输出 |
| `cancel()` | `async_cancel()` | 🔑 | 取消任务 |
| `wait_for_completion()` | `async_wait_for_completion()` | 🔑 | 轮询直到任务完成 |
| `query_v2()` | `async_query_v2()` | 🔑 | V2 查询接口 |

### 标准模型 API

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `run_model_api()` | `async_run_model_api()` | 🔑 | 通用标准模型 API 调用（图像/视频/音频/3D） |
| `preview_model_price()` | `async_preview_model_price()` | 🔑 | 预估标准模型调用价格 |
| `wait_for_query_v2_completion()` | `async_wait_for_query_v2_completion()` | 🔑 | 基于 V2 查询轮询模型任务完成 |

### 输出历史与文件下载

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `query_output_history_v2()` | `async_query_output_history_v2()` | 🪪 | 查询任务输出历史（支持状态/类型/时间过滤） |
| `download_history_outputs()` | `async_download_history_outputs()` | — | 并发下载历史记录中的输出文件（默认 5 并发） |
| `download_file()` | `async_download_file()` | — | 下载单个文件到本地 |
| `download_outputs()` | `async_download_outputs()` | 🔑 | 下载任务输出列表 |
| `download_task_outputs()` | `async_download_task_outputs()` | 🔑 | 根据 task_id 查询并下载全部输出 |

### 文件上传

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `upload_file()` | `async_upload_file()` | 🔑 | 上传通用文件（图片/视频/音频） |
| `upload_image()` | `async_upload_image()` | 🔑 | 上传图片 |
| `upload_lora()` | `async_upload_lora()` | 🔑 | 上传 LoRA 模型 |

### 工作流与调试

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `get_workflow_json()` | `async_get_workflow_json()` | 🔑 | 获取工作流 JSON 字符串 |
| `get_workflow_json_parsed()` | `async_get_workflow_json_parsed()` | 🔑 | 获取解析后的工作流对象 |
| `create_modifier()` | — | — | 创建 NodeModifier 实例 |

### 调用日志详情

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `get_call_log_detail()` | `async_get_call_log_detail()` | 🪪 | 查询调用日志详情（基本信息、输出文件、费用、请求参数、响应详情） |

### 工具函数

| 函数 | 说明 |
|------|------|
| `bootstrap_env(script_dir)` | 从脚本目录/当前目录加载 `.env` 文件到环境变量 |
| `get_env(name, default)` | 安全读取环境变量，不存在返回默认值 |
| `get_required_env(name)` | 强制读取环境变量，不存在抛 `ValueError` |
| `to_dict(obj)` | 递归将 dataclass/enum 树转换为纯 dict，便于 JSON 序列化 |

### 账户与队列

| 同步方法 | 异步方法 | 认证 | 说明 |
|---------|---------|------|------|
| `get_account_status()` | `async_get_account_status()` | 🔑 | 获取账户信息（余额、任务数、API 类型） |
| `list_api_keys()` | `async_list_api_keys()` | 🔑 | 查询 API Key 列表 |
| `get_queue_status()` | `async_get_queue_status()` | 🔑 | 查询当前队列状态 |
| `validate_api_key()` | `async_validate_api_key()` | 🔑 | 验证 API Key 是否有效 |
| `get_webhook_detail()` | `async_get_webhook_detail()` | 🔑 | 查询 webhook 事件详情 |
| `retry_webhook()` | `async_retry_webhook()` | 🔑 | 重新发送 webhook 事件 |

## NodeModifier

`NodeModifier` 用于用链式 API 构造 `node_info_list`，让工作流参数修改更直观（需 **API Key** 认证）。

```python
from runninghub_sdk import modify_nodes

modifier = (
    modify_nodes()
    .text("6", "a portrait in film style")
    .negative_text("7", "blurry, low quality")
    .seed("3", 12345)
    .steps("3", 25)
    .cfg("3", 7.5)
    .size("5", 1024, 768)
    .sampler("3", "dpmpp_2m")
    .scheduler("3", "karras")
    .image("10", "uploaded-file.png")
)
```

常用方法如下：

| 方法 | 说明 |
|------|------|
| `set(node_id, field_name, value)` | 通用设置 |
| `text(node_id, text)` | 设置提示词 |
| `negative_text(node_id, text)` | 设置负面提示词 |
| `seed(node_id, seed)` | 设置随机种子 |
| `steps(node_id, steps)` | 设置采样步数 |
| `cfg(node_id, cfg)` | 设置 CFG |
| `size(node_id, width, height)` | 设置图像尺寸 |
| `sampler(node_id, name)` | 设置采样器 |
| `scheduler(node_id, name)` | 设置调度器 |
| `denoise(node_id, value)` | 设置去噪强度 |
| `image(node_id, file_name)` | 设置图片文件 |
| `video(node_id, file_name)` | 设置视频文件 |
| `audio(node_id, file_name)` | 设置音频文件 |
| `lora(node_id, file_name)` | 设置 LoRA 文件 |
| `checkpoint(node_id, name)` | 设置模型名 |

## AI App 使用

AI App 接口通过 **API Key** 认证，适合直接调用 RunningHub 页面上的应用。`webappId` 可以从 AI App 详情页链接中获取，例如 `https://www.runninghub.cn/ai-detail/1937084629516193794` 最后的数字就是 `webappId`。

推荐先读取 AI App 的可调用示例，再按节点修改参数并运行：

```python
from runninghub_sdk import RunningHubClient, modify_nodes

with RunningHubClient(api_key="your-api-key") as client:
    demo = client.get_ai_app_api_demo("1937084629516193794")

    for node in demo.node_info_list:
        print(node.node_id, node.field_name, node.field_type, node.description)

    modifier = (
        modify_nodes()
        .set("52", "prompt", "把人物发型改成齐耳短发")
        .set("37", "aspect_ratio", "1:1")
    )

    task = client.run_ai_app_with_modifier(
        "1937084629516193794",
        modifier,
    )
    outputs = client.wait_for_completion(task.task_id)

    for output in outputs:
        print(output.file_url)
```

如果 AI App 包含 `IMAGE`、`AUDIO`、`VIDEO` 一类输入，通常先上传文件，再把返回的 `fileName` 设置回对应节点的 `fieldValue`：

```python
from runninghub_sdk import RunningHubClient, modify_nodes

with RunningHubClient(api_key="your-api-key") as client:
    uploaded = client.upload_image("input.png")

    modifier = (
        modify_nodes()
        .set("39", "image", uploaded["fileName"])
        .set("52", "prompt", "保留人物姿态，改成胶片质感")
    )

    task = client.run_ai_app_with_modifier("1937084629516193794", modifier)
    outputs = client.wait_for_completion(task.task_id)

    for output in outputs:
        print(output.file_url)
```

AI App 开启加密访问时，可以在运行时传入 `access_password`：

```python
task = client.run_ai_app(
    webapp_id="1937084629516193794",
    node_info_list=[
        {"nodeId": "52", "fieldName": "prompt", "fieldValue": "一张电影感人像"}
    ],
    access_password="your-password",
)
```

### 获取公共模型列表

可以通过公共模型列表接口拉取 RunningHub 提供的可用模型，并按类型、名称、基础模型、标签做筛选。

```python
from runninghub_sdk import RunningHubClient

with RunningHubClient(api_key="your-api-key") as client:
    models = client.list_public_models(
        resource_type="UNET",
        resource_name="realDream",
        base_models=["Flux2-Klein-9B"],
        current=1,
        size=10,
    )

    print(models.total)
    for record in models.records:
        print(record.resource_name, record.resource_type)
        if record.versions:
            print(record.versions[0].version_resource_name)
```

`resource_type` 当前支持文档中的 `UNET`、`CHECKPOINT`、`LORA`、`GGUF`。

## 标准模型 API 使用

标准模型 API 的端点很多，不适合为每个模型单独维护一套方法。SDK 提供了通用调用入口 `run_model_api()`，你只需要传模型端点和对应请求体即可。

例如调用 `f-2-dev/text-to-image`：

```python
from runninghub_sdk import RunningHubClient

with RunningHubClient(api_key="your-api-key") as client:
    task = client.run_model_api(
        "/openapi/v2/rhart-image/f-2-dev/text-to-image",
        {
            "12##text": "在一片非洲大草原上，一只真实非洲狮的摄影照片",
            "41##select": "9:16",
            "30##value": 1024,
            "29##value": 1024,
            "43##file_type": "png",
        },
    )

    result = client.wait_for_query_v2_completion(task.task_id)
    print(result.results)
```

也可以只传相对路径，SDK 会自动补成 `/openapi/v2/...`：

```python
task = client.run_model_api(
    "rhart-audio/text-to-audio/speech-2.8-hd",
    {
        "text": "Bonjour! How are you today?",
        "voice_id": "Wise_Woman",
        "enable_base64_output": False,
        "english_normalization": False,
    },
)
```

调用前可以先做价格预估。把原始模型路径换给 `preview_model_price()` 即可，SDK 会自动转换成 `/openapi/v2/price-preview/...`：

```python
price = client.preview_model_price(
    "rhart-image/f-2-dev/text-to-image",
    {
        "12##text": "一张电影感狮子海报",
        "41##select": "9:16",
        "43##file_type": "png",
    },
)

print(price.estimated_price, price.currency)
```

## 用户信息查询（需用户 Token）

需要先通过 `from_login()` 或 `login()` 获取用户级 Token：

```python
from runninghub_sdk import RunningHubClient

# 从登录 token 缓存恢复
client = RunningHubClient.from_token_cache("./token.json")

# 查询用户信息 — identify 就是 userId
user = client.get_user_info(user_id="2013415890368073729")
print(f"昵称: {user.nick_name}")
print(f"手机: {user.mobile}")
print(f"会员: {user.member_info.member_name}（到期: {user.member_info.member_expired_time}）")
print(f"RH币: {user.total_coin}")
print(f"钱包余额: {user.wallet_info.balance} 元")
print(f"API Key: {user.api_key}")

# 查询 API Key 详情
api_key_info = client.get_user_api_key(user_id=user.id)
print(f"共享 API: {api_key_info.shared_api.api_key}（并发: {api_key_info.shared_api.concurrent_limit}）")
print(f"普通 API: {api_key_info.normal_api_key}")
print(f"月消费: {api_key_info.monthly_cost} 元")
```

## 门户模板与 Webapp 浏览（需用户 Token）

浏览 RunningHub 市场中的模板和应用，支持关键词搜索和分页：

```python
from runninghub_sdk import RunningHubClient, PortalTemplateListRequest, WebappListRequest

client = RunningHubClient.from_login("138xxxxxxxx", "your_password")

# 搜索模板
templates = client.list_portal_templates(
    PortalTemplateListRequest(search="LTX", size=10, current=1)
)
print(f"模板总数: {templates.total}")
for record in templates.records:
    print(f"  - {record.name}（作者: {record.owner.name}，使用: {record.statistics_info.use_count} 次）")

# 浏览 Webapp
webapps = client.list_webapps(WebappListRequest(size=10, sort="RECOMMEND"))
for app in webapps.records:
    print(f"  - {app.get('name', 'N/A')}")
```

## 账户、队列与 webhook 调试

```python
from runninghub_sdk import RunningHubClient

with RunningHubClient(api_key="your-api-key") as client:
    if not client.validate_api_key():
        print("API Key 无效")
        raise SystemExit(1)

    account = client.get_account_status()
    print(account.remain_coins, account.current_task_counts, account.api_type)
    keys = client.list_api_keys()
    for key in keys:
        print(key.key, key.status, key.visible)

    queue = client.get_queue_status()
    print(queue.api_key_type, queue.running_count, queue.queued_count)
```


## 输出历史查询与并发下载

查询历史任务输出并批量下载，需要用户 Token 认证（`from_login` 或传入 `access_token`）。

```python
from runninghub_sdk import RunningHubClient, OutputHistoryV2Request

client = RunningHubClient.from_login(
    "138xxxxxxxx", "your_password",
    token_cache="./token.json",
)

# 查询历史记录（支持按状态、任务类型过滤）
history = client.query_output_history_v2(
    OutputHistoryV2Request(
        size=20,
        status=["SUCCESS"],
        task_type=["WEBAPP", "API"],
        has_output=True,
    )
)
print(f"查到 {history.total} 条记录")

# 并发下载所有输出文件（默认 5 并发）
result = client.download_history_outputs(
    records=history.records,
    output_dir="./downloads",
    concurrency=8,
)
print(f"已下载: {len(result['downloaded'])}")
print(f"已跳过: {len(result['skipped'])}")
print(f"失败:   {len(result['failed'])}")
```

### 异步版本

```python
import asyncio
from runninghub_sdk import RunningHubClient, OutputHistoryV2Request

token = RunningHubClient.login("138xxxxxxxx", "your_password")

async def main():
    async with RunningHubClient(api_key=token.access_token) as client:
        history = await client.async_query_output_history_v2(
            request=OutputHistoryV2Request(
                size=50, status=["SUCCESS"],
                task_type=["WEBAPP", "API"], has_output=True,
            ),
            access_token=token.access_token,
        )

        result = await client.async_download_history_outputs(
            records=history.records,
            output_dir="./downloads",
            concurrency=10,
        )
        print(f"已下载 {len(result['downloaded'])} 个")

asyncio.run(main())
```

## 错误处理

```python
from runninghub_sdk import ErrorCode, RunningHubError, TaskError, TimeoutError

try:
    outputs = client.wait_for_completion(task.task_id)
except TimeoutError as error:
    print(f"任务超时: {error.task_id}")
except TaskError as error:
    print(f"任务失败: {error.failed_reason}")
except RunningHubError as error:
    if error.code == ErrorCode.API_KEY_INVALID:
        print("API Key 无效")
```

## 调用日志查询

查询指定任务的完整调用日志，包括基本信息、输出文件列表、费用、请求参数和响应详情。需要用户级别 Token（来自手机号+密码登录）。

```python
from runninghub_sdk import RunningHubClient, bootstrap_env

# 从环境变量加载
bootstrap_env()
client = RunningHubClient.from_env()

# user_id 自动从 JWT 解码（登录返回的 access_token 中提取 sub）
import base64, json
payload = json.loads(base64.urlsafe_b64decode(client.api_key.split(".")[1] + "=="))
user_id = payload["sub"]

detail = client.get_call_log_detail(
    task_id="2066351966031925250",
    user_id=user_id,
)

# 基本信息
print(detail.basic_info.api_name)
print(detail.basic_info.task_status)
print(f"消耗: {detail.basic_info.coin_num} 金币，耗时 {detail.basic_info.duration} 秒")

# 输出文件
for output in detail.outputs:
    print(output.file_url)

# 请求参数（已自动解析为 dict）
import json
print(json.dumps(detail.request_info.api_request_params, indent=2, ensure_ascii=False))

# 响应详情
print(detail.response_info.status)
for result in detail.response_info.results:
    print(f"节点 {result.node_id}: {result.url}")

# 费用
print(f"消耗: {detail.cost_info.coin_num} 金币")

# 异步版本
async def main():
    async with RunningHubClient(api_key=client.api_key) as c:
        detail = await c.async_get_call_log_detail(
            task_id="...", user_id=user_id,
        )
```

也可以通过 `to_dict()` 将全部信息转为 JSON 友好格式：

```python
from runninghub_sdk import to_dict
import json

print(json.dumps(to_dict(detail), indent=2, ensure_ascii=False))
```

## 类型定义

SDK 暴露了全部 API 的请求/响应类型，便于静态检查和 IDE 补全：

```python
from runninghub_sdk import (
    # 任务
    CreateTaskResponse, TaskOutput, TaskStatus,
    NodeInput, ModelPricePreview, V2QueryResult,
    # 上传
    UploadResponseData, LoraUploadResponse,
    # 账户
    AccountStatus, ApiKeyInfo, QueueStatus, WebhookDetail,
    # 认证（用户 Token）
    RunningHubToken, AccessAuthResponse,
    UserInfoRequest, UserInfoResponse,
    MemberInfo, WalletInfo, ProductPackage,
    UserApiKeyRequest, UserApiKeyResponse,
    SharedApiInfo, ExclusiveApiInfo, BalanceInfo,
    # 门户
    PortalTemplateListRequest, PortalTemplateListResponse,
    PortalTemplateRecord, PortalTemplateOwner,
    WebappListRequest, WebappListResponse,
    # 输出历史
    OutputHistoryV2Request, OutputHistoryV2Response,
    # AI App
    AiAppRunRequest, AiAppApiCallDemo,
    PublicModelListRequest, PublicModelListResponse,
    # 调用日志
    CallLogDetailRequest, CallLogDetailResponse,
    CallLogBasicInfo, CallLogOutputItem,
    CallLogCostInfo, CallLogRequestInfo,
    CallLogResultItem, CallLogUsage,
    CallLogTaskUsageRecord, CallLogResponseInfo,
    # 工具函数
    bootstrap_env, get_env, get_required_env, to_dict,
)
```

## 更多示例

更多可运行示例见 [examples/](examples/) 目录，包含：

- 手机号密码登录 & 自动缓存 Token — [runninghub_login.py](examples/runninghub_login.py)
- 从缓存恢复客户端 & 自动续期 — [get_webapp_detail.py](examples/get_webapp_detail.py)
- 任务状态查询 & V2 查询 — [query_task_status.py](examples/query_task_status.py)
- 工作流详情获取 & JSON 解析 — [get_workflow_detail.py](examples/get_workflow_detail.py)
- AI App 详情查询 — [get_webapp_detail.py](examples/get_webapp_detail.py)
- 门户模板搜索 & Webapp 浏览 — [query_portal_api.py](examples/query_portal_api.py)
- 输出历史查询 & 并发下载 — [query_output_history_v2.py](examples/query_output_history_v2.py)
- 调用日志详情查询 — [task_detail.py](examples/task_detail.py)
- 历史文件批量下载 — [download_history_outputs.py](examples/download_history_outputs.py)

## 详细使用案例

下面给出几类更贴近实际业务的调用方式。完整脚本可继续参考 [examples/](examples/) 目录。

### 案例 1：先读取工作流结构，再按节点动态改参

适合你拿到一个现成 workflow，但还不确定提示词节点、采样节点、尺寸节点编号时使用。

```python
from runninghub_sdk import RunningHubClient, modify_nodes

with RunningHubClient(api_key="your-api-key") as client:
    workflow = client.get_workflow_json_parsed("your-workflow-id")

    print("可用节点:")
    for node_id, node_data in workflow.items():
        class_type = node_data.get("class_type", "unknown")
        inputs = list(node_data.get("inputs", {}).keys())
        print(node_id, class_type, inputs)

    modifier = (
        modify_nodes()
        .text("6", "a cinematic portrait, 85mm lens, natural light")
        .negative_text("7", "low quality, blurry, deformed")
        .seed("3", 20260510)
        .steps("3", 30)
        .cfg("3", 7.0)
        .size("5", 1024, 1536)
    )

    task = client.run_with_modifier("your-workflow-id", modifier)
    outputs = client.wait_for_completion(task.task_id)

    for output in outputs:
        print(output.file_url)
```

### 案例 2：AI App 场景下先上传素材，再运行应用

适合图生图、音频驱动、视频输入这类 AI App。流程一般是：获取节点示例、上传文件、把上传结果回填到节点、发起任务。

```python
from runninghub_sdk import RunningHubClient, modify_nodes

with RunningHubClient(api_key="your-api-key") as client:
    demo = client.get_ai_app_api_demo("1937084629516193794")
    print(demo.webapp_name)

    uploaded = client.upload_image("./assets/reference.png")

    modifier = (
        modify_nodes()
        .set("39", "image", uploaded["fileName"])
        .set("52", "prompt", "保持人物身份一致，改成电影海报风格")
        .set("37", "aspect_ratio", "3:4")
    )

    task = client.run_ai_app_with_modifier(
        "1937084629516193794",
        modifier,
    )
    outputs = client.wait_for_completion(task.task_id)

    for output in outputs:
        print(output.file_type, output.file_url)
```

### 案例 3：调用标准模型 API 前先做价格预估

适合标准模型 API 接口较多、计费需要前置校验的情况。推荐顺序：先 `preview_model_price()`，再 `run_model_api()`，最后走 V2 查询。

```python
from runninghub_sdk import RunningHubClient

endpoint = "rhart-image/f-2-dev/text-to-image"
payload = {
    "12##text": "a product poster of a premium coffee grinder on a marble table",
    "41##select": "4:3",
    "30##value": 1280,
    "29##value": 960,
    "43##file_type": "png",
}

with RunningHubClient(api_key="your-api-key") as client:
    price = client.preview_model_price(endpoint, payload)
    print("预估价格:", price.estimated_price, price.currency)

    task = client.run_model_api(endpoint, payload)
    result = client.wait_for_query_v2_completion(task.task_id)

    print("任务状态:", result.status)
    print("输出结果:", result.results)
```

### 案例 4：上线前做账户、队列和 webhook 自检

适合接入生产环境前检查账户余额、当前队列占用，以及排查 webhook 回调失败问题。

```python
from runninghub_sdk import RunningHubClient

with RunningHubClient(api_key="your-api-key") as client:
    account = client.get_account_status()
    print(account.remain_coins, account.api_type, account.api_type_enum)

    queue = client.get_queue_status()
    print(queue.api_key_type, queue.api_key_type_enum)
    print(queue.running_count, queue.queued_count)

    detail = client.get_webhook_detail("1904154698679771137")
    print(detail.callback_status, detail.callback_status_enum)
    print(detail.callback_response)
```

### 案例 5：查询任务调用日志详情

适合排查任务执行情况、查看输入输出和费用明细。需要用户级别 Token（手机号+密码登录）。

```python
from runninghub_sdk import RunningHubClient, bootstrap_env, to_dict
import json, base64

bootstrap_env()
client = RunningHubClient.from_env()

# 从 JWT 解码 user_id
payload = json.loads(base64.urlsafe_b64decode(client.api_key.split(".")[1] + "=="))
user_id = payload["sub"]

# 查询调用日志
detail = client.get_call_log_detail(
    task_id="2066351966031925250",
    user_id=user_id,
)

# 基本信息
info = detail.basic_info
print(f"接口: {info.api_name}，状态: {info.task_status}")
print(f"消耗: {info.coin_num} 金币 | 耗时: {info.duration} 秒")

# 输出文件列表
for out in detail.outputs:
    print(out.file_url)

# 请求参数（已自动解析为 dict）
print(json.dumps(detail.request_info.api_request_params, indent=2, ensure_ascii=False))

# 响应中的结果列表
for result in detail.response_info.results:
    print(f"节点 {result.node_id}: {result.output_type}")

# to_dict 一键转 JSON
print(json.dumps(to_dict(detail), indent=2, ensure_ascii=False))
```

## 💬 技术交流

欢迎加入 RunningHub Crew 社区，一起探讨 AI 工作流编排、MCP 协议与 agent 开发！

<p align="center">
  <a href="https://qm.qq.com/q/your-link-here" target="_blank">
    <table>
      <tr>
        <td align="center" width="280">
          <img src="img/e978_720.jpg" width="200" alt="QQ 群二维码" />
          <br>
          <sub><b>扫码加群</b></sub>
        </td>
        <td valign="middle">
          &nbsp;&nbsp;&nbsp;<b>🐧 QQ 交流群：484184109</b>
          <br><br>
          &nbsp;&nbsp;&nbsp;📢 问题反馈 · 功能建议 · 经验分享
          <br>
          &nbsp;&nbsp;&nbsp;🤖 第一时间获取项目更新动态
        </td>
      </tr>
    </table>
  </a>
</p>
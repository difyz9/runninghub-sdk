# RunningHub ComfyUI SDK 使用示例

## 安装依赖

```bash
pip install runninghub-sdk
```

如果你要直接验证当前仓库里的本地封装，而不是验证已经安装到环境中的旧版本，推荐在仓库根目录执行：

```bash
PYTHONPATH=src python examples/smoke_validate_sdk.py
```

两个案例脚本现在都会优先读取仓库根目录下的 `.env`，并且不会覆盖你已经显式导出的环境变量。

例如可以这样准备：

```bash
cp .env.example .env
```

然后按你的实际配置修改 [/.env.example](/Users/apple/opt/difyz_0329/0509/runninghub-sdk/.env.example) 里的值即可。

这个脚本会串行验证：账户状态、队列状态、公共模型列表、标准模型价格预估，以及可选的 AI App 示例读取。

需要的环境变量：

```bash
export RUNNINGHUB_API_KEY="your-api-key"
export RUNNINGHUB_AI_APP_ID="1937084629516193794"  # 可选
```

## SDK 冒烟验证案例

完整脚本见 [examples/smoke_validate_sdk.py](examples/smoke_validate_sdk.py)。这个案例的目标不是跑重任务，而是先验证 SDK 里最关键的一批封装是否可用。

## 真实工作流任务验证案例

如果你要验证 `run()`、`run_with_modifier()`、`get_workflow_json_parsed()` 和 `wait_for_completion()` 这一整条链路，可以直接运行 [examples/run_workflow_task.py](examples/run_workflow_task.py)。

最小运行方式只需要 API Key 和一个可直接运行的工作流 ID：

```bash
PYTHONPATH=src python examples/run_workflow_task.py
```

如果这两个值已经写进仓库根目录的 `.env`，就不需要再单独 `export`。

如果你还想顺带验证 `NodeModifier`，再补充对应节点 ID 和参数：

```bash
export RUNNINGHUB_PROMPT_NODE_ID="6"
export RUNNINGHUB_PROMPT_TEXT="a cinematic portrait, ultra detailed"
export RUNNINGHUB_NEGATIVE_PROMPT_NODE_ID="7"
export RUNNINGHUB_NEGATIVE_PROMPT_TEXT="blurry, low quality"
export RUNNINGHUB_SAMPLER_NODE_ID="3"
export RUNNINGHUB_SEED="12345"
export RUNNINGHUB_STEPS="28"
export RUNNINGHUB_CFG="7.0"
export RUNNINGHUB_SIZE_NODE_ID="5"
export RUNNINGHUB_WIDTH="1024"
export RUNNINGHUB_HEIGHT="1024"
PYTHONPATH=src python examples/run_workflow_task.py
```

脚本会先打印工作流前几个节点，方便你确认节点 ID，再提交任务并持续输出状态变化，最后打印生成结果 URL。

## 指定 AI App V2 任务案例

如果你要把某条 `curl /openapi/v2/run/ai-app/{id}` 请求直接换成 SDK 调用，可以参考 [examples/run_ai_app_v2_storyboard.py](examples/run_ai_app_v2_storyboard.py)。

这个脚本使用现有的 `run_model_api()` 调用：

```python
result = client.run_model_api(
    "/openapi/v2/run/ai-app/2016407933692678145",
    payload,
)
final_result = client.wait_for_query_v2_completion(result.task_id)
```

运行方式：

```bash
PYTHONPATH=src python examples/run_ai_app_v2_storyboard.py
```

如果你想换成别的 AI App ID，可以在 `.env` 或环境变量中设置：

```bash
export RUNNINGHUB_AI_APP_V2_ID="2016407933692678145"
```

## 基础使用

```python
from runninghub_sdk import RunningHubClient

# 创建客户端
client = RunningHubClient(api_key="your-api-key")

# 发起任务
task = client.run(
    workflow_id="your-workflow-id",
    node_info_list=[
        {"nodeId": "6", "fieldName": "text", "fieldValue": "a beautiful girl"},
        {"nodeId": "3", "fieldName": "seed", "fieldValue": 12345},
    ]
)

print(f"任务ID: {task.task_id}")

# 等待任务完成
outputs = client.wait_for_completion(
    task.task_id,
    poll_interval=3.0,  # 每3秒查询一次
    timeout=600.0,      # 10分钟超时
    on_status_change=lambda status: print(f"状态: {status}")
)

# 输出结果
for output in outputs:
    print(f"结果URL: {output.file_url}")

# 关闭客户端
client.close()
```

## AI App 使用

```python
from runninghub_sdk import RunningHubClient, modify_nodes

client = RunningHubClient(api_key="your-api-key")

# 读取 AI App 节点示例
demo = client.get_ai_app_api_demo("1937084629516193794")
print("AI App:", demo.webapp_name)
for node in demo.node_info_list:
    print(node.node_id, node.field_name, node.field_type, node.field_value)

# 修改 AI App 参数并运行
modifier = (
    modify_nodes()
    .set("52", "prompt", "把人物发型改成齐耳短发")
    .set("37", "aspect_ratio", "1:1")
)

task = client.run_ai_app_with_modifier("1937084629516193794", modifier)
outputs = client.wait_for_completion(task.task_id)

for output in outputs:
    print(output.file_url)

client.close()
```

## AI App 上传图片后运行

```python
from runninghub_sdk import RunningHubClient, modify_nodes

client = RunningHubClient(api_key="your-api-key")

uploaded = client.upload_image("input.png")

modifier = (
    modify_nodes()
    .set("39", "image", uploaded["fileName"])
    .set("52", "prompt", "保留构图，转成杂志封面风格")
)

task = client.run_ai_app_with_modifier("1937084629516193794", modifier)
outputs = client.wait_for_completion(task.task_id)

for output in outputs:
    print(output.file_url)

client.close()
```

## 异步 AI App 使用

```python
import asyncio

from runninghub_sdk import RunningHubClient, modify_nodes


async def main() -> None:
    async with RunningHubClient(api_key="your-api-key") as client:
        demo = await client.async_get_ai_app_api_demo("1937084629516193794")
        print(demo.webapp_name)

        modifier = modify_nodes().set("52", "prompt", "赛博朋克风格肖像")
        task = await client.async_run_ai_app_with_modifier(
            "1937084629516193794",
            modifier,
        )
        outputs = await client.async_wait_for_completion(task.task_id)

        for output in outputs:
            print(output.file_url)


asyncio.run(main())
```

## 获取公共模型列表

```python
from runninghub_sdk import RunningHubClient

client = RunningHubClient(api_key="your-api-key")

models = client.list_public_models(
    resource_type="UNET",
    resource_name="realDream",
    base_models=["Flux2-Klein-9B"],
    current=1,
    size=10,
)

print(f"总数: {models.total}, 当前页: {models.current}/{models.pages}")
for record in models.records:
    print(record.resource_name, record.resource_type, record.node_model_name)
    for tag in record.tags or []:
        print("  标签:", tag.name)
    for version in record.versions or []:
        print("  版本:", version.version, version.version_resource_name)

client.close()
```

## 异步获取公共模型列表

```python
import asyncio

from runninghub_sdk import RunningHubClient


async def main() -> None:
    async with RunningHubClient(api_key="your-api-key") as client:
        models = await client.async_list_public_models(
            resource_type="LORA",
            current=1,
            size=5,
        )
        for record in models.records:
            print(record.resource_name)


asyncio.run(main())
```

## 通用标准模型 API 调用

```python
from runninghub_sdk import RunningHubClient

client = RunningHubClient(api_key="your-api-key")

task = client.run_model_api(
    "rhart-image/f-2-dev/text-to-image",
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

client.close()
```

## 标准模型 API 价格预估

```python
from runninghub_sdk import RunningHubClient

client = RunningHubClient(api_key="your-api-key")

price = client.preview_model_price(
    "rhart-image/f-2-dev/text-to-image",
    {
        "12##text": "一张电影感狮子海报",
        "41##select": "9:16",
        "43##file_type": "png",
    },
)

print(price.estimated_price, price.currency, price.price_text)

client.close()
```

## 异步标准模型 API 调用

```python
import asyncio

from runninghub_sdk import RunningHubClient


async def main() -> None:
    async with RunningHubClient(api_key="your-api-key") as client:
        task = await client.async_run_model_api(
            "rhart-audio/text-to-audio/speech-2.8-hd",
            {
                "text": "Bonjour! How are you today?",
                "voice_id": "Wise_Woman",
                "enable_base64_output": False,
                "english_normalization": False,
            },
        )
        result = await client.async_wait_for_query_v2_completion(task.task_id)
        print(result.results)


asyncio.run(main())
```

## 获取账户信息和队列状态

```python
from runninghub_sdk import RunningHubClient

client = RunningHubClient(api_key="your-api-key")

account = client.get_account_status()
print(account.remain_coins, account.current_task_counts, account.api_type)

keys = client.list_api_keys()
for key in keys:
    print(key.key, key.status, key.created_at)

queue = client.get_queue_status()
print(queue.api_key_type, queue.running_count, queue.queued_count, queue.total_current_tasks)

client.close()
```

## 查询并重试 webhook 事件

```python
from runninghub_sdk import RunningHubClient

client = RunningHubClient(api_key="your-api-key")

detail = client.get_webhook_detail("1904154698679771137")
print(detail.id, detail.callback_status, detail.callback_response)

client.retry_webhook(detail.id, detail.webhook_url)

client.close()
```

## 异步账户与 webhook 接口

```python
import asyncio

from runninghub_sdk import RunningHubClient


async def main() -> None:
    async with RunningHubClient(api_key="your-api-key") as client:
        account = await client.async_get_account_status()
        print(account.remain_coins)

        queue = await client.async_get_queue_status()
        print(queue.running_count)

        detail = await client.async_get_webhook_detail("1904154698679771137")
        print(detail.callback_status)


asyncio.run(main())
```

## 场景案例：批量生成多组工作流结果

```python
from runninghub_sdk import RunningHubClient, modify_nodes

prompts = [
    "a product photo of a luxury watch on black velvet",
    "a product photo of a silver mechanical watch on marble",
    "a product photo of a dress watch under studio lighting",
]

with RunningHubClient(api_key="your-api-key") as client:
    for index, prompt in enumerate(prompts, start=1):
        modifier = (
            modify_nodes()
            .text("6", prompt)
            .seed("3", 1000 + index)
            .steps("3", 28)
        )
        task = client.run_with_modifier("your-workflow-id", modifier)
        outputs = client.wait_for_completion(task.task_id)
        print(f"第 {index} 组结果:")
        for output in outputs:
            print(output.file_url)
```

## 场景案例：先做价格预估，再调用标准模型

```python
from runninghub_sdk import RunningHubClient

endpoint = "rhart-image/f-2-dev/text-to-image"
payload = {
    "12##text": "a luxury perfume bottle in a cinematic commercial scene",
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
    print(result.results)
```

## 场景案例：根据账户与队列状态控制是否继续提交任务

```python
from runninghub_sdk import RunningHubClient, modify_nodes

with RunningHubClient(api_key="your-api-key") as client:
    account = client.get_account_status()
    queue = client.get_queue_status()

    print("余额:", account.remain_coins)
    print("队列:", queue.running_count, queue.queued_count)

    if int(queue.queued_count) > 10:
        raise RuntimeError("当前排队任务过多，稍后再提交")

    modifier = modify_nodes().text("6", "a cinematic travel poster")
    task = client.run_with_modifier("your-workflow-id", modifier)
    outputs = client.wait_for_completion(task.task_id)
    print(outputs)
```

## 场景案例：AI App 图像输入链路

```python
from runninghub_sdk import RunningHubClient, modify_nodes

with RunningHubClient(api_key="your-api-key") as client:
    uploaded = client.upload_image("./assets/model-input.png")

    modifier = (
        modify_nodes()
        .set("39", "image", uploaded["fileName"])
        .set("52", "prompt", "改成高级时尚杂志封面")
        .set("37", "aspect_ratio", "3:4")
    )

    task = client.run_ai_app_with_modifier("1937084629516193794", modifier)
    outputs = client.wait_for_completion(task.task_id)
    for output in outputs:
        print(output.file_url)
```

## 使用节点修改器（推荐）

```python
from runninghub_sdk import RunningHubClient, modify_nodes

client = RunningHubClient(api_key="your-api-key")

# 链式调用设置参数
modifier = (
    modify_nodes()
    .text("6", "a beautiful sunset over mountains")  # 设置提示词
    .seed("3", 98765)                                # 设置种子
    .steps("3", 25)                                  # 设置步数
    .cfg("3", 7.5)                                   # 设置CFG
    .size("5", 1024, 768)                           # 设置尺寸
    .sampler("3", "dpmpp_2m")                       # 设置采样器
)

# 使用修改器发起任务
task = client.run_with_modifier("your-workflow-id", modifier)
outputs = client.wait_for_completion(task.task_id)

for output in outputs:
    print(output.file_url)

client.close()
```

## 使用上下文管理器

```python
from runninghub_sdk import RunningHubClient

# 自动管理资源
with RunningHubClient(api_key="your-api-key") as client:
    task = client.run("your-workflow-id")
    outputs = client.wait_for_completion(task.task_id)
    # 退出with块时自动关闭客户端
```

## 上传图片并使用

```python
from runninghub_sdk import RunningHubClient, modify_nodes

client = RunningHubClient(api_key="your-api-key")

# 上传图片
with open("input.png", "rb") as f:
    result = client.upload_image(f)
    file_name = result["fileName"]

# 使用上传的图片
modifier = (
    modify_nodes()
    .image("10", file_name)                # LoadImage节点
    .text("6", "style transfer to anime")  # 设置提示词
)

task = client.run_with_modifier("your-workflow-id", modifier)
outputs = client.wait_for_completion(task.task_id)

client.close()
```

## 异步使用

```python
import asyncio
from runninghub_sdk import RunningHubClient, modify_nodes

async def main():
    # 异步上下文
    async with RunningHubClient(api_key="your-api-key") as client:
        # 创建修改器
        modifier = (
            modify_nodes()
            .text("6", "a beautiful landscape")
            .seed("3", 12345)
        )

        # 异步发起任务
        task = await client.async_run_with_modifier("your-workflow-id", modifier)

        # 异步等待完成
        outputs = await client.async_wait_for_completion(
            task.task_id,
            poll_interval=3.0,
            on_status_change=lambda s: print(f"状态: {s}")
        )

        for output in outputs:
            print(output.file_url)

asyncio.run(main())
```

## 错误处理

```python
from runninghub_sdk import (
    RunningHubClient,
    RunningHubError,
    TaskError,
    ErrorCode,
)
from runninghub_sdk.exceptions import TimeoutError as RHTimeoutError

client = RunningHubClient(api_key="your-api-key")

try:
    task = client.run("your-workflow-id")
    outputs = client.wait_for_completion(task.task_id)
except RHTimeoutError as e:
    print(f"任务超时: {e.task_id}")
except TaskError as e:
    print(f"任务失败: {e}")
    if e.failed_reason:
        print(f"失败原因: {e.failed_reason}")
except RunningHubError as e:
    if e.code == ErrorCode.API_KEY_INVALID:
        print("API Key无效")
    elif e.code == ErrorCode.TASK_NOT_FOUND:
        print("任务不存在")
    else:
        print(f"API错误 [{e.code}]: {e.message}")

client.close()
```

## 查看工作流结构

```python
from runninghub_sdk import RunningHubClient

client = RunningHubClient(api_key="your-api-key")

# 获取工作流JSON
workflow = client.get_workflow_json_parsed("your-workflow-id")

print("工作流节点:")
for node_id, node_data in workflow.items():
    print(f"  节点 {node_id}: {node_data.get('class_type', 'unknown')}")
    if 'inputs' in node_data:
        for input_name in node_data['inputs']:
            print(f"    - {input_name}")

client.close()
```

## 上传LoRA

```python
from runninghub_sdk import RunningHubClient, modify_nodes

client = RunningHubClient(api_key="your-api-key")

# 上传LoRA文件
lora_file_name = client.upload_lora("my-lora-name", "path/to/lora.safetensors")

# 使用上传的LoRA
modifier = (
    modify_nodes()
    .lora("20", lora_file_name)       # RHLoraLoader节点
    .lora_strength("20", 0.8)         # 设置强度
    .text("6", "styled portrait")
)

task = client.run_with_modifier("your-workflow-id", modifier)
outputs = client.wait_for_completion(task.task_id)

client.close()
```

## NodeModifier 可用方法

| 方法 | 说明 |
|------|------|
| `set(node_id, field_name, value)` | 通用设置 |
| `text(node_id, text)` | 设置提示词 |
| `negative_text(node_id, text)` | 设置负面提示词 |
| `seed(node_id, seed)` | 设置种子 |
| `steps(node_id, steps)` | 设置步数 |
| `cfg(node_id, cfg)` | 设置CFG |
| `size(node_id, width, height)` | 设置尺寸 |
| `sampler(node_id, name)` | 设置采样器 |
| `scheduler(node_id, name)` | 设置调度器 |
| `denoise(node_id, value)` | 设置去噪强度 |
| `image(node_id, file_name)` | 设置图片 |
| `video(node_id, file_name)` | 设置视频 |
| `audio(node_id, file_name)` | 设置音频 |
| `lora(node_id, file_name)` | 设置LoRA |
| `checkpoint(node_id, name)` | 设置模型 |
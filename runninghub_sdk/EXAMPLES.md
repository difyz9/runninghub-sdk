# RunningHub ComfyUI SDK 使用示例

## 安装依赖

```bash
pip install httpx
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
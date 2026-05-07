# RunningHub ComfyUI SDK

一个轻量级的 Python SDK，用于调用 RunningHub 的 ComfyUI API。

## 特性

- 支持同步和异步两种模式
- 使用 httpx 实现，性能优秀
- 完整的类型注解，IDE 友好
- 链式节点修改器，代码简洁
- 支持文件上传（图片、视频、音频、LoRA）
- 自动轮询等待任务完成

## 安装

```bash
pip install httpx
```

将 `runninghub_sdk` 目录复制到你的项目中即可使用。

## 快速开始

### 同步使用

```python
from runninghub_sdk import RunningHubClient, modify_nodes

# 创建客户端
with RunningHubClient(api_key="your-api-key") as client:
    # 使用节点修改器设置参数
    modifier = (
        modify_nodes()
        .text("6", "a beautiful sunset")
        .seed("3", 12345)
        .steps("3", 25)
    )

    # 发起任务
    task = client.run_with_modifier("workflow-id", modifier)

    # 等待完成
    outputs = client.wait_for_completion(task.task_id)

    # 输出结果
    for output in outputs:
        print(output.file_url)
```

### 异步使用

```python
import asyncio
from runninghub_sdk import RunningHubClient, modify_nodes

async def main():
    async with RunningHubClient(api_key="your-api-key") as client:
        modifier = modify_nodes().text("6", "a beautiful landscape")
        task = await client.async_run_with_modifier("workflow-id", modifier)
        outputs = await client.async_wait_for_completion(task.task_id)

        for output in outputs:
            print(output.file_url)

asyncio.run(main())
```

## API 方法

### 任务相关

| 同步方法 | 异步方法 | 说明 |
|---------|---------|------|
| `run()` | `async_run()` | 发起任务 |
| `run_with_modifier()` | `async_run_with_modifier()` | 使用修改器发起任务 |
| `get_status()` | `async_get_status()` | 查询状态 |
| `get_outputs()` | `async_get_outputs()` | 查询结果 |
| `wait_for_completion()` | `async_wait_for_completion()` | 等待完成 |
| `cancel()` | `async_cancel()` | 取消任务 |

### 上传相关

| 同步方法 | 异步方法 | 说明 |
|---------|---------|------|
| `upload_file()` | `async_upload_file()` | 上传文件 |
| `upload_image()` | `async_upload_image()` | 上传图片 |
| `upload_lora()` | `async_upload_lora()` | 上传LoRA |

### 工作流相关

| 同步方法 | 异步方法 | 说明 |
|---------|---------|------|
| `get_workflow_json()` | `async_get_workflow_json()` | 获取JSON字符串 |
| `get_workflow_json_parsed()` | `async_get_workflow_json_parsed()` | 获取JSON对象 |

## 节点修改器

NodeModifier 支持链式调用，简化参数设置：

```python
from runninghub_sdk import modify_nodes

modifier = (
    modify_nodes()
    .text("6", "a beautiful girl")      # CLIPTextEncode 节点
    .seed("3", 12345)                   # KSampler 节点
    .steps("3", 25)                     # 采样步数
    .cfg("3", 7.5)                      # CFG 值
    .size("5", 1024, 768)               # EmptyLatentImage 节点
    .sampler("3", "dpmpp_2m")           # 采样器
    .image("10", "uploaded-file.png")   # LoadImage 节点
)
```

### 可用方法

| 方法 | 说明 |
|------|------|
| `set(node_id, field_name, value)` | 通用设置 |
| `text(node_id, text)` | 设置提示词 |
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

## 错误处理

```python
from runninghub_sdk import (
    RunningHubError,
    TaskError,
    TimeoutError,
    ErrorCode,
)

try:
    outputs = client.wait_for_completion(task.task_id)
except TimeoutError as e:
    print(f"任务超时: {e.task_id}")
except TaskError as e:
    print(f"任务失败: {e.failed_reason}")
except RunningHubError as e:
    if e.code == ErrorCode.API_KEY_INVALID:
        print("API Key 无效")
```

## 类型定义

SDK 提供完整的类型定义：

```python
from runninghub_sdk import (
    TaskStatus,           # 任务状态枚举
    NodeInput,            # 节点输入
    CreateTaskResponse,   # 创建任务响应
    TaskOutput,           # 任务输出
    UploadResponseData,   # 上传响应
)
```

## 示例

更多示例请参考 [EXAMPLES.md](runninghub_sdk/EXAMPLES.md)。

## License

MIT
# RunningHub ComfyUI SDK

`runninghub-sdk` 是一个面向 RunningHub ComfyUI OpenAPI 的 Python SDK，支持任务创建、状态轮询、结果查询、文件上传，以及用链式 NodeModifier 修改工作流节点参数。

这个子目录可以直接作为 Python 包发布根目录使用，也可以单独进入目录后执行构建和上传命令发布到 PyPI。

## 特性

- 同时支持同步和异步调用
- 基于 `httpx`，接口简单，依赖精简
- 提供完整类型注解，适合 IDE 自动补全
- 支持 `NodeModifier` 链式修改节点输入
- 支持图片、视频、音频、LoRA 等文件上传
- 支持自动轮询等待任务完成

## 安装

```bash
pip install runninghub-sdk
```

如果你是在本仓库中本地开发，也可以进入 `runninghub_sdk` 目录后安装开发依赖：

```bash
pip install -e .[dev]
```

## 快速开始

### 同步调用

```python
from runninghub_sdk import RunningHubClient, modify_nodes

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

### 任务接口

| 同步方法 | 异步方法 | 说明 |
|---------|---------|------|
| `run()` | `async_run()` | 发起任务 |
| `run_with_modifier()` | `async_run_with_modifier()` | 使用修改器发起任务 |
| `get_status()` | `async_get_status()` | 查询任务状态 |
| `get_outputs()` | `async_get_outputs()` | 查询任务输出 |
| `wait_for_completion()` | `async_wait_for_completion()` | 轮询直到任务完成 |
| `query_v2()` | `async_query_v2()` | 调用 V2 查询接口 |

### 文件上传

| 同步方法 | 异步方法 | 说明 |
|---------|---------|------|
| `upload_file()` | `async_upload_file()` | 上传通用文件 |
| `upload_image()` | `async_upload_image()` | 上传图片 |
| `upload_lora()` | `async_upload_lora()` | 上传 LoRA |

### 工作流读取

| 同步方法 | 异步方法 | 说明 |
|---------|---------|------|
| `get_workflow_json()` | `async_get_workflow_json()` | 获取工作流 JSON 字符串 |
| `get_workflow_json_parsed()` | `async_get_workflow_json_parsed()` | 获取解析后的工作流对象 |

## NodeModifier

`NodeModifier` 用于用链式 API 构造 `node_info_list`，让工作流参数修改更直观。

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

## 类型定义

SDK 暴露了常用类型，便于静态检查和 IDE 补全：

```python
from runninghub_sdk import (
    CreateTaskResponse,
    NodeInput,
    TaskOutput,
    TaskStatus,
    UploadResponseData,
)
```

## 更多示例

更多可运行示例见 [EXAMPLES.md](EXAMPLES.md)。

## 在 `runninghub_sdk` 目录发布到 PyPI

进入当前目录后执行：

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

如果你使用 API Token，推荐先设置环境变量：

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-xxxxxxxxxxxxxxxxxxxx
python -m twine upload dist/*
```

发布前建议先上传到 TestPyPI 做一次验证：

```bash
python -m twine upload --repository testpypi dist/*
```

## License

MIT
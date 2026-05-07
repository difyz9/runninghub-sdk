# NodeModifier 使用说明

## 概述

`NodeModifier` 是 RunningHub SDK 提供的节点参数修改器，支持链式调用，用于构建 `nodeInfoList` 参数。

## 导入

```python
from runninghub_sdk import modify_nodes
```

## 基本用法

### 1. 通用方法 `set()`

修改任意节点的任意字段：

```python
modifier = modify_nodes()

# 修改节点100的text字段
modifier.set("100", "text", "a beautiful girl")

# 修改节点3的seed字段
modifier.set("3", "seed", 12345)

# 修改节点3的steps字段
modifier.set("3", "steps", 25)
```

**参数说明：**

| 参数 | 类型 | 说明 |
|-----|------|------|
| `node_id` | str | 节点ID |
| `field_name` | str | 字段名称 |
| `field_value` | str/int/float/bool | 字段值 |

### 2. 链式调用

```python
modifier = (
    modify_nodes()
    .set("100", "text", "a beautiful girl")
    .set("3", "seed", 12345)
    .set("3", "steps", 25)
    .set("5", "width", 1024)
    .set("5", "height", 768)
)
```

### 3. 获取修改列表

```python
# 获取 NodeInput 对象列表
node_list = modifier.to_list()

# 获取字典列表（可直接用于API）
dict_list = modifier.to_dict_list()
# 输出: [{"nodeId": "100", "fieldName": "text", "fieldValue": "..."}, ...]
```

## 便捷方法

SDK 为常用操作提供了快捷方法：

### 提示词相关

```python
# 设置正向提示词
modifier.text("6", "a beautiful sunset over mountains")

# 设置负面提示词
modifier.negative_text("7", "ugly, blurry, low quality")
```

### 采样器相关

```python
# 设置种子
modifier.seed("3", 12345)

# 设置步数
modifier.steps("3", 25)

# 设置CFG值
modifier.cfg("3", 7.5)

# 设置采样器
modifier.sampler("3", "dpmpp_2m")

# 设置调度器
modifier.scheduler("3", "karras")

# 设置去噪强度（图生图）
modifier.denoise("3", 0.6)
```

### 尺寸相关

```python
# 设置图片尺寸
modifier.size("5", 1024, 768)

# 设置尺寸和批次大小
modifier.size("5", 1024, 768, batch_size=4)
```

### 文件相关

```python
# 设置图片（LoadImage节点）
modifier.image("10", "api/xxx.png")

# 设置视频（LoadVideo节点）
modifier.video("7", "api/xxx.mp4")

# 设置音频（LoadAudio节点）
modifier.audio("2", "api/xxx.mp3")
```

### LoRA相关

```python
# 设置LoRA文件
modifier.lora("20", "api-lora-cn/xxx.safetensors")

# 设置LoRA强度
modifier.lora_strength("20", 0.8)
```

### 模型相关

```python
# 设置模型检查点
modifier.checkpoint("4", "model.safetensors")
```

## 完整方法列表

| 方法 | 等价的set调用 | 说明 |
|------|--------------|------|
| `set(id, name, value)` | - | 通用方法，可修改任何字段 |
| `text(id, text)` | `.set(id, "text", text)` | 设置提示词 |
| `negative_text(id, text)` | `.set(id, "text", text)` | 设置负面提示词 |
| `seed(id, seed)` | `.set(id, "seed", seed)` | 设置种子 |
| `steps(id, steps)` | `.set(id, "steps", steps)` | 设置步数 |
| `cfg(id, cfg)` | `.set(id, "cfg", cfg)` | 设置CFG值 |
| `size(id, w, h)` | `.set(id, "width", w).set(id, "height", h)` | 设置尺寸 |
| `sampler(id, name)` | `.set(id, "sampler_name", name)` | 设置采样器 |
| `scheduler(id, name)` | `.set(id, "scheduler", name)` | 设置调度器 |
| `denoise(id, value)` | `.set(id, "denoise", value)` | 设置去噪强度 |
| `image(id, file)` | `.set(id, "image", file)` | 设置图片 |
| `video(id, file)` | `.set(id, "video", file)` | 设置视频 |
| `audio(id, file)` | `.set(id, "audio", file)` | 设置音频 |
| `lora(id, file)` | `.set(id, "lora_name", file)` | 设置LoRA |
| `lora_strength(id, strength)` | `.set(id, "strength_model", strength)` | 设置LoRA强度 |
| `checkpoint(id, name)` | `.set(id, "ckpt_name", name)` | 设置模型 |

## 如何确定字段名

### 方法1：查看workflow JSON

```python
from runninghub_sdk import RunningHubClient

client = RunningHubClient(api_key="your-api-key")

# 获取workflow结构
workflow = client.get_workflow_json_parsed("workflow-id")

# 查看节点100的所有可配置字段
print(workflow["100"]["inputs"])
# 输出: {"text": "", "clip": ["4", 1]}
# 这表示节点100有一个 "text" 字段可以修改
```

### 方法2：在RunningHub平台查看

1. 登录 RunningHub 平台
2. 打开 workflow 编辑页面
3. 点击目标节点
4. 查看参数面板中的字段名称

## 使用示例

### 文本生图

```python
from runninghub_sdk import RunningHubClient, modify_nodes

client = RunningHubClient(api_key="your-api-key")

modifier = (
    modify_nodes()
    .text("6", "a beautiful girl in a flower garden")
    .seed("3", 12345)
    .steps("3", 25)
    .cfg("3", 7.5)
    .size("5", 1024, 768)
)

task = client.run_with_modifier("workflow-id", modifier)
outputs = client.wait_for_completion(task.task_id)
```

### 图生图

```python
# 上传图片
with open("input.png", "rb") as f:
    result = client.upload_image(f)

modifier = (
    modify_nodes()
    .image("10", result["fileName"])  # LoadImage节点
    .text("6", "anime style, beautiful girl")
    .denoise("3", 0.6)  # 去噪强度，控制重绘程度
    .seed("3", 12345)
)

task = client.run_with_modifier("workflow-id", modifier)
```

### 使用LoRA

```python
# 上传LoRA
lora_file = client.upload_lora("my-lora", "lora.safetensors")

modifier = (
    modify_nodes()
    .lora("20", lora_file)
    .lora_strength("20", 0.8)
    .text("6", "styled portrait")
)

task = client.run_with_modifier("workflow-id", modifier)
```

### 修改任意字段

```python
# 假设节点100有一个自定义字段 "custom_prompt"
modifier = (
    modify_nodes()
    .set("100", "custom_prompt", "special value")
    .set("100", "another_field", 42)
    .set("3", "seed", 99999)
)

task = client.run_with_modifier("workflow-id", modifier)
```

## 其他操作

### 批量添加

```python
from runninghub_sdk import NodeInput

modifications = [
    NodeInput(node_id="6", field_name="text", field_value="test1"),
    NodeInput(node_id="3", field_name="seed", field_value=123),
]

modifier = modify_nodes().add_many(modifications)
```

### 清空修改

```python
modifier = modify_nodes().text("6", "test").seed("3", 123)
print(len(modifier))  # 输出: 2

modifier.clear()
print(len(modifier))  # 输出: 0
```

### 查看修改数量

```python
modifier = modify_nodes().text("6", "test").seed("3", 123)
print(len(modifier))  # 输出: 2
print(repr(modifier))  # 输出: NodeModifier(modifications=2)
```

## 注意事项

1. **节点ID是字符串**：所有方法的 `node_id` 参数都是字符串类型
2. **字段名区分大小写**：确保字段名与workflow中的定义一致
3. **链式调用**：所有方法都返回 `self`，支持链式调用
4. **类型匹配**：`field_value` 的类型应与字段期望的类型一致

## 常见问题

### Q: 如何知道节点ID？

A: 在RunningHub平台的workflow编辑器中，点击节点可以看到节点ID。或者在workflow JSON中，键就是节点ID。

### Q: 字段名写错了会怎样？

A: API会返回错误，提示字段不存在。建议先用 `get_workflow_json_parsed()` 查看字段名。

### Q: 可以修改多个节点的同一个字段吗？

A: 可以，每个修改都是独立的：

```python
modifier = (
    modify_nodes()
    .text("6", "positive prompt")
    .text("7", "negative prompt")
)
```

### Q: 便捷方法和set方法可以混用吗？

A: 可以，它们是等价的：

```python
# 这两种写法效果相同
modifier = modify_nodes().text("6", "test")
modifier = modify_nodes().set("6", "text", "test")
```
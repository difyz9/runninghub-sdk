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

## Flux.1 Krea Dev 文生图 AI App

如果你要把一条 `curl /openapi/v2/run/ai-app/1950946384071557121` 的文生图请求直接换成 SDK 调用，可以参考 [examples/txt2img/run_ai_app_flux_krea_text_to_image.py](examples/txt2img/run_ai_app_flux_krea_text_to_image.py)。

这个脚本默认已经内置了你提供的三个节点：

- 节点 `53`：文生图提示词
- 节点 `52`：图像比例
- 节点 `56`：批量生成数量

运行方式：

```bash
python examples/txt2img/run_ai_app_flux_krea_text_to_image.py
```

如果你想临时覆盖提示词、比例或批量数，可以直接传参数：

```bash
python examples/txt2img/run_ai_app_flux_krea_text_to_image.py \
    --prompt "a cinematic portrait of a cyberpunk biker woman in neon city night" \
    --aspect-ratio "9:16 portrait 768x1344" \
    --batch-size 2
```

也支持通过环境变量覆盖默认值：

```bash
export RUNNINGHUB_FLUX_KREA_PROMPT="your prompt"
export RUNNINGHUB_FLUX_KREA_ASPECT_RATIO="1:1 square 1024x1024"
export RUNNINGHUB_FLUX_KREA_BATCH_SIZE="1"
python examples/txt2img/run_ai_app_flux_krea_text_to_image.py
```

## 指定 Workflow V2 任务案例

如果这是普通 RunningHub 工作流，更推荐直接走 SDK 的任务流接口，可以参考 [examples/run_workflow_v2_qwen_camera.py](examples/run_workflow_v2_qwen_camera.py)。

这个脚本实际使用的是：

```python
task = client.run(
    workflow_id="2051509626218270722",
    node_info_list=[],
    add_metadata=True,
    instance_type="default",
    use_personal_queue=False,
)
outputs = client.wait_for_completion(task.task_id)
```

运行方式：

```bash
python examples/run_workflow_v2_qwen_camera.py
```

如果你想换成别的 workflow ID，可以在 `.env` 或环境变量中设置：

```bash
export RUNNINGHUB_QWEN_CAMERA_WORKFLOW_ID="2051509626218270722"
```

如果你要直接验证 `NodeModifier`，这个脚本也已经内置了该工作流的一组默认节点：

- 正向提示词节点：`147`
- 负向提示词节点：`143`
- 采样器节点：`137`
- 输入图片节点：`106`

例如：

```bash
export RUNNINGHUB_QWEN_CAMERA_POSITIVE_PROMPT="multi angle camera control, cinematic lighting"
export RUNNINGHUB_QWEN_CAMERA_NEGATIVE_PROMPT="blurry, low quality"
export RUNNINGHUB_QWEN_CAMERA_SEED="12345"
export RUNNINGHUB_QWEN_CAMERA_STEPS="28"
export RUNNINGHUB_QWEN_CAMERA_CFG="7.0"
export RUNNINGHUB_QWEN_CAMERA_IMAGE_PATH="./assets/input.png"
python examples/run_workflow_v2_qwen_camera.py
```

脚本会自动上传图片并把返回的 `fileName` 回填到 `LoadImage` 节点，然后再提交任务。

## 豆包 Seedance 文生视频案例

如果你要调用豆包 + Seedance 1.5 Pro 文生视频工作流，可以直接参考 [examples/run_workflow_doubao_seedance_video.py](examples/run_workflow_doubao_seedance_video.py)。

这个脚本使用 SDK 任务流接口：

```python
task = client.run(
    workflow_id="2004066004755988481",
    node_info_list=[],
    add_metadata=True,
    instance_type="default",
    use_personal_queue=False,
)
outputs = client.wait_for_completion(task.task_id)
```

运行方式：

```bash
python examples/run_workflow_doubao_seedance_video.py
```

如果你想换成别的 workflow ID，可以在 `.env` 或环境变量中设置：

```bash
export RUNNINGHUB_DOUBAO_VIDEO_WORKFLOW_ID="2004066004755988481"
```

## DeepSeek 生成文案后驱动豆包视频

如果你希望先用 DeepSeek 生成视频脚本文案，保存到本地 JSON，再把其中的 `video_prompt` 自动喂给豆包工作流，可以直接运行 [examples/run_doubao_video_from_deepseek_prompt.py](examples/run_doubao_video_from_deepseek_prompt.py)。

这条链路会同时依赖两类 key：

- `RUNNINGHUB_API_KEY`：RunningHub OpenAPI key，只用于 SDK 提交工作流任务
- `DEEPSEEK_API_KEY`：DeepSeek LLM key，只用于生成视频文案 JSON

这两个 key 不是同一个服务的凭证，不能互相替代。

这个脚本会执行三步：

1. 调用 [examples/deepseek_video_prompt.py](examples/deepseek_video_prompt.py) 生成结构化 JSON
2. 保存到本地 `outputs/deepseek_doubao_video_prompt.json`
3. 读取其中的 `video_prompt`，通过 SDK 的 `run()` 提交到 `2004066004755988481`

运行方式：

```bash
python examples/run_doubao_video_from_deepseek_prompt.py
```

最小配置建议：

```bash
cp .env.example .env
```

然后至少确认这两个值已经填对：

```dotenv
RUNNINGHUB_API_KEY=your-runninghub-key
DEEPSEEK_API_KEY=your-deepseek-key
```

默认回填的是豆包工作流里节点 `1` 的 `prompt` 字段。如果你的工作流节点有变化，可以在 `.env` 里改：

```bash
export RUNNINGHUB_DOUBAO_VIDEO_PROMPT_NODE_ID="1"
```

## DeepSeek 生成首尾帧视频提示词

如果你要先用 DeepSeek 生成首帧、尾帧以及首尾帧视频工作流可直接使用的提示词，可以运行 [examples/first2last/deepseek_first2last_prompt.py](examples/first2last/deepseek_first2last_prompt.py)。

这个脚本会返回并保存一份结构化 JSON，默认包含这些字段：

- `first_frame_prompt`：首帧图片提示词
- `last_frame_prompt`：尾帧图片提示词
- `transition_prompt`：从首帧过渡到尾帧的镜头和动作描述
- `positive_prompt`：可直接喂给首尾帧视频工作流的正向提示词
- `negative_prompt`：负向提示词

运行方式：

```bash
python examples/first2last/deepseek_first2last_prompt.py
```

也可以直接在命令行里覆盖主题、风格和镜头语言：

```bash
python examples/first2last/deepseek_first2last_prompt.py \
    --idea "A white fox spirit walks out of a winter shrine and transforms into a girl under lantern light." \
    --style "cinematic, fantasy, ultra detailed, elegant lighting" \
    --camera "wide shot that transitions into a medium close-up"
```

脚本默认会把 JSON 保存到 `outputs/deepseek_first2last_prompt.json`。如果只想换模型或输出路径，也可以追加：

```bash
python examples/first2last/deepseek_first2last_prompt.py --model deepseek-chat --output outputs/custom_first2last_prompt.json
```

## Seedance 2.0 图生视频案例

如果你要调用 Seedance 2.0 图生视频工作流，可以参考 [examples/run_workflow_seedance_image_to_video.py](examples/run_workflow_seedance_image_to_video.py)。

这个脚本默认对应工作流 `2037036284312559617`，底层还是走 SDK 的任务流接口：

```python
task = client.run(
    workflow_id="2037036284312559617",
    node_info_list=[],
    add_metadata=True,
    instance_type="default",
    use_personal_queue=False,
)
outputs = client.wait_for_completion(task.task_id)
```

同时它也支持可选的图生视频参数覆盖：

- `RUNNINGHUB_SEEDANCE_FIRST_FRAME_PATH`：首帧图片，本地文件会先上传再回填到 `LoadImage` 节点 `2`
- `RUNNINGHUB_SEEDANCE_LAST_FRAME_PATH`：尾帧图片，本地文件会先上传再回填到 `LoadImage` 节点 `3`
- `RUNNINGHUB_SEEDANCE_PROMPT`：视频描述词，回填到主节点 `1/prompt`
- `RUNNINGHUB_SEEDANCE_RESOLUTION`、`RUNNINGHUB_SEEDANCE_DURATION`、`RUNNINGHUB_SEEDANCE_RATIO`
- `RUNNINGHUB_SEEDANCE_SEED`、`RUNNINGHUB_SEEDANCE_GENERATE_AUDIO`

运行方式：

```bash
python examples/run_workflow_seedance_image_to_video.py
```

如果你只想按默认工作流参数直接跑，不需要额外设置 `nodeInfoList`。

如果你要传入首尾帧和 prompt，可以这样：

```bash
export RUNNINGHUB_SEEDANCE_FIRST_FRAME_PATH="./examples/img/first.png"
export RUNNINGHUB_SEEDANCE_LAST_FRAME_PATH="./examples/img/last.png"
export RUNNINGHUB_SEEDANCE_PROMPT="epic temple knights, cinematic camera movement, realistic lighting"
python examples/run_workflow_seedance_image_to_video.py
```

## Wan 2.2 首尾帧视频案例

如果你要调用首尾帧生成视频工作流 `2011275998205054977`，可以直接运行 [examples/first2last/run_workflow_wan22_first2last_video.py](examples/first2last/run_workflow_wan22_first2last_video.py)。

这个脚本默认也支持最原始的空 `nodeInfoList` 提交方式，对应你给出的 curl：

```python
task = client.run(
    workflow_id="2011275998205054977",
    node_info_list=[],
    add_metadata=True,
    instance_type="default",
    use_personal_queue=False,
)
outputs = client.wait_for_completion(task.task_id)
```

运行方式：

```bash
python examples/first2last/run_workflow_wan22_first2last_video.py
```

如果你要把本地首帧和尾帧上传后再提交，可以设置：

- `RUNNINGHUB_FIRST2LAST_FIRST_FRAME_PATH`：回填到远端工作流 `ImageLoader` 节点 `43`
- `RUNNINGHUB_FIRST2LAST_LAST_FRAME_PATH`：回填到远端工作流 `ImageLoader` 节点 `44`
- `RUNNINGHUB_FIRST2LAST_POSITIVE_PROMPT`：回填到 `WanVideoTextEncode` 节点 `30/positive_prompt`
- `RUNNINGHUB_FIRST2LAST_NEGATIVE_PROMPT`：回填到 `WanVideoTextEncode` 节点 `30/negative_prompt`
- `RUNNINGHUB_FIRST2LAST_SEED`：同时覆盖两个采样器节点 `27` 和 `28` 的 `seed`

例如：

```bash
export RUNNINGHUB_FIRST2LAST_FIRST_FRAME_PATH="./examples/img/first.png"
export RUNNINGHUB_FIRST2LAST_LAST_FRAME_PATH="./examples/img/last.png"
export RUNNINGHUB_FIRST2LAST_POSITIVE_PROMPT="cinematic temple corridor, slow push-in, coherent motion, realistic lighting"
export RUNNINGHUB_FIRST2LAST_NEGATIVE_PROMPT="blurry, low quality, overexposed, static frame, bad anatomy"
export RUNNINGHUB_FIRST2LAST_SEED="12345"
python examples/first2last/run_workflow_wan22_first2last_video.py
```

## DaSiWa 首尾帧视频案例

如果你要调用 DaSiWa 版首尾帧视频工作流 `2008457370875207681`，可以直接运行 [examples/first02/run_workflow_dasiwa_first2last_video.py](examples/first02/run_workflow_dasiwa_first2last_video.py)。

这个脚本默认同样支持你给出的最小请求，也就是空 `nodeInfoList` 直接提交：

```python
task = client.run(
    workflow_id="2008457370875207681",
    node_info_list=[],
    add_metadata=True,
    instance_type="default",
    use_personal_queue=False,
)
outputs = client.wait_for_completion(task.task_id)
```

运行方式：

```bash
python examples/first02/run_workflow_dasiwa_first2last_video.py
```

这个工作流的真实远端节点里：

- 首帧图片是 `LoadImage` 节点 `110`
- 尾帧图片是 `LoadImage` 节点 `111`
- 手动提示词文本是 `CR Text` 节点 `131`
- `ImpactSwitch` 节点 `130` 默认走 LLM 自动生成提示词；如果你设置 `RUNNINGHUB_FIRST02_PROMPT`，脚本会自动把它切到手动提示词
- 负面提示词是节点 `67`
- 时长秒数是节点 `101`
- 两段采样种子是节点 `79` 和 `80`

例如：

```bash
export RUNNINGHUB_FIRST02_FIRST_FRAME_PATH="./examples/img/ComfyUI_00001_lemgi_1778400809.png"
export RUNNINGHUB_FIRST02_LAST_FRAME_PATH="./examples/img/ComfyUI_00002_rfcrc_1778400809.png"
export RUNNINGHUB_FIRST02_PROMPT="anime warrior transforms with intense purple energy, cinematic mid shot, dynamic smoke and lightning"
export RUNNINGHUB_FIRST02_NEGATIVE_PROMPT="blurry, low quality, static pose, extra limbs, distorted hands"
export RUNNINGHUB_FIRST02_DURATION_SECONDS="5"
export RUNNINGHUB_FIRST02_SEED="12345"
python examples/first02/run_workflow_dasiwa_first2last_video.py
```

## 最受欢迎美学文生图案例

如果你要调用文生图工作流 `2037071836214730753`，可以参考 [examples/run_workflow_popular_aesthetics_text_to_image.py](examples/run_workflow_popular_aesthetics_text_to_image.py)。

这个脚本默认直接复刻你给的请求体，底层仍然走 SDK 的任务流接口：

```python
task = client.run(
    workflow_id="2037071836214730753",
    node_info_list=[],
    add_metadata=True,
    instance_type="default",
    use_personal_queue=False,
)
outputs = client.wait_for_completion(task.task_id)
```

脚本另外支持几项已经对齐过节点 ID 的可选覆盖参数：

- `RUNNINGHUB_POPULAR_AESTHETICS_PROMPT`：正向提示词，默认回填到节点 `57/text`
- `RUNNINGHUB_POPULAR_AESTHETICS_NEGATIVE_PROMPT`：负向提示词，默认回填到节点 `43/text`
- `RUNNINGHUB_POPULAR_AESTHETICS_SEED`、`RUNNINGHUB_POPULAR_AESTHETICS_STEPS`、`RUNNINGHUB_POPULAR_AESTHETICS_CFG`
- `RUNNINGHUB_POPULAR_AESTHETICS_SAMPLER_NAME`、`RUNNINGHUB_POPULAR_AESTHETICS_SCHEDULER`
- `RUNNINGHUB_POPULAR_AESTHETICS_WIDTH`、`RUNNINGHUB_POPULAR_AESTHETICS_HEIGHT`、`RUNNINGHUB_POPULAR_AESTHETICS_BATCH_SIZE`

运行方式：

```bash
python examples/run_workflow_popular_aesthetics_text_to_image.py
```

如果你只想按工作流默认参数直接跑，不需要额外设置 `nodeInfoList`。

如果你要临时覆盖 prompt 和出图尺寸，可以这样：

```bash
export RUNNINGHUB_POPULAR_AESTHETICS_PROMPT="JK short skirt, camisole top, cinematic fashion photography, soft light"
export RUNNINGHUB_POPULAR_AESTHETICS_NEGATIVE_PROMPT="blurry, low quality, bad anatomy"
export RUNNINGHUB_POPULAR_AESTHETICS_WIDTH="1088"
export RUNNINGHUB_POPULAR_AESTHETICS_HEIGHT="1920"
python examples/run_workflow_popular_aesthetics_text_to_image.py
```

## AI 漫剧角色卡制作案例

如果你要调用角色卡制作工作流 `2051599273845895169`，可以参考 [examples/ai2role/run_workflow_ai2role_character_card.py](examples/ai2role/run_workflow_ai2role_character_card.py)。

这个脚本默认直接复刻你给的请求体，底层仍然走 SDK 的任务流接口：

```python
task = client.run(
    workflow_id="2051599273845895169",
    node_info_list=[],
    add_metadata=True,
    instance_type="default",
    use_personal_queue=False,
)
outputs = client.wait_for_completion(task.task_id)
```

它额外支持几项已经对齐过节点 ID 的可选覆盖参数：

- `RUNNINGHUB_AI2ROLE_CHARACTER_TEXT`：角色描述文本，默认写到节点 `6/text`
- `RUNNINGHUB_AI2ROLE_REFERENCE_IMAGE_PATH`：可选参考图，会先上传后回填到节点 `9/image`
- `RUNNINGHUB_AI2ROLE_ASPECT_RATIO`、`RUNNINGHUB_AI2ROLE_RESOLUTION`
- `RUNNINGHUB_AI2ROLE_SEED`

运行方式：

```bash
python examples/ai2role/run_workflow_ai2role_character_card.py
```

如果只想按工作流默认参数直接跑，不需要额外设置 `nodeInfoList`。

如果你要覆盖角色描述和参考图，可以这样：

```bash
export RUNNINGHUB_AI2ROLE_CHARACTER_TEXT="姓名：霞\n年龄：22 岁\n性别：女\n风格：国漫\n外貌：冷白皮，清冷五官，黑长直，暗黑极简长裙"
export RUNNINGHUB_AI2ROLE_REFERENCE_IMAGE_PATH="./examples/ai2role/reference.png"
python examples/ai2role/run_workflow_ai2role_character_card.py
```

## DeepSeek 设计角色提示词

如果你想先用 DeepSeek 设计角色，并生成可直接用于角色卡工作流的提示词 JSON，可以运行 [examples/ai2role/deepseek_character_prompt.py](examples/ai2role/deepseek_character_prompt.py)。

这个脚本会返回一份结构化角色设计数据，包含：

- `character_card_input`：直接可用于角色卡工作流的角色设定文本
- `visual_prompt`：角色形象提示词
- `color_palette_prompt`：配色和光影提示词
- `negative_prompt`：负向提示词

运行方式：

```bash
python examples/ai2role/deepseek_character_prompt.py
```

如果要自定义角色方向：

```bash
python examples/ai2role/deepseek_character_prompt.py \
    --idea "设计一位危险又优雅的女刺客角色" \
    --style "国漫，成熟角色设计，电影级角色海报" \
    --world "架空古风奇幻"
```

## DeepSeek 生成后直接驱动角色卡工作流

如果你希望让 DeepSeek 先生成角色设定，再自动提交到角色卡工作流，可以运行 [examples/ai2role/run_ai2role_character_card_from_deepseek_prompt.py](examples/ai2role/run_ai2role_character_card_from_deepseek_prompt.py)。

这条链路会执行三步：

1. 调用 DeepSeek 生成结构化角色设计 JSON
2. 保存到本地 `outputs/deepseek_ai2role_character_prompt.json`
3. 读取其中的 `character_card_input`、`visual_prompt`、`color_palette_prompt` 和 `negative_prompt`，组合后通过 SDK 提交到角色卡工作流

运行方式：

```bash
python examples/ai2role/run_ai2role_character_card_from_deepseek_prompt.py
```

这条链路同样依赖两类 key：

- `RUNNINGHUB_API_KEY`：RunningHub OpenAPI key，用于提交角色卡工作流
- `DEEPSEEK_API_KEY`：DeepSeek key，用于生成角色设计 JSON

## DeepSeek 分镜制作案例

如果你想先用 DeepSeek 生成分镜提示词，再直接驱动一键漫剧分镜流工作流 `2013908081847046145`，可以使用 [examples/fenjing/run_fenjing_from_deepseek_prompt.py](examples/fenjing/run_fenjing_from_deepseek_prompt.py)。

这个案例会优先读取 `examples/fenjing/.env`，然后执行三步：

1. 调用 DeepSeek 生成结构化分镜 JSON
2. 把提示词 JSON 保存到 `examples/fenjing/outputs/`
3. 提交分镜工作流，并把生成图片下载到 `examples/fenjing/downloads/`

其中单独的 DeepSeek 生成脚本是 [examples/fenjing/deepseek_storyboard_prompt.py](examples/fenjing/deepseek_storyboard_prompt.py)。

运行方式：

```bash
python examples/fenjing/run_fenjing_from_deepseek_prompt.py
```

如果你只想先看 DeepSeek 生成的分镜提示词 JSON，可以运行：

```bash
python examples/fenjing/deepseek_storyboard_prompt.py
```

这个案例默认会把 DeepSeek 生成的分镜文本回填到工作流里的两个 `CR Prompt Text` 节点：`343` 和 `411`。如果你的工作流副本节点不同，可以通过 `RUNNINGHUB_FENJING_PROMPT_NODE_IDS` 覆盖。

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
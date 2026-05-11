export RUNNINGHUB_POPULAR_AESTHETICS_PROMPT="JK short skirt, camisole top, cinematic fashion photography, soft light"
export RUNNINGHUB_POPULAR_AESTHETICS_NEGATIVE_PROMPT="blurry, low quality, bad anatomy"
export RUNNINGHUB_POPULAR_AESTHETICS_WIDTH="1088"
export RUNNINGHUB_POPULAR_AESTHETICS_HEIGHT="1920"
python examples/run_workflow_popular_aesthetics_text_to_image.py

如果任务已经跑完，只想把固定输出图片直接下载到本地，可以在当前目录运行：

```bash
python download_popular_aesthetics_images.py
```

默认会下载到 `examples/txt2img/downloads/popular_aesthetics/`，也可以自定义目录：

```bash
python download_popular_aesthetics_images.py --output-dir ./downloads/result-images
```
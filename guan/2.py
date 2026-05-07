
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from runninghub_sdk import RunningHubClient, modify_nodes

API_KEY = "c4dbb7471a1649219a6a3cbe7827df47"
WORKFLOW_ID = "2051599273845895169"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def save_outputs(outputs, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=60.0) as client:
        for index, output in enumerate(outputs, start=1):
            parsed = urlparse(output.file_url)
            suffix = Path(parsed.path).suffix or ".png"
            file_path = output_dir / f"{WORKFLOW_ID}_{index}{suffix}"

            response = client.get(output.file_url)
            response.raise_for_status()
            file_path.write_bytes(response.content)

            print(f"saved: {file_path}")

with RunningHubClient(api_key=API_KEY) as client:
    modifier = (
        modify_nodes()
        .text("6", """姓名：空
年龄：22岁
性别：女
风格：国漫3D风格
外貌：绝美惊艳女神，顶级颜值，冷白皮通透无瑕，骨相皮相俱佳，五官精致立体、清冷疏离感，柔顺黑长直微垂长发，发丝细腻有层次，琉璃质感暗红色眼眸，眼型魅惑清冷，高级氛围感，电影级光影，高清细节，极致美颜""")
        .seed("3", 123456789)
        .set("3", "temperature", 0.7)
        .set("3", "model", "gemini-3.1-pro-preview")
        .seed("4", 987654321)
        .set("4", "aspectRatio", "16:9")
        .set("4", "resolution", "2k")
    )

    task = client.run_with_modifier(
        WORKFLOW_ID,
        modifier,
        add_metadata=True,
        instance_type="plus",
        use_personal_queue=False,
    )

    print("task_id:", task.task_id)
    print("status:", task.task_status)

    outputs = client.wait_for_completion(
        task.task_id,
        poll_interval=3,
        timeout=600,
        on_status_change=lambda status: print("status:", status),
    )

    for output in outputs:
        print(output.file_url)

save_outputs(outputs, OUTPUT_DIR)
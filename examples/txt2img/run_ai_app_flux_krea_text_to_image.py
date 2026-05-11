"""Run the Flux.1 Krea Dev text-to-image AI App via the SDK.

This example mirrors the following request shape:
    POST /openapi/v2/run/ai-app/1950946384071557121
    {
      "nodeInfoList": [...],
      "instanceType": "default",
      "usePersonalQueue": "false"
    }

It uses the SDK's `run_model_api()` helper for submission and
`wait_for_query_v2_completion()` for polling the V2 query endpoint.

Usage:
    python examples/txt2img/run_ai_app_flux_krea_text_to_image.py
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any, Dict, List
from urllib.request import urlopen


def find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "src" / "runninghub_sdk" / "__init__.py").exists():
            return candidate
    raise RuntimeError("Could not locate repository root containing src/runninghub_sdk")


REPO_ROOT = find_repo_root()
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


DEFAULT_AI_APP_ID = "1950946384071557121"
DEFAULT_PROMPT = """中国女子，在繁华喧嚣的都市街头，一位英姿飒爽的美女跨坐在一辆酷炫的黑色重型摩托车上。她身着一件修身的黑色皮质夹克，夹克表面光滑，泛着冷峻的光泽，拉链和纽扣均为银色金属质地，凸显出机车风格。夹克内搭配一件红色的露脐短款打底衫，鲜明的红黑撞色，既展现出她的火辣热情，又不失酷帅。下身穿一条黑色紧身牛仔裤，完美勾勒出她修长笔直的双腿，脚蹬一双黑色马丁靴，靴面有银色铆钉装饰，与夹克的金属元素相呼应。
美女留着一头利落的齐肩短发，发尾微微内卷，显得干练又时尚。她戴着一副黑色镜面墨镜，镜片反射出街道的景象，增添了神秘的气息。耳朵上挂着一对造型独特的金属骷髅耳环，彰显个性；脖子上围着一条带有金属链条的黑色皮质颈圈，酷感十足；手上戴着一双黑色皮质手套，手指关节处有银色护甲，细节处尽显霸气。
特写美女面部，她的眼睛大而明亮，在墨镜后若隐若现，眼神犀利且自信；眉毛浓密而高挑，尽显英气；鼻梁高挺笔直，使五官更加立体；嘴唇涂抹着艳丽的红色口红，在黑与红的色调搭配下，极具视觉冲击力，皮肤白皙紧致，泛着健康的光泽。
她身体微微前倾，双手稳稳地握住摩托车车把，左腿撑地，右腿搭在脚蹬上，准备随时启动出发。嘴角带着一丝不羁的微笑，流露出对速度与自由的向往。画面采用对角线构图，从画面左下角的美女腿部延伸至右上角的摩托车把手，以低视角拍摄，突出美女的高大形象和摩托车的霸气，给人一种扑面而来的压迫感与视觉震撼。
景深方面，将焦点对准美女，使她清晰锐利，背景的街道和来往车辆适度虚化，引导观者的视线集中在美女身上。光线来源于街道两旁的路灯和城市建筑的霓虹灯，暖黄色的路灯洒在美女身上，勾勒出她的轮廓，而五彩斑斓的霓虹灯在地面和车身形成光影交错，营造出繁华都市夜晚的动感氛围，同时冷色的霓虹灯光与暖色调的路灯形成对比，突出美女在画面中的主体地位，强化画面的情感张力。背景的都市街头车水马龙，高楼大厦灯火辉煌，与美女骑摩托车的形象相互映衬，展现出都市的活力与美女追求自由、个性的特质。"""
DEFAULT_ASPECT_RATIO = "9:16 portrait 768x1344"
DEFAULT_BATCH_SIZE = 2
ASPECT_RATIO_FIELD_DATA = (
    '[["custom", "1:1 square 1024x1024", "3:4 portrait 896x1152", '
    '"5:8 portrait 832x1216", "9:16 portrait 768x1344", '
    '"9:21 portrait 640x1536", "4:3 landscape 1152x896", '
    '"3:2 landscape 1216x832", "16:9 landscape 1344x768", '
    '"21:9 landscape 1536x640"]]'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Flux.1 Krea Dev text-to-image AI App via RunningHub SDK."
    )
    parser.add_argument(
        "--prompt",
        default=os.getenv("RUNNINGHUB_FLUX_KREA_PROMPT", DEFAULT_PROMPT),
        help="Text prompt for image generation.",
    )
    parser.add_argument(
        "--aspect-ratio",
        default=os.getenv("RUNNINGHUB_FLUX_KREA_ASPECT_RATIO", DEFAULT_ASPECT_RATIO),
        help="Aspect ratio option label expected by the AI App.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=int(os.getenv("RUNNINGHUB_FLUX_KREA_BATCH_SIZE", str(DEFAULT_BATCH_SIZE))),
        help="Number of images to generate.",
    )
    parser.add_argument(
        "--instance-type",
        default=os.getenv("RUNNINGHUB_FLUX_KREA_INSTANCE_TYPE", "default"),
        help="RunningHub instance type.",
    )
    parser.add_argument(
        "--use-personal-queue",
        default=os.getenv("RUNNINGHUB_FLUX_KREA_USE_PERSONAL_QUEUE", "false"),
        choices=("true", "false"),
        help="Whether to use the personal queue.",
    )
    return parser.parse_args()


def bootstrap_env() -> list[Path]:
    loaded_paths: list[Path] = []
    for env_path in (Path(__file__).resolve().parent / ".env", REPO_ROOT / ".env"):
        if env_path.exists():
            loaded_paths.append(env_path)
            with open(env_path, "r", encoding="utf-8") as file_obj:
                for line in file_obj:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue

                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    if key and value and key not in os.environ:
                        os.environ[key] = value
    return loaded_paths


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    node_info_list: List[Dict[str, Any]] = [
        {
            "nodeId": "53",
            "fieldName": "text",
            "fieldValue": args.prompt,
            "description": "输入提示词",
        },
        {
            "nodeId": "52",
            "fieldName": "aspect_ratio",
            "fieldData": ASPECT_RATIO_FIELD_DATA,
            "fieldValue": args.aspect_ratio,
            "description": "图像分辨率",
        },
        {
            "nodeId": "56",
            "fieldName": "int",
            "fieldValue": str(args.batch_size),
            "description": "图像批次数量",
        },
    ]

    return {
        "nodeInfoList": node_info_list,
        "instanceType": args.instance_type,
        "usePersonalQueue": args.use_personal_queue,
    }


def print_request_preview(payload: Dict[str, Any], ai_app_id: str) -> None:
    print_section("1. Request Preview")
    print("endpoint:", f"/openapi/v2/run/ai-app/{ai_app_id}")
    print("node_count:", len(payload["nodeInfoList"]))
    print("instanceType:", payload["instanceType"])
    print("usePersonalQueue:", payload["usePersonalQueue"])
    for item in payload["nodeInfoList"]:
        print(
            f"nodeId={item['nodeId']} | fieldName={item['fieldName']} | "
            f"fieldValue={item['fieldValue']}"
        )


def submit_task(
    client: Any,
    ai_app_id: str,
    payload: Dict[str, Any],
) -> str | None:
    print_section("2. Submit Task")
    result = client.run_model_api(f"/openapi/v2/run/ai-app/{ai_app_id}", payload)
    print("task_id:", result.task_id)
    print("status:", result.status)
    print("error_code:", result.error_code)
    print("error_message:", result.error_message)

    if result.error_code and result.error_code != "0":
        print("submit_failed: True")
        print(
            "submit_failure_reason:",
            f"error_code={result.error_code}, error_message={result.error_message}",
        )
        return None

    if not result.task_id:
        print("submit_failed: True")
        print("submit_failure_reason: task_id is empty")
        return None

    return result.task_id


def build_download_dir(task_id: str) -> Path:
    base_dir = os.getenv("RUNNINGHUB_FLUX_KREA_DOWNLOAD_DIR", "").strip()
    if base_dir:
        return Path(base_dir).expanduser().resolve() / task_id
    return REPO_ROOT / "downloads" / "flux_krea_text_to_image" / task_id


def download_results(results: List[Dict[str, Any]], task_id: str) -> None:
    download_dir = build_download_dir(task_id)
    download_dir.mkdir(parents=True, exist_ok=True)

    print_section("5. Download Results")
    for index, item in enumerate(results, start=1):
        url = item.get("url")
        output_type = item.get("outputType", "unknown")
        node_id = item.get("nodeId", "")
        if not url:
            print(f"[{index}] skipped: missing url, outputType={output_type}, nodeId={node_id}")
            continue

        file_name = Path(url.split("?", 1)[0]).name
        target_path = download_dir / file_name
        with urlopen(url, timeout=300) as response:
            target_path.write_bytes(response.read())
        print(
            f"[{index}] downloaded: {target_path} | "
            f"outputType={output_type} | nodeId={node_id}"
        )


def wait_for_result(client: Any, task_id: str) -> None:
    poll_interval = float(os.getenv("RUNNINGHUB_FLUX_KREA_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_FLUX_KREA_TIMEOUT", "1800"))
    last_status: Any = None

    def on_status_change(status: TaskStatus) -> None:
        nonlocal last_status
        if status != last_status:
            print(f"status -> {status}")
            last_status = status

    print_section("3. Wait For Completion")
    result = client.wait_for_query_v2_completion(
        task_id,
        poll_interval=poll_interval,
        timeout=timeout,
        on_status_change=on_status_change,
    )

    print_section("4. Results")
    print("status:", result.status)
    print("error_code:", result.error_code)
    print("error_message:", result.error_message)
    print("results:", result.results)

    if result.results:
        download_results(result.results, task_id)
    else:
        print_section("5. Download Results")
        print("No downloadable results returned.")


def main() -> int:
    args = parse_args()

    try:
        from runninghub_sdk import RunningHubClient
        from runninghub_sdk.exceptions import RunningHubError
    except ImportError as exc:
        raise SystemExit(
            "Missing SDK dependency. Install project dependencies first, for example with 'pip install -e .'."
        ) from exc

    loaded_paths = bootstrap_env()
    if loaded_paths:
        print(f"loaded_env: {loaded_paths[0]}")
    else:
        print("loaded_env: <none>")
    api_key = get_required_env("RUNNINGHUB_API_KEY")
    ai_app_id = os.getenv("RUNNINGHUB_FLUX_KREA_AI_APP_ID", DEFAULT_AI_APP_ID).strip()
    payload = build_payload(args)

    print_request_preview(payload, ai_app_id)

    try:
        with RunningHubClient(api_key=api_key) as client:
            task_id = submit_task(client, ai_app_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Flux Krea text-to-image AI App task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Flux Krea text-to-image AI App finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
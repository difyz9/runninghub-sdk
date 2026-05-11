"""Run the scene-setting AI App via the SDK.

This example targets RunningHub AI App `2023042898589130753` and defaults to
the scene-setting mode described on the API detail page:

    POST /openapi/v2/run/ai-app/2023042898589130753

Unlike a hardcoded demo, it resolves the current editable nodes from
`get_ai_app_api_demo()` first, then fills the scene-oriented defaults.

Usage:
    python examples/txt2img/run_ai_app_scene_setting.py
    python examples/txt2img/run_ai_app_scene_setting.py \
        --prompt "ancient cliffside temple city at sunrise, cinematic wide shot" \
        --split-mode 2 \
        --reference-image ./examples/img/scene_ref.png
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List


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


DEFAULT_AI_APP_ID = "2023042898589130753"
DEFAULT_SCENE_PROMPT = (
    "ancient cliffside observatory above the clouds, monumental stone stairs, "
    "mist drifting through the arches, cinematic concept art, ultra detailed, "
    "moody sunrise lighting, wide establishing shot"
)
DEFAULT_SCENE_MODE = "2"
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_SPLIT_MODE = "1"
DEFAULT_CHANNEL = "Third-party"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the scene-setting AI App via RunningHub SDK."
    )
    parser.add_argument(
        "--prompt",
        default=os.getenv("RUNNINGHUB_SCENE_SETTING_PROMPT", DEFAULT_SCENE_PROMPT),
        help="Scene prompt text passed to the AI App.",
    )
    parser.add_argument(
        "--aspect-ratio",
        default=os.getenv("RUNNINGHUB_SCENE_SETTING_ASPECT_RATIO", DEFAULT_ASPECT_RATIO),
        help="Aspect ratio option exposed by the AI App, for example 16:9.",
    )
    parser.add_argument(
        "--split-mode",
        default=os.getenv("RUNNINGHUB_SCENE_SETTING_SPLIT_MODE", DEFAULT_SPLIT_MODE),
        choices=("1", "2", "3"),
        help="1: no split, 2: four-grid, 3: nine-grid.",
    )
    parser.add_argument(
        "--reference-image",
        default=os.getenv("RUNNINGHUB_SCENE_SETTING_REFERENCE_IMAGE", "").strip(),
        help="Optional local image path used as the reference image input.",
    )
    parser.add_argument(
        "--channel",
        default=os.getenv("RUNNINGHUB_SCENE_SETTING_CHANNEL", DEFAULT_CHANNEL),
        help="Model channel option exposed by the AI App.",
    )
    parser.add_argument(
        "--instance-type",
        default=os.getenv("RUNNINGHUB_SCENE_SETTING_INSTANCE_TYPE", "default"),
        help="RunningHub instance type.",
    )
    parser.add_argument(
        "--use-personal-queue",
        default=os.getenv("RUNNINGHUB_SCENE_SETTING_USE_PERSONAL_QUEUE", "false"),
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


def extract_list_options(field_data: str) -> list[str]:
    if not field_data:
        return []

    try:
        parsed = json.loads(field_data)
    except json.JSONDecodeError:
        return []

    if isinstance(parsed, list) and parsed and all(isinstance(item, dict) for item in parsed):
        return [str(item.get("index", item.get("name", ""))) for item in parsed if item]

    if (
        isinstance(parsed, list)
        and parsed
        and isinstance(parsed[0], list)
    ):
        return [str(item) for item in parsed[0]]

    return []


def find_demo_node(nodes: Iterable[Any], label: str, predicate: Any) -> Any:
    for node in nodes:
        if predicate(node):
            return node
    raise SystemExit(f"Could not resolve required AI App node for: {label}")


def build_demo_node_map(demo: Any) -> Dict[str, Any]:
    nodes = demo.node_info_list
    return {
        "mode": find_demo_node(
            nodes,
            "scene mode selector",
            lambda node: node.description.startswith("人物、场景选择"),
        ),
        "aspect_ratio": find_demo_node(
            nodes,
            "aspect ratio",
            lambda node: node.field_name == "aspectRatio",
        ),
        "split_mode": find_demo_node(
            nodes,
            "split mode",
            lambda node: "图片分割方式" in node.description,
        ),
        "prompt": find_demo_node(
            nodes,
            "scene prompt",
            lambda node: "提示词" in node.description,
        ),
        "reference_image": find_demo_node(
            nodes,
            "reference image",
            lambda node: node.field_name == "image",
        ),
        "channel": find_demo_node(
            nodes,
            "channel",
            lambda node: node.field_name == "channel",
        ),
    }


def validate_list_value(node: Any, value: str, field_label: str) -> None:
    options = extract_list_options(node.field_data)
    if options and value not in options:
        raise SystemExit(
            f"Unsupported {field_label}: {value}. Available options: {', '.join(options)}"
        )


def build_node_payload(node: Any, value: str) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "nodeId": node.node_id,
        "fieldName": node.field_name,
        "fieldValue": value,
        "description": node.description,
    }
    if node.field_data and node.field_type == "LIST":
        item["fieldData"] = node.field_data
    return item


def build_payload(client: Any, ai_app_id: str, args: argparse.Namespace) -> tuple[Dict[str, Any], Dict[str, Any], str | None]:
    demo = client.get_ai_app_api_demo(ai_app_id)
    node_map = build_demo_node_map(demo)

    validate_list_value(node_map["aspect_ratio"], args.aspect_ratio, "aspect ratio")
    validate_list_value(node_map["channel"], args.channel, "channel")

    node_info_list: List[Dict[str, Any]] = [
        build_node_payload(node_map["mode"], DEFAULT_SCENE_MODE),
        build_node_payload(node_map["aspect_ratio"], args.aspect_ratio),
        build_node_payload(node_map["split_mode"], args.split_mode),
        build_node_payload(node_map["prompt"], args.prompt),
        build_node_payload(node_map["channel"], args.channel),
    ]

    uploaded_reference: str | None = None
    if args.reference_image:
        reference_path = Path(args.reference_image).expanduser().resolve()
        if not reference_path.exists():
            raise SystemExit(f"Reference image not found: {reference_path}")

        upload_result = client.upload_image(reference_path)
        uploaded_reference = upload_result["fileName"]
        node_info_list.append(
            build_node_payload(node_map["reference_image"], uploaded_reference)
        )

    payload = {
        "nodeInfoList": node_info_list,
        "instanceType": args.instance_type,
        "usePersonalQueue": args.use_personal_queue,
    }
    return payload, node_map, uploaded_reference


def print_request_preview(
    payload: Dict[str, Any],
    ai_app_id: str,
    node_map: Dict[str, Any],
    uploaded_reference: str | None,
) -> None:
    print_section("1. Request Preview")
    print("endpoint:", f"/openapi/v2/run/ai-app/{ai_app_id}")
    print("node_count:", len(payload["nodeInfoList"]))
    print("instanceType:", payload["instanceType"])
    print("usePersonalQueue:", payload["usePersonalQueue"])
    print(
        "resolved_nodes:",
        {
            key: f"{node.node_id}/{node.field_name}"
            for key, node in node_map.items()
        },
    )
    if uploaded_reference:
        print("uploaded_reference:", uploaded_reference)
    for item in payload["nodeInfoList"]:
        print(
            f"nodeId={item['nodeId']} | fieldName={item['fieldName']} | "
            f"fieldValue={item['fieldValue']}"
        )


def submit_task(client: Any, ai_app_id: str, payload: Dict[str, Any]) -> str | None:
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
    base_dir = os.getenv("RUNNINGHUB_SCENE_SETTING_DOWNLOAD_DIR", "").strip()
    if base_dir:
        return Path(base_dir).expanduser().resolve() / task_id
    return REPO_ROOT / "downloads" / "scene_setting" / task_id


def download_results(client: Any, results: List[Dict[str, Any]], task_id: str) -> None:
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
        client.download_file(url, target_path)
        print(
            f"[{index}] downloaded: {target_path} | "
            f"outputType={output_type} | nodeId={node_id}"
        )


def wait_for_result(client: Any, task_id: str) -> None:
    poll_interval = float(os.getenv("RUNNINGHUB_SCENE_SETTING_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_SCENE_SETTING_TIMEOUT", "1800"))
    last_status: Any = None

    def on_status_change(status: Any) -> None:
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
        download_results(client, result.results, task_id)
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
    ai_app_id = os.getenv("RUNNINGHUB_SCENE_SETTING_AI_APP_ID", DEFAULT_AI_APP_ID).strip()

    try:
        with RunningHubClient(api_key=api_key) as client:
            payload, node_map, uploaded_reference = build_payload(client, ai_app_id, args)
            print_request_preview(payload, ai_app_id, node_map, uploaded_reference)
            task_id = submit_task(client, ai_app_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Scene-setting AI App task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Scene-setting AI App finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
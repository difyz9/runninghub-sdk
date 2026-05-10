"""Generate a video prompt with DeepSeek, save it as JSON, then run the Doubao video workflow.

Flow:
1. Call DeepSeek to generate a structured prompt payload
2. Save the payload to a local JSON file
3. Extract `video_prompt` from that JSON
4. Submit the Doubao + Seedance workflow with that prompt
5. Wait for completion and print output URLs

Environment:
    The script will load the repository root `.env` first.

Required environment variables:
    RUNNINGHUB_API_KEY

Optional environment variables:
    DEEPSEEK_API_KEY
    RUNNINGHUB_DOUBAO_VIDEO_WORKFLOW_ID
    RUNNINGHUB_DOUBAO_VIDEO_PROMPT_NODE_ID
    RUNNINGHUB_DOUBAO_VIDEO_POLL_INTERVAL
    RUNNINGHUB_DOUBAO_VIDEO_TIMEOUT
    RUNNINGHUB_DEEPSEEK_PROMPT_OUTPUT
    RUNNINGHUB_DEEPSEEK_MODEL
    RUNNINGHUB_DEEPSEEK_IDEA
    RUNNINGHUB_DEEPSEEK_STYLE
    RUNNINGHUB_DEEPSEEK_DURATION

Usage:
    python examples/run_doubao_video_from_deepseek_prompt.py
"""

from __future__ import annotations

import os
import sys
from argparse import Namespace
from pathlib import Path
from typing import Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from deepseek_video_prompt import (
    bootstrap_env as bootstrap_deepseek_env,
    print_result,
    request_prompt_payload,
    save_output,
)
from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_WORKFLOW_ID = "2004066004755988481"
DEFAULT_PROMPT_NODE_ID = "1"


def bootstrap_env() -> list[Path]:
    loaded_paths: list[Path] = []
    for env_path in (Path(__file__).resolve().parent / ".env", REPO_ROOT / ".env"):
        if env_path.exists():
            loaded_paths.append(env_path)
            load_env_file(env_path)
    return loaded_paths


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_deepseek_args() -> Namespace:
    return Namespace(
        idea=os.getenv(
            "RUNNINGHUB_DEEPSEEK_IDEA",
            "A glamorous Shanghai songstress in a 1930s parlor, camera slowly pushing in as she turns toward a warm gramophone glow.",
        ),
        style=os.getenv(
            "RUNNINGHUB_DEEPSEEK_STYLE",
            "cinematic, elegant, vintage Chinese interior, realistic, smooth camera movement, moody lighting",
        ),
        duration=os.getenv("RUNNINGHUB_DEEPSEEK_DURATION", "8 seconds"),
        output=os.getenv(
            "RUNNINGHUB_DEEPSEEK_PROMPT_OUTPUT",
            "outputs/deepseek_doubao_video_prompt.json",
        ),
        model=os.getenv("RUNNINGHUB_DEEPSEEK_MODEL", "deepseek-chat"),
    )


def compose_doubao_prompt(prompt_json: Dict[str, Any]) -> str:
    scene_prompts = prompt_json.get("scene_prompts") or []
    cleaned_scenes = [str(item).strip().rstrip(";；。.") for item in scene_prompts if str(item).strip()]

    if len(cleaned_scenes) >= 3:
        segments = [
            f"0-2 秒：{cleaned_scenes[0]}",
            f"2-5 秒：{cleaned_scenes[1]}",
            f"5-8 秒：{cleaned_scenes[2]}",
        ]
        final_prompt = "；\n".join(segments) + "。"
    else:
        final_prompt = str(prompt_json.get("video_prompt", "")).strip()

    if not final_prompt:
        raise SystemExit("DeepSeek prompt JSON does not contain usable prompt content.")

    return final_prompt


def generate_prompt_json() -> Dict[str, Any]:
    print_section("1. Generate Prompt JSON")
    deepseek_loaded_paths = bootstrap_deepseek_env()
    if deepseek_loaded_paths:
        print(f"deepseek_loaded_env: {deepseek_loaded_paths[0]}")
    else:
        print("deepseek_loaded_env: <none>")
    args = build_deepseek_args()
    data = request_prompt_payload(args)
    data["doubao_prompt"] = compose_doubao_prompt(data)
    output_path = REPO_ROOT / args.output
    save_output(data, output_path)
    print_result(data, output_path)
    print()
    print("doubao_prompt:")
    print(data["doubao_prompt"])
    return data


def build_payload(video_prompt: str) -> Dict[str, Any]:
    prompt_node_id = os.getenv(
        "RUNNINGHUB_DOUBAO_VIDEO_PROMPT_NODE_ID",
        DEFAULT_PROMPT_NODE_ID,
    ).strip()
    return {
        "addMetadata": True,
        "nodeInfoList": [
            {
                "nodeId": prompt_node_id,
                "fieldName": "prompt",
                "fieldValue": video_prompt,
            }
        ],
        "instanceType": "default",
        "usePersonalQueue": False,
    }


def print_request_preview(payload: Dict[str, Any], workflow_id: str) -> None:
    print_section("2. Request Preview")
    print("sdk_method:", "RunningHubClient.run")
    print("workflow_id:", workflow_id)
    print("node_count:", len(payload["nodeInfoList"]))
    for item in payload["nodeInfoList"]:
        print(
            f"nodeId={item['nodeId']} | fieldName={item['fieldName']} | "
            f"fieldValue={item['fieldValue']}"
        )


def submit_task(
    client: RunningHubClient,
    workflow_id: str,
    payload: Dict[str, Any],
) -> str | None:
    print_section("3. Submit Task")
    task = client.run(
        workflow_id=workflow_id,
        node_info_list=payload["nodeInfoList"],
        add_metadata=payload["addMetadata"],
        instance_type=payload["instanceType"],
        use_personal_queue=payload["usePersonalQueue"],
    )
    print("task_id:", task.task_id)
    print("task_status:", task.task_status)
    print("client_id:", task.client_id)
    print("prompt_tips:", task.prompt_tips)

    if not task.task_id:
        print("submit_failed: True")
        print("submit_failure_reason: task_id is empty")
        return None

    return task.task_id


def wait_for_result(client: RunningHubClient, task_id: str) -> None:
    poll_interval = float(os.getenv("RUNNINGHUB_DOUBAO_VIDEO_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_DOUBAO_VIDEO_TIMEOUT", "1800"))
    last_status: TaskStatus | None = None

    def on_status_change(status: TaskStatus) -> None:
        nonlocal last_status
        if status != last_status:
            print(f"status -> {status}")
            last_status = status

    print_section("4. Wait For Completion")
    outputs = client.wait_for_completion(
        task_id,
        poll_interval=poll_interval,
        timeout=timeout,
        on_status_change=on_status_change,
    )

    print_section("5. Results")
    for index, output in enumerate(outputs, start=1):
        print(f"[{index}] file_type={output.file_type}")
        print(f"    node_id={output.node_id}")
        print(f"    file_url={output.file_url}")
        print(f"    consume_coins={output.consume_coins}")
        print(f"    task_cost_time={output.task_cost_time}")


def main() -> int:
    loaded_paths = bootstrap_env()
    if loaded_paths:
        print(f"loaded_env: {loaded_paths[0]}")
    else:
        print("loaded_env: <none>")
    api_key = get_required_env("RUNNINGHUB_API_KEY")
    workflow_id = os.getenv("RUNNINGHUB_DOUBAO_VIDEO_WORKFLOW_ID", DEFAULT_WORKFLOW_ID).strip()
    prompt_json = generate_prompt_json()
    payload = build_payload(prompt_json["doubao_prompt"])

    print_request_preview(payload, workflow_id)

    try:
        with RunningHubClient(api_key=api_key) as client:
            task_id = submit_task(client, workflow_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Doubao video workflow task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("DeepSeek -> Doubao video workflow finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Run the Seedance 2.0 image-to-video workflow via the SDK.

This example uses the SDK task flow interface for the workflow:
`run()` + `wait_for_completion()`.

It mirrors the following request shape:
    POST /openapi/v2/run/workflow/2037036284312559617
    {
      "addMetadata": true,
      "nodeInfoList": [],
      "instanceType": "default",
      "usePersonalQueue": "false"
    }

Optional node overrides are also supported for this workflow, including:
- first frame image upload
- last frame image upload
- prompt / resolution / duration / ratio / audio / seed

Usage:
    python examples/run_workflow_seedance_image_to_video.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file, modify_nodes
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_WORKFLOW_ID = "2037036284312559617"
DEFAULT_FIRST_FRAME_NODE_ID = "2"
DEFAULT_LAST_FRAME_NODE_ID = "3"
DEFAULT_VIDEO_NODE_ID = "1"


def bootstrap_env() -> None:
    for env_path in (Path(__file__).resolve().parent / ".env", REPO_ROOT / ".env"):
        if env_path.exists():
            load_env_file(env_path)


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def get_optional_env(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def get_optional_int(name: str) -> int | None:
    value = get_optional_env(name)
    return int(value) if value is not None else None


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_payload(client: RunningHubClient) -> Dict[str, Any]:
    modifier = modify_nodes()

    first_frame_path = get_optional_env("RUNNINGHUB_SEEDANCE_FIRST_FRAME_PATH")
    if first_frame_path:
        first_frame_node_id = (
            get_optional_env("RUNNINGHUB_SEEDANCE_FIRST_FRAME_NODE_ID")
            or DEFAULT_FIRST_FRAME_NODE_ID
        )
        uploaded = client.upload_image(first_frame_path)
        modifier.image(first_frame_node_id, uploaded["fileName"])

    last_frame_path = get_optional_env("RUNNINGHUB_SEEDANCE_LAST_FRAME_PATH")
    if last_frame_path:
        last_frame_node_id = (
            get_optional_env("RUNNINGHUB_SEEDANCE_LAST_FRAME_NODE_ID")
            or DEFAULT_LAST_FRAME_NODE_ID
        )
        uploaded = client.upload_image(last_frame_path)
        modifier.image(last_frame_node_id, uploaded["fileName"])

    video_node_id = get_optional_env("RUNNINGHUB_SEEDANCE_VIDEO_NODE_ID") or DEFAULT_VIDEO_NODE_ID
    prompt = get_optional_env("RUNNINGHUB_SEEDANCE_PROMPT")
    resolution = get_optional_env("RUNNINGHUB_SEEDANCE_RESOLUTION")
    duration = get_optional_env("RUNNINGHUB_SEEDANCE_DURATION")
    ratio = get_optional_env("RUNNINGHUB_SEEDANCE_RATIO")
    seed = get_optional_int("RUNNINGHUB_SEEDANCE_SEED")
    generate_audio = get_optional_env("RUNNINGHUB_SEEDANCE_GENERATE_AUDIO")

    if prompt:
        modifier.set(video_node_id, "prompt", prompt)
    if resolution:
        modifier.set(video_node_id, "resolution", resolution)
    if duration:
        modifier.set(video_node_id, "duration", duration)
    if ratio:
        modifier.set(video_node_id, "ratio", ratio)
    if seed is not None:
        modifier.seed(video_node_id, seed)
    if generate_audio is not None:
        modifier.set(video_node_id, "generateAudio", generate_audio.lower() == "true")

    return {
        "addMetadata": True,
        "nodeInfoList": modifier.to_dict_list(),
        "instanceType": "default",
        "usePersonalQueue": False,
    }


def print_request_preview(payload: Dict[str, Any], workflow_id: str) -> None:
    print_section("1. Request Preview")
    print("sdk_method:", "RunningHubClient.run")
    print("workflow_id:", workflow_id)
    print("addMetadata:", payload["addMetadata"])
    print("node_count:", len(payload["nodeInfoList"]))
    print("instanceType:", payload["instanceType"])
    print("usePersonalQueue:", payload["usePersonalQueue"])
    if payload["nodeInfoList"]:
        print("node_overrides:")
        for item in payload["nodeInfoList"]:
            print(
                f"  nodeId={item['nodeId']} | fieldName={item['fieldName']} | "
                f"fieldValue={item['fieldValue']}"
            )


def submit_task(
    client: RunningHubClient,
    workflow_id: str,
    payload: Dict[str, Any],
) -> str | None:
    print_section("2. Submit Task")
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
    poll_interval = float(os.getenv("RUNNINGHUB_SEEDANCE_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_SEEDANCE_TIMEOUT", "1800"))
    last_status: TaskStatus | None = None

    def on_status_change(status: TaskStatus) -> None:
        nonlocal last_status
        if status != last_status:
            print(f"status -> {status}")
            last_status = status

    print_section("3. Wait For Completion")
    outputs = client.wait_for_completion(
        task_id,
        poll_interval=poll_interval,
        timeout=timeout,
        on_status_change=on_status_change,
    )

    print_section("4. Results")
    for index, output in enumerate(outputs, start=1):
        print(f"[{index}] file_type={output.file_type}")
        print(f"    node_id={output.node_id}")
        print(f"    file_url={output.file_url}")
        print(f"    consume_coins={output.consume_coins}")
        print(f"    task_cost_time={output.task_cost_time}")

    download_dir = REPO_ROOT / "downloads" / "seedance_image_to_video" / task_id
    print_section("5. Download Outputs")
    downloaded_paths = client.download_outputs(outputs, download_dir)
    print("download_dir:", download_dir)
    for path in downloaded_paths:
        print("saved:", path)


def main() -> int:
    bootstrap_env()
    api_key = get_required_env("RUNNINGHUB_API_KEY")
    workflow_id = os.getenv("RUNNINGHUB_SEEDANCE_WORKFLOW_ID", DEFAULT_WORKFLOW_ID).strip()

    try:
        with RunningHubClient(api_key=api_key) as client:
            payload = build_payload(client)
            print_request_preview(payload, workflow_id)
            task_id = submit_task(client, workflow_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Seedance image-to-video workflow task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Seedance image-to-video workflow finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



# export RUNNINGHUB_SEEDANCE_FIRST_FRAME_PATH="./examples/img/first.png"
# export RUNNINGHUB_SEEDANCE_LAST_FRAME_PATH="./examples/img/last.png"
# export RUNNINGHUB_SEEDANCE_PROMPT="epic temple knights, cinematic camera movement, realistic lighting"
# python examples/run_workflow_seedance_image_to_video.py
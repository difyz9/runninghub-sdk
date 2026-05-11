"""Run the Fusion X start/end-frame 360 camera transition workflow via the SDK.

This example mirrors the following request shape:
    POST /openapi/v2/run/workflow/1935147311754321921
    {
      "addMetadata": true,
      "nodeInfoList": [],
      "instanceType": "default",
      "usePersonalQueue": "false"
    }

The workflow can run with an empty nodeInfoList. Optional overrides are supported
for first/last frame images, positive/negative prompt, duration, and sampler seed.

Usage:
    python examples/demo02/run_workflow_fusionx_first2last_video.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict


def find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for candidate in (current, *current.parents):
        if (candidate / "src" / "runninghub_sdk" / "__init__.py").exists():
            return candidate
    raise RuntimeError("Could not locate repository root containing src/runninghub_sdk")


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = find_repo_root()
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file, modify_nodes
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_WORKFLOW_ID = "1935147311754321921"
DEFAULT_FIRST_FRAME_NODE_ID = "1"
DEFAULT_LAST_FRAME_NODE_ID = "2"
DEFAULT_POSITIVE_PROMPT_NODE_ID = "52"
DEFAULT_NEGATIVE_PROMPT_NODE_ID = "53"
DEFAULT_DURATION_NODE_ID = "58"
DEFAULT_SAMPLER_NODE_ID = "8"


def bootstrap_env() -> list[Path]:
    loaded_paths: list[Path] = []
    for env_path in (SCRIPT_DIR / ".env", REPO_ROOT / ".env"):
        if env_path.exists():
            loaded_paths.append(env_path)
            load_env_file(env_path)
    return loaded_paths


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

    first_frame_path = get_optional_env("RUNNINGHUB_FUSIONX_FIRST_FRAME_PATH")
    last_frame_path = get_optional_env("RUNNINGHUB_FUSIONX_LAST_FRAME_PATH")
    if bool(first_frame_path) ^ bool(last_frame_path):
        raise SystemExit(
            "RUNNINGHUB_FUSIONX_FIRST_FRAME_PATH and "
            "RUNNINGHUB_FUSIONX_LAST_FRAME_PATH must be set together."
        )

    if first_frame_path and last_frame_path:
        first_frame_node_id = (
            get_optional_env("RUNNINGHUB_FUSIONX_FIRST_FRAME_NODE_ID")
            or DEFAULT_FIRST_FRAME_NODE_ID
        )
        last_frame_node_id = (
            get_optional_env("RUNNINGHUB_FUSIONX_LAST_FRAME_NODE_ID")
            or DEFAULT_LAST_FRAME_NODE_ID
        )
        first_uploaded = client.upload_image(first_frame_path)
        last_uploaded = client.upload_image(last_frame_path)
        modifier.image(first_frame_node_id, first_uploaded["fileName"])
        modifier.image(last_frame_node_id, last_uploaded["fileName"])

    positive_prompt = get_optional_env("RUNNINGHUB_FUSIONX_PROMPT")
    if positive_prompt:
        positive_prompt_node_id = (
            get_optional_env("RUNNINGHUB_FUSIONX_POSITIVE_PROMPT_NODE_ID")
            or DEFAULT_POSITIVE_PROMPT_NODE_ID
        )
        modifier.set(positive_prompt_node_id, "prompt", positive_prompt)

    negative_prompt = get_optional_env("RUNNINGHUB_FUSIONX_NEGATIVE_PROMPT")
    if negative_prompt:
        negative_prompt_node_id = (
            get_optional_env("RUNNINGHUB_FUSIONX_NEGATIVE_PROMPT_NODE_ID")
            or DEFAULT_NEGATIVE_PROMPT_NODE_ID
        )
        modifier.set(negative_prompt_node_id, "prompt", negative_prompt)

    duration_seconds = get_optional_int("RUNNINGHUB_FUSIONX_DURATION_SECONDS")
    if duration_seconds is not None:
        duration_node_id = (
            get_optional_env("RUNNINGHUB_FUSIONX_DURATION_NODE_ID")
            or DEFAULT_DURATION_NODE_ID
        )
        modifier.set(duration_node_id, "value", duration_seconds)

    seed = get_optional_int("RUNNINGHUB_FUSIONX_SEED")
    if seed is not None:
        sampler_node_id = get_optional_env("RUNNINGHUB_FUSIONX_SAMPLER_NODE_ID") or DEFAULT_SAMPLER_NODE_ID
        modifier.seed(sampler_node_id, seed)

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
    poll_interval = float(os.getenv("RUNNINGHUB_FUSIONX_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_FUSIONX_TIMEOUT", "1800"))
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

    download_dir = REPO_ROOT / "downloads" / "fusionx_first2last_video" / task_id
    print_section("5. Download Outputs")
    downloaded_paths = client.download_outputs(outputs, download_dir)
    print("download_dir:", download_dir)
    for path in downloaded_paths:
        print("saved:", path)


def main() -> int:
    loaded_paths = bootstrap_env()
    if loaded_paths:
        print(f"loaded_env: {loaded_paths[0]}")
    else:
        print("loaded_env: <none>")

    api_key = get_required_env("RUNNINGHUB_API_KEY")
    workflow_id = os.getenv("RUNNINGHUB_FUSIONX_WORKFLOW_ID", DEFAULT_WORKFLOW_ID).strip()

    try:
        with RunningHubClient(api_key=api_key) as client:
            payload = build_payload(client)
            print_request_preview(payload, workflow_id)
            task_id = submit_task(client, workflow_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Fusion X first-to-last video workflow task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Fusion X first-to-last video workflow finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
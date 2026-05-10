"""Run the Doubao + Seedance 1.5 Pro text-to-video workflow via the SDK.

This example uses the SDK task flow interface for the workflow:
`run()` + `wait_for_completion()`.

It mirrors the following request shape:
    POST /openapi/v2/run/workflow/2004066004755988481
    {
      "addMetadata": true,
      "nodeInfoList": [],
      "instanceType": "default",
      "usePersonalQueue": "false"
    }

Environment:
    The script will load the repository root `.env` first.

Required environment variables:
    RUNNINGHUB_API_KEY

Optional overrides:
    RUNNINGHUB_DOUBAO_VIDEO_WORKFLOW_ID
    RUNNINGHUB_DOUBAO_VIDEO_POLL_INTERVAL
    RUNNINGHUB_DOUBAO_VIDEO_TIMEOUT

Usage:
    python examples/run_workflow_doubao_seedance_video.py
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

from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_WORKFLOW_ID = "2004066004755988481"


def bootstrap_env() -> None:
    env_path = REPO_ROOT / ".env"
    load_env_file(env_path)


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_payload() -> Dict[str, Any]:
    return {
        "addMetadata": True,
        "nodeInfoList": [],
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
    poll_interval = float(os.getenv("RUNNINGHUB_DOUBAO_VIDEO_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_DOUBAO_VIDEO_TIMEOUT", "1800"))
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

    download_output_files(client, task_id, outputs)


def download_output_files(
    client: RunningHubClient,
    task_id: str,
    outputs: List[Any],
) -> None:
    download_dir = REPO_ROOT / "downloads" / "doubao_video" / task_id
    print_section("5. Download Outputs")
    downloaded_paths = client.download_outputs(outputs, download_dir)
    print("download_dir:", download_dir)
    for path in downloaded_paths:
        print("saved:", path)


def main() -> int:
    bootstrap_env()
    api_key = get_required_env("RUNNINGHUB_API_KEY")
    api_key = "57d048160f1e4dcfa0ba163bd54ae6ea"
    workflow_id = os.getenv("RUNNINGHUB_DOUBAO_VIDEO_WORKFLOW_ID", DEFAULT_WORKFLOW_ID).strip()
    payload = build_payload()

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
    print("Doubao video workflow task finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Run the provided workflow via the SDK task flow interface.

Although the original request can be expressed as a V2 workflow endpoint,
for a normal RunningHub workflow the SDK's task flow interface is the more
direct and stable entrypoint: `run()` + `wait_for_completion()`.

Environment:
    The script will load the repository root `.env` first.

Required environment variables:
    RUNNINGHUB_API_KEY

Optional overrides:
    RUNNINGHUB_QWEN_CAMERA_WORKFLOW_ID
    RUNNINGHUB_QWEN_CAMERA_POLL_INTERVAL
    RUNNINGHUB_QWEN_CAMERA_TIMEOUT

Usage:
    python examples/run_workflow_v2_qwen_camera.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file, modify_nodes
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_WORKFLOW_ID = "2051509626218270722"
DEFAULT_POSITIVE_PROMPT_NODE_ID = "147"
DEFAULT_NEGATIVE_PROMPT_NODE_ID = "143"
DEFAULT_SAMPLER_NODE_ID = "137"
DEFAULT_IMAGE_NODE_ID = "106"


def bootstrap_env() -> None:
    env_path = REPO_ROOT / ".env"
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


def get_optional_float(name: str) -> float | None:
    value = get_optional_env(name)
    return float(value) if value is not None else None


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_payload() -> Dict[str, Any]:
    return {
        "addMetadata": True,
        "nodeInfoList": [],
        "instanceType": "default",
        "usePersonalQueue": False,
    }


def build_node_info_list(client: RunningHubClient) -> list[Dict[str, Any]]:
    modifier = modify_nodes()

    positive_prompt = get_optional_env("RUNNINGHUB_QWEN_CAMERA_POSITIVE_PROMPT")
    if positive_prompt:
        prompt_node_id = get_optional_env("RUNNINGHUB_QWEN_CAMERA_POSITIVE_NODE_ID") or DEFAULT_POSITIVE_PROMPT_NODE_ID
        modifier.text(prompt_node_id, positive_prompt)

    negative_prompt = get_optional_env("RUNNINGHUB_QWEN_CAMERA_NEGATIVE_PROMPT")
    if negative_prompt:
        negative_node_id = get_optional_env("RUNNINGHUB_QWEN_CAMERA_NEGATIVE_NODE_ID") or DEFAULT_NEGATIVE_PROMPT_NODE_ID
        modifier.negative_text(negative_node_id, negative_prompt)

    sampler_node_id = get_optional_env("RUNNINGHUB_QWEN_CAMERA_SAMPLER_NODE_ID") or DEFAULT_SAMPLER_NODE_ID
    seed = get_optional_int("RUNNINGHUB_QWEN_CAMERA_SEED")
    steps = get_optional_int("RUNNINGHUB_QWEN_CAMERA_STEPS")
    cfg = get_optional_float("RUNNINGHUB_QWEN_CAMERA_CFG")
    sampler_name = get_optional_env("RUNNINGHUB_QWEN_CAMERA_SAMPLER_NAME")
    scheduler = get_optional_env("RUNNINGHUB_QWEN_CAMERA_SCHEDULER")

    if seed is not None:
        modifier.seed(sampler_node_id, seed)
    if steps is not None:
        modifier.steps(sampler_node_id, steps)
    if cfg is not None:
        modifier.cfg(sampler_node_id, cfg)
    if sampler_name:
        modifier.sampler(sampler_node_id, sampler_name)
    if scheduler:
        modifier.scheduler(sampler_node_id, scheduler)

    image_path = get_optional_env("RUNNINGHUB_QWEN_CAMERA_IMAGE_PATH")
    if image_path:
        image_node_id = get_optional_env("RUNNINGHUB_QWEN_CAMERA_IMAGE_NODE_ID") or DEFAULT_IMAGE_NODE_ID
        uploaded = client.upload_image(image_path)
        modifier.image(image_node_id, uploaded["fileName"])

    return modifier.to_dict_list()


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
    poll_interval = float(os.getenv("RUNNINGHUB_QWEN_CAMERA_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_QWEN_CAMERA_TIMEOUT", "1800"))
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


def main() -> int:
    bootstrap_env()
    api_key = get_required_env("RUNNINGHUB_API_KEY")
    workflow_id = os.getenv("RUNNINGHUB_QWEN_CAMERA_WORKFLOW_ID", DEFAULT_WORKFLOW_ID).strip()
    print(f"Using api_key: {api_key}")
    try:
        with RunningHubClient(api_key=api_key) as client:
            payload = build_payload()
            payload["nodeInfoList"] = build_node_info_list(client)
            print_request_preview(payload, workflow_id)
            task_id = submit_task(client, workflow_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Workflow task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Workflow task finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
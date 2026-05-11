"""Run the popular aesthetics text-to-image workflow via the SDK.

This example uses the SDK task flow interface for the workflow:
`run()` + `wait_for_completion()`.

It mirrors the following request shape:
    POST /openapi/v2/run/workflow/2037071836214730753
    {
      "addMetadata": true,
      "nodeInfoList": [],
      "instanceType": "default",
      "usePersonalQueue": "false"
    }

Optional node overrides are also supported for this workflow, including:
- prompt / negative prompt
- seed / steps / cfg / sampler / scheduler
- width / height / batch size

Usage:
    python examples/run_workflow_popular_aesthetics_text_to_image.py
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


REPO_ROOT = find_repo_root()
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file, modify_nodes
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_WORKFLOW_ID = "2037071836214730753"
DEFAULT_PROMPT_NODE_ID = "57"
DEFAULT_NEGATIVE_PROMPT_NODE_ID = "43"
DEFAULT_SAMPLER_NODE_ID = "51"
DEFAULT_LATENT_NODE_ID = "39"


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


def get_optional_float(name: str) -> float | None:
    value = get_optional_env(name)
    return float(value) if value is not None else None


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_payload() -> Dict[str, Any]:
    modifier = modify_nodes()

    prompt_node_id = (
        get_optional_env("RUNNINGHUB_POPULAR_AESTHETICS_PROMPT_NODE_ID")
        or DEFAULT_PROMPT_NODE_ID
    )
    negative_prompt_node_id = (
        get_optional_env("RUNNINGHUB_POPULAR_AESTHETICS_NEGATIVE_PROMPT_NODE_ID")
        or DEFAULT_NEGATIVE_PROMPT_NODE_ID
    )
    sampler_node_id = (
        get_optional_env("RUNNINGHUB_POPULAR_AESTHETICS_SAMPLER_NODE_ID")
        or DEFAULT_SAMPLER_NODE_ID
    )
    latent_node_id = (
        get_optional_env("RUNNINGHUB_POPULAR_AESTHETICS_LATENT_NODE_ID")
        or DEFAULT_LATENT_NODE_ID
    )

    prompt = get_optional_env("RUNNINGHUB_POPULAR_AESTHETICS_PROMPT")
    negative_prompt = get_optional_env("RUNNINGHUB_POPULAR_AESTHETICS_NEGATIVE_PROMPT")
    seed = get_optional_int("RUNNINGHUB_POPULAR_AESTHETICS_SEED")
    steps = get_optional_int("RUNNINGHUB_POPULAR_AESTHETICS_STEPS")
    cfg = get_optional_float("RUNNINGHUB_POPULAR_AESTHETICS_CFG")
    sampler_name = get_optional_env("RUNNINGHUB_POPULAR_AESTHETICS_SAMPLER_NAME")
    scheduler = get_optional_env("RUNNINGHUB_POPULAR_AESTHETICS_SCHEDULER")
    width = get_optional_int("RUNNINGHUB_POPULAR_AESTHETICS_WIDTH")
    height = get_optional_int("RUNNINGHUB_POPULAR_AESTHETICS_HEIGHT")
    batch_size = get_optional_int("RUNNINGHUB_POPULAR_AESTHETICS_BATCH_SIZE")

    if prompt:
        modifier.set(prompt_node_id, "text", prompt)
    if negative_prompt:
        modifier.set(negative_prompt_node_id, "text", negative_prompt)
    if seed is not None:
        modifier.seed(sampler_node_id, seed)
    if steps is not None:
        modifier.set(sampler_node_id, "steps", steps)
    if cfg is not None:
        modifier.set(sampler_node_id, "cfg", cfg)
    if sampler_name:
        modifier.set(sampler_node_id, "sampler_name", sampler_name)
    if scheduler:
        modifier.set(sampler_node_id, "scheduler", scheduler)
    if width is not None:
        modifier.set(latent_node_id, "width", width)
    if height is not None:
        modifier.set(latent_node_id, "height", height)
    if batch_size is not None:
        modifier.set(latent_node_id, "batch_size", batch_size)

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
    poll_interval = float(os.getenv("RUNNINGHUB_POPULAR_AESTHETICS_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_POPULAR_AESTHETICS_TIMEOUT", "1800"))
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

    download_dir = REPO_ROOT / "downloads" / "popular_aesthetics_text_to_image" / task_id
    print_section("5. Download Outputs")
    downloaded_paths = client.download_outputs(outputs, download_dir)
    print("download_dir:", download_dir)
    for path in downloaded_paths:
        print("saved:", path)


def main() -> int:
    bootstrap_env()
    api_key = get_required_env("RUNNINGHUB_API_KEY")
    workflow_id = os.getenv(
        "RUNNINGHUB_POPULAR_AESTHETICS_WORKFLOW_ID", DEFAULT_WORKFLOW_ID
    ).strip()

    try:
        with RunningHubClient(api_key=api_key) as client:
            payload = build_payload()
            print_request_preview(payload, workflow_id)
            task_id = submit_task(client, workflow_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Popular aesthetics text-to-image workflow task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Popular aesthetics text-to-image workflow finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
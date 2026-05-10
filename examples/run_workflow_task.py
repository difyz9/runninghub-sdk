"""Run a real RunningHub workflow task and wait for completion.

This example is intended to validate the SDK's task submission and polling
encapsulation against a real workflow.

Required environment variables:
    RUNNINGHUB_API_KEY
    RUNNINGHUB_WORKFLOW_ID

Optional environment variables for modifier-based validation:
    RUNNINGHUB_PROMPT_NODE_ID
    RUNNINGHUB_PROMPT_TEXT
    RUNNINGHUB_NEGATIVE_PROMPT_NODE_ID
    RUNNINGHUB_NEGATIVE_PROMPT_TEXT
    RUNNINGHUB_SAMPLER_NODE_ID
    RUNNINGHUB_SEED
    RUNNINGHUB_STEPS
    RUNNINGHUB_CFG
    RUNNINGHUB_SIZE_NODE_ID
    RUNNINGHUB_WIDTH
    RUNNINGHUB_HEIGHT
    RUNNINGHUB_POLL_INTERVAL
    RUNNINGHUB_TIMEOUT

Usage:
    export RUNNINGHUB_API_KEY="your-api-key"
    export RUNNINGHUB_WORKFLOW_ID="your-workflow-id"
    export RUNNINGHUB_PROMPT_NODE_ID="6"
    export RUNNINGHUB_PROMPT_TEXT="a cinematic portrait, ultra detailed"
    export RUNNINGHUB_SAMPLER_NODE_ID="3"
    export RUNNINGHUB_SEED="12345"
    export RUNNINGHUB_STEPS="28"
    export RUNNINGHUB_CFG="7.0"
    export RUNNINGHUB_SIZE_NODE_ID="5"
    export RUNNINGHUB_WIDTH="1024"
    export RUNNINGHUB_HEIGHT="1024"
    PYTHONPATH=src python examples/run_workflow_task.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file, modify_nodes
from runninghub_sdk.exceptions import RunningHubError


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def bootstrap_env() -> None:
    env_path = REPO_ROOT / ".env"
    load_env_file(env_path)


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


def preview_workflow_nodes(client: RunningHubClient, workflow_id: str) -> None:
    print_section("1. Workflow Preview")
    workflow = client.get_workflow_json_parsed(workflow_id)
    print("workflow_id:", workflow_id)
    print("node_count:", len(workflow))

    for node_id, node_data in list(workflow.items())[:8]:
        class_type = node_data.get("class_type", "unknown")
        input_names = list(node_data.get("inputs", {}).keys())
        print(f"node_id={node_id} | class_type={class_type} | inputs={input_names}")


def build_modifier_from_env():
    modifier = modify_nodes()

    prompt_node_id = get_optional_env("RUNNINGHUB_PROMPT_NODE_ID")
    prompt_text = get_optional_env("RUNNINGHUB_PROMPT_TEXT")
    if prompt_node_id and prompt_text:
        modifier.text(prompt_node_id, prompt_text)

    negative_prompt_node_id = get_optional_env("RUNNINGHUB_NEGATIVE_PROMPT_NODE_ID")
    negative_prompt_text = get_optional_env("RUNNINGHUB_NEGATIVE_PROMPT_TEXT")
    if negative_prompt_node_id and negative_prompt_text:
        modifier.negative_text(negative_prompt_node_id, negative_prompt_text)

    sampler_node_id = get_optional_env("RUNNINGHUB_SAMPLER_NODE_ID")
    seed = get_optional_int("RUNNINGHUB_SEED")
    steps = get_optional_int("RUNNINGHUB_STEPS")
    cfg = get_optional_float("RUNNINGHUB_CFG")
    if sampler_node_id and seed is not None:
        modifier.seed(sampler_node_id, seed)
    if sampler_node_id and steps is not None:
        modifier.steps(sampler_node_id, steps)
    if sampler_node_id and cfg is not None:
        modifier.cfg(sampler_node_id, cfg)

    size_node_id = get_optional_env("RUNNINGHUB_SIZE_NODE_ID")
    width = get_optional_int("RUNNINGHUB_WIDTH")
    height = get_optional_int("RUNNINGHUB_HEIGHT")
    if size_node_id and width is not None and height is not None:
        modifier.size(size_node_id, width, height)

    return modifier


def print_modifier_summary(modifier) -> None:
    print_section("2. Modifier Summary")
    if len(modifier) == 0:
        print("No node overrides provided. The workflow will run with default parameters.")
        return

    for item in modifier.to_dict_list():
        print(item)


def run_task(client: RunningHubClient, workflow_id: str) -> str:
    modifier = build_modifier_from_env()
    print_modifier_summary(modifier)

    print_section("3. Submit Task")
    if len(modifier) == 0:
        task = client.run(workflow_id)
    else:
        task = client.run_with_modifier(workflow_id, modifier)

    print("task_id:", task.task_id)
    print("task_status:", task.task_status)
    print("client_id:", task.client_id)
    if task.prompt_tips:
        print("prompt_tips:", task.prompt_tips)
    return task.task_id


def wait_and_print_outputs(client: RunningHubClient, task_id: str) -> None:
    poll_interval = float(os.getenv("RUNNINGHUB_POLL_INTERVAL", "3"))
    timeout = float(os.getenv("RUNNINGHUB_TIMEOUT", "600"))
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

    print_section("5. Outputs")
    for index, output in enumerate(outputs, start=1):
        print(f"[{index}] file_type={output.file_type}")
        print(f"    node_id={output.node_id}")
        print(f"    file_url={output.file_url}")
        print(f"    consume_coins={output.consume_coins}")
        print(f"    task_cost_time={output.task_cost_time}")


def main() -> int:
    bootstrap_env()
    api_key = get_required_env("RUNNINGHUB_API_KEY")
    workflow_id = get_required_env("RUNNINGHUB_WORKFLOW_ID")

    try:
        with RunningHubClient(api_key=api_key) as client:
            preview_workflow_nodes(client, workflow_id)
            task_id = run_task(client, workflow_id)
            wait_and_print_outputs(client, task_id)
    except RunningHubError as exc:
        print(f"Workflow validation failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Workflow task validation finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
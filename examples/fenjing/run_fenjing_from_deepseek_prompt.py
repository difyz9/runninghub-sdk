"""Generate a storyboard prompt with DeepSeek, save it under the fenjing directory, run the workflow, and download outputs locally.

Usage:
    python examples/fenjing/run_fenjing_from_deepseek_prompt.py
"""

from __future__ import annotations

import os
import sys
from argparse import Namespace
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

from deepseek_storyboard_prompt import (
    bootstrap_env as bootstrap_deepseek_env,
    print_result,
    request_prompt_payload,
    save_output,
)
from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file, modify_nodes
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_WORKFLOW_ID = "2013908081847046145"
DEFAULT_PROMPT_NODE_IDS = ("1",)


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


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_deepseek_args() -> Namespace:
    return Namespace(
        idea=os.getenv(
            "RUNNINGHUB_DEEPSEEK_FENJING_IDEA",
            "主角深夜误入荒废寺庙，在恐惧中逐步发现庙内异样，气氛持续升级。",
        ),
        style=os.getenv(
            "RUNNINGHUB_DEEPSEEK_FENJING_STYLE",
            "国漫分镜，电影感构图，悬疑惊悚，强氛围光影",
        ),
        characters=os.getenv(
            "RUNNINGHUB_DEEPSEEK_FENJING_CHARACTERS",
            "主角：年轻男性，谨慎、紧张、易受惊。",
        ),
        output=os.getenv(
            "RUNNINGHUB_DEEPSEEK_FENJING_OUTPUT",
            str(SCRIPT_DIR / "outputs" / "deepseek_fenjing_storyboard_prompt.json"),
        ),
        model=os.getenv("RUNNINGHUB_DEEPSEEK_FENJING_MODEL", "deepseek-chat"),
    )


def compose_workflow_prompt(prompt_json: Dict[str, Any]) -> str:
    storyboard_prompt = str(prompt_json.get("storyboard_prompt", "")).strip()
    if not storyboard_prompt:
        raise SystemExit("DeepSeek prompt JSON does not contain usable storyboard_prompt.")
    return storyboard_prompt


def resolve_prompt_node_ids(client: RunningHubClient, workflow_id: str) -> list[str]:
    configured_node_ids = get_optional_env("RUNNINGHUB_FENJING_PROMPT_NODE_IDS")
    if configured_node_ids:
        return [item.strip() for item in configured_node_ids.split(",") if item.strip()]

    workflow_json = client.get_workflow_json_parsed(workflow_id)
    resolved_node_ids: list[str] = []

    if isinstance(workflow_json, dict) and "nodes" not in workflow_json:
        for node_id, node_data in workflow_json.items():
            if not isinstance(node_data, dict):
                continue
            if node_data.get("class_type") != "CR Prompt Text":
                continue

            prompt_value = str(node_data.get("inputs", {}).get("prompt", "")).strip()
            if "Slot 1" in prompt_value:
                resolved_node_ids.append(str(node_id))

    if resolved_node_ids:
        return resolved_node_ids

    return list(DEFAULT_PROMPT_NODE_IDS)


def generate_prompt_json() -> Dict[str, Any]:
    print_section("1. Generate Storyboard Prompt JSON")
    deepseek_loaded_paths = bootstrap_deepseek_env()
    if deepseek_loaded_paths:
        print(f"deepseek_loaded_env: {deepseek_loaded_paths[0]}")
    else:
        print("deepseek_loaded_env: <none>")
    args = build_deepseek_args()
    data = request_prompt_payload(args)
    data["workflow_storyboard_prompt"] = compose_workflow_prompt(data)
    output_path = Path(args.output)
    save_output(data, output_path)
    print_result(data, output_path)
    print()
    print("workflow_storyboard_prompt:")
    print(data["workflow_storyboard_prompt"])
    return data


def build_payload(
    client: RunningHubClient,
    workflow_id: str,
    storyboard_prompt: str,
) -> Dict[str, Any]:
    modifier = modify_nodes()
    prompt_node_ids = resolve_prompt_node_ids(client, workflow_id)

    for node_id in prompt_node_ids:
        if node_id:
            modifier.set(node_id, "prompt", storyboard_prompt)

    return {
        "addMetadata": True,
        "nodeInfoList": modifier.to_dict_list(),
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
    poll_interval = float(os.getenv("RUNNINGHUB_FENJING_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_FENJING_TIMEOUT", "1800"))
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

    download_dir = SCRIPT_DIR / "downloads" / f"fenjing_{task_id}"
    print_section("6. Download Outputs")
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
    workflow_id = os.getenv("RUNNINGHUB_FENJING_WORKFLOW_ID", DEFAULT_WORKFLOW_ID).strip()
    try:
        with RunningHubClient(api_key=api_key) as client:
            prompt_json = generate_prompt_json()
            payload = build_payload(client, workflow_id, prompt_json["workflow_storyboard_prompt"])
            print_request_preview(payload, workflow_id)
            task_id = submit_task(client, workflow_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Fenjing workflow task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("DeepSeek -> fenjing workflow finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
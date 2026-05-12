"""Run the reference-image storyboard workflow via the SDK.

This example mirrors the following request shape:
    POST /openapi/v2/run/workflow/2011257263360577538
    {
      "addMetadata": true,
      "nodeInfoList": [],
      "instanceType": "default",
      "usePersonalQueue": "false"
    }

The workflow is intended to generate consistent storyboard frames from a single
reference image plus a textual scene requirement. By default, this script fills:

- node `74/image`: reference image
- node `103/text`: storyboard requirement text

Usage:
    python examples/run_workflow_reference_storyboard.py
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


DEFAULT_WORKFLOW_ID = "2011257263360577538"
DEFAULT_REFERENCE_IMAGE_NODE_ID = "74"
DEFAULT_PROMPT_NODE_ID = "103"
SUPPORTED_IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")
DEFAULT_PROMPT = (
    "这是一组电影感分镜头，基于参考图保持人物外观、服装、发型、色调和光影一致，"
    "生成 3 张连续剧情分镜，不同运镜和景别，动作衔接自然，适合做一致性分镜头。"
)


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


def resolve_reference_image_path() -> str:
    configured_path = get_optional_env("RUNNINGHUB_STORYBOARD_REFERENCE_IMAGE_PATH")
    if configured_path:
        return configured_path

    image_candidates = sorted(
        path for path in SCRIPT_DIR.iterdir() if path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
    )
    if not image_candidates:
        raise SystemExit(
            "Missing reference image. Set RUNNINGHUB_STORYBOARD_REFERENCE_IMAGE_PATH "
            "or place an image in the current example directory."
        )
    return str(image_candidates[0])


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_payload(client: RunningHubClient) -> Dict[str, Any]:
    modifier = modify_nodes()

    reference_image_path = resolve_reference_image_path()
    reference_image_node_id = (
        get_optional_env("RUNNINGHUB_STORYBOARD_REFERENCE_IMAGE_NODE_ID")
        or DEFAULT_REFERENCE_IMAGE_NODE_ID
    )
    prompt_node_id = (
        get_optional_env("RUNNINGHUB_STORYBOARD_PROMPT_NODE_ID")
        or DEFAULT_PROMPT_NODE_ID
    )
    storyboard_prompt = (
        get_optional_env("RUNNINGHUB_STORYBOARD_PROMPT")
        or DEFAULT_PROMPT
    )

    uploaded_reference = client.upload_image(reference_image_path)
    modifier.image(reference_image_node_id, uploaded_reference["fileName"])
    modifier.text(prompt_node_id, storyboard_prompt)

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
    poll_interval = float(os.getenv("RUNNINGHUB_STORYBOARD_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_STORYBOARD_TIMEOUT", "1800"))
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

    download_dir = REPO_ROOT / "downloads" / "reference_storyboard" / task_id
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
    workflow_id = os.getenv("RUNNINGHUB_STORYBOARD_WORKFLOW_ID", DEFAULT_WORKFLOW_ID).strip()

    try:
        with RunningHubClient(api_key=api_key) as client:
            payload = build_payload(client)
            print_request_preview(payload, workflow_id)
            task_id = submit_task(client, workflow_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Reference storyboard workflow task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Reference storyboard workflow finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
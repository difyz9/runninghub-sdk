"""Generate an AI2Role character design with DeepSeek, save it as JSON, then run the character card workflow.

Flow:
1. Call DeepSeek to generate a structured character design payload
2. Save the payload to a local JSON file
3. Extract the role-card-ready text from that JSON
4. Submit the AI2Role character card workflow with that text
5. Wait for completion and print output URLs

Usage:
    python examples/ai2role/run_ai2role_character_card_from_deepseek_prompt.py
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


REPO_ROOT = find_repo_root()
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from deepseek_character_prompt import (
    bootstrap_env as bootstrap_deepseek_env,
    print_result,
    request_prompt_payload,
    save_output,
)
from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file, modify_nodes
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_WORKFLOW_ID = "2051599273845895169"
DEFAULT_CHARACTER_TEXT_NODE_ID = "6"
DEFAULT_REFERENCE_IMAGE_NODE_ID = "9"
DEFAULT_IMAGE_GENERATOR_NODE_ID = "4"


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


def get_optional_env(name: str) -> str | None:
    value = os.getenv(name, "").strip()
    return value or None


def get_optional_int(name: str) -> int | None:
    value = get_optional_env(name)
    return int(value) if value is not None else None


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_deepseek_args() -> Namespace:
    return Namespace(
        idea=os.getenv(
            "RUNNINGHUB_DEEPSEEK_CHARACTER_IDEA",
            "设计一位冷艳、克制、具有强烈记忆点的国漫女性角色，用于角色卡首版设定。",
        ),
        style=os.getenv(
            "RUNNINGHUB_DEEPSEEK_CHARACTER_STYLE",
            "国漫，精致角色设计，电影感光影，适合角色卡立绘",
        ),
        world=os.getenv("RUNNINGHUB_DEEPSEEK_CHARACTER_WORLD", "都市奇幻"),
        output=os.getenv(
            "RUNNINGHUB_DEEPSEEK_CHARACTER_OUTPUT",
            "outputs/deepseek_ai2role_character_prompt.json",
        ),
        model=os.getenv("RUNNINGHUB_DEEPSEEK_CHARACTER_MODEL", "deepseek-chat"),
    )


def compose_character_text(prompt_json: Dict[str, Any]) -> str:
    base_text = str(prompt_json.get("character_card_input", "")).strip()
    if not base_text:
        raise SystemExit("DeepSeek prompt JSON does not contain usable character_card_input.")

    visual_prompt = str(prompt_json.get("visual_prompt", "")).strip()
    color_palette_prompt = str(prompt_json.get("color_palette_prompt", "")).strip()
    negative_prompt = str(prompt_json.get("negative_prompt", "")).strip()

    parts = [base_text]
    if visual_prompt:
        parts.append(f"画面提示：{visual_prompt}")
    if color_palette_prompt:
        parts.append(f"配色提示：{color_palette_prompt}")
    if negative_prompt:
        parts.append(f"负面提示：{negative_prompt}")
    return "\n".join(parts)


def generate_prompt_json() -> Dict[str, Any]:
    print_section("1. Generate Character Prompt JSON")
    deepseek_loaded_paths = bootstrap_deepseek_env()
    if deepseek_loaded_paths:
        print(f"deepseek_loaded_env: {deepseek_loaded_paths[0]}")
    else:
        print("deepseek_loaded_env: <none>")
    args = build_deepseek_args()
    data = request_prompt_payload(args)
    data["workflow_character_text"] = compose_character_text(data)
    output_path = REPO_ROOT / args.output
    save_output(data, output_path)
    print_result(data, output_path)
    print()
    print("workflow_character_text:")
    print(data["workflow_character_text"])
    return data


def build_payload(client: RunningHubClient, character_text: str) -> Dict[str, Any]:
    modifier = modify_nodes()

    character_text_node_id = (
        get_optional_env("RUNNINGHUB_AI2ROLE_CHARACTER_TEXT_NODE_ID")
        or DEFAULT_CHARACTER_TEXT_NODE_ID
    )
    reference_image_node_id = (
        get_optional_env("RUNNINGHUB_AI2ROLE_REFERENCE_IMAGE_NODE_ID")
        or DEFAULT_REFERENCE_IMAGE_NODE_ID
    )
    image_generator_node_id = (
        get_optional_env("RUNNINGHUB_AI2ROLE_IMAGE_GENERATOR_NODE_ID")
        or DEFAULT_IMAGE_GENERATOR_NODE_ID
    )

    reference_image_path = get_optional_env("RUNNINGHUB_AI2ROLE_REFERENCE_IMAGE_PATH")
    aspect_ratio = get_optional_env("RUNNINGHUB_AI2ROLE_ASPECT_RATIO")
    resolution = get_optional_env("RUNNINGHUB_AI2ROLE_RESOLUTION")
    seed = get_optional_int("RUNNINGHUB_AI2ROLE_SEED")

    modifier.set(character_text_node_id, "text", character_text)

    if reference_image_path:
        uploaded = client.upload_image(reference_image_path)
        modifier.image(reference_image_node_id, uploaded["fileName"])

    if aspect_ratio:
        modifier.set(image_generator_node_id, "aspectRatio", aspect_ratio)
    if resolution:
        modifier.set(image_generator_node_id, "resolution", resolution)
    if seed is not None:
        modifier.seed(image_generator_node_id, seed)

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
    poll_interval = float(os.getenv("RUNNINGHUB_AI2ROLE_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_AI2ROLE_TIMEOUT", "1800"))
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

    download_dir = REPO_ROOT / "downloads" / "ai2role_character_card" / task_id
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
    workflow_id = os.getenv("RUNNINGHUB_AI2ROLE_WORKFLOW_ID", DEFAULT_WORKFLOW_ID).strip()
    prompt_json = generate_prompt_json()

    try:
        with RunningHubClient(api_key=api_key) as client:
            payload = build_payload(client, prompt_json["workflow_character_text"])
            print_request_preview(payload, workflow_id)
            task_id = submit_task(client, workflow_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"AI2Role character card workflow task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("DeepSeek -> AI2Role character card workflow finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Run the FLUX2-Klein storyboard workflow via the workflow API.

This example mirrors the following request shape:
    POST /openapi/v2/run/workflow/2013614452058361857
    {
      "addMetadata": true,
      "nodeInfoList": [],
      "instanceType": "default",
      "usePersonalQueue": "false"
    }

Usage:
    PYTHONPATH=src python examples/demo04/run_workflow_flux2_klein_storyboard.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import httpx


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

from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_WORKFLOW_ID = "2013614452058361857"
DEFAULT_REFERENCE_IMAGE_NODE_ID = "30"
SUPPORTED_IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")


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


def get_bool_env(name: str, default: bool) -> bool:
    value = get_optional_env(name)
    if value is None:
        return default
    normalized = value.lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise SystemExit(f"Invalid boolean value for {name}: {value}")


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def resolve_reference_image_path() -> str:
    configured_path = get_optional_env("RUNNINGHUB_FLUX2_KLEIN_REFERENCE_IMAGE_PATH")
    if configured_path:
        return configured_path

    image_candidates = sorted(
        path for path in SCRIPT_DIR.iterdir() if path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
    )
    if not image_candidates:
        raise SystemExit(
            "Missing reference image. Set RUNNINGHUB_FLUX2_KLEIN_REFERENCE_IMAGE_PATH "
            "or place an image in the current example directory."
        )
    return str(image_candidates[0])


def build_payload(client: RunningHubClient) -> Dict[str, Any]:
    reference_image_path = resolve_reference_image_path()
    reference_image_node_id = (
        get_optional_env("RUNNINGHUB_FLUX2_KLEIN_REFERENCE_IMAGE_NODE_ID")
        or DEFAULT_REFERENCE_IMAGE_NODE_ID
    )
    uploaded = client.upload_image(reference_image_path)

    return {
        "addMetadata": get_bool_env("RUNNINGHUB_FLUX2_KLEIN_ADD_METADATA", True),
        "nodeInfoList": [
            {
                "nodeId": reference_image_node_id,
                "fieldName": "image",
                "fieldValue": uploaded["fileName"],
            }
        ],
        "instanceType": get_optional_env("RUNNINGHUB_FLUX2_KLEIN_INSTANCE_TYPE") or "default",
        "usePersonalQueue": (
            get_optional_env("RUNNINGHUB_FLUX2_KLEIN_USE_PERSONAL_QUEUE") or "false"
        ),
    }


def build_download_dir(task_id: str) -> Path:
    base_dir = get_optional_env("RUNNINGHUB_FLUX2_KLEIN_DOWNLOAD_DIR")
    if base_dir:
        return Path(base_dir).expanduser().resolve() / task_id
    return REPO_ROOT / "downloads" / "flux2_klein_storyboard" / task_id


def download_results(results: List[Dict[str, Any]], task_id: str) -> None:
    download_dir = build_download_dir(task_id)
    download_dir.mkdir(parents=True, exist_ok=True)

    print_section("5. Download Results")
    with httpx.Client(timeout=300.0, follow_redirects=True) as downloader:
        for index, item in enumerate(results, start=1):
            url = item.get("url")
            output_type = item.get("outputType", "unknown")
            node_id = item.get("nodeId", "")
            if not url:
                print(f"[{index}] skipped: missing url, outputType={output_type}, nodeId={node_id}")
                continue

            file_name = Path(url.split("?", 1)[0]).name
            target_path = download_dir / file_name
            response = downloader.get(url)
            response.raise_for_status()
            target_path.write_bytes(response.content)
            print(
                f"[{index}] downloaded: {target_path} | "
                f"outputType={output_type} | nodeId={node_id}"
            )


def print_request_preview(payload: Dict[str, Any], workflow_id: str) -> None:
    print_section("1. Request Preview")
    print("endpoint:", f"/openapi/v2/run/workflow/{workflow_id}")
    print("addMetadata:", payload["addMetadata"])
    print("node_count:", len(payload["nodeInfoList"]))
    print("instanceType:", payload["instanceType"])
    print("usePersonalQueue:", payload["usePersonalQueue"])
    for item in payload["nodeInfoList"]:
        print(
            f"node_id={item['nodeId']} | field_name={item['fieldName']} | "
            f"field_value={item['fieldValue']}"
        )


def submit_task(
    client: RunningHubClient,
    workflow_id: str,
    payload: Dict[str, Any],
) -> str | None:
    print_section("2. Submit Task")
    result = client.run_model_api(f"/openapi/v2/run/workflow/{workflow_id}", payload)
    print("task_id:", result.task_id)
    print("status:", result.status)
    print("error_code:", result.error_code)
    print("error_message:", result.error_message)
    print("client_id:", result.client_id)
    print("prompt_tips:", result.prompt_tips)

    if result.error_code and result.error_code != "0":
        print("submit_failed: True")
        print(
            "submit_failure_reason:",
            f"error_code={result.error_code}, error_message={result.error_message}",
        )
        return None

    if not result.task_id:
        print("submit_failed: True")
        print("submit_failure_reason: task_id is empty")
        return None

    return result.task_id


def wait_for_result(client: RunningHubClient, task_id: str) -> None:
    poll_interval = float(get_optional_env("RUNNINGHUB_FLUX2_KLEIN_POLL_INTERVAL") or "5")
    timeout = float(get_optional_env("RUNNINGHUB_FLUX2_KLEIN_TIMEOUT") or "1800")
    last_status: TaskStatus | None = None

    def on_status_change(status: TaskStatus) -> None:
        nonlocal last_status
        if status != last_status:
            print(f"status -> {status}")
            last_status = status

    print_section("3. Wait For Completion")
    result = client.wait_for_query_v2_completion(
        task_id,
        poll_interval=poll_interval,
        timeout=timeout,
        on_status_change=on_status_change,
    )

    print_section("4. Results")
    print("status:", result.status)
    print("error_code:", result.error_code)
    print("error_message:", result.error_message)
    print("results:", result.results)

    if result.results:
        download_results(result.results, task_id)
    else:
        print_section("5. Download Results")
        print("No downloadable results returned.")


def main() -> int:
    loaded_paths = bootstrap_env()
    if loaded_paths:
        print(f"loaded_env: {loaded_paths[0]}")
    else:
        print("loaded_env: <none>")

    api_key = get_required_env("RUNNINGHUB_API_KEY")
    workflow_id = (
        get_optional_env("RUNNINGHUB_FLUX2_KLEIN_WORKFLOW_ID") or DEFAULT_WORKFLOW_ID
    )

    try:
        with RunningHubClient(api_key=api_key) as client:
            payload = build_payload(client)
            print_request_preview(payload, workflow_id)
            task_id = submit_task(client, workflow_id, payload)
            if not task_id:
                return 1
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"FLUX2-Klein workflow task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("FLUX2-Klein workflow finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
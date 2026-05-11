"""Run the provided AI App image-to-video task via the SDK.

This example mirrors the following request shape:
	POST /openapi/v2/run/ai-app/2028770613413814273
	{
	  "nodeInfoList": [
		{
		  "nodeId": "34",
		  "fieldName": "image",
		  "fieldValue": "uploaded-file-name.png"
		},
		{
		  "nodeId": "374",
		  "fieldName": "text",
		  "fieldValue": ""
		}
	  ],
	  "instanceType": "default",
	  "usePersonalQueue": "false"
	}

The script uploads a local image first, then injects the returned fileName into
node 34 before submitting the AI App task.

Usage:
	python examples/img2video/img2video.py
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


DEFAULT_AI_APP_ID = "2028770613413814273"
DEFAULT_IMAGE_NODE_ID = "34"
DEFAULT_TEXT_NODE_ID = "374"
DEFAULT_PROMPT_TEXT = "电影感镜头缓慢推进，人物保持自然呼吸与轻微表情变化，发丝和衣摆随风轻动，光影细腻，画面稳定流畅"
DEFAULT_IMAGE_PATH = REPO_ROOT / "examples" / "img" / "ComfyUI_00001_lemgi_1778400809.png"


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


def resolve_image_path() -> Path:
	configured_path = get_optional_env("RUNNINGHUB_IMG2VIDEO_IMAGE_PATH")
	if configured_path:
		return Path(configured_path).expanduser().resolve()
	return DEFAULT_IMAGE_PATH


def build_download_dir(task_id: str) -> Path:
	base_dir = get_optional_env("RUNNINGHUB_IMG2VIDEO_DOWNLOAD_DIR")
	if base_dir:
		return Path(base_dir).expanduser().resolve() / task_id
	return REPO_ROOT / "downloads" / "img2video_ai_app" / task_id


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


def build_payload(client: RunningHubClient) -> Dict[str, Any]:
	image_path = resolve_image_path()
	if not image_path.exists():
		raise SystemExit(
			"Missing input image. Set RUNNINGHUB_IMG2VIDEO_IMAGE_PATH or ensure the default example image exists: "
			f"{image_path}"
		)
	uploaded = client.upload_image(image_path)

	image_node_id = get_optional_env("RUNNINGHUB_IMG2VIDEO_IMAGE_NODE_ID") or DEFAULT_IMAGE_NODE_ID
	text_node_id = get_optional_env("RUNNINGHUB_IMG2VIDEO_TEXT_NODE_ID") or DEFAULT_TEXT_NODE_ID
	prompt_text = os.getenv("RUNNINGHUB_IMG2VIDEO_TEXT", DEFAULT_PROMPT_TEXT)

	node_info_list: List[Dict[str, Any]] = [
		{
			"nodeId": image_node_id,
			"fieldName": "image",
			"fieldValue": uploaded["fileName"],
			"description": "加载图片",
		},
		{
			"nodeId": text_node_id,
			"fieldName": "text",
			"fieldValue": prompt_text,
			"description": "简单提示词（非常非常简单需要）",
		},
	]

	return {
		"nodeInfoList": node_info_list,
		"instanceType": "default",
		"usePersonalQueue": False,
	}


def print_request_preview(payload: Dict[str, Any], ai_app_id: str) -> None:
	print_section("1. Request Preview")
	print("endpoint:", f"/openapi/v2/run/ai-app/{ai_app_id}")
	print("node_count:", len(payload["nodeInfoList"]))
	for item in payload["nodeInfoList"]:
		print(
			f"node_id={item['nodeId']} | field_name={item['fieldName']} | "
			f"field_value={item['fieldValue']} | description={item.get('description', '')}"
		)


def submit_task(
	client: RunningHubClient,
	ai_app_id: str,
	payload: Dict[str, Any],
) -> str | None:
	print_section("2. Submit Task")
	result = client.run_model_api(f"/openapi/v2/run/ai-app/{ai_app_id}", payload)
	print("task_id:", result.task_id)
	print("status:", result.status)
	print("error_code:", result.error_code)
	print("error_message:", result.error_message)

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
	poll_interval = float(os.getenv("RUNNINGHUB_IMG2VIDEO_POLL_INTERVAL", "5"))
	timeout = float(os.getenv("RUNNINGHUB_IMG2VIDEO_TIMEOUT", "1800"))
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
	ai_app_id = os.getenv("RUNNINGHUB_IMG2VIDEO_AI_APP_ID", DEFAULT_AI_APP_ID).strip()
	print("default_image_path:", resolve_image_path())
	print("default_prompt_text:", os.getenv("RUNNINGHUB_IMG2VIDEO_TEXT", DEFAULT_PROMPT_TEXT))

	try:
		with RunningHubClient(api_key=api_key) as client:
			payload = build_payload(client)
			print_request_preview(payload, ai_app_id)
			task_id = submit_task(client, ai_app_id, payload)
			if not task_id:
				return 1
			wait_for_result(client, task_id)
	except RunningHubError as exc:
		print(f"AI App img2video task failed: {exc}", file=sys.stderr)
		return 1

	print_section("Done")
	print("AI App img2video task finished successfully.")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())

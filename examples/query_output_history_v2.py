"""Call RunningHub web history API and print formatted JSON response.

SDK 替代方案（推荐）：
    client = RunningHubClient.from_env()
    result = client.query_output_history_v2(
        OutputHistoryV2Request(size=30, current=1, status=[TaskStatus.SUCCESS]),
    )
    返回 OutputHistoryV2Response 类型，无需手动解析 JSON。

本脚本为独立调试工具，直接使用 raw httpx 调用。
Endpoint:
  https://www.runninghub.cn/api/output/v2/history

This example is for validating browser-captured request behavior.
Authorization token is read from environment variable by default
and can be overridden from CLI args.

Usage:
  export RH_WEB_BEARER_TOKEN="<your bearer token>"
  python examples/query_output_history_v2.py

    # save to specific file (default saves response.json.data)
    python examples/query_output_history_v2.py --output history_result.json

    # save full debug object instead of only response.json.data
    python examples/query_output_history_v2.py --save-full

  # override default payload
  python examples/query_output_history_v2.py --size 10 --current 2 --status SUCCESS,FAILED

    # override token by arg (prefer env in practice)
    python examples/query_output_history_v2.py --token "eyJ..."
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from runninghub_sdk import load_env_file


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_ENDPOINT = "https://www.runninghub.cn/api/output/v2/history"
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36"
)
DEFAULT_TASK_TYPES = [
    "API",
    "WEBAPP",
    "WORKFLOW",
    "ExclAPI",
    "CORPAPI",
    "FAST_WEBAPP",
    "FAST_WEBAPP_V2",
    "SKU_WEBAPP_API",
    "SKU_WORKFLOW_API",
]


def bootstrap_env() -> None:
    for env_path in (SCRIPT_DIR / ".env", Path.cwd() / ".env"):
        if env_path.exists():
            load_env_file(env_path)


def parse_csv_values(raw: str) -> List[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def maybe_null_string(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"", "none", "null"}:
        return None
    return value


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    return {
        "size": args.size,
        "current": args.current,
        "status": parse_csv_values(args.status),
        "taskType": parse_csv_values(args.task_type),
        "hasOutput": args.has_output,
        "fastCreation": maybe_null_string(args.fast_creation),
        "fromId": args.from_id,
        "taskName": args.task_name,
        "reloadData": args.reload_data,
    }


def build_headers(args: argparse.Namespace) -> Dict[str, str]:
    token = args.token or os.getenv("RH_WEB_BEARER_TOKEN", "").strip()
    if not token:
        raise SystemExit(
            "Missing bearer token. Set RH_WEB_BEARER_TOKEN or use --token."
        )

    headers: Dict[str, str] = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": args.user_agent,
    }
    if token:
        headers["authorization"] = f"Bearer {token}"
    return headers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate RunningHub /api/output/v2/history API call."
    )
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--token", default="")
    parser.add_argument("--user-agent", default=DEFAULT_USER_AGENT)

    parser.add_argument("--size", type=int, default=30)
    parser.add_argument("--current", type=int, default=1)
    parser.add_argument("--status", default="SUCCESS")
    parser.add_argument("--task-type", default=",".join(DEFAULT_TASK_TYPES))

    parser.add_argument("--has-output", action="store_true", default=True)
    parser.add_argument("--no-has-output", dest="has_output", action="store_false")
    parser.add_argument("--fast-creation", default="null")
    parser.add_argument("--from-id", default="")
    parser.add_argument("--task-name", default="")
    parser.add_argument("--reload-data", action="store_true", default=False)

    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--output", default="query_output_history_v2_result.json")
    parser.add_argument("--save-full", action="store_true", default=False)
    return parser.parse_args()


def main() -> int:
    bootstrap_env()
    args = parse_args()

    payload = build_payload(args)
    headers = build_headers(args)

    with httpx.Client(timeout=args.timeout) as client:
        response = client.post(args.endpoint, json=payload, headers=headers)

    result: Dict[str, Any] = {
        "request": {
            "endpoint": args.endpoint,
            "payload": payload,
            "headers": {
                "accept": headers.get("accept"),
                "content-type": headers.get("content-type"),
                "user-agent": headers.get("user-agent"),
                "authorization": "Bearer ***",
            },
        },
        "response": {
            "status_code": response.status_code,
            "ok": response.is_success,
        },
    }

    try:
        result["response"]["json"] = response.json()
    except json.JSONDecodeError:
        result["response"]["text"] = response.text

    data_only_output: Any = result
    response_json = result.get("response", {}).get("json")
    if isinstance(response_json, dict) and "data" in response_json:
        data_only_output = response_json.get("data")

    file_content = result if args.save_full else data_only_output

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(file_content, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"Saved result to: {output_path.resolve()}")
    return 0 if response.is_success else 1


if __name__ == "__main__":
    raise SystemExit(main())





# export RH_WEB_BEARER_TOKEN=你的JWT字符串（不要带 Bearer 前缀）
# PYTHONPATH=../src python query_output_history_v2.py --size 30 --current 1 --status SUCCESS --task-type API,WEBAPP,WORKFLOW,ExclAPI,CORPAPI,FAST_WEBAPP,FAST_WEBAPP_V2,SKU_WEBAPP_API,SKU_WORKFLOW_API --has-output --fast-creation null --from-id "" --task-name "" --timeout 30
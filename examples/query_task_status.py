"""Query a RunningHub task status & results, print as formatted JSON.

Supports:
  - Basic status (QUEUED / RUNNING / SUCCESS / FAILED)
  - V2 query with detailed results
  - Task outputs (file URLs, types, costs)
  - Webhook detail

Usage:
    pip install runninghub-sdk
    export RUNNINGHUB_API_KEY="your-api-key"

    # Full query (status + V2 + outputs + webhook)
    python examples/query_task_status.py <task_id>

    # Quick V2 query only (lighter, with result URLs)
    python examples/query_task_status.py <task_id> --v2-only
"""

from __future__ import annotations

import json
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict

from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file
from runninghub_sdk.exceptions import RunningHubError


SCRIPT_DIR = Path(__file__).resolve().parent


def bootstrap_env() -> None:
    for env_path in (SCRIPT_DIR / ".env", Path.cwd() / ".env"):
        if env_path.exists():
            load_env_file(env_path)


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def to_dict(obj: Any) -> Any:
    """Recursively convert a dataclass/enum instance to a JSON-friendly dict."""
    if hasattr(obj, '__dataclass_fields__'):
        return {k: to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    return obj


def query_task(client: RunningHubClient, task_id: str) -> Dict[str, Any]:
    """Query task via V2 API and return a structured result dict."""
    result: Dict[str, Any] = {"task_id": task_id}

    # 1. Basic status
    result["status"] = client.get_status(task_id).value

    # 2. V2 query (detailed info with results)
    v2 = client.query_v2(task_id)
    result["v2_query"] = to_dict(v2)

    # 3. Outputs (only available on SUCCESS)
    if result["status"] == "SUCCESS":
        try:
            outputs = client.get_outputs(task_id)
            result["outputs"] = to_dict(outputs)
        except RunningHubError as exc:
            result["outputs_error"] = str(exc)

    # 4. Webhook detail (best-effort)
    try:
        webhook = client.get_webhook_detail(task_id)
        result["webhook"] = to_dict(webhook)
    except RunningHubError:
        result["webhook"] = None

    return result


def print_help() -> None:
    print(__doc__)


def main() -> int:
    bootstrap_env()

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        return 1 if len(sys.argv) < 2 else 0

    task_id = sys.argv[1]
    v2_only = "--v2-only" in sys.argv

    api_key = get_required_env("RUNNINGHUB_API_KEY")

    try:
        with RunningHubClient(api_key=api_key) as client:
            if v2_only:
                # Quick V2 query only
                v2 = client.query_v2(task_id)
                print(json.dumps(to_dict(v2), indent=2, ensure_ascii=False))
            else:
                # Full query: status + V2 + outputs + webhook
                result = query_task(client, task_id)
                print(json.dumps(result, indent=2, ensure_ascii=False))

    except RunningHubError as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

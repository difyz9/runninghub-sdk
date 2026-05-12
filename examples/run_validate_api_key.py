"""Validate the current RunningHub API key through queue status.

This script uses `/openapi/v2/queue/status` as the API key validity probe.
If the request succeeds, the key is considered valid and the current queue
status is printed.

Usage:
    python examples/run_validate_api_key.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from runninghub_sdk import RunningHubClient, load_env_file
from runninghub_sdk.exceptions import RunningHubError


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    load_env_file(REPO_ROOT / ".env")
    api_key = get_required_env("RUNNINGHUB_API_KEY")

    try:
        with RunningHubClient(api_key=api_key) as client:
            is_valid = client.validate_api_key()
            print("is_valid:", is_valid)
            if not is_valid:
                print("API Key is invalid.")
                return 1

            queue = client.get_queue_status()
            print("api_key_type:", queue.api_key_type)
            print("concurrent_limit:", queue.concurrent_limit)
            print("running_count:", queue.running_count)
            print("queued_count:", queue.queued_count)
            print("total_current_tasks:", queue.total_current_tasks)
    except RunningHubError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
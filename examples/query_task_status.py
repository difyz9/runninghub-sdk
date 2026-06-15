#!/usr/bin/env python3
"""查询任务状态和结果，以格式化 JSON 输出。

支持：
  - 基本状态查询 (QUEUED / RUNNING / SUCCESS / FAILED)
  - V2 详细查询（含结果 URL）
  - 任务输出（文件 URL、类型、费用）
  - Webhook 详情

Usage:
    cd runninghub-sdk

    # .env 中有账号信息（RUNNINGHUB_API_KEY 或 RUNNINGHUB_USERNAME+密码）
    python examples/query_task_status.py <task_id>

    # 快速 V2 查询（更轻量，含结果 URL）
    python examples/query_task_status.py <task_id> --v2-only
"""

from __future__ import annotations

import json
import sys

from runninghub_sdk import (
    RunningHubClient,
    TaskStatus,
    bootstrap_env,
    to_dict,
)
from runninghub_sdk.exceptions import RunningHubError


def query_task(client: RunningHubClient, task_id: str) -> dict:
    """查询任务，返回结构化结果。"""
    result: dict = {"task_id": task_id}

    # 1. 基本状态
    result["status"] = client.get_status(task_id).value

    # 2. V2 查询
    v2 = client.query_v2(task_id)
    result["v2_query"] = to_dict(v2)

    # 3. 输出（仅 SUCCESS 可用）
    if result["status"] == "SUCCESS":
        try:
            outputs = client.get_outputs(task_id)
            result["outputs"] = to_dict(outputs)
        except RunningHubError as exc:
            result["outputs_error"] = str(exc)

    # 4. Webhook 详情
    try:
        result["webhook"] = to_dict(client.get_webhook_detail(task_id))
    except RunningHubError:
        result["webhook"] = None

    return result


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 1 if len(sys.argv) < 2 else 0

    task_id = sys.argv[1]
    v2_only = "--v2-only" in sys.argv

    bootstrap_env()
    try:
        client = RunningHubClient.from_env()
    except ValueError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    try:
        with client:
            if v2_only:
                v2 = client.query_v2(task_id)
                print(json.dumps(to_dict(v2), indent=2, ensure_ascii=False))
            else:
                result = query_task(client, task_id)
                print(json.dumps(result, indent=2, ensure_ascii=False))

    except RunningHubError as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

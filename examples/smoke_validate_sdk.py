"""RunningHub SDK smoke validation example.

This script is intended to quickly verify that the main encapsulated SDK
interfaces work end-to-end against a real API key.

Covered capabilities:
1. Account status and queue status
2. Public model listing
3. Standard model price preview
4. Optional AI App demo metadata fetch

Usage:
    export RUNNINGHUB_API_KEY="your-api-key"
    export RUNNINGHUB_AI_APP_ID="1937084629516193794"  # optional
    PYTHONPATH=src python examples/smoke_validate_sdk.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from runninghub_sdk import RunningHubClient, load_env_file
from runninghub_sdk.exceptions import RunningHubError


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def bootstrap_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_env_file(env_path)


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def validate_account_and_queue(client: RunningHubClient) -> None:
    print_section("1. Account And Queue")

    account = client.get_account_status()
    print("remain_coins:", account.remain_coins)
    print("api_type:", account.api_type)
    print("api_type_enum:", account.api_type_enum)
    print("current_task_counts:", account.current_task_counts)

    queue = client.get_queue_status()
    print("api_key_type:", queue.api_key_type)
    print("api_key_type_enum:", queue.api_key_type_enum)
    print("running_count:", queue.running_count)
    print("queued_count:", queue.queued_count)


def validate_public_models(client: RunningHubClient) -> None:
    print_section("2. Public Model Listing")

    models = client.list_public_models(
        resource_type="CHECKPOINT",
        current=1,
        size=3,
    )

    print("total:", models.total)
    print("page:", f"{models.current}/{models.pages}")
    for index, record in enumerate(models.records, start=1):
        print(
            f"[{index}] {record.resource_name} | "
            f"type={record.resource_type} | "
            f"base={record.base_model_name}"
        )


def validate_price_preview(client: RunningHubClient) -> None:
    print_section("3. Standard Model Price Preview")

    endpoint = "rhart-image/f-2-dev/text-to-image"
    payload = {
        "12##text": "a premium coffee product poster in studio lighting",
        "41##select": "1:1",
        "30##value": 1024,
        "29##value": 1024,
        "43##file_type": "png",
    }

    price = client.preview_model_price(endpoint, payload)
    print("endpoint:", endpoint)
    print("estimated_price:", price.estimated_price)
    print("currency:", price.currency)
    print("price_text:", price.price_text)
    print("is_free_this_call:", price.is_free_this_call)


def validate_ai_app_demo(client: RunningHubClient, webapp_id: Optional[str]) -> None:
    if not webapp_id:
        print_section("4. AI App Demo")
        print("skipped: RUNNINGHUB_AI_APP_ID is not set")
        return

    print_section("4. AI App Demo")
    demo = client.get_ai_app_api_demo(webapp_id)
    print("webapp_name:", demo.webapp_name)
    print("node_count:", len(demo.node_info_list))

    for node in demo.node_info_list[:5]:
        print(
            f"node_id={node.node_id} | "
            f"field_name={node.field_name} | "
            f"field_type={node.field_type} | "
            f"default={node.field_value}"
        )


def main() -> int:
    bootstrap_env()
    api_key = get_required_env("RUNNINGHUB_API_KEY")
    ai_app_id = os.getenv("RUNNINGHUB_AI_APP_ID", "").strip() or None

    try:
        with RunningHubClient(api_key=api_key) as client:
            validate_account_and_queue(client)
            validate_public_models(client)
            validate_price_preview(client)
            validate_ai_app_demo(client, ai_app_id)
    except RunningHubError as exc:
        print(f"RunningHub API validation failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Smoke validation finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""Batch-run the Wan 2.2 first-to-last workflow from sorted images in the local download directory.

Default behavior:
- Reads images from examples/first2last/download
- Sorts them by file name
- Uses adjacent pairs: image[0]->image[1], image[1]->image[2], ...
- Submits one workflow task per pair

Usage:
    python examples/first2last/run_batch_first2last_from_downloads.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

from run_workflow_wan22_first2last_video import (
    REPO_ROOT,
    RunningHubClient,
    RunningHubError,
    bootstrap_env,
    build_payload,
    get_required_env,
    print_section,
    submit_task,
    wait_for_result,
)


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT_DIR = SCRIPT_DIR / "download"
SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def resolve_input_dir() -> Path:
    configured = os.getenv("RUNNINGHUB_FIRST2LAST_BATCH_INPUT_DIR", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return DEFAULT_INPUT_DIR


def list_input_images(input_dir: Path) -> List[Path]:
    if not input_dir.exists():
        raise SystemExit(f"Input directory does not exist: {input_dir}")

    images = [
        path for path in sorted(input_dir.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES
    ]

    if len(images) < 2:
        raise SystemExit(
            f"Need at least 2 images in {input_dir}, found {len(images)}."
        )

    return images


def main() -> int:
    loaded_paths = bootstrap_env()
    if loaded_paths:
        print(f"loaded_env: {loaded_paths[0]}")
    else:
        print("loaded_env: <none>")

    input_dir = resolve_input_dir()
    images = list_input_images(input_dir)
    api_key = get_required_env("RUNNINGHUB_API_KEY")

    print_section("Batch Input")
    print("input_dir:", input_dir)
    print("image_count:", len(images))
    for index, image_path in enumerate(images, start=1):
        print(f"[{index}] {image_path.name}")

    try:
        with RunningHubClient(api_key=api_key) as client:
            total_pairs = len(images) - 1
            for pair_index in range(total_pairs):
                first_frame_path = images[pair_index]
                last_frame_path = images[pair_index + 1]

                os.environ["RUNNINGHUB_FIRST2LAST_FIRST_FRAME_PATH"] = str(first_frame_path)
                os.environ["RUNNINGHUB_FIRST2LAST_LAST_FRAME_PATH"] = str(last_frame_path)

                print_section(f"Pair {pair_index + 1}/{total_pairs}")
                print("first_frame:", first_frame_path)
                print("last_frame:", last_frame_path)

                payload = build_payload(client)
                task_id = submit_task(
                    client,
                    os.getenv("RUNNINGHUB_FIRST2LAST_WORKFLOW_ID", "2011275998205054977").strip(),
                    payload,
                )
                if not task_id:
                    return 1
                wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"Batch first-to-last workflow failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("Batch first-to-last workflow finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
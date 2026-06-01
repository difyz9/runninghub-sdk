"""Download files from history result JSON.

Reads records from `query_output_history_v2_result.json` and downloads each
`fileUrl` to one output folder. Filename uses `outputName`.

Usage:
  python examples/download_history_outputs.py
  python examples/download_history_outputs.py --input examples/query_output_history_v2_result.json --output-dir examples/downloads --concurrency 8
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import unquote, urlparse

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download fileUrl items from history JSON with concurrency."
    )
    parser.add_argument(
        "--input",
        default="query_output_history_v2_result.json",
        help="Path to history JSON file",
    )
    parser.add_argument(
        "--output-dir",
        default="downloads",
        help="Directory to save downloaded files",
    )
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--overwrite", action="store_true", default=False)
    return parser.parse_args()


def sanitize_filename(name: str) -> str:
    illegal_chars = '<>:"/\\|?*\0'
    safe = "".join("_" if ch in illegal_chars else ch for ch in name).strip()
    return safe or "unnamed_file"


def filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    raw_name = Path(unquote(parsed.path)).name
    return sanitize_filename(raw_name or "unnamed_file")


def load_records(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    if isinstance(data, dict):
        if isinstance(data.get("records"), list):
            return [item for item in data["records"] if isinstance(item, dict)]

        if isinstance(data.get("data"), list):
            return [item for item in data["data"] if isinstance(item, dict)]

        if isinstance(data.get("data"), dict) and isinstance(data["data"].get("records"), list):
            return [item for item in data["data"]["records"] if isinstance(item, dict)]

        response = data.get("response")
        if isinstance(response, dict):
            response_json = response.get("json")
            if isinstance(response_json, dict):
                response_data = response_json.get("data")
                if isinstance(response_data, list):
                    return [item for item in response_data if isinstance(item, dict)]
                if isinstance(response_data, dict) and isinstance(response_data.get("records"), list):
                    return [item for item in response_data["records"] if isinstance(item, dict)]

    raise ValueError("Unsupported JSON structure: cannot find records list")


def build_tasks(records: List[Dict[str, Any]]) -> List[Tuple[str, str]]:
    tasks: List[Tuple[str, str]] = []
    for row in records:
        file_url = str(row.get("fileUrl") or "").strip()
        if not file_url:
            continue
        output_name = str(row.get("outputName") or "").strip()
        if not output_name:
            output_name = filename_from_url(file_url)
        tasks.append((file_url, sanitize_filename(output_name)))
    return tasks


def uniquify_names(tasks: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    seen: Dict[str, int] = {}
    unique_tasks: List[Tuple[str, str]] = []

    for url, name in tasks:
        base = Path(name).stem
        ext = Path(name).suffix
        count = seen.get(name, 0)
        if count == 0:
            unique_name = name
        else:
            unique_name = f"{base}_{count}{ext}"
        seen[name] = count + 1
        unique_tasks.append((url, unique_name))

    return unique_tasks


async def download_one(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    url: str,
    output_path: Path,
    retries: int,
    overwrite: bool,
) -> Tuple[str, str]:
    if output_path.exists() and not overwrite:
        return ("skipped", output_path.name)

    async with semaphore:
        last_error = ""
        for attempt in range(retries + 1):
            try:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_bytes(response.content)
                return ("downloaded", output_path.name)
            except Exception as exc:
                last_error = str(exc)
                if output_path.exists():
                    output_path.unlink(missing_ok=True)
                if attempt >= retries:
                    return ("failed", f"{output_path.name}: {last_error}")
        return ("failed", f"{output_path.name}: {last_error}")


async def run() -> int:
    args = parse_args()

    if args.concurrency <= 0:
        raise SystemExit("--concurrency must be greater than 0")

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    records = load_records(input_path)
    raw_tasks = build_tasks(records)
    tasks = uniquify_names(raw_tasks)

    if not tasks:
        print("No downloadable items found (missing fileUrl/outputName).")
        return 0

    semaphore = asyncio.Semaphore(args.concurrency)
    timeout = httpx.Timeout(args.timeout)

    async with httpx.AsyncClient(timeout=timeout) as client:
        jobs = [
            download_one(
                client=client,
                semaphore=semaphore,
                url=url,
                output_path=output_dir / name,
                retries=args.retries,
                overwrite=args.overwrite,
            )
            for url, name in tasks
        ]
        results = await asyncio.gather(*jobs)

    downloaded = [msg for status, msg in results if status == "downloaded"]
    skipped = [msg for status, msg in results if status == "skipped"]
    failed = [msg for status, msg in results if status == "failed"]

    print(f"Total: {len(tasks)}")
    print(f"Downloaded: {len(downloaded)}")
    print(f"Skipped: {len(skipped)}")
    print(f"Failed: {len(failed)}")
    print(f"Output directory: {output_dir.resolve()}")

    if failed:
        print("Failed items:")
        for item in failed:
            print(f"- {item}")
        return 1

    return 0


def main() -> int:
    return asyncio.run(run())


if __name__ == "__main__":
    raise SystemExit(main())

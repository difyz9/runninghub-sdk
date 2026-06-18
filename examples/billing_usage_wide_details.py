#!/usr/bin/env python3
"""查询账单用量明细，展示完整用量记录和统计信息。
支持自动翻页遍历所有记录，并可选批量下载所有生成资源到本地。

工作流：
  1. 遍历账单用量（支持分页）→ 获取所有 SUCCESS 任务
  2. 对每个任务调用 get_call_log_detail() → 获取输出文件 URL
  3. 并发下载到本地目录

Usage:
    cd runninghub-sdk

    # .env 中有账号信息，自动登录
    python examples/billing_usage_wide_details.py

    # 自动翻页遍历所有记录
    python examples/billing_usage_wide_details.py --all

    # 批量下载所有生成资源（自动翻页 + 并发下载）
    python examples/billing_usage_wide_details.py --download

    # 自定义时间范围 + 下载
    python examples/billing_usage_wide_details.py --start "2026-06-12 00:00:00" --end "2026-06-18 23:59:59" --download

    # 下载失败的任务
    python examples/billing_usage_wide_details.py --status FAILED --download

    # 限制并发数
    python examples/billing_usage_wide_details.py --download --workers 3
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

from runninghub_sdk import (
    RunningHubClient,
    BillingUsageWideDetailRequest,
    BillingUsageWideDetailResponse,
    bootstrap_env,
    to_dict,
)
from runninghub_sdk.exceptions import RunningHubError


def parse_args() -> dict:
    args = {
        "start": "",
        "end": "",
        "size": 50,
        "status": "SUCCESS",
        "cursor": None,
        "all_pages": False,
        "download": False,
        "workers": 5,
        "output_dir": "downloads",
        "no_stats": False,
        "no_child": False,
    }
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        elif argv[i] == "--start" and i + 1 < len(argv):
            args["start"] = argv[i + 1]
            i += 2
        elif argv[i] == "--end" and i + 1 < len(argv):
            args["end"] = argv[i + 1]
            i += 2
        elif argv[i] == "--size" and i + 1 < len(argv):
            args["size"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--status" and i + 1 < len(argv):
            args["status"] = argv[i + 1]
            i += 2
        elif argv[i] == "--cursor" and i + 1 < len(argv):
            args["cursor"] = argv[i + 1]
            i += 2
        elif argv[i] == "--no-stats":
            args["no_stats"] = True
            i += 1
        elif argv[i] == "--no-child":
            args["no_child"] = True
            i += 1
        elif argv[i] == "--all":
            args["all_pages"] = True
            i += 1
        elif argv[i] == "--download":
            args["download"] = True
            i += 1
        elif argv[i] == "--workers" and i + 1 < len(argv):
            args["workers"] = int(argv[i + 1])
            i += 2
        elif argv[i] == "--output-dir" and i + 1 < len(argv):
            args["output_dir"] = argv[i + 1]
            i += 2
        else:
            print(f"未知参数: {argv[i]}")
            print(__doc__)
            sys.exit(1)

    # 默认时间范围：最近 7 天
    if not args["start"]:
        args["start"] = (date.today() - timedelta(days=7)).strftime("%Y-%m-%d") + " 00:00:00"
    if not args["end"]:
        args["end"] = date.today().strftime("%Y-%m-%d") + " 23:59:59"

    return args


def print_billing_detail(detail: BillingUsageWideDetailResponse) -> None:
    """打印用量明细"""
    print("=" * 60)
    print("📊 账单用量明细")
    print("=" * 60)

    print(f"\n📈 统计:")
    print(f"  总记录数:    {detail.total}")
    print(f"  总耗时(秒):  {detail.duration}")
    print(f"  总金币:      {detail.coin_num:.4f}")
    print(f"  总金额:      {detail.amount:.4f} {detail.currency}")
    print(f"  更多数据:    {'✅ 是' if detail.has_next else '❌ 否'}")

    records = detail.records or []
    print(f"\n📋 记录 ({len(records)}):")
    for idx, r in enumerate(records, start=1):
        print(f"\n  [{idx}] {r.task_name}")
        print(f"        任务 ID:  {r.task_id}")
        print(f"        状态:     {r.task_status}")
        print(f"        类型:     {r.task_category_display} ({r.call_type_display})")
        print(f"        工作流:   {r.workflow_name}")
        print(f"        创建时间: {r.create_time}")
        print(f"        金币:     {r.coin_amount}")
        if r.money_amount:
            print(f"        金额:     {r.money_amount}")
        if r.money_duration != "0":
            print(f"        时长(秒): {r.money_duration}")


def format_cursor(cursor: str) -> str:
    if len(cursor) > 40:
        return cursor[:40] + "..."
    return cursor


def download_task_outputs(
    client: RunningHubClient,
    task_id: str,
    user_id: str,
    task_name: str,
    output_dir: Path,
    http_client: httpx.Client,
    overwrite: bool = False,
) -> Tuple[str, int, int]:
    """查询单个任务的调用日志并下载所有输出文件。

    Returns:
        (task_name, downloaded_count, failed_count)
    """
    try:
        detail = client.get_call_log_detail(task_id=task_id, user_id=user_id)
    except RunningHubError as exc:
        return (task_name, 0, 0, str(exc))

    outputs = detail.outputs or []
    if not outputs:
        return (task_name, 0, 0, "无输出")

    # 按任务名建子目录（清理非法字符）
    safe_name = "".join(c if c.isalnum() or c in " _-" else "_" for c in task_name).strip()
    task_dir = output_dir / (safe_name or f"task_{task_id}")
    task_dir.mkdir(parents=True, exist_ok=True)

    downloaded = 0
    failed = 0
    errors = []

    for out in outputs:
        if not out.file_url:
            continue
        url = out.file_url
        # 从 URL 提取文件名
        fname = out.output_name or Path(url.split("?")[0]).name
        fpath = task_dir / fname

        if fpath.exists() and not overwrite:
            downloaded += 1  # 已存在算成功
            continue

        try:
            resp = http_client.get(url, follow_redirects=True, timeout=120)
            resp.raise_for_status()
            fpath.write_bytes(resp.content)
            downloaded += 1
        except Exception as exc:
            failed += 1
            errors.append(str(exc))

    status = f"✅ {downloaded} 个" if failed == 0 else f"✅ {downloaded} 个 / ❌ {failed} 个失败"
    return (task_name, downloaded, failed, status)


def main() -> int:
    bootstrap_env()
    args = parse_args()

    try:
        client = RunningHubClient.from_env()
    except ValueError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    # 从 JWT 提取 user_id
    user_id = None
    try:
        import base64
        payload = json.loads(base64.urlsafe_b64decode(client.api_key.split(".")[1] + "=="))
        user_id = payload.get("sub")
    except Exception:
        pass

    if not user_id:
        print("❌ 无法从 JWT 提取 user_id", file=sys.stderr)
        return 1

    req = BillingUsageWideDetailRequest(
        start_date_time=args["start"],
        end_date_time=args["end"],
        size=args["size"],
        include_stats=not args["no_stats"],
        include_child_tasks=not args["no_child"],
        cursor=args["cursor"],
        task_status=args["status"],
    )

    try:
        print(f"🔍 查询范围: {args['start']} → {args['end']}")
        if args["status"]:
            print(f"  状态筛选: {args['status']}")
        if args["cursor"]:
            print(f"  游标: {format_cursor(args['cursor'])}")
        print()

        # ========== 收集所有 SUCCESS 任务 ==========
        need_download = args["download"] or args["all_pages"]
        if need_download:
            print("📄 遍历账单记录...")
            all_tasks: List[Dict[str, Any]] = []
            for page in client.iter_billing_usage_pages(req):
                for r in page.records:
                    if r.task_status == "SUCCESS" and r.task_id:
                        all_tasks.append({
                            "task_id": r.task_id,
                            "task_name": r.task_name,
                            "create_time": r.create_time,
                        })
                print(f"  已扫描 {len(all_tasks)} 个 SUCCESS 任务 (进度 {page.records[-1].create_time if page.records else '?'})")

            print(f"\n📋 共 {len(all_tasks)} 个 SUCCESS 任务")

            if not all_tasks:
                print("没有需要下载的任务。")
                return 0

            if args["download"]:
                # ========== 批量下载 ==========
                output_dir = Path(args["output_dir"])
                output_dir.mkdir(parents=True, exist_ok=True)

                print(f"\n⬇️  开始下载到: {output_dir.resolve()}")
                print(f"  并发数: {args['workers']}")
                start_time = time.time()

                total_downloaded = 0
                total_failed = 0
                task_count = 0

                with httpx.Client(timeout=120) as http_client:
                    with ThreadPoolExecutor(max_workers=args["workers"]) as executor:
                        futures = {}
                        for t in all_tasks:
                            future = executor.submit(
                                download_task_outputs,
                                client, t["task_id"], user_id,
                                t["task_name"], output_dir, http_client,
                            )
                            futures[future] = t

                        for future in as_completed(futures):
                            t = futures[future]
                            task_count += 1
                            try:
                                name, d, f, status = future.result()
                                total_downloaded += d
                                total_failed += f
                                print(f"  [{task_count}/{len(all_tasks)}] {name}: {status}")
                            except Exception as exc:
                                print(f"  [{task_count}/{len(all_tasks)}] {t['task_name']}: ❌ {exc}")

                elapsed = time.time() - start_time
                print(f"\n{'=' * 60}")
                print(f"✅ 下载完成!")
                print(f"  处理任务: {task_count}")
                print(f"  成功下载: {total_downloaded} 个文件")
                print(f"  失败:     {total_failed} 个文件")
                print(f"  耗时:     {elapsed:.1f} 秒")
                print(f"  保存到:   {output_dir.resolve()}")
            else:
                # 仅 --all（不下载）时打印统计
                for t in all_tasks:
                    print(f"  {t['task_name']} ({t['task_id']}) @ {t['create_time']}")

        else:
            detail = client.get_billing_usage_wide_details(req)
            print_billing_detail(detail)

            print("\n" + "=" * 60)
            print("完整响应数据（JSON）")
            print("=" * 60, end="\n\n")
            print(json.dumps(to_dict(detail), indent=2, ensure_ascii=False))

            if detail.has_next and detail.next_cursor:
                print(f"\n💡 下一页: --cursor \"{detail.next_cursor}\"")
                print(f"   自动翻页: --all")
                print(f"   批量下载: --download")

    except RunningHubError as exc:
        print(f"❌ API 错误: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

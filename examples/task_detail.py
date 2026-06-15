#!/usr/bin/env python3
"""查询任务调用日志详情，展示完整调用日志信息。

调用 POST /api/openapi/my/call/log/detail 接口，使用用户级别的 Bearer token
查询指定任务的调用日志，包括基本信息、输出文件、费用、请求参数和响应详情。

Usage:
    cd runninghub-sdk

    # .env 中有账号信息，自动登录 + 自动获取 user_id
    python examples/task_detail.py <task_id>

    # 示例：
    python examples/task_detail.py 2066351966031925250
"""

from __future__ import annotations

import json
import sys

from runninghub_sdk import (
    RunningHubClient,
    bootstrap_env,
    to_dict,
)
from runninghub_sdk.exceptions import RunningHubError


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    # 从命令行或环境变量获取 task_id
    task_id = ""
    if len(sys.argv) >= 2 and not sys.argv[1].startswith("-"):
        task_id = sys.argv[1]
    if not task_id:
        task_id = __import__("os").getenv("RUNNINGHUB_TASK_ID", "").strip()
    if not task_id:
        print("请提供 task_id，例如：")
        print("  python examples/task_detail.py 2066351966031925250")
        return 1

    # 从 .env 加载，一键创建客户端（自动登录获取 token 和 user_id）
    bootstrap_env()
    try:
        client = RunningHubClient.from_env()
    except ValueError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    # 从 JWT 中提取 user_id
    token = client.api_key  # from_env 里已经 login，api_key 就是 access_token
    user_id = None
    try:
        import base64
        parts = token.split(".")
        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded))
        user_id = payload.get("sub")
    except Exception:
        pass

    if not user_id:
        print("❌ 无法从 JWT 中提取 user_id", file=sys.stderr)
        return 1

    print(f"👤 用户 ID: {user_id}\n")

    try:
        detail = client.get_call_log_detail(
            task_id=task_id,
            user_id=user_id,
        )

        # ========== 打印格式化详情 ==========
        print("=" * 60)
        print("📋 调用日志详情")
        print("=" * 60)

        info = detail.basic_info
        if info:
            print("\n📌 基本信息:")
            print(f"  接口名称:      {info.api_name}")
            print(f"  接口类型:      {info.api_type}")
            print(f"  API Key 类型:  {info.api_key_type}")
            print(f"  任务状态:      {info.task_status}")
            print(f"  任务 ID:       {info.task_id}")
            print(f"  调用时间:      {info.call_time}")
            print(f"  耗时(秒):      {info.duration}")
            print(f"  消耗金币:      {info.coin_num}")
            if info.amount:
                print(f"  消耗金额:      {info.amount}")

        outputs = detail.outputs or []
        if outputs:
            print(f"\n📎 输出文件 ({len(outputs)}):")
            for idx, out in enumerate(outputs, start=1):
                print(f"  [{idx}] {out.output_name} ({out.output_type})")
                if out.file_preview_url:
                    print(f"       预览: {out.file_preview_url}")

        cost = detail.cost_info
        if cost:
            print(f"\n💰 费用信息:")
            print(f"  消耗金币: {cost.coin_num}")
            if cost.amount:
                print(f"  消耗金额: {cost.amount}")

        req = detail.request_info
        if req and req.api_request_params:
            print(f"\n📤 请求参数:")
            params = req.get_request_params_parsed()
            print(json.dumps(params, indent=2, ensure_ascii=False))

        resp = detail.response_info
        if resp:
            print(f"\n📥 响应详情:")
            print(f"  任务状态:    {resp.status}")
            print(f"  错误代码:    {resp.error_code}")
            print(f"  错误信息:    {resp.error_message}")

            results = resp.results or []
            if results:
                print(f"\n  结果列表 ({len(results)}):")
                for r in results[:5]:
                    print(f"    - 节点 {r.node_id}: {r.url} ({r.output_type})")
                if len(results) > 5:
                    print(f"    ... 还有 {len(results) - 5} 条")

            usage = resp.usage
            if usage:
                print(f"\n  用量信息:")
                print(f"    消耗金币:      {usage.consume_coins}")
                print(f"    耗时(秒):      {usage.task_cost_time}")
                if usage.consume_money:
                    print(f"    消耗金额:      {usage.consume_money}")

            task_usage = resp.task_usage_list or []
            if task_usage:
                print(f"\n  任务用量记录 ({len(task_usage)}):")
                for tu in task_usage:
                    print(f"    任务 {tu.task_id} 状态={tu.task_status}")

        # ========== JSON 完整输出 ==========
        print("\n" + "=" * 60)
        print("完整响应数据（JSON）")
        print("=" * 60, end="\n\n")
        print(json.dumps(to_dict(detail), indent=2, ensure_ascii=False))

    except RunningHubError as exc:
        print(f"❌ API 错误: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

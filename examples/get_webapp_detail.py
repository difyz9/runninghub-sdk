#!/usr/bin/env python3
"""获取 AI App 详情，展示完整信息（标签、输入节点、封面、统计等）。

调用 POST /api/webapp/detail 接口，返回 AI App 的完整元信息。

Usage:
    cd runninghub-sdk

    # .env 中有账号信息，自动登录
    python examples/get_webapp_detail.py <webapp_id>
    python examples/get_webapp_detail.py 2059941104472125442
"""

from __future__ import annotations

import json
import os
import sys

from runninghub_sdk import (
    RunningHubClient,
    AiAppDetailResponse,
    AiAppNodeInfo,
    bootstrap_env,
    to_dict,
)
from runninghub_sdk.exceptions import RunningHubError


def describe_node(node: AiAppNodeInfo) -> str:
    """用简短的字符串描述一个输入节点。"""
    fv = node.field_value
    if len(fv) > 80:
        fv = fv[:80] + "…"
    return f"[{node.node_id}] {node.node_name}.{node.field_name} ({node.field_type}) = {fv}"


def print_webapp_detail(detail: AiAppDetailResponse) -> None:
    """打印 AI App 详情"""
    print("=" * 60)
    print("AI App 基本信息")
    print("=" * 60)
    print(f"  ID:          {detail.id}")
    print(f"  名称:        {detail.name}")
    if detail.description:
        print(f"  描述:        {detail.description}")
    print(f"  实例类型:    {detail.instanceType}")
    print(f"  状态:        webappState={detail.webappState}")
    print()

    if detail.owner:
        print(f"👤 作者: {detail.owner.name}  (ID: {detail.owner.id})")
    print()

    tags = detail.tags or []
    print(f"🏷️  标签 ({len(tags)}):")
    for tag in tags:
        en = f" / {tag.name_en}" if tag.name_en else ""
        print(f"    #{tag.name}{en}")

    stats = detail.statisticsInfo
    if stats:
        print(f"\n📊 统计信息:")
        print(f"    使用次数: {stats.use_count}")
        print(f"    收藏数:   {stats.collect_count}")
        print(f"    点赞数:   {stats.like_count}")
        print(f"    下载数:   {stats.download_count}")

    nodes = detail.inputNodes or []
    print(f"\n🔌 输入节点 ({len(nodes)}):")
    for node in nodes:
        print(f"    {describe_node(node)}")

    covers = detail.covers or []
    if covers:
        print(f"\n🖼️  封面 ({len(covers)}):")
        for c in covers[:3]:
            print(f"    {c.url} ({c.image_width}x{c.image_height})")

    pa = detail.publishAccess
    if pa:
        print(f"\n🔐 发布权限:")
        print(f"    公开范围: {pa.publish_scope}")
        print(f"    已授权:   {pa.granted}")
        print(f"    需密码:   {pa.need_password}")

    if detail.publishTime:
        print(f"\n📅 发布时间: {detail.publishTime}")
    if detail.updateTime:
        print(f"🔄 更新时间: {detail.updateTime}")


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    webapp_id = ""
    if len(sys.argv) >= 2 and not sys.argv[1].startswith("-"):
        webapp_id = sys.argv[1]
    if not webapp_id:
        webapp_id = os.getenv("WEBAPP_ID", "").strip()
    if not webapp_id:
        print("请提供 webapp_id，例如：")
        print("  python examples/get_webapp_detail.py 2059941104472125442")
        print("  或: export WEBAPP_ID='2059941104472125442'")
        return 1

    bootstrap_env()
    try:
        client = RunningHubClient.from_env()
    except ValueError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    try:
        print(f"正在获取 AI App 详情: {webapp_id}\n")
        detail = client.get_webapp_detail(webapp_id)

        print_webapp_detail(detail)

        # JSON 完整输出
        print("\n" + "=" * 60)
        print("完整响应数据（JSON）")
        print("=" * 60, end="\n\n")
        print(json.dumps(to_dict(detail), indent=2, ensure_ascii=False))

    except RunningHubError as exc:
        if "TOKEN_INVALID" in str(exc):
            print(
                "❌ 该接口需要用户级别的 Bearer token（普通 API Key 无效）。\n"
                "   请确保 .env 中设置了 RUNNINGHUB_USERNAME + RUNNINGHUB_PASSWORD",
                file=sys.stderr,
            )
        else:
            print(f"❌ API 错误: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

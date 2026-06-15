#!/usr/bin/env python3
"""获取工作流详情，并解析 workflowContent 中的完整 ComfyUI 节点信息。

调用 POST /api/workflow/copy 接口，返回工作流的元信息
(id、name 等) 以及 workflowContent（ComfyUI 工作流 JSON）。

Usage:
    cd runninghub-sdk

    # .env 中有账号信息，自动登录
    python examples/get_workflow_detail.py <workflow_id>
    python examples/get_workflow_detail.py 2061460089676066817
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from runninghub_sdk import (
    RunningHubClient,
    WorkflowCopyResponse,
    bootstrap_env,
    to_dict,
)
from runninghub_sdk.exceptions import RunningHubError


SCRIPT_DIR = Path(__file__).resolve().parent


def print_workflow_detail(workflow: WorkflowCopyResponse) -> None:
    """打印工作流详情"""
    print("=" * 60)
    print("工作流基本信息")
    print("=" * 60)
    print(f"  ID:   {workflow.id}")
    print(f"  名称: {workflow.name}")
    if workflow.desc:
        print(f"  描述: {workflow.desc}")
    if workflow.systemWorkflow is not None:
        print(f"  系统工作流: {workflow.systemWorkflow}")
    print()

    print("=" * 60)
    print("workflowContent 解析结果（ComfyUI 工作流 JSON）")
    print("=" * 60)

    content = workflow.get_workflow_content_parsed()

    nodes = content.get("nodes", [])
    print(f"\n📦 节点数量: {len(nodes)}")
    for node in nodes:
        nid = node.get("id", "?")
        ntype = node.get("type", "?")
        title = node.get("properties", {}).get("Node name for S&R", ntype)
        disabled = node.get("flags", {}).get("disabled", False)
        disabled_tag = " [❌ DISABLED]" if disabled else ""
        print(f"    [{nid:>3}] {title}{disabled_tag}")

    links = content.get("links", [])
    print(f"\n🔗 连接数量: {len(links)}")
    for link in links[:5]:
        print(f"    {link[1]} → {link[3]}")
    if len(links) > 5:
        print(f"    ... 还有 {len(links) - 5} 条")

    groups = content.get("groups", [])
    if groups:
        print(f"\n📁 分组: {len(groups)} 个")
        for g in groups:
            print(f"    {g.get('title', '(未命名)')}")

    print(f"\n📋 extra 字段: {json.dumps(content.get('extra', {}), indent=2, ensure_ascii=False)}")


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    workflow_id = ""
    if len(sys.argv) >= 2 and not sys.argv[1].startswith("-"):
        workflow_id = sys.argv[1]
    if not workflow_id:
        workflow_id = os.getenv("WORKFLOW_ID", "").strip()
    if not workflow_id:
        print("请提供 workflow_id，例如：")
        print("  python examples/get_workflow_detail.py 2061460089676066817")
        print("  或: export WORKFLOW_ID='2061460089676066817'")
        return 1

    bootstrap_env()
    try:
        client = RunningHubClient.from_env()
    except ValueError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    try:
        print(f"正在获取工作流详情: {workflow_id}\n")
        workflow = client.copy_workflow(workflow_id)

        print_workflow_detail(workflow)

        print("\n" + "=" * 60)
        print("原始 workflowContent（完整 JSON）")
        print("=" * 60, end="\n\n")

        content = workflow.get_workflow_content_parsed()
        print(json.dumps(content, indent=2, ensure_ascii=False))

        # 写入本地 JSON 文件
        output_dir = SCRIPT_DIR / "downloads"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{workflow.name}_{workflow_id}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"\n✅ workflowContent 已保存到: {output_path}")

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

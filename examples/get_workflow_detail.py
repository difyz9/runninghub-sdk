"""获取工作流详情，并解析 workflowContent 中的完整 ComfyUI 节点信息。

调用 POST /api/workflow/copy 接口，返回工作流的元信息
(id、name 等) 以及 workflowContent（ComfyUI 工作流 JSON）。

支持两种认证方式（按优先级自动选择）：

  1. API Key 方式（推荐）
     设置环境变量 RUNNINGHUB_API_KEY

  2. 手机号 + 密码登录方式
     设置环境变量 RUNNINGHUB_USERNAME 和 RUNNINGHUB_PASSWORD

Usage:
    pip install runninghub-sdk

    # 方式一：API Key（推荐）
    export RUNNINGHUB_API_KEY="your-api-key"
    python examples/get_workflow_detail.py <workflow_id>

    # 方式二：手机号 + 密码
    export RUNNINGHUB_USERNAME="138xxxxxxxx"
    export RUNNINGHUB_PASSWORD="your_password"
    python examples/get_workflow_detail.py <workflow_id>

    # workflowId 也可以通过环境变量指定
    export WORKFLOW_ID="2061460089676066817"
    python examples/get_workflow_detail.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from runninghub_sdk import RunningHubClient, WorkflowCopyResponse, load_env_file
from runninghub_sdk.exceptions import RunningHubError


SCRIPT_DIR = Path(__file__).resolve().parent


def bootstrap_env() -> None:
    for env_path in (SCRIPT_DIR / ".env", Path.cwd() / ".env"):
        if env_path.exists():
            load_env_file(env_path)


def get_credentials() -> tuple[str, str] | None:
    """获取认证信息，优先使用手机号+密码登录。

    注意：/api/workflow/copy 接口需要用户级别的 Bearer token，
    普通 API Key 无法调用，因此优先使用手机号+密码登录。
    """
    username = os.getenv("RUNNINGHUB_USERNAME", "").strip()
    password = os.getenv("RUNNINGHUB_PASSWORD", "").strip()
    if username and password:
        print(f"🔐 使用手机号登录: {username}\n")
        token = RunningHubClient.login(username, password)
        print(f"   ✅ 登录成功（token 过期时间: {token.expire_in}s）\n")
        return (token.access_token, True)

    api_key = os.getenv("RUNNINGHUB_API_KEY", "").strip()
    if api_key:
        print("🔑 使用 API Key 认证\n")
        return (api_key, False)

    return None


HELP_TEXT = """请设置认证信息（二选一）：

  方式一：手机号 + 密码（推荐，本接口需要用户级别 token）
    export RUNNINGHUB_USERNAME='手机号'
    export RUNNINGHUB_PASSWORD='密码'

  方式二：API Key（仅部分接口可用）
    export RUNNINGHUB_API_KEY='your-api-key'
"""


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

    # 解析 workflowContent
    print("=" * 60)
    print("workflowContent 解析结果（ComfyUI 工作流 JSON）")
    print("=" * 60)

    content = workflow.get_workflow_content_parsed()

    # 节点列表
    nodes = content.get("nodes", [])
    print(f"\n📦 节点数量: {len(nodes)}")
    for node in nodes:
        nid = node.get("id", "?")
        ntype = node.get("type", "?")
        title = node.get("properties", {}).get("Node name for S&R", ntype)
        disabled = node.get("flags", {}).get("disabled", False)
        disabled_tag = " [❌ DISABLED]" if disabled else ""
        print(f"    [{nid:>3}] {title}{disabled_tag}")

    # 连接信息
    links = content.get("links", [])
    print(f"\n🔗 连接数量: {len(links)}")
    for link in links[:5]:  # 最多显示前 5 条
        print(f"    {link[1]} → {link[3]}")
    if len(links) > 5:
        print(f"    ... 还有 {len(links) - 5} 条")

    # 分组信息（如果有）
    groups = content.get("groups", [])
    if groups:
        print(f"\n📁 分组: {len(groups)} 个")
        for g in groups:
            print(f"    {g.get('title', '(未命名)')}")

    print(f"\n📋 extra 字段: {json.dumps(content.get('extra', {}), indent=2, ensure_ascii=False)}")


def print_help() -> None:
    print(__doc__)


def main() -> int:
    bootstrap_env()

    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help"):
        print_help()
        return 0

    # 优先从命令行参数获取 workflowId，其次从环境变量
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

    creds = get_credentials()
    if creds is None:
        print(HELP_TEXT, file=sys.stderr)
        return 1

    access_token, _ = creds

    try:
        with RunningHubClient(api_key=access_token) as client:
            print(f"正在获取工作流详情: {workflow_id}\n")
            workflow = client.copy_workflow(workflow_id)

            # 打印基本信息
            print_workflow_detail(workflow)

            print("\n" + "=" * 60)
            print("原始 workflowContent（完整 JSON）")
            print("=" * 60, end="\n\n")

            # 打印格式化的完整 workflowContent
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
                "   请改用手机号+密码登录：\n"
                f"   export RUNNINGHUB_USERNAME='手机号'\n"
                "   export RUNNINGHUB_PASSWORD='密码'",
                file=sys.stderr,
            )
        else:
            print(f"❌ API 错误: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

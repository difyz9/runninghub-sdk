"""获取 AI App 详情，展示完整信息（标签、输入节点、封面、统计等）。

调用 POST /api/webapp/detail 接口，返回 AI App 的完整元信息。

Usage:
    pip install runninghub-sdk

    # 方式一：手机号 + 密码（推荐，本接口需要用户级别 token）
    export RUNNINGHUB_USERNAME='手机号'
    export RUNNINGHUB_PASSWORD='密码'
    python examples/get_webapp_detail.py <webapp_id>

    # 方式二：API Key（仅部分接口可用）
    export RUNNINGHUB_API_KEY="your-api-key"

    # webappId 也可以通过环境变量指定
    export WEBAPP_ID="2059941104472125442"
    python examples/get_webapp_detail.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from runninghub_sdk import (
    RunningHubClient,
    AiAppDetailResponse,
    AiAppNodeInfo,
    load_env_file,
)
from runninghub_sdk.exceptions import RunningHubError


SCRIPT_DIR = Path(__file__).resolve().parent


def bootstrap_env() -> None:
    for env_path in (SCRIPT_DIR / ".env", Path.cwd() / ".env"):
        if env_path.exists():
            load_env_file(env_path)


def get_credentials() -> tuple[str, str] | None:
    """获取认证信息，优先使用手机号+密码登录。"""
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


def describe_node(node: AiAppNodeInfo) -> str:
    """用简短的字符串描述一个输入节点。"""
    fv = node.field_value
    # 长文本只取前 80 个字符
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

    # 作者
    if detail.owner:
        print(f"👤 作者: {detail.owner.name}  (ID: {detail.owner.id})")
    print()

    # 标签
    tags = detail.tags or []
    print(f"🏷️  标签 ({len(tags)}):")
    for tag in tags:
        en = f" / {tag.name_en}" if tag.name_en else ""
        print(f"    #{tag.name}{en}")

    # 统计信息
    stats = detail.statisticsInfo
    if stats:
        print(f"\n📊 统计信息:")
        print(f"    使用次数: {stats.use_count}")
        print(f"    收藏数:   {stats.collect_count}")
        print(f"    点赞数:   {stats.like_count}")
        print(f"    下载数:   {stats.download_count}")

    # 输入节点
    nodes = detail.inputNodes or []
    print(f"\n🔌 输入节点 ({len(nodes)}):")
    for node in nodes:
        print(f"    {describe_node(node)}")

    # 封面
    covers = detail.covers or []
    if covers:
        print(f"\n🖼️  封面 ({len(covers)}):")
        for c in covers[:3]:  # 最多显示 3 张
            print(f"    {c.url} ({c.image_width}x{c.image_height})")

    # 发布权限
    pa = detail.publishAccess
    if pa:
        print(f"\n🔐 发布权限:")
        print(f"    公开范围: {pa.publish_scope}")
        print(f"    已授权:   {pa.granted}")
        print(f"    需密码:   {pa.need_password}")

    # 时间
    if detail.publishTime:
        print(f"\n📅 发布时间: {detail.publishTime}")
    if detail.updateTime:
        print(f"🔄 更新时间: {detail.updateTime}")


def print_help() -> None:
    print(__doc__)


def main() -> int:
    bootstrap_env()

    if len(sys.argv) >= 2 and sys.argv[1] in ("-h", "--help"):
        print_help()
        return 0

    # 优先从命令行参数获取 webappId，其次从环境变量
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

    creds = get_credentials()
    if creds is None:
        print(HELP_TEXT, file=sys.stderr)
        return 1

    access_token, _ = creds

    try:
        with RunningHubClient(api_key=access_token) as client:
            print(f"正在获取 AI App 详情: {webapp_id}\n")
            detail = client.get_webapp_detail(webapp_id)

            # 打印格式化详情
            print_webapp_detail(detail)

            # 以 JSON 形式打印完整数据
            print("\n" + "=" * 60)
            print("完整响应数据（JSON）")
            print("=" * 60, end="\n\n")
            print(json.dumps(
                {
                    "id": detail.id,
                    "name": detail.name,
                    "description": detail.description,
                    "instanceType": detail.instanceType,
                    "webappState": detail.webappState,
                    "workflowState": detail.workflowState,
                    "publishTime": detail.publishTime,
                    "updateTime": detail.updateTime,
                    "tags": [{"id": t.id, "name": t.name, "nameEn": t.name_en} for t in (detail.tags or [])],
                    "owner": {"id": detail.owner.id, "name": detail.owner.name} if detail.owner else None,
                    "inputNodes": [
                        {"nodeId": n.node_id, "nodeName": n.node_name, "fieldName": n.field_name,
                         "fieldValue": n.field_value, "fieldType": n.field_type}
                        for n in (detail.inputNodes or [])
                    ],
                    "statisticsInfo": {
                        "useCount": detail.statisticsInfo.use_count,
                        "likeCount": detail.statisticsInfo.like_count,
                        "collectCount": detail.statisticsInfo.collect_count,
                        "downloadCount": detail.statisticsInfo.download_count,
                    } if detail.statisticsInfo else None,
                    "covers": [{"url": c.url, "width": c.image_width, "height": c.image_height}
                               for c in (detail.covers or [])],
                    "publishAccess": {
                        "accessType": detail.publishAccess.access_type,
                        "granted": detail.publishAccess.granted,
                        "needPassword": detail.publishAccess.need_password,
                    } if detail.publishAccess else None,
                },
                indent=2,
                ensure_ascii=False,
            ))

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

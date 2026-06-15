#!/usr/bin/env python3
"""查询 RunningHub 门户模板和 Webapp 列表。

演示 Portal/Webapp API 集成：
  - get_access_token()      — 获取用户级别 access token
  - list_portal_templates() — 查询模板列表（支持搜索、分页、排序）
  - list_webapps()          — 查询 Webapp 列表

Usage:
    cd runninghub-sdk

    # .env 中有账号信息，自动登录
    python examples/query_portal_api.py templates
    python examples/query_portal_api.py templates --search "LTX"
    python examples/query_portal_api.py webapps
    python examples/query_portal_api.py token
"""

from __future__ import annotations

import json
import sys

from runninghub_sdk import (
    RunningHubClient,
    PortalTemplateListRequest,
    WebappListRequest,
    bootstrap_env,
    to_dict,
)
from runninghub_sdk.exceptions import RunningHubError


def cmd_token(client: RunningHubClient) -> dict:
    """获取 access token。"""
    return to_dict(client.get_access_token())


def cmd_templates(
    client: RunningHubClient,
    search: str = "",
    page: int = 1,
    size: int = 10,
    sort: str = "RECOMMEND",
) -> dict:
    """查询模板列表。"""
    request = PortalTemplateListRequest(
        size=size, current=page, search=search, sort=sort,
    )
    return to_dict(client.list_portal_templates(request))


def cmd_webapps(
    client: RunningHubClient,
    search: str = "",
    page: int = 1,
    size: int = 10,
    sort: str = "RECOMMEND",
) -> dict:
    """查询 Webapp 列表。"""
    request = WebappListRequest(
        size=size, current=page, search=search, sort=sort,
    )
    return to_dict(client.list_webapps(request))


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 1 if len(sys.argv) < 2 else 0

    command = sys.argv[1]
    search = ""
    page = 1
    size = 10
    sort = "RECOMMEND"

    args_iter = iter(sys.argv[2:])
    for arg in args_iter:
        if arg == "--search" or arg == "-s":
            search = next(args_iter, "")
        elif arg == "--page" or arg == "-p":
            page = int(next(args_iter, "1"))
        elif arg == "--size":
            size = int(next(args_iter, "10"))
        elif arg == "--sort":
            sort = next(args_iter, "RECOMMEND")

    bootstrap_env()
    try:
        client = RunningHubClient.from_env()
    except ValueError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1

    try:
        with client:
            if command == "token":
                result = cmd_token(client)
            elif command == "templates":
                result = cmd_templates(client, search=search, page=page, size=size, sort=sort)
            elif command == "webapps":
                result = cmd_webapps(client, search=search, page=page, size=size, sort=sort)
            else:
                print(f"Unknown command: {command}")
                print(__doc__)
                return 1

            print(json.dumps(result, indent=2, ensure_ascii=False))

    except RunningHubError as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

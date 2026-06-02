"""Query RunningHub portal templates & webapps, print as formatted JSON.

Demonstrates the new Portal/Webapp API integration:
  - get_access_token()      — Get a user-level access token
  - list_portal_templates() — List portal templates with filters
  - list_webapps()          — List webapps with filters

Usage:
    pip install runninghub-sdk
    export RUNNINGHUB_API_KEY="your-api-key"

    # List portal templates (first page, default sort)
    python examples/query_portal_api.py templates

    # List portal templates with search keyword
    python examples/query_portal_api.py templates --search "LTX"

    # List webapps (first page, recommend sort)
    python examples/query_portal_api.py webapps

    # Get an access token only
    python examples/query_portal_api.py token
"""

from __future__ import annotations

import json
import os
import sys
from enum import Enum
from pathlib import Path
from typing import Any

from runninghub_sdk import (
    RunningHubClient,
    PortalTemplateListRequest,
    PortalTemplateListResponse,
    WebappListRequest,
    WebappListResponse,
    load_env_file,
)
from runninghub_sdk.exceptions import RunningHubError


SCRIPT_DIR = Path(__file__).resolve().parent


def bootstrap_env() -> None:
    for env_path in (SCRIPT_DIR / ".env", Path.cwd() / ".env"):
        if env_path.exists():
            load_env_file(env_path)


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def to_dict(obj: Any) -> Any:
    """Recursively convert a dataclass/enum instance to a JSON-friendly dict."""
    if hasattr(obj, '__dataclass_fields__'):
        return {k: to_dict(getattr(obj, k)) for k in obj.__dataclass_fields__}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    return obj


def print_help() -> None:
    print(__doc__)


def cmd_token(client: RunningHubClient) -> Dict[str, Any]:
    """Get an access token and return it."""
    result = client.get_access_token()
    return to_dict(result)


def cmd_templates(
    client: RunningHubClient,
    search: str = "",
    page: int = 1,
    size: int = 10,
    sort: str = "RECOMMEND",
) -> Dict[str, Any]:
    """List portal templates and return the structured response."""
    request = PortalTemplateListRequest(
        size=size,
        current=page,
        search=search,
        sort=sort,
    )
    result = client.list_portal_templates(request)
    return to_dict(result)


def cmd_webapps(
    client: RunningHubClient,
    search: str = "",
    page: int = 1,
    size: int = 10,
    sort: str = "RECOMMEND",
) -> Dict[str, Any]:
    """List webapps and return the structured response."""
    request = WebappListRequest(
        size=size,
        current=page,
        search=search,
        sort=sort,
    )
    result = client.list_webapps(request)
    return to_dict(result)


def main() -> int:
    bootstrap_env()

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print_help()
        return 1 if len(sys.argv) < 2 else 0

    command = sys.argv[1]
    search = ""
    page = 1
    size = 10
    sort = "RECOMMEND"

    # Parse optional flags
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

    api_key = get_required_env("RUNNINGHUB_API_KEY")

    try:
        with RunningHubClient(api_key=api_key) as client:
            if command == "token":
                result = cmd_token(client)
            elif command == "templates":
                result = cmd_templates(client, search=search, page=page, size=size, sort=sort)
            elif command == "webapps":
                result = cmd_webapps(client, search=search, page=page, size=size, sort=sort)
            else:
                print(f"Unknown command: {command}")
                print_help()
                return 1

            print(json.dumps(result, indent=2, ensure_ascii=False))

    except RunningHubError as exc:
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

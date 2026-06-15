#!/usr/bin/env python3
"""
Login to https://www.runninghub.cn with a mobile number/password and print tokens.

Usage:
  python examples/runninghub_login.py -u 158xxxxxxxx -p 'your_password'

You can also use environment variables:
  RUNNINGHUB_USERNAME=158xxxxxxxx RUNNINGHUB_PASSWORD='your_password' python examples/runninghub_login.py

Alternatively, use .env file and from_env():
  bootstrap_env() + RunningHubClient.from_env()
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys

from runninghub_sdk import RunningHubClient, bootstrap_env
from runninghub_sdk.exceptions import RunningHubError


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Login to RunningHub and print token JSON.")
    parser.add_argument("-u", "--username", default=os.getenv("RUNNINGHUB_USERNAME"), help="mobile number")
    parser.add_argument("-p", "--password", default=os.getenv("RUNNINGHUB_PASSWORD"), help="password")
    parser.add_argument("--timeout", type=int, default=30, help="request timeout seconds")
    parser.add_argument("--save", help="optional path to save token JSON")
    return parser.parse_args()


def main() -> int:
    bootstrap_env()
    args = parse_args()
    username = args.username or input("RunningHub username/mobile: ").strip()
    password = args.password or getpass.getpass("RunningHub password: ")

    try:
        token = RunningHubClient.login(username, password, timeout=args.timeout)
    except RunningHubError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    token_json = {
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "expire_in": token.expire_in,
        "expires_at_ms": token.expires_at_ms,
        "identify": token.identify,
        "user_id": token.user_id,
        "first_login": token.first_login,
    }
    output = json.dumps(token_json, ensure_ascii=False, indent=2)
    print(output)

    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            f.write(output + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

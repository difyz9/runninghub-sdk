#!/usr/bin/env python3
"""
Login to https://www.runninghub.cn with a mobile number/password and print tokens.

Usage:
  python3 runninghub_login.py -u 158xxxxxxxx -p 'your_password'

You can also use environment variables:
  RUNNINGHUB_USERNAME=158xxxxxxxx RUNNINGHUB_PASSWORD='your_password' python3 runninghub_login.py
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


BASE_URL = "https://www.runninghub.cn"
LOGIN_PATH = "/uc/pwdLogin"


class RunningHubLoginError(RuntimeError):
    pass


@dataclass
class RunningHubToken:
    access_token: str
    refresh_token: str
    expire_in: int
    identify: str | None = None
    first_login: bool | None = None
    raw: dict[str, Any] | None = None

    @property
    def expires_at_ms(self) -> int:
        # RunningHub returns expire_in in milliseconds.
        return int(time.time() * 1000) + self.expire_in

    def to_dict(self) -> dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expire_in": self.expire_in,
            "expires_at_ms": self.expires_at_ms,
            "identify": self.identify,
            "first_login": self.first_login,
        }


def md5_text(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str], timeout: int) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RunningHubLoginError(f"HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RunningHubLoginError(f"request failed: {exc.reason}") from exc

    try:
        return json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise RunningHubLoginError(f"invalid JSON response: {response_body[:300]}") from exc


def login(username: str, password: str, *, timeout: int = 30) -> RunningHubToken:
    """
    Login with mobile number and plaintext password.

    The RunningHub frontend sends MD5(password) to /uc/pwdLogin.
    """
    payload = {
        "mobile": username,
        "password": md5_text(password),
        "channel": None,
        "inviteCode": None,
        "serviceAgreement": True,
    }
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
        "User-Language": "zh_CN",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
        ),
    }

    response = post_json(f"{BASE_URL}{LOGIN_PATH}", payload, headers, timeout)
    if response.get("code") != 0:
        message = response.get("msg") or response.get("message") or response
        raise RunningHubLoginError(f"login failed: {message}")

    data = response.get("data") or {}
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    if not access_token or not refresh_token:
        raise RunningHubLoginError(f"login succeeded but token fields are missing: {response}")

    return RunningHubToken(
        access_token=access_token,
        refresh_token=refresh_token,
        expire_in=int(data.get("expire_in") or 0),
        identify=data.get("identify"),
        first_login=data.get("firstLogin"),
        raw=response,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Login to RunningHub and print token JSON.")
    parser.add_argument("-u", "--username", default=os.getenv("RUNNINGHUB_USERNAME"), help="mobile number")
    parser.add_argument("-p", "--password", default=os.getenv("RUNNINGHUB_PASSWORD"), help="password")
    parser.add_argument("--timeout", type=int, default=30, help="request timeout seconds")
    parser.add_argument("--save", help="optional path to save token JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    username = args.username or input("RunningHub username/mobile: ").strip()
    password = args.password or getpass.getpass("RunningHub password: ")

    try:
        token = login(username, password, timeout=args.timeout)
    except RunningHubLoginError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    token_json = token.to_dict()
    output = json.dumps(token_json, ensure_ascii=False, indent=2)
    print(output)

    if args.save:
        with open(args.save, "w", encoding="utf-8") as file:
            file.write(output + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

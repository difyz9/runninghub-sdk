"""
获取并打印当前 API Key 的账户状态信息。

This script demonstrates how to use the RunningHub SDK to fetch and display
the account status associated with the provided API key. It prints details
such as remaining credits, running tasks, and balance.

Usage:
    python examples/run_get_account_status.py

Prerequisites:
    - Ensure the `RUNNINGHUB_API_KEY` environment variable is set in a .env file
      in the project's root directory.
"""

import os
from dotenv import load_dotenv
from runninghub_sdk import RunningHubClient


def main():
    """
    主函数，用于获取并打印账户状态。
    """
    # 从 .env 文件加载环境变量
    load_dotenv()

    # 从环境变量获取 API Key
    api_key = os.getenv("RUNNINGHUB_API_KEY")
    if not api_key:
        print("错误：请在 .env 文件中设置 RUNNINGHUB_API_KEY")
        return

    try:
        # 初始化客户端
        client = RunningHubClient(api_key=api_key)

        # 获取账户状态
        print("正在查询账户信息...")
        account_status = client.get_account_status()

        # 打印账户信息
        print("\n✅ 账户信息获取成功！")
        print("--------------------")
        print(f"剩余点数: {account_status.remain_coins}")
        print(f"当前任务数: {account_status.current_task_counts}")
        if account_status.remain_money is not None:
            print(f"剩余金额: {account_status.remain_money} {account_status.currency or ''}")
        print(f"API类型: {account_status.api_type}")
        print("--------------------")

    except Exception as e:
        print(f"\n❌ 操作失败: {e}")


if __name__ == "__main__":
    main()

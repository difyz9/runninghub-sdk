"""
RunningHub SDK 异步测试脚本

测试文本生图功能（异步版本）
"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runninghub_sdk import RunningHubClient, modify_nodes
from runninghub_sdk.config import get_api_key

WORKFLOW_ID = "2033812894801993729"
TEXT_NODE_ID = "6"
INSTANCE_TYPE = "plus"  # 可选: "plus" 使用48G显存机器, None 使用默认24G机器


async def test_async_text_to_image(text: str):
    """异步测试文本生图"""
    print(f"=== 异步测试文本生图 ===")
    print(f"提示词: {text}\n")

    try:
        API_KEY = get_api_key()
    except ValueError as e:
        print(f"错误: {e}")
        return

    async with RunningHubClient(api_key=API_KEY) as client:
        modifier = modify_nodes().text(TEXT_NODE_ID, text)

        print("发起任务...")
        task = await client.async_run_with_modifier(WORKFLOW_ID, modifier, instance_type=INSTANCE_TYPE)
        print(f"任务ID: {task.task_id}\n")

        print("等待完成...")
        outputs = await client.async_wait_for_completion(
            task.task_id,
            poll_interval=3.0,
            on_status_change=lambda s: print(f"  状态: {s}")
        )

        print("\n=== 结果 ===")
        for output in outputs:
            print(f"  链接: {output.file_url}")
            print(f"  类型: {output.file_type}")
            print(f"  耗时: {output.task_cost_time} 秒")
            print(f"  消耗: {output.consume_money} 元")


async def main():
    texts = [
        "a beautiful sunset over mountains",
        "a cute panda eating bamboo",
    ]

    if len(sys.argv) > 1:
        texts = [" ".join(sys.argv[1:])]

    for text in texts:
        await test_async_text_to_image(text)
        print()


if __name__ == "__main__":
    asyncio.run(main())
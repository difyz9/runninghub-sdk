"""
简单测试示例

使用方法:
1. 在项目根目录的 .env 文件中配置 API Key
2. 运行: python test_simple.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runninghub_sdk import RunningHubClient, modify_nodes
from runninghub_sdk.config import get_api_key

# ========== 配置 ==========
WORKFLOW_ID = "2033812894801993729"
TEXT_NODE_ID = "6"
PROMPT = "胸部饱满的少女，穿着黄色比基尼，在田野里荡秋千，秋千高高的荡起，开心的笑，画面唯美梦幻"
INSTANCE_TYPE = "plus"  # 可选: "plus" 使用48G显存机器, None 使用默认24G机器
# ============================


def main():
    # 从配置文件获取 API Key
    try:
        API_KEY = get_api_key()
    except ValueError as e:
        print(f"\n错误: {e}\n")
        print("配置方法:")
        print("  1. 复制 .env.example 为 .env")
        print("  2. 在 .env 中设置 RUNNINGHUB_API_KEY=your-api-key")
        print()
        return

    print("=" * 50)
    print("RunningHub SDK 文本生图测试")
    print("=" * 50)
    print(f"Workflow ID: {WORKFLOW_ID}")
    print(f"文本节点: {TEXT_NODE_ID}")
    print(f"提示词: {PROMPT}")
    print("=" * 50)
    print()

    with RunningHubClient(api_key=API_KEY) as client:
        # 设置文本
        modifier = modify_nodes().text(TEXT_NODE_ID, PROMPT)

        # 发起任务
        print("[1/3] 发起任务...")
        task = client.run_with_modifier(
            WORKFLOW_ID,
            modifier,
            instance_type=INSTANCE_TYPE
        )
        print(f"      任务ID: {task.task_id}")
        if INSTANCE_TYPE:
            print(f"      实例类型: {INSTANCE_TYPE}")

        # 等待完成
        print("[2/3] 等待生成...")
        outputs = client.wait_for_completion(
            task.task_id,
            poll_interval=3.0,
            timeout=300.0,
        )

        # 输出结果
        print("[3/3] 完成!")
        print()
        print("-" * 50)
        print("生成结果:")
        print(outputs)
        print("-" * 50)

        for i, output in enumerate(outputs, 1):
            print(f"\n图片 {i}:")
            print(f"  链接: {output.file_url}")
            print(f"  类型: {output.file_type}")
            print(f"  耗时: {output.task_cost_time} 秒")
            print(f"  消耗: {output.consume_money} 元")

        print()
        print("=" * 50)
        print("测试完成!")
        print("=" * 50)


if __name__ == "__main__":
    main()
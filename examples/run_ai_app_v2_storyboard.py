"""Run the provided openapi/v2/run/ai-app task via the SDK.

This example mirrors the user's curl request with the existing SDK method
`run_model_api()`, then waits for completion through `/openapi/v2/query`.

Environment:
    The script will load the repository root `.env` first.

Required environment variables:
    RUNNINGHUB_API_KEY

Optional overrides:
    RUNNINGHUB_AI_APP_V2_ID
    RUNNINGHUB_AI_APP_V2_POLL_INTERVAL
    RUNNINGHUB_AI_APP_V2_TIMEOUT

Usage:
    PYTHONPATH=src python examples/run_ai_app_v2_storyboard.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from runninghub_sdk import RunningHubClient, TaskStatus, load_env_file
from runninghub_sdk.exceptions import RunningHubError


DEFAULT_AI_APP_ID = "2016407933692678145"


def bootstrap_env() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_env_file(env_path)


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def build_payload() -> Dict[str, Any]:
    novel_content = """周围的人越聚越多，他们都听到了电话听筒里传出来的声音。
在场众人都惊呆了。
林家虽不是海城首富，却也是海城数得上号的豪门。
豪门子女，每个月有几十万几百万零用钱是非常正常的。
他们还从来都没有听说过哪家豪门千金，每个月连一毛钱零用钱都没有的。
林家是独一份。
难怪林浅穿的这么寒酸，参加宴会连件像样的礼服都没有。
就算不在身边养大，但到底是林家的真千金，亲生孩子一分不给，养女却每个月给一百万千娇万宠着。
林家能允许这么炸裂的事发声，想来这一家子也是拎不清的。
宾客们窃窃私语，林彦书只觉如芒在背，一张脸羞愤的通红。
他不相信这种丢脸的事情会发生在林家。
他们林家家大业大，还不至于连区区几十万零用钱都吝啬给血肉至亲。
林彦书当即冷声质问林浅，“就算财务没有给你打钱，爸妈肯定会给你零用钱吧。”
林浅面露讥讽，目光看向人群中的林父林母，淡淡道，“林先生和林夫人有没有给我零用钱，林大少不妨亲自问问他们，毕竟我的话你不相信，你爸妈的话你肯定会相信。”
林父林母身子猛然一僵，羞愧的不敢与她对视。
“爸，妈，你们一定给过她零用钱，对不对？”林彦书认真的看着他们。
林父眼神闪躲，“我以为你们会给她，所以我就......”
林母满目愧疚，眼泪在眼眶中打转，心疼道，“我也以为你们会......浅浅，你没钱怎么不早说，你要是早点告诉妈妈，妈妈肯定会给你钱的。”
“都是妈妈不好，妈妈没有早点发现才让你受了委屈，但你要相信妈妈对你和对婉儿是一视同仁的。”
林浅似笑非笑的看着她，在她淡漠的目光下，林母尴尬地垂下了眸子。
林浅也是今天才知道，原来是自己的亲生母亲禁止财务给她打钱，这还不算，她竟还把林婉儿的零用钱提到了一百万，生怕委屈了她的宝贝养女。
如此厚此薄彼，她还好意思说一视同仁。
堂堂豪门贵妇，吃穿用度皆是上乘，随便一双袜子都要大几百块，她会看不出自己亲生女儿从头到脚加起来不超过一百块的衣服面料好坏？
她不是看不到，她只是不在意。
道歉，也不过是在外人面前惺惺作态。
好在，她早看清了这一家子人的丑恶嘴脸，她的这颗心早已淬炼的百毒不侵，不对他们抱有期待她便坚不可摧。
眼见着林浅对母亲的道歉置若罔闻，众目睽睽之下让林家颜面尽失，林彦书才生出的那一点点愧疚顿时荡然无存。
他冷声呵斥，“长了一张嘴你不会说吗？我们又不是你肚子里的蛔虫，谁知道你心里想的是什么，你要是早说，我们还能缺了你钱花不成？”
“我说了。”林浅声音很轻却透着冷意，“只是你们没当回事。”
林彦书蹙眉，刚要否认，脑海中突然浮现一段记忆。
那是一个午后，他们一家四口围坐在沙发上有说有笑。
林浅扭捏着走过来，她死死抓着校服衣摆，还未说话，脸就先涨得通红。
她憋了好半天，才轻声说，“爸，妈，你们能不能给我五千，学费......”
“啪！”
他一把将手里的报纸摔在茶几上，怒视着林浅指责，“钱钱钱，你就知道钱，你回到这个家就是为了要钱来的是吗？如果林家没钱你是不是就不回来了？真不知道爸妈非要把你接回来干什么。”
“你要是没什么事就多看看书，高一的第一次月考婉儿拿了全校第十名，你第几名？”
“我、我第一......”
“行了行了，倒数第一你还好意思拿出来说。”
他都已经让财务给她的银行卡每个月打五十万了，她居然狮子大开口，张口就要五千万。
婉儿都没有这么多钱，她也不看看自己凭什么。
林浅的眼泪顿时流了下来，像是受了天大的委屈。
他只觉得烦躁，连看财经报纸的心情都没有了。
还好婉儿懂事，摇着他的胳膊撒娇，“哥哥我这次考了第十名，你有没有奖励啊？”
他怎抵得住软萌可爱的小妹撒娇，顿时就把林浅带来的不痛快抛到脑后，捏着她的小脸，宠溺道，“婉儿想要什么奖励？”
“我看上了一个价值十万的包包，哥哥给我买好不好？”
“好好好，只要婉儿喜欢，别说十万，就是一百万也给你买。”
哄完林婉儿，他又不悦的训斥林浅，“你还杵在这干什么？还不回自己房间好好学习。”
林浅委屈至极，转身跑了。
林父林母同时叹息。
“要是浅浅有婉儿一半懂事就好了。”
......
......
“林大少可是想起来了？”
林浅的声音拉回他的思绪，他整颗心都被她那一声声的林大少撕扯的鲜血淋漓。
他是她的哥哥，亲哥哥，不是什么林大少。
可自她出狱，她连一声哥哥都不愿意叫了。
他沉着眸子，恼恨道，“还不是因为你学习太差，考个倒数第一，你好意思要钱，我都不好意思奖励你。”
闻言，林浅的眸子越发清冷，被这样一双无情的眼神看着，林彦书竟莫名心虚，他咬牙喝道，“说你两句，你还不服气。”
“高中三年，我的成绩年年蝉联年级第一，怎么到了林大少嘴里就成了年级倒数第一了？”
眼看着林彦书露出不可置信的表情，林浅勾唇冷笑，心里生出了一抹报复的快感，“也对，林大少连我在哪个学校上学都不知道，不清楚我的学习成绩也是情有可原。”
林彦书如遭雷击，呆立当场。
他仿佛听到了什么天方夜谭，声音带着一丝不易察觉的沙哑，“你难道不是在盛辉高中上学？”
盛辉是海城最好的贵族高中，林婉儿就是从盛辉毕业的，凡是海城有钱有权人家的孩子，都会选择把孩子送到这所高中。
林彦书想当然的认为林浅也在盛辉上学。
他猛地看向林父林母，声音颤抖的厉害，“爸，妈，林浅回来后，你们有没有把她的学籍迁过来？”
......
林父的脸涨得通红，他张了张嘴，却只发出几个含混不清的音节，像是被抽去了脊骨一般，往日的威严荡然无存。
林母则是嘴唇微微颤抖，眼神中满是惊惶与无措，那精心打理的妆容此刻也掩不住脸上的难堪。
两人就这么僵立在原地，周围的空气仿佛都凝固了。
林彦书的脸色一寸一寸变白，过往对林浅的认知如大厦倾颓，那些曾经笃定的轻视与不屑，此刻都化为了锋利的刀刃，无情地刺向他自己。
他差点找不到自己的声音，喉咙像是被人死死掐住，发出的声音异常颤抖，“浅浅，高中三年，你到底在哪上的？”"""

    node_info_list: List[Dict[str, Any]] = [
        {
            "nodeId": "209",
            "fieldName": "string",
            "fieldValue": "中国现代时尚都市小说题材",
            "description": "小说题材（可以留空自动识别）",
        },
        {
            "nodeId": "418",
            "fieldName": "string",
            "fieldValue": "所有的角色和角色的造型",
            "description": "提取目标（角色、造型、道具、场景）",
        },
        {
            "nodeId": "409",
            "fieldName": "select",
            "fieldValue": "1",
            "description": "绘画风格选择",
        },
        {
            "nodeId": "226",
            "fieldName": "select",
            "fieldValue": "4",
            "description": "渲染选择",
        },
        {
            "nodeId": "506",
            "fieldName": "select",
            "fieldValue": "1",
            "description": "强度选择（可选1-8级，自定义调下面数值）",
        },
        {
            "nodeId": "500",
            "fieldName": "value",
            "fieldValue": "0.5000000000000001",
            "description": "渲染强度（强度选择1时可自行调节）",
        },
        {
            "nodeId": "437",
            "fieldName": "select",
            "fieldValue": "2",
            "description": "布局选择",
        },
        {
            "nodeId": "321",
            "fieldName": "string",
            "fieldValue": novel_content,
            "description": "小说/文案/内容",
        },
    ]

    return {
        "nodeInfoList": node_info_list,
        "instanceType": "default",
        "usePersonalQueue": "false",
    }


def print_request_preview(payload: Dict[str, Any], ai_app_id: str) -> None:
    print_section("1. Request Preview")
    print("endpoint:", f"/openapi/v2/run/ai-app/{ai_app_id}")
    print("node_count:", len(payload["nodeInfoList"]))
    for item in payload["nodeInfoList"]:
        print(
            f"node_id={item['nodeId']} | field_name={item['fieldName']} | "
            f"description={item.get('description', '')}"
        )


def submit_task(client: RunningHubClient, ai_app_id: str, payload: Dict[str, Any]) -> str:
    print_section("2. Submit Task")
    result = client.run_model_api(f"/openapi/v2/run/ai-app/{ai_app_id}", payload)
    print("task_id:", result.task_id)
    print("status:", result.status)
    print("error_code:", result.error_code)
    print("error_message:", result.error_message)
    return result.task_id


def wait_for_result(client: RunningHubClient, task_id: str) -> None:
    poll_interval = float(os.getenv("RUNNINGHUB_AI_APP_V2_POLL_INTERVAL", "5"))
    timeout = float(os.getenv("RUNNINGHUB_AI_APP_V2_TIMEOUT", "1800"))
    last_status: TaskStatus | None = None

    def on_status_change(status: TaskStatus) -> None:
        nonlocal last_status
        if status != last_status:
            print(f"status -> {status}")
            last_status = status

    print_section("3. Wait For Completion")
    result = client.wait_for_query_v2_completion(
        task_id,
        poll_interval=poll_interval,
        timeout=timeout,
        on_status_change=on_status_change,
    )

    print_section("4. Results")
    print("status:", result.status)
    print("error_code:", result.error_code)
    print("error_message:", result.error_message)
    print("results:", result.results)


def main() -> int:
    bootstrap_env()
    api_key = get_required_env("RUNNINGHUB_API_KEY")
    ai_app_id = os.getenv("RUNNINGHUB_AI_APP_V2_ID", DEFAULT_AI_APP_ID).strip()
    payload = build_payload()

    print_request_preview(payload, ai_app_id)

    try:
        with RunningHubClient(api_key=api_key) as client:
            task_id = submit_task(client, ai_app_id, payload)
            wait_for_result(client, task_id)
    except RunningHubError as exc:
        print(f"AI App V2 task failed: {exc}", file=sys.stderr)
        return 1

    print_section("Done")
    print("AI App V2 task finished successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
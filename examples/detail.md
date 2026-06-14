
https://www.runninghub.cn/api/webapp/detail

参数为账号密码登录后的Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyMDEzNDE1ODkwMzY4MDczNzI5IiwiZXhwIjoxNzgzMDM3NDY2LCJjcmVhdGVkIjoxNzgwNDQ1NDY2NTM1LCJ1c2VybmFtZSI6ImM5MTUzMWNiZjMzMzdmYmU5OTg2MTJkYTQxMTJlYTk5IiwidXNlclJlZ2lvbiI6InpoX0NOIn0.9O8ERY0TdOyhD1V-xIkvds9UtgzLN9JBWWgnbIYHEokknzRsNd3BY_8gZ_VrOSpeMMW--alhSG5giAlg8RX-2g


请求体：
{"webappId":"2059941104472125442"}


返回值：

{
    "code": 0,
    "msg": "success",
    "errorMessages": null,
    "data": {
        "id": "2059941104472125442",
        "workflowId": null,
        "name": "文生图2.0",
        "tags": [
            {
                "id": "1871151815242543197",
                "name": "文生图",
                "nameEn": "Text-to-Image",
                "labels": null
            }
        ],
        "owner": {
            "id": "1992787680532586498",
            "avatar": "https://rh-images.xiaoyaoyou.com/default_head_icon.png",
            "name": "user_8i4cwvh9"
        },
        "publishTime": "2026-05-28T10:13:26.000+00:00",
        "updateTime": "2026-05-28T10:13:26.000+00:00",
        "inputNodes": [
            {
                "nodeId": "18",
                "nodeName": "RH_RhartImageG2TextToImage",
                "fieldName": "aspectRatio",
                "fieldValue": "9:16",
                "fieldData": "[[\"empty\", \"3:2\", \"1:1\", \"2:3\", \"5:4\", \"4:5\", \"16:9\", \"9:16\", \"21:9\", \"3:4\", \"4:3\"], {\"default\": \"empty\"}]",
                "fieldType": "LIST",
                "description": "aspectRatio",
                "descriptionCn": null,
                "descriptionEn": "aspectRatio"
            },
            {
                "nodeId": "18",
                "nodeName": "RH_RhartImageG2TextToImage",
                "fieldName": "resolution",
                "fieldValue": "2k",
                "fieldData": "[[\"1k\", \"2k\", \"4k\"], {\"default\": \"1k\"}]",
                "fieldType": "LIST",
                "description": "resolution",
                "descriptionCn": null,
                "descriptionEn": "resolution"
            },
            {
                "nodeId": "18",
                "nodeName": "RH_RhartImageG2TextToImage",
                "fieldName": "prompt",
                "fieldValue": "\n\n请创作一张竖版高完成度「神话人物破框立像档案 / 3D Mythic Breakout Character Poster」。\n\n【主题人物】：【海贼王】动漫里的角色【女帝】\n【人物身份】：【女帝】\n【神话背景】：【海贼王】\n【核心关键词】：【女帝】\n【主色调】：【蓝色】\n【前景破框道具】：【情书】\n【标志性场景】：【大海】\n\n画面结构：\n中央是一位完整全身、超写实、电影级3D神话人物，占据最大视觉权重。\n人物必须真实、立体、材质细节丰富，不能卡通化，不能普通插画化。\n\n人物的手部、武器、法器或关键道具必须朝观者方向强烈前冲，形成明显近大远小、破框而出的3D视觉冲击。\n前景道具必须完整可见、清晰可辨识，不能被裁切或变形。\n\n人物四周布置 6–8 组轻质悬浮神话事件簇。\n事件簇不是厚卡片，而是半透明玻璃感、薄型亚克力感、带流光边框、细金线、几何线条、微发光边缘的神话信息切片。\n每组可包含：节点标题、简短说明、小型名场面碎片图、编号、连接线和神话符号。\n事件簇要多角度悬浮、错位叠层，有空间裂变感，但不能遮挡主角和前景道具。\n\n左侧设置大字【人物姓名】，使用东方神话感书法 / 碑刻 / 墨迹字体。\n旁边只放少量身份标签和关键词，不要放大段系列标题。\n\n底部设置轻量化神话索引线，用细金线、小圆点和简短节点串联人物关键路径，不要做厚重底栏。\n\n背景使用浅色古纸、神话卷轴、云雾、法阵、宫阙、山海、战场、水浪、火焰、古寺或对应场景元素。\n中央人物要“重、实、强”，四周信息要“轻、薄、透、悬浮”，形成强烈设计反差。\n\n整体效果要求：\n电影级神话主视觉、高端信息设计感、强烈3D破框冲击、神话氛围浓、画面清晰、完成度高、适合作为同系列人物海报持续复用。",
                "fieldData": "[\"STRING\", {\"default\": \"\", \"multiline\": true}]",
                "fieldType": "STRING",
                "description": "prompt",
                "descriptionCn": null,
                "descriptionEn": "prompt"
            }
        ],
        "description": "<p>调用一次0.1元</p>",
        "webappState": 1,
        "workflowState": 0,
        "covers": [
            {
                "id": "2059941109882777601",
                "objName": "c8665ebe72fcb11e1794a626fff87051/2026-05-28/463c451b3699bb9c71051673430163f5.png",
                "url": "https://rh-images.xiaoyaoyou.com/c8665ebe72fcb11e1794a626fff87051/2026-05-28/463c451b3699bb9c71051673430163f5.png",
                "thumbnailUri": "https://rh-images.xiaoyaoyou.com/c8665ebe72fcb11e1794a626fff87051/2026-05-28/463c451b3699bb9c71051673430163f5.png?imageMogr2/format/jpg/ignore-error/1",
                "imageWidth": "760",
                "imageHeight": "1354"
            }
        ],
        "chineseCovers": [
            {
                "id": "2059941109882777601",
                "objName": "c8665ebe72fcb11e1794a626fff87051/2026-05-28/463c451b3699bb9c71051673430163f5.png",
                "url": "https://rh-images.xiaoyaoyou.com/c8665ebe72fcb11e1794a626fff87051/2026-05-28/463c451b3699bb9c71051673430163f5.png",
                "thumbnailUri": "https://rh-images.xiaoyaoyou.com/c8665ebe72fcb11e1794a626fff87051/2026-05-28/463c451b3699bb9c71051673430163f5.png?imageMogr2/format/jpg/ignore-error/1",
                "imageWidth": "760",
                "imageHeight": "1354"
            }
        ],
        "englishCovers": [
            {
                "id": "2059941554504167426",
                "objName": "c8665ebe72fcb11e1794a626fff87051/9d612e6287164b40aa43347f8596b0d1.webp",
                "url": "https://rh-images.xiaoyaoyou.com/c8665ebe72fcb11e1794a626fff87051/9d612e6287164b40aa43347f8596b0d1.webp",
                "thumbnailUri": "https://rh-images.xiaoyaoyou.com/c8665ebe72fcb11e1794a626fff87051/9d612e6287164b40aa43347f8596b0d1.webp?imageMogr2/format/jpg/ignore-error/1",
                "imageWidth": "1023",
                "imageHeight": "1537"
            }
        ],
        "preview": null,
        "curl": null,
        "statisticsInfo": {
            "likeCount": "0",
            "downloadCount": "0",
            "useCount": "7",
            "pv": "0",
            "collectCount": "1"
        },
        "instanceType": "lite",
        "runningSuccessRate": null,
        "avgRunningSeconds": null,
        "popSparkVideo": false,
        "publishAccess": {
            "accessType": 0,
            "publishScope": 0,
            "encrypted": false,
            "granted": true,
            "needPassword": false,
            "owner": false,
            "visibleUsers": []
        },
        "canModifyPublishType": true,
        "canModifyPublishScope": true
    }
}

## SDK 调用方式

```python
from runninghub_sdk import RunningHubClient

# 登录获取用户 token（/api/webapp/detail 需要用户级别 Bearer token）
token = RunningHubClient.login("手机号", "密码")
client = RunningHubClient(api_key=token.access_token)

# 获取 AI App 详情
detail = client.get_webapp_detail("2059941104472125442")

print(f"名称: {detail.name}")
print(f"描述: {detail.description}")

# 输入节点
for node in detail.inputNodes or []:
    print(f"  [{node.nodeId}] {node.fieldName}: {node.fieldValue}")

# 标签
for tag in detail.tags or []:
    print(f"  #{tag.name}")

# 统计信息
stats = detail.statisticsInfo
print(f"使用次数: {stats.use_count}, 收藏: {stats.collect_count}")

# 作者
print(f"作者: {detail.owner.name}")

# 异步调用
import asyncio

async def main():
    async with RunningHubClient(api_key=token.access_token) as client:
        detail = await client.async_get_webapp_detail("2059941104472125442")
        print(detail.name)

asyncio.run(main())
```
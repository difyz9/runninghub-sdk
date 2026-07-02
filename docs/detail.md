https://www.runninghub.cn/api/webapp/detail

{"webappId":"2035369813215813634"}


{
    "code": 0,
    "msg": "success",
    "errorMessages": null,
    "data": {
        "id": "2035369813215813634",
        "workflowId": null,
        "name": "LTX2.3图生视频【优化版】",
        "tags": [
            {
                "id": "1871151815242543200",
                "name": "文生视频",
                "nameEn": "Text-to-Video",
                "labels": null
            },
            {
                "id": "1871151815242543199",
                "name": "图生视频",
                "nameEn": "Image-to-Video",
                "labels": null
            }
        ],
        "owner": {
            "id": "2029791031435993089",
            "avatar": "https://rh-images.xiaoyaoyou.com/default_head_icon.png",
            "name": "慢跑者"
        },
        "publishTime": "2026-06-27T12:03:53.000+00:00",
        "updateTime": "2026-06-27T12:03:53.000+00:00",
        "inputNodes": [
            {
                "nodeId": "191",
                "nodeName": "LoadImage",
                "fieldName": "image",
                "fieldValue": "b170588b06162448b4af1ef5a44bcaa7c82b80bcff31a787a280fed9144c8ea6.png",
                "fieldData": "[[\"example.png\", \"None\", \"example.png\", \"keep_this_dic\"], {\"image_upload\": true}]",
                "fieldType": "IMAGE",
                "description": "image",
                "descriptionCn": null,
                "descriptionEn": "image"
            },
            {
                "nodeId": "58",
                "nodeName": "Int",
                "fieldName": "value",
                "fieldValue": "8",
                "fieldData": "[\"INT\", {\"default\": 0}]",
                "fieldType": "INT",
                "description": "时长",
                "descriptionCn": null,
                "descriptionEn": "Duration"
            },
            {
                "nodeId": "185",
                "nodeName": "ImpactSwitch",
                "fieldName": "select",
                "fieldValue": "2",
                "fieldData": "[{\"name\":\"input2\",\"index\":2.0,\"description\":\"qwen 大模型生成内容\",\"fastIndex\":2.0,\"descriptionEn\":\"qwen large model generates content\"},{\"name\":\"input1\",\"index\":1.0,\"description\":\"用户输入内容\",\"fastIndex\":1.0,\"descriptionEn\":\"User input content\"}]",
                "fieldType": "SWITCH",
                "description": "提示词选择",
                "descriptionCn": null,
                "descriptionEn": "Prompt selection"
            },
            {
                "nodeId": "162",
                "nodeName": "CR Text",
                "fieldName": "text",
                "fieldValue": "",
                "fieldData": "[\"STRING\", {\"default\": \"\", \"multiline\": true}]",
                "fieldType": "STRING",
                "description": "提示词",
                "descriptionCn": null,
                "descriptionEn": "Prompt"
            },
            {
                "nodeId": "116",
                "nodeName": "easy int",
                "fieldName": "value",
                "fieldValue": "1920",
                "fieldData": "[\"INT\", {\"max\": 999999, \"min\": -999999, \"default\": 0}]",
                "fieldType": "INT",
                "description": "长边尺寸",
                "descriptionCn": null,
                "descriptionEn": "Long edge size"
            },
            {
                "nodeId": "193",
                "nodeName": "ImpactSwitch",
                "fieldName": "select",
                "fieldValue": "3",
                "fieldData": "[{\"name\":\"input8\",\"index\":8.0,\"description\":\"通用\",\"fastIndex\":8.0,\"descriptionEn\":\"General\"},{\"name\":\"input7\",\"index\":7.0,\"description\":\"固定镜头\",\"fastIndex\":7.0,\"descriptionEn\":\"Fixed lens\"},{\"name\":\"input6\",\"index\":6.0,\"description\":\"镜头下降\",\"fastIndex\":6.0,\"descriptionEn\":\"The camera moves down\"},{\"name\":\"input5\",\"index\":5.0,\"description\":\"镜头上升\",\"fastIndex\":5.0,\"descriptionEn\":\"Camera rises\"},{\"name\":\"input4\",\"index\":4.0,\"description\":\"镜头向右运动\",\"fastIndex\":4.0,\"descriptionEn\":\"The camera moves to the right\"},{\"name\":\"input3\",\"index\":3.0,\"description\":\"镜头向左运动\",\"fastIndex\":3.0,\"descriptionEn\":\"The camera moves to the left\"},{\"name\":\"input2\",\"index\":2.0,\"description\":\"镜头拉远\",\"fastIndex\":2.0,\"descriptionEn\":\"Camera pull back\"},{\"name\":\"input1\",\"index\":1.0,\"description\":\"镜头推进\",\"fastIndex\":1.0,\"descriptionEn\":\"Camera push-in\"}]",
                "fieldType": "SWITCH",
                "description": "运镜选择",
                "descriptionCn": null,
                "descriptionEn": "Camera movement selection"
            }
        ],
        "description": "<p>上传图片，生成高质视频(默认是Qwen大模型自动生成提示词，如果自己输入提示词，请在提示词选择处选择“用户输入内容”)</p>",
        "webappState": 1,
        "workflowState": 0,
        "covers": [
            {
                "id": "2035929785888677890",
                "objName": "0062d63e56b6112c1cfdd453d72e272f/2026-03-23/07ae0a9fb2947862eac3ede7327c323d.mp4",
                "url": "https://rh-images.xiaoyaoyou.com/0062d63e56b6112c1cfdd453d72e272f/2026-03-23/07ae0a9fb2947862eac3ede7327c323d.mp4",
                "thumbnailUri": "https://rh-images.xiaoyaoyou.com/0062d63e56b6112c1cfdd453d72e272f/2026-03-23/07ae0a9fb2947862eac3ede7327c323d.mp4?imageMogr2/format/jpeg/ignore-error/1",
                "imageWidth": null,
                "imageHeight": null
            }
        ],
        "chineseCovers": [
            {
                "id": "2035929785888677890",
                "objName": "0062d63e56b6112c1cfdd453d72e272f/2026-03-23/07ae0a9fb2947862eac3ede7327c323d.mp4",
                "url": "https://rh-images.xiaoyaoyou.com/0062d63e56b6112c1cfdd453d72e272f/2026-03-23/07ae0a9fb2947862eac3ede7327c323d.mp4",
                "thumbnailUri": "https://rh-images.xiaoyaoyou.com/0062d63e56b6112c1cfdd453d72e272f/2026-03-23/07ae0a9fb2947862eac3ede7327c323d.mp4?imageMogr2/format/jpeg/ignore-error/1",
                "imageWidth": null,
                "imageHeight": null
            }
        ],
        "englishCovers": [],
        "preview": null,
        "curl": null,
        "statisticsInfo": {
            "likeCount": "7",
            "downloadCount": "0",
            "useCount": "899",
            "pv": "0",
            "collectCount": "33"
        },
        "instanceType": null,
        "runningSuccessRate": "100",
        "avgRunningSeconds": "296",
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
https://www.runninghub.cn/api/openapi/my/call/log/detail

请求体
{"taskId":"2066351966031925250","userId":"2013415890368073729"}

返回值：


{
    "code": 0,
    "msg": "success",
    "errorMessages": null,
    "data": {
        "basicInfo": {
            "apiName": "一键漫剧分镜流（免费版）",
            "apiType": "API",
            "apiKeyType": "1",
            "taskStatus": "SUCCESS",
            "taskId": "2066351966031925250",
            "callTime": "2026-06-15 10:47:54",
            "duration": "121",
            "amount": null,
            "coinNum": "25"
        },
        "list": [
            {
                "outputName": "ComfyUI_00001_aitpc_1781491790.png",
                "outputType": "png",
                "fileUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00001_aitpc_1781491790.png",
                "filePreviewUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00001_aitpc_1781491790.png?imageMogr2/format/jpeg/ignore-error/1"
            },
            {
                "outputName": "ComfyUI_00002_piiyg_1781491790.png",
                "outputType": "png",
                "fileUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00002_piiyg_1781491790.png",
                "filePreviewUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00002_piiyg_1781491790.png?imageMogr2/format/jpeg/ignore-error/1"
            },
            {
                "outputName": "ComfyUI_00003_anuyf_1781491791.png",
                "outputType": "png",
                "fileUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00003_anuyf_1781491791.png",
                "filePreviewUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00003_anuyf_1781491791.png?imageMogr2/format/jpeg/ignore-error/1"
            },
            {
                "outputName": "ComfyUI_00004_jcjoy_1781491791.png",
                "outputType": "png",
                "fileUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00004_jcjoy_1781491791.png",
                "filePreviewUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00004_jcjoy_1781491791.png?imageMogr2/format/jpeg/ignore-error/1"
            },
            {
                "outputName": "ComfyUI_00005_puyit_1781491791.png",
                "outputType": "png",
                "fileUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00005_puyit_1781491791.png",
                "filePreviewUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00005_puyit_1781491791.png?imageMogr2/format/jpeg/ignore-error/1"
            },
            {
                "outputName": "ComfyUI_00006_yqdrl_1781491791.png",
                "outputType": "png",
                "fileUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00006_yqdrl_1781491791.png",
                "filePreviewUrl": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00006_yqdrl_1781491791.png?imageMogr2/format/jpeg/ignore-error/1"
            }
        ],
        "costInfo": {
            "amount": null,
            "coinNum": "25"
        },
        "requestInfo": {
            "apiRequestParams": "{\"apiKey\":\"e21352d73fd845c7b59ae8ba8009e3d8\",\"randomSeed\":true,\"workflowId\":\"2013908081847046145\",\"addMetadata\":true,\"nodeInfoList\":[{\"nodeId\":\"115\",\"fieldName\":\"image\",\"fieldValue\":\"https://rh-images-switch-1252422369.cos.ap-guangzhou.myqcloud.com/input/openapi/369d4e941b92c3d58dc6d81cbf5b527502021cb2c8c2aa99c7fa5883a0e0c110.png?q-sign-algorithm=sha1&q-ak=AKIDv56FISEJUsKsMeELk0gmbNCGKTYSaZ3N&q-sign-time=1781491673%3B1781578073&q-key-time=1781491673%3B1781578073&q-header-list=host&q-url-param-list=&q-signature=a414edb047453061d615d8b47afbc5ac89a4df8d\"},{\"nodeId\":\"118\",\"fieldName\":\"image\",\"fieldValue\":\"https://rh-images-switch-1252422369.cos.ap-guangzhou.myqcloud.com/input/openapi/14fd254dca1ce3527ed9aa676328d65ec8a48859968af82bd7d1b06b812f8d95.jpeg?q-sign-algorithm=sha1&q-ak=AKIDv56FISEJUsKsMeELk0gmbNCGKTYSaZ3N&q-sign-time=1781491674%3B1781578074&q-key-time=1781491674%3B1781578074&q-header-list=host&q-url-param-list=&q-signature=03e93409966b78cc4a1e157480ea7c89b6c29590\"},{\"nodeId\":\"1\",\"fieldName\":\"prompt\",\"fieldValue\":\"Slot 1: 纯黑缓冲帧，无画面内容。\\n\\nSlot 2: 环境：清晨校园主路，两侧樱花树，阳光透过树叶洒下斑驳光影。主体：男生穿着白衬衫，背着书包，正朝前走来。动作：脚步轻快，微微低头看手机。情绪：轻松自在。镜头：中景跟拍，从侧面平视，虚化背景突出人物。\\n\\nSlot 3: 环境：校园草坪边的长椅旁，一棵大樱花树，花瓣飘落。主体：女生穿着连衣裙，坐在长椅上低头看书。动作：翻动书页，发丝被微风吹起。情绪：专注而恬静。镜头：中景，从男生视角的过肩镜头，带出女生侧影。\\n\\nSlot 4: 环境：同上，但焦点在男生面部。主体：男生停下脚步，抬头看向女生方向。动作：眼睛睁大，嘴角微微上扬。情绪：惊讶与心动。镜头：近景特写男生脸部，背景虚化成淡淡粉色花影。\\n\\nSlot 5: 环境：女生抬头，两人视线相交。主体：两人面对面，相隔约十米。动作：女生合上书本，微微歪头；男生下意识举手想打招呼又放下。情绪：羞涩而温暖。镜头：中全景，两人各占画面一侧，中间留出樱花飘落的通透空间。\\n\\nSlot 6: 环境：光线柔和，花瓣飘近镜头。主体：两人相视微笑，脸颊微红。动作：同时轻轻点头示意。情绪：甜蜜的初遇。镜头：特写两人眼神交流，浅景深，仅清晰呈现眼睛和微笑的嘴角。\"},{\"nodeId\":\"50\",\"fieldName\":\"prompt\",\"fieldValue\":\"---参考图1的人物张元清三视图。参考图2的场景。\"},{\"nodeId\":\"48\",\"fieldName\":\"prefix\",\"fieldValue\":\" \"},{\"nodeId\":\"48\",\"fieldName\":\"suffix\",\"fieldValue\":\" \"},{\"nodeId\":\"159\",\"fieldName\":\"添加前缀\",\"fieldValue\":\" \"},{\"nodeId\":\"159\",\"fieldName\":\"添加后缀\",\"fieldValue\":\" \"},{\"nodeId\":\"139\",\"fieldName\":\"string_7\",\"fieldValue\":\" \"},{\"nodeId\":\"139\",\"fieldName\":\"delimiter\",\"fieldValue\":\" \"},{\"nodeId\":\"139\",\"fieldName\":\"string_8\",\"fieldValue\":\" \"},{\"nodeId\":\"71\",\"fieldName\":\"separator\",\"fieldValue\":\" \"},{\"nodeId\":\"96\",\"fieldName\":\"text\",\"fieldValue\":\" \"},{\"nodeId\":\"60\",\"fieldName\":\"separator\",\"fieldValue\":\" \"},{\"nodeId\":\"61\",\"fieldName\":\"separator\",\"fieldValue\":\" \"},{\"nodeId\":\"62\",\"fieldName\":\"separator\",\"fieldValue\":\" \"},{\"nodeId\":\"63\",\"fieldName\":\"separator\",\"fieldValue\":\" \"}],\"retainSeconds\":0,\"usePersonalQueue\":false}"
        },
        "responseInfo": {
            "taskId": "2066351966031925250",
            "status": "SUCCESS",
            "errorCode": "",
            "errorMessage": "",
            "results": [
                {
                    "url": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00001_aitpc_1781491790.png",
                    "nodeId": "117",
                    "outputType": "png",
                    "text": null
                },
                {
                    "url": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00002_piiyg_1781491790.png",
                    "nodeId": "117",
                    "outputType": "png",
                    "text": null
                },
                {
                    "url": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00003_anuyf_1781491791.png",
                    "nodeId": "117",
                    "outputType": "png",
                    "text": null
                },
                {
                    "url": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00004_jcjoy_1781491791.png",
                    "nodeId": "117",
                    "outputType": "png",
                    "text": null
                },
                {
                    "url": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00005_puyit_1781491791.png",
                    "nodeId": "117",
                    "outputType": "png",
                    "text": null
                },
                {
                    "url": "https://rh-images-1252422369.cos.ap-beijing.myqcloud.com/c91531cbf3337fbe998612da4112ea99/output/ComfyUI_00006_yqdrl_1781491791.png",
                    "nodeId": "117",
                    "outputType": "png",
                    "text": null
                }
            ],
            "clientId": "",
            "promptTips": "",
            "failedReason": {},
            "usage": {
                "consumeMoney": null,
                "consumeCoins": "25",
                "taskCostTime": "121",
                "thirdPartyConsumeMoney": null
            },
            "parentTaskId": null,
            "taskUsageList": [
                {
                    "taskId": "2066351966031925250",
                    "parentTaskId": null,
                    "taskStatus": "SUCCESS",
                    "usage": {
                        "consumeMoney": null,
                        "consumeCoins": "25",
                        "taskCostTime": "121",
                        "thirdPartyConsumeMoney": null
                    }
                }
            ]
        }
    }
}
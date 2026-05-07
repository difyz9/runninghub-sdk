
from runninghub_sdk import RunningHubClient

API_KEY = "你的 api key"
WORKFLOW_ID = "2051599273845895169"

node_info_list = [
    {"nodeId": "6", "fieldName": "text", "fieldValue": "这里放角色卡描述"},
    {"nodeId": "3", "fieldName": "seed", "fieldValue": 123456789},
    {"nodeId": "3", "fieldName": "temperature", "fieldValue": 0.7},
    {"nodeId": "3", "fieldName": "model", "fieldValue": "gemini-3.1-pro-preview"},
    {"nodeId": "4", "fieldName": "seed", "fieldValue": 987654321},
    {"nodeId": "4", "fieldName": "aspectRatio", "fieldValue": "16:9"},
    {"nodeId": "4", "fieldName": "resolution", "fieldValue": "2k"},
]

with RunningHubClient(api_key=API_KEY) as client:
    task = client.run(WORKFLOW_ID, node_info_list=node_info_list)
    print(task.task_id)
    outputs = client.wait_for_completion(task.task_id)
    for output in outputs:
        print(output.file_url)
        
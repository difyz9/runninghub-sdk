"""RunningHub Web FastAPI 后端服务"""

import sys
import os
import logging

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 加载根目录的 .env 文件
from dotenv import load_dotenv
env_file = os.path.join(project_root, '.env')
load_dotenv(env_file)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("runninghub-web")

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from runninghub_sdk import RunningHubClient, modify_nodes
from runninghub_sdk.exceptions import RunningHubError

app = FastAPI(title="RunningHub Web API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局客户端（需要配置 API Key）
client: Optional[RunningHubClient] = None

def get_client(api_key: str = None) -> RunningHubClient:
    """获取或创建客户端"""
    global client
    if api_key:
        return RunningHubClient(api_key=api_key)
    if client is None:
        # 从环境变量获取 API Key
        api_key = os.getenv("RUNNINGHUB_API_KEY", "")
        if not api_key:
            raise HTTPException(status_code=500, detail="API Key 未配置，请设置 RUNNINGHUB_API_KEY 环境变量")
        client = RunningHubClient(api_key=api_key)
    return client


# Pydantic 模型
class NodeInput(BaseModel):
    nodeId: str
    fieldName: str
    fieldValue: str | int | bool | float


class CreateTaskRequest(BaseModel):
    workflowId: str
    nodeInfoList: Optional[List[NodeInput]] = None
    addMetadata: bool = True
    webhookUrl: Optional[str] = None
    instanceType: Optional[str] = None
    usePersonalQueue: bool = False
    apiKey: Optional[str] = None


class TaskResponse(BaseModel):
    taskId: str
    taskStatus: str
    clientId: str
    promptTips: str


class OutputResponse(BaseModel):
    fileUrl: str
    fileType: str
    taskCostTime: str
    nodeId: str
    thirdPartyConsumeMoney: Optional[str] = None
    consumeMoney: Optional[str] = None
    consumeCoins: str


@app.get("/")
async def root():
    return {"message": "RunningHub Web API"}


@app.post("/api/run", response_model=TaskResponse)
async def run_task(request: CreateTaskRequest):
    """创建任务"""
    try:
        c = get_client(request.apiKey)
        
        node_list = None
        if request.nodeInfoList:
            node_list = [
                {"nodeId": n.nodeId, "fieldName": n.fieldName, "fieldValue": n.fieldValue}
                for n in request.nodeInfoList
            ]
        
        result = c.run(
            workflow_id=request.workflowId,
            node_info_list=node_list,
            add_metadata=request.addMetadata,
            webhook_url=request.webhookUrl,
            instance_type=request.instanceType,
            use_personal_queue=request.usePersonalQueue,
        )
        
        return TaskResponse(
            taskId=result.task_id,
            taskStatus=result.task_status,
            clientId=result.client_id,
            promptTips=result.prompt_tips,
        )
    except RunningHubError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status/{task_id}")
async def get_status(task_id: str, api_key: str = None):
    """查询任务状态"""
    try:
        c = get_client(api_key)
        status = c.get_status(task_id)
        return status
    except RunningHubError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/outputs/{task_id}", response_model=List[OutputResponse])
async def get_outputs(task_id: str, api_key: str = None):
    """获取任务输出"""
    try:
        c = get_client(api_key)
        outputs = c.get_outputs(task_id)
        return [
            OutputResponse(
                fileUrl=o.file_url,
                fileType=o.file_type,
                taskCostTime=o.task_cost_time,
                nodeId=o.node_id,
                thirdPartyConsumeMoney=o.third_party_consume_money,
                consumeMoney=o.consume_money,
                consumeCoins=o.consume_coins,
            )
            for o in outputs
        ]
    except RunningHubError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cancel/{task_id}")
async def cancel_task(task_id: str, api_key: str = None):
    """取消任务"""
    try:
        c = get_client(api_key)
        c.cancel(task_id)
        return {"message": "Task cancelled"}
    except RunningHubError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), api_key: str = Form(None)):
    """上传文件"""
    try:
        logger.info(f"上传文件请求: filename={file.filename}, content_type={file.content_type}")
        
        c = get_client(api_key)
        content = await file.read()
        logger.info(f"文件内容大小: {len(content)} bytes")
        
        # 使用原始文件名上传
        result = c.upload_file(content, filename=file.filename)
        logger.info(f"上传结果: type={result.type}, file_name={result.file_name}, download_url={result.download_url}, size={result.size}")
        
        if not result.file_name:
            logger.error("上传失败: fileName 为空")
            raise HTTPException(status_code=500, detail="上传失败，服务器未返回文件名")
        
        return {
            "fileName": result.file_name,
            "downloadUrl": result.download_url,
        }
    except RunningHubError as e:
        logger.error(f"RunningHub错误: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"上传异常: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-lora")
async def upload_lora(
    loraName: str = Form(...),
    file: UploadFile = File(...),
    api_key: str = Form(None),
):
    """上传 LoRA"""
    try:
        c = get_client(api_key)
        content = await file.read()
        file_name = c.upload_lora(loraName, content)
        return {"fileName": file_name}
    except RunningHubError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/workflow/{workflow_id}")
async def get_workflow(workflow_id: str, api_key: str = None):
    """获取工作流 JSON"""
    try:
        c = get_client(api_key)
        workflow = c.get_workflow_json_parsed(workflow_id)
        return workflow
    except RunningHubError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 节点类型到可配置字段的映射（只保留文本、图片、视频、音频节点）
NODE_CONFIGURABLE_FIELDS = {
    # 文本节点
    "CLIPTextEncode": [
        {"fieldName": "text", "fieldType": "STRING", "description": "文本内容"}
    ],
    # 图片节点
    "LoadImage": [
        {"fieldName": "image", "fieldType": "IMAGE", "description": "输入图片"}
    ],
    # 视频节点
    "VHS_LoadVideo": [
        {"fieldName": "video", "fieldType": "VIDEO", "description": "输入视频"}
    ],
    # 音频节点
    "LoadAudio": [
        {"fieldName": "audio", "fieldType": "AUDIO", "description": "输入音频"}
    ],
}


def detect_node_type(class_type: str, inputs: dict, node_title: str) -> list:
    """智能检测节点类型，返回可配置字段列表"""
    
    # 文本节点检测
    if class_type == "CLIPTextEncode" or "text" in inputs:
        return [{"fieldName": "text", "fieldType": "STRING", "description": "文本内容"}]
    
    # 图片节点检测
    if class_type == "LoadImage" or ("image" in inputs and not isinstance(inputs.get("image"), list)):
        return [{"fieldName": "image", "fieldType": "IMAGE", "description": "输入图片"}]
    
    # 视频节点检测
    if class_type == "VHS_LoadVideo" or "video" in inputs or "加载视频" in node_title:
        return [{"fieldName": "video", "fieldType": "VIDEO", "description": "输入视频"}]
    
    # 音频节点检测
    if class_type == "LoadAudio" or "audio" in inputs:
        return [{"fieldName": "audio", "fieldType": "AUDIO", "description": "输入音频"}]
    
    # 其他节点不提取参数
    return []


@app.get("/api/workflow/{workflow_id}/params")
async def get_workflow_params(workflow_id: str, api_key: str = None):
    """获取工作流可配置参数列表（只提取文本、图片、视频、音频节点）"""
    try:
        c = get_client(api_key)
        workflow = c.get_workflow_json_parsed(workflow_id)
        
        params = []
        for node_id, node_data in workflow.items():
            class_type = node_data.get("class_type", "")
            inputs = node_data.get("inputs", {})
            meta = node_data.get("_meta", {})
            node_title = meta.get("title", class_type)
            
            # 智能检测节点类型
            configurable = detect_node_type(class_type, inputs, node_title)
            
            for field_config in configurable:
                field_name = field_config["fieldName"]
                field_type = field_config["fieldType"]
                
                # 获取默认值，跳过连接类型的输入（如 ["4", 0]）
                default_value = inputs.get(field_name)
                if isinstance(default_value, list):
                    continue
                
                param = {
                    "nodeId": node_id,
                    "nodeName": node_title,
                    "classType": class_type,
                    "fieldName": field_name,
                    "fieldType": field_type,
                    "defaultValue": default_value,
                    "description": field_config.get("description", field_name),
                }
                
                params.append(param)
        
        return {
            "workflowId": workflow_id,
            "params": params
        }
    except RunningHubError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

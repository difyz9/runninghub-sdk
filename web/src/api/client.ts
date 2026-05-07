import type { TaskRequest, TaskResponse, TaskOutput, WorkflowParamsResponse, UploadResponse } from '../types/task';

const API_BASE = '/api';

// 获取工作流参数
export async function getWorkflowParams(workflowId: string, apiKey?: string): Promise<WorkflowParamsResponse> {
  const params = new URLSearchParams();
  if (apiKey) params.append('api_key', apiKey);
  
  const response = await fetch(`${API_BASE}/workflow/${workflowId}/params?${params}`);
  if (!response.ok) {
    throw new Error(`获取工作流参数失败: ${response.statusText}`);
  }
  return response.json();
}

// 创建任务
export async function createTask(request: TaskRequest): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE}/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });
  if (!response.ok) {
    throw new Error(`创建任务失败: ${response.statusText}`);
  }
  return response.json();
}

// 查询任务状态
export async function getTaskStatus(taskId: string, apiKey?: string): Promise<string> {
  const params = new URLSearchParams();
  if (apiKey) params.append('api_key', apiKey);
  
  const response = await fetch(`${API_BASE}/status/${taskId}?${params}`);
  if (!response.ok) {
    throw new Error(`查询状态失败: ${response.statusText}`);
  }
  return response.json();
}

// 获取任务输出
export async function getTaskOutputs(taskId: string, apiKey?: string): Promise<TaskOutput[]> {
  const params = new URLSearchParams();
  if (apiKey) params.append('api_key', apiKey);
  
  const response = await fetch(`${API_BASE}/outputs/${taskId}?${params}`);
  if (!response.ok) {
    throw new Error(`获取输出失败: ${response.statusText}`);
  }
  return response.json();
}

// 取消任务
export async function cancelTask(taskId: string, apiKey?: string): Promise<void> {
  const params = new URLSearchParams();
  if (apiKey) params.append('api_key', apiKey);
  
  const response = await fetch(`${API_BASE}/cancel/${taskId}?${params}`, { method: 'POST' });
  if (!response.ok) {
    throw new Error(`取消任务失败: ${response.statusText}`);
  }
}

// 上传文件
export async function uploadFile(file: File, apiKey?: string): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (apiKey) formData.append('api_key', apiKey);
  
  const response = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`上传文件失败: ${response.statusText}`);
  }
  return response.json();
}

// 上传LoRA
export async function uploadLora(loraName: string, file: File, apiKey?: string): Promise<{ fileName: string }> {
  const formData = new FormData();
  formData.append('loraName', loraName);
  formData.append('file', file);
  if (apiKey) formData.append('api_key', apiKey);
  
  const response = await fetch(`${API_BASE}/upload-lora`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    throw new Error(`上传LoRA失败: ${response.statusText}`);
  }
  return response.json();
}

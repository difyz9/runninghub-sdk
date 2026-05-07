// 工作流参数类型
export interface WorkflowParam {
  nodeId: string;
  nodeName: string;
  classType: string;
  fieldName: string;
  fieldType: 'STRING' | 'INT' | 'FLOAT' | 'SELECT' | 'IMAGE' | 'VIDEO' | 'AUDIO';
  defaultValue: string | number | null;
  description: string;
  options?: string[];
}

export interface WorkflowParamsResponse {
  workflowId: string;
  params: WorkflowParam[];
}

// 任务相关类型
export interface TaskRequest {
  workflowId: string;
  nodeInfoList?: NodeInput[];
  addMetadata?: boolean;
  webhookUrl?: string;
  instanceType?: string;
  usePersonalQueue?: boolean;
  apiKey?: string;
}

export interface NodeInput {
  nodeId: string;
  fieldName: string;
  fieldValue: string | number | boolean;
}

export interface TaskResponse {
  taskId: string;
  taskStatus: string;
  clientId: string;
  promptTips: string;
}

export interface TaskOutput {
  fileUrl: string;
  fileType: string;
  taskCostTime: string;
  nodeId: string;
  thirdPartyConsumeMoney?: string;
  consumeMoney?: string;
  consumeCoins: string;
}

export type TaskStatusType = 'QUEUED' | 'RUNNING' | 'SUCCESS' | 'FAILED';

export interface UploadResponse {
  fileName: string;
  downloadUrl: string;
}

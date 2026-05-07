import { useState } from 'react';
import type { WorkflowParam, NodeInput } from '../types/task';
import { getWorkflowParams, uploadFile, createTask } from '../api/client';

interface WorkflowFormProps {
  onSubmit: (taskId: string) => void;
}

export function WorkflowForm({ onSubmit }: WorkflowFormProps) {
  const [workflowId, setWorkflowId] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [instanceType, setInstanceType] = useState<'default' | 'plus'>('default');
  const [params, setParams] = useState<WorkflowParam[]>([]);
  const [paramValues, setParamValues] = useState<Record<string, string | number>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 加载工作流参数
  const loadParams = async () => {
    if (!workflowId.trim()) {
      setError('请输入工作流ID');
      return;
    }
    setLoading(true);
    setError(null);
    
    try {
      const response = await getWorkflowParams(workflowId, apiKey);
      setParams(response.params);
      
      // 设置默认值
      const defaults: Record<string, string | number> = {};
      response.params.forEach(p => {
        const key = `${p.nodeId}_${p.fieldName}`;
        defaults[key] = p.defaultValue ?? '';
      });
      setParamValues(defaults);
    } catch (e) {
      setError(e instanceof Error ? e.message : '获取参数失败');
      setParams([]);
    } finally {
      setLoading(false);
    }
  };

  // 处理参数值变化
  const handleValueChange = (key: string, value: string | number) => {
    setParamValues(prev => ({ ...prev, [key]: value }));
  };

  // 文件上传
  const handleFileUpload = async (key: string, file: File) => {
    setLoading(true);
    try {
      const result = await uploadFile(file, apiKey);
      setParamValues(prev => ({ ...prev, [key]: result.fileName }));
    } catch (e) {
      setError(e instanceof Error ? e.message : '上传失败');
    } finally {
      setLoading(false);
    }
  };

  // 提交任务
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (params.length === 0) {
      setError('请先加载工作流参数');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // 构建 nodeInfoList
      const nodeInfoList: NodeInput[] = params.map(p => {
        const key = `${p.nodeId}_${p.fieldName}`;
        return {
          nodeId: p.nodeId,
          fieldName: p.fieldName,
          fieldValue: paramValues[key] ?? p.defaultValue ?? '',
        };
      });
      
      const response = await createTask({
        workflowId,
        nodeInfoList,
        apiKey,
        instanceType,
      });
      
      onSubmit(response.taskId);
    } catch (e) {
      setError(e instanceof Error ? e.message : '创建任务失败');
    } finally {
      setLoading(false);
    }
  };

  // 渲染单个参数输入
  const renderParamInput = (param: WorkflowParam) => {
    const key = `${param.nodeId}_${param.fieldName}`;
    const value = paramValues[key] ?? param.defaultValue ?? '';

    switch (param.fieldType) {
      case 'STRING':
        return (
          <textarea
            className="param-input textarea"
            value={value}
            onChange={e => handleValueChange(key, e.target.value)}
            placeholder={param.description}
            rows={3}
          />
        );

      case 'INT':
        return (
          <input
            type="number"
            className="param-input"
            value={value}
            onChange={e => handleValueChange(key, parseInt(e.target.value) || 0)}
            placeholder={param.description}
          />
        );

      case 'FLOAT':
        return (
          <input
            type="number"
            step="0.1"
            className="param-input"
            value={value}
            onChange={e => handleValueChange(key, parseFloat(e.target.value) || 0)}
            placeholder={param.description}
          />
        );

      case 'SELECT':
        return (
          <select
            className="param-input"
            value={value}
            onChange={e => handleValueChange(key, e.target.value)}
          >
            {param.options?.map(opt => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        );

      case 'IMAGE':
      case 'VIDEO':
      case 'AUDIO':
        return (
          <div className="file-upload">
            <input
              type="file"
              accept={param.fieldType === 'IMAGE' ? 'image/*' : param.fieldType === 'VIDEO' ? 'video/*' : 'audio/*'}
              onChange={e => {
                const file = e.target.files?.[0];
                if (file) handleFileUpload(key, file);
              }}
            />
            {value && <span className="file-name">{value}</span>}
          </div>
        );

      default:
        return (
          <input
            type="text"
            className="param-input"
            value={value}
            onChange={e => handleValueChange(key, e.target.value)}
            placeholder={param.description}
          />
        );
    }
  };

  return (
    <form className="workflow-form" onSubmit={handleSubmit}>
      <div className="form-section">
        <h3>工作流配置</h3>
        
        <div className="form-row">
          <label>工作流 ID</label>
          <div className="input-with-button">
            <input
              type="text"
              value={workflowId}
              onChange={e => setWorkflowId(e.target.value)}
              placeholder="输入工作流ID"
            />
            <button
              type="button"
              onClick={loadParams}
              disabled={loading}
              className="btn-secondary"
            >
              {loading ? '加载中...' : '加载参数'}
            </button>
          </div>
        </div>

        <div className="form-row">
          <label>API Key（可选）</label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder="使用环境变量中的 API Key"
          />
        </div>

        <div className="form-row">
          <label>实例类型</label>
          <select
            className="param-input"
            value={instanceType}
            onChange={e => setInstanceType(e.target.value as 'default' | 'plus')}
          >
            <option value="default">默认 (24G 显存)</option>
            <option value="plus">Plus (48G 显存)</option>
          </select>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {params.length > 0 && (
        <div className="form-section">
          <h3>参数设置</h3>
          
          {params.map(param => (
            <div key={`${param.nodeId}_${param.fieldName}`} className="form-row">
              <label>
                <span className="label-title">{param.description}</span>
                <span className="label-meta">[{param.nodeName}]</span>
              </label>
              {renderParamInput(param)}
            </div>
          ))}

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? '提交中...' : '运行工作流'}
          </button>
        </div>
      )}
    </form>
  );
}

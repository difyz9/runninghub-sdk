import { useState, useEffect } from 'react';
import Header from './components/Header';
import { WorkflowForm } from './components/WorkflowForm';
import TaskStatus from './components/TaskStatus';
import OutputDisplay from './components/OutputDisplay';
import type { TaskOutput, TaskStatusType } from './types/task';
import { getTaskStatus, getTaskOutputs } from './api/client';

function App() {
  const [taskId, setTaskId] = useState<string | null>(null);
const [status, setStatus] = useState<TaskStatusType | null>(null);
  const [outputs, setOutputs] = useState<TaskOutput[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  // 轮询任务状态
  useEffect(() => {
    if (!taskId || !isRunning) return;

    const pollInterval = setInterval(async () => {
      try {
const newStatus = await getTaskStatus(taskId) as TaskStatusType;
        setStatus(newStatus);

        if (newStatus === 'SUCCESS') {
          const result = await getTaskOutputs(taskId);
          setOutputs(result);
          setIsRunning(false);
        } else if (newStatus === 'FAILED') {
          setIsRunning(false);
          setError('任务执行失败');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : '查询状态失败');
      }
    }, 6000);

    return () => clearInterval(pollInterval);
  }, [taskId, isRunning]);

  // 处理表单提交
  const handleFormSubmit = (newTaskId: string) => {
    setTaskId(newTaskId);
    setIsRunning(true);
setStatus('RUNNING' as TaskStatusType);
    setError(null);
    setOutputs([]);
  };

  return (
    <div className="app">
      <Header />
      
      <main className="container">
        <div className="hero">
          <h1 className="hero-title">RunningHub ComfyUI</h1>
          <p className="hero-subtitle">
            在浏览器中轻松调用 ComfyUI 工作流，生成高质量图像
          </p>
        </div>

        <div className="main-layout">
          <div className="main-content">
            <WorkflowForm onSubmit={handleFormSubmit} />

            {error && (
              <div className="error-message" style={{ marginTop: '1rem' }}>
                {error}
              </div>
            )}
          </div>

          <div className="main-sidebar">
            {taskId && (
              <TaskStatus
                taskId={taskId}
                status={status}
                isRunning={isRunning}
              />
            )}

            {outputs.length > 0 && (
              <OutputDisplay outputs={outputs} />
            )}
          </div>
        </div>
      </main>

      <footer className="footer">
        <p className="footer-text">
          RunningHub ComfyUI SDK © 2026
        </p>
      </footer>
    </div>
  );
}

export default App;

import type { TaskStatusType } from '../types/task';

interface TaskStatusProps {
  taskId: string;
  status: TaskStatusType | null;
  isRunning: boolean;
}

function TaskStatus({ taskId, status, isRunning }: TaskStatusProps) {
  const getStatusClass = () => {
    if (!status) return '';
    switch (status) {
      case 'QUEUED':
        return 'status-queued';
      case 'RUNNING':
        return 'status-running';
      case 'SUCCESS':
        return 'status-success';
      case 'FAILED':
        return 'status-failed';
      default:
        return '';
    }
  };

  const getStatusText = () => {
    if (!status) return '未知';
    switch (status) {
      case 'QUEUED':
        return '排队中';
      case 'RUNNING':
        return '运行中';
      case 'SUCCESS':
        return '成功';
      case 'FAILED':
        return '失败';
      default:
        return status;
    }
  };

  return (
    <div className="task-status-card">
      <div className="task-status-header">
        <span className="task-status-title">任务状态</span>
        <span className={`status-badge ${getStatusClass()}`}>
          {getStatusText()}
        </span>
      </div>

      <div className="task-status-content">
        <div className="task-status-row">
          <span className="task-status-label">任务 ID</span>
          <span className="task-status-value">{taskId}</span>
        </div>

        {isRunning && (
          <div className="loading-overlay" style={{ marginTop: '1rem' }}>
            <div className="spinner"></div>
            <span className="loading-text">正在生成图像...</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default TaskStatus;

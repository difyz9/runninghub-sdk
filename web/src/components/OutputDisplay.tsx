import type { TaskOutput } from '../types/task';

interface OutputDisplayProps {
  outputs: TaskOutput[];
}

function OutputDisplay({ outputs }: OutputDisplayProps) {
  if (outputs.length === 0) {
    return null;
  }

  return (
    <div className="output-display" style={{ marginTop: '1rem' }}>
      <h3 className="output-display-title">生成结果</h3>
      
      <div className="output-display-grid">
        {outputs.map((output, index) => (
          <div key={index} className="output-item">
            <img
              src={output.fileUrl}
              alt={`Output ${index + 1}`}
              className="output-item-image"
            />
            <div className="output-item-info">
              <span className="output-item-type">{output.fileType}</span>
              <a
                href={output.fileUrl}
                download
                className="output-item-download"
                target="_blank"
                rel="noopener noreferrer"
              >
                下载
              </a>
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginTop: '1rem' }}>
        <div className="task-status-row">
          <span className="task-status-label">生成耗时</span>
          <span className="task-status-value">{outputs[0]?.taskCostTime || '-'}s</span>
        </div>
        {outputs[0]?.consumeCoins && (
          <div className="task-status-row">
            <span className="task-status-label">消耗金币</span>
            <span className="task-status-value">{outputs[0].consumeCoins}</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default OutputDisplay;

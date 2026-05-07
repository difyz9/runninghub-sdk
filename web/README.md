# RunningHub Web 前端应用

基于 React 18 的 RunningHub ComfyUI Web 界面，使用黑白灰极简配色风格。

## 项目结构

```
runninghub-studio/
├── .env                    # API Key 配置
├── .env.example            # 配置示例
├── runninghub_sdk/         # Python SDK
├── server/                 # FastAPI 后端
│   ├── main.py
│   └── requirements.txt
├── web/                    # React 前端
│   ├── src/
│   │   ├── components/     # React 组件
│   │   ├── styles/         # 样式文件
│   │   ├── types/          # 类型定义
│   │   └── api/            # API 客户端
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── docs/
└── tests/
```

## 快速开始

### 1. 配置 API Key

在项目根目录创建 `.env` 文件：

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
RUNNINGHUB_API_KEY=your-api-key-here
```

### 2. 安装依赖

**前端依赖：**

```bash
cd web
npm install
```

**后端依赖：**

```bash
cd server
pip install -r requirements.txt
```

### 3. 启动服务

**启动后端（端口 8000）：**

```bash
cd server
python main.py
```

或使用 uvicorn：

```bash
cd server
uvicorn main:app --reload --port 8000
```

**启动前端开发服务器（端口 3000）：**

```bash
cd web
npm run dev
```

### 4. 访问应用

打开浏览器访问：http://localhost:3000

## 功能特性

### 工作流参数设置
- 提示词（正向/负向）
- 采样步数、CFG、种子
- 图片尺寸（宽度/高度）
- 采样器/调度器选择
- 去噪强度

### 任务管理
- 创建任务
- 实时状态轮询
- 进度显示
- 取消任务

### 结果展示
- 生成的图片展示
- 下载链接
- 任务详情（耗时、费用）

## API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/run` | POST | 创建任务 |
| `/api/status/{task_id}` | GET | 查询状态 |
| `/api/outputs/{task_id}` | GET | 获取结果 |
| `/api/cancel/{task_id}` | POST | 取消任务 |
| `/api/upload` | POST | 上传文件 |
| `/api/upload-lora` | POST | 上传 LoRA |
| `/api/workflow/{workflow_id}` | GET | 获取工作流 |

## 设计风格

使用 UI/UX Pro 黑白灰极简配色（Minimalism & Swiss Style）：

- 背景色：白色 (#FFFFFF) / 浅灰 (#F5F5F5)
- 文本色：黑色 (#000000) / 灰色 (#666666)
- 强调色：信任蓝 (#2563EB)
- 边框色：灰色 (#E5E7EB)

特点：简洁、功能性强、网格布局、高对比度、无阴影。

## 构建生产版本

```bash
cd web
npm run build
```

构建产物在 `web/dist` 目录。

## 技术栈

- **前端**: React 18 + Vite + TypeScript
- **后端**: FastAPI + Python
- **HTTP 客户端**: httpx
- **设计**: 黑白灰极简风格

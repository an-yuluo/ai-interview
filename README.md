# AI 模拟面试系统

基于 AI 的全栈模拟面试辅助系统，支持简历解析、自定义面试场景、流式对话交互、多维度评分和逐题复盘。

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Pinia + Vue Router |
| UI | ECharts (雷达图) + marked + highlight.js |
| 后端 | Python FastAPI + httpx |
| AI | DeepSeek API (兼容 OpenAI 格式) |
| 简历解析 | PyPDF2 + python-docx |

## 快速开始

### 1. 后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key

# 启动后端
uvicorn main:app --reload --port 8000
```

### 2. 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 3. 访问

打开浏览器访问 `http://localhost:5173`

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

## 本地开发

### 1. 后端

```bash
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

## Railway 一键部署

### 前置准备

1. 注册 [GitHub](https://github.com) 账号
2. 注册 [Railway](https://railway.app) 账号（用 GitHub 登录即可）
3. 获取 [DeepSeek API Key](https://platform.deepseek.com)

### 部署步骤

**Step 1: 创建 GitHub 仓库并推送代码**

```bash
# 在 GitHub 上新建一个空仓库（不要勾选 README/gitignore），然后：
git remote add origin https://github.com/你的用户名/ai-interview.git
git branch -M main
git push -u origin main
```

**Step 2: Railway 部署**

1. 打开 [railway.app/new](https://railway.app/new)
2. 选择 "Deploy from GitHub repo"
3. 选择你刚创建的 `ai-interview` 仓库
4. Railway 会自动识别 `railway.toml` 并开始构建

**Step 3: 配置环境变量**

1. 在 Railway 项目面板中，点击 "Variables"
2. 添加变量：`DEEPSEEK_API_KEY` = `你的API密钥`
3. Railway 会自动重新部署

**Step 4: 获取永久域名**

1. 部署成功后，点击 "Settings" → "Networking"
2. 点击 "Generate Domain"
3. 获得永久域名，如 `ai-interview-production.up.railway.app`

### 代码更新自动同步

推送代码到 GitHub 后，Railway 会自动重新构建并部署：

```bash
git add -A
git commit -m "描述你的改动"
git push
# Railway 自动部署，约 1-2 分钟后生效
```

# 🚀 部署到 Vercel 指南

这个版本的应用采用了 **前后端分离** 架构 (FastAPI + 纯HTML/JS)，专为 Serverless 环境设计。

## 📁 目录结构

`vercel_app/`
- `api/`: Python 后端 (FastAPI)，包含所有 Agent 逻辑
- `public/`: 纯静态前端 (HTML/CSS/JS)
- `vercel.json`: 路由配置

## 🛠️ 本地运行

1. 确保虚拟环境已激活:
   ```bash
   source venv/bin/activate
   ```

2. 安装新增依赖:
   ```bash
   pip install fastapi uvicorn
   ```

3. 运行启动脚本:
   ```bash
   chmod +x run_web.sh
   ./run_web.sh
   ```

4. 打开浏览器访问: [http://localhost:8000](http://localhost:8000)

## ☁️ 部署到 Vercel (完全免费)

### 方式 1: 使用 GitHub (推荐)
1. 将代码推送到 GitHub
2. 登录 [Vercel Dashboard](https://vercel.com)
3. 点击 "Add New..." -> "Project"
4. 导入你的 GitHub 仓库
5. **重要配置**:
   - **Root Directory**: 点击 Edit，选择 `vercel_app`
   - **Environment Variables**: 添加你的 API Key
     - `api-key`: `你的API密钥`
6. 点击 Deploy！🚀

### 方式 2: 使用 Vercel CLI
1. 安装 CLI: `npm i -g vercel`
2. 在项目根目录运行:
   ```bash
   cd vercel_app
   vercel
   ```

## 🎨 自定义

- **前端**: 修改 `vercel_app/public/style.css` 来调整配色
- **后端**: 修改 `vercel_app/api/src/agent` 下的代码来调整 Agent 逻辑

## ⚠️ 注意事项

- Vercel 免费版 Serverless Function 有 **10秒超时限制** (如果是 Hobby 计划)。
- 本项目使用了 **流式响应 (Streaming)**，这有助于规避硬性超时，但在某些极其复杂的分析场景下可能会中断。
- 如果遇到超时问题，建议:
  1. 减少 `Max Rounds` (辩论轮次)
  2. 减少新闻搜索数量
  3. 或者升级到 Vercel Pro (60秒超时)

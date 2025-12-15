# 快速启动指南

## ✅ 已解决的问题

1. ✅ **端口8000被占用** - 已清理
2. ✅ **package.json缺失** - 已创建
3. ✅ **src/agent/__init__.py导入错误** - 已修复

---

## 🚀 现在启动步骤

### Terminal 1 - 启动后端

```bash
cd /Users/haoyin/Documents/QT_formal/langChainAgent
source venv/bin/activate
cd api
python main.py
```

**看到这个提示就成功了**:
```
🚀 Starting AI Stock Analysis API...
📊 4-Layer Multi-Agent System (11 Agents)
📖 API Docs: http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

访问: http://localhost:8000/docs 查看API文档

---

### Terminal 2 - 启动前端

```bash
cd /Users/haoyin/Documents/QT_formal/langChainAgent/frontend

# 首次安装依赖
npm install

# 启动开发服务器
npm run dev
```

**看到这个提示就成功了**:
```
VITE v5.x ready in xxx ms
➜  Local:   http://localhost:5173/
```

访问: http://localhost:5173

---

## 🧪 测试完整流程

1. 打开浏览器 → http://localhost:5173
2. 输入股票代码 → 600519 (贵州茅台)
3. 点击设置图标 ⚙️ → 输入你的API Key
4. 点击 Run 按钮 → 开始分析

**应该看到**:
- Layer 1: 基本面、情绪、新闻、技术分析
- Layer 2: 多空博弈
- Layer 3: 交易决策
- Layer 4: 风控建议

---

## ⚠️ 常见问题

### 问题1: 端口已被占用
```bash
ERROR: [Errno 48] address already in use
```

**解决**:
```bash
# 清理占用8000端口的进程
lsof -ti:8000 | xargs kill -9
```

### 问题2: npm install 失败
```bash
# 清理npm缓存重试
npm cache clean --force
npm install
```

### 问题3: CORS错误
- 后端已配置允许 localhost:5173
- 确保两个服务都在运行
- 检查浏览器控制台的实际错误

---

## 📝 项目现在的状态

- ✅ 后端代码已修复（无硬编码）
- ✅ 前端配置已创建
- ✅ 部署文档已完成
- ✅ 项目已清理干净

**可以开始测试和演示了！** 🎉

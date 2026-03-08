# 本地测试快速指南

## 📁 目录关系说明

**重要**: 你们有两套前端，但应该只用一套！

| 目录 | 用途 | 是否使用 |
|------|------|---------|
| `frontend/` | **你们开发的React前端** | ✅ 使用 |
| `vercel_app/public/` | 旧的HTML前端 | ❌ 不用 |
| `api/main.py` | **后端API (Render部署)** | ✅ 使用 |
| `vercel_app/api/index.py` | 旧的后端 | ❌ 不用 |

**结论**: 
- **前端**: 部署 `frontend/` 到 Vercel
- **后端**: 部署 `api/main.py` 到 Render  
- **忽略** `vercel_app/` 目录

---

## 🧪 本地测试步骤

### 1️⃣ 启动后端（模拟Render）

```bash
# Terminal 1
cd /Users/haoyin/Documents/QT_formal/langChainAgent
source venv/bin/activate
cd api
python main.py
```

**预期输出**:
```
🚀 Starting AI Stock Analysis API...
INFO: Uvicorn running on http://0.0.0.0:8000
```

✅ 后端运行在 `http://localhost:8000`

**测试后端**:
```bash
# 新开一个terminal
curl http://localhost:8000/api/health

# 预期返回
{"status":"ok","version":"2.0.0-enhanced"}
```

---

### 2️⃣ 启动前端（模拟Vercel）

前端API配置在 `frontend/src/App.jsx` 第11行:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/analyze';
```

**方法A: 直接启动（使用默认配置）**
```bash
# Terminal 2
cd /Users/haoyin/Documents/QT_formal/langChainAgent/frontend

# 首次需要安装依赖
npm install

# 启动开发服务器
npm run dev
```

**方法B: 使用环境变量（推荐）**
```bash
# 创建 .env.local 文件
cd frontend
echo "VITE_API_URL=http://localhost:8000/api/analyze" > .env.local

# 启动
npm run dev
```

**预期输出**:
```
VITE v5.x ready in xxx ms
➜  Local:   http://localhost:5173/
```

✅ 前端运行在 `http://localhost:5173`

---

### 3️⃣ 测试完整流程

1. **打开浏览器** → `http://localhost:5173`
2. **输入股票代码** → `600519` (贵州茅台)
3. **点击设置图标** → 输入API Key
4. **点击Run按钮** → 开始分析

**检查点**:
- ✅ 前端显示"系统就绪"
- ✅ 能输入股票代码
- ✅ 点击Run后显示loading
- ✅ 后端Terminal显示请求日志
- ✅ 前端实时显示4层分析结果

---

## 🔧 常见问题

### ❌ CORS错误

**Frontend Console显示**:
```
Access to fetch at 'http://localhost:8000/api/analyze' 
has been blocked by CORS policy
```

**解决**: 检查 `api/main.py` 的CORS配置:
```python
allow_origins=[
    "http://localhost:5173",  # ← 确保有这行
    "*"
]
```

---

### ❌ 前端连接不到后端

**检查**:
1. 后端是否运行？访问 `http://localhost:8000/docs`
2. 前端API地址正确？查看 `App.jsx` 第11行
3. 浏览器F12 → Network查看请求

---

### ❌ 缺少package.json

如果`npm install`失败，需要创建 `frontend/package.json`:

```bash
cd frontend
npm init vite@latest . --template react
# 选择: React, JavaScript
npm install
```

---

## 🚀 生产部署配置

### 开发环境
```
前端: http://localhost:5173  (本地测试)
后端: http://localhost:8000  (本地测试)
```

### 生产环境
```
前端: https://你的项目.vercel.app  (Vercel自动分配)
后端: https://你的服务.onrender.com  (Render自动分配)
```

**前端需要改的配置**:

在 `frontend/` 创建 `.env.production`:
```
VITE_API_URL=https://你的Render后端URL.onrender.com/api/analyze
```

Vercel部署时添加环境变量:
```
VITE_API_URL = https://xxx.onrender.com/api/analyze
```

---

## 📋 部署总结

| 步骤 | 动作 | 文档 |
|------|------|------|
| 1 | 本地测试前后端联调 | 本文档 |
| 2 | 部署后端到Render | `RENDER_DEPLOY.md` |
| 3 | 获取Render后端URL | Render Dashboard |
| 4 | 配置前端环境变量 | `FRONTEND_VERCEL.md` |
| 5 | 部署前端到Vercel | `FRONTEND_VERCEL.md` |

---

**关键点**:
- ✅ 只用 `frontend/` 不用 `vercel_app/public/`
- ✅ 只用 `api/main.py` 不用 `vercel_app/api/`
- ✅ 本地测试通过再部署
- ✅ 前端通过环境变量配置后端URL

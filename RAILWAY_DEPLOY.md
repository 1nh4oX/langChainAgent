# Railway 后端部署指南

## 🚂 为什么选择Railway？

- ✅ **完全免费** - $5试用额度，够用很久
- ✅ **不需要绑卡** - 用GitHub登录即可
- ✅ **自动部署** - Git推送后自动重新部署
- ✅ **支持Python** - 完美支持FastAPI + LangChain

---

## 🚀 部署步骤

### 步骤1: 推送代码到GitHub

```bash
cd /Users/haoyin/Documents/QT_formal/langChainAgent
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

---

### 步骤2: 注册Railway

1. 访问 **https://railway.app**
2. 点击 **Start a New Project**
3. 选择 **Login with GitHub** (推荐)

---

### 步骤3: 创建项目

1. 点击 **New Project**
2. 选择 **Deploy from GitHub repo**
3. 选择你的仓库 `langChainAgent`
4. Railway会自动检测Python项目

---

### 步骤4: 配置环境变量

在Railway Dashboard中:

1. 点击你的项目
2. 选择 **Variables** 标签
3. 添加环境变量:

```
api-key = sk-你的API密钥
base-url = https://api.siliconflow.cn/v1
PORT = 8000
```

---

### 步骤5: 设置部署命令（可选）

Railway会自动检测，但你也可以手动设置:

**Settings** → **Deploy**:
```
Build Command: pip install -r requirements.txt
Start Command: cd api && python main.py
```

---

### 步骤6: 部署

1. 点击 **Deploy**
2. 等待3-5分钟完成构建
3. 看到 **Success** 就部署成功了！

---

### 步骤7: 获取部署URL

1. 在Railway Dashboard，点击 **Settings**
2. 找到 **Domains** 部分
3. 点击 **Generate Domain**
4. Railway会给你一个URL，例如:
   ```
   https://langchain-agent-backend-production.up.railway.app
   ```

**复制这个URL** - 前端需要用！

---

### 步骤8: 测试部署

访问:
```
https://你的URL.railway.app/api/health
```

应该返回:
```json
{"status":"ok","version":"2.0.0-enhanced"}
```

---

## 🎨 配置前端

### 方法1: 环境变量（推荐）

在 `frontend/` 创建 `.env.production`:
```
VITE_API_URL=https://你的Railway后端URL.railway.app/api/analyze
```

### 方法2: 直接修改

编辑 `frontend/src/App.jsx` 第11行:
```javascript
const API_URL = 'https://你的Railway URL.railway.app/api/analyze'
```

---

## 📊 Railway优势

### vs Render
- ✅ 不需要绑卡
- ✅ 不会自动休眠
- ✅ 启动更快
- ✅ 每月$5额度（够用很久）

### vs Vercel
- ✅ 支持长时间运行的Python进程
- ✅ 没有50ms CPU限制
- ✅ 更适合后端API

---

## 🔄 自动部署

配置好后，每次推送代码Railway会自动重新部署:

```bash
git add .
git commit -m "Update backend"
git push origin main
```

Railway检测到推送后自动部署，无需手动操作！

---

## 📝 常见问题

### Q1: 如何查看日志？
**A**: Railway Dashboard → 你的项目 → **Deployments** → 点击最新部署 → **View Logs**

### Q2: 部署失败怎么办？
**A**: 
1. 检查环境变量是否设置正确
2. 查看部署日志找错误
3. 确保 `requirements.txt` 完整

### Q3: 如何更新环境变量？
**A**: Railway Dashboard → **Variables** → 添加/修改 → 自动重新部署

### Q4: Railway会收费吗？
**A**: 
- 免费$5额度
- 对于演示项目完全够用
- 超出后才收费（很难超）

---

## ⚠️ 注意事项

1. **保存部署URL**: 部署成功后记得复制Railway给的URL
2. **配置前端**: 前端需要配置这个URL才能连接后端
3. **环境变量**: API Key一定要在Railway Dashboard设置，不要写在代码里

---

## 🎯 下一步

1. ✅ 后端部署成功
2. ⏭️ 把Railway URL告诉前端开发者
3. ⏭️ 前端部署到Vercel或Cloudflare Pages
4. ⏭️ 完整测试

---

## 📚 相关文档

- Railway官方文档: https://docs.railway.app
- 前端部署: 参考 `FRONTEND_VERCEL.md`
- 本地测试: 参考 `START_HERE.md`

**部署成功后，你的后端就可以24/7运行了！** 🎉

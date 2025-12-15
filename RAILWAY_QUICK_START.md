# Railway 部署快速开始

## ✅ 已完成配置

1. ✅ **railway.json** - Railway配置文件
2. ✅ **Procfile** - 启动命令配置
3. ✅ **前端API配置** - 支持环境变量

---

## 🚀 现在就可以部署！

### 第1步: 推送代码
```bash
git add .
git commit -m "Add Railway deployment config"
git push origin main
```

### 第2步: 访问Railway
1. 打开 **https://railway.app**
2. 用GitHub登录
3. 点击 **New Project**
4. 选择 **Deploy from GitHub repo**
5. 选择你的 `langChainAgent` 仓库

### 第3步: 设置环境变量
在Railway Dashboard添加:
```
api-key = sk-你的API密钥
base-url = https://api.siliconflow.cn/v1
PORT = 8000
```

### 第4步: 获取URL
1. Railway Dashboard → **Settings**
2. **Domains** → **Generate Domain**
3. 复制生成的URL（类似 `xxx.railway.app`）

### 第5步: 配置前端
创建 `frontend/.env.production`:
```
VITE_API_URL=https://你的Railway URL.railway.app/api/analyze
```

---

## 🎯 优势

- ✅ **完全免费** - $5试用额度
- ✅ **不绑卡** - GitHub登录即可
- ✅ **不休眠** - 24/7运行
- ✅ **自动部署** - Git推送即部署

---

## 📚 详细文档

查看 [`RAILWAY_DEPLOY.md`](file:///Users/haoyin/Documents/QT_formal/langChainAgent/RAILWAY_DEPLOY.md) 获取完整指南。

**开始部署吧！** 🚂

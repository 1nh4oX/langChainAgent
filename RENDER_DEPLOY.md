# Render 后端部署指南

## 🎯 部署方案

**架构**: 
- 前端: Vercel (静态网站托管)
- 后端: Render (Python API服务)

这个方案是**完全免费**的，非常适合演示demo。

---

## 🚀 快速部署步骤

### 前置准备

1. **GitHub仓库**: 确保代码已推送到GitHub
2. **Render账号**: 访问 https://render.com 注册免费账号
3. **API Key**: 准备好硅基流动的API Key

---

### 方法一: 使用 render.yaml 一键部署 ⭐推荐

#### 步骤1: 推送代码
```bash
cd /Users/haoyin/Documents/QT_formal/langChainAgent
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

#### 步骤2: 在Render创建服务
1. 登录 https://dashboard.render.com
2. 点击 **New** → **Blueprint**
3. 连接你的GitHub仓库
4. Render会自动检测到 `render.yaml` 文件
5. 点击 **Apply**

#### 步骤3: 配置环境变量
在Render Dashboard中设置环境变量:
- Key: `api-key`
- Value: 你的硅基流动API Key (例如: `sk-xxxxx`)

#### 步骤4: 部署
Render会自动开始构建和部署。等待3-5分钟。

---

### 方法二: 手动创建Web Service

#### 步骤1: 创建Web Service
1. 登录 https://dashboard.render.com
2. 点击 **New** → **Web Service**
3. 连接GitHub仓库并选择 `langChainAgent` 仓库

#### 步骤2: 配置项目
```
Name: langchain-agent-backend
Environment: Python 3
Region: Oregon (US West)
Branch: main
Root Directory: (留空)

Build Command: 
pip install --upgrade pip && pip install -r requirements.txt

Start Command:
cd api && python main.py
```

#### 步骤3: 选择计划
- 选择 **Free** (免费方案)

#### 步骤4: 添加环境变量
在 "Environment" 标签下添加:
```
api-key = sk-你的硅基流动API密钥
base-url = https://api.siliconflow.cn/v1
PYTHON_VERSION = 3.9.18
```

#### 步骤5: 创建服务
点击 **Create Web Service**，等待部署完成。

---

## 📝 部署后配置

### 获取后端URL
部署成功后，Render会提供一个URL，例如:
```
https://langchain-agent-backend.onrender.com
```

⚠️ **重要**: 复制这个URL，前端需要配置这个地址。

---

### 测试后端
访问以下URL测试后端是否正常:
```
https://你的后端URL/api/health
```

预期返回:
```json
{
  "status": "ok",
  "version": "2.0.0-enhanced"
}
```

---

## 🔧 前端配置 (告知前端开发者)

前端需要修改API endpoint配置:

**配置位置**: `frontend/` 目录中的环境配置文件

**需要修改的内容**:
```javascript
// 将API base URL改为Render部署的地址
const API_BASE_URL = "https://你的后端URL.onrender.com"
```

**CORS已配置**: 后端已经允许所有Vercel域名的跨域请求，无需额外配置。

---

## ⚠️ Render免费版限制

### 限制说明
1. **自动休眠**: 15分钟无请求会自动休眠
2. **冷启动**: 休眠后首次请求需要30-60秒唤醒
3. **运行时间**: 每月750小时免费额度
4. **带宽**: 每月100GB流量

### 对演示的影响
- ✅ **完全够用**: 对于课程作业演示，这些限制是可以接受的
- ⚠️ **演示前预热**: 展示前5分钟访问一次后端，避免冷启动
- 💡 **优化体验**: 在前端添加loading提示，告知用户首次加载较慢

---

## 🐛 常见问题

### 1. 部署失败
**错误**: "Build failed"

**解决方案**:
- 检查 `requirements.txt` 是否正确
- 查看Render的构建日志，定位具体错误
- 确保Python版本兼容 (建议3.9或3.10)

### 2. 运行时错误
**错误**: "Application failed to start"

**解决方案**:
- 检查环境变量 `api-key` 是否设置
- 查看Runtime日志
- 确认 `api/main.py` 路径正确

### 3. API调用失败
**错误**: "CORS error" 或 "Network error"

**解决方案**:
- 确认后端URL配置正确
- 检查前端是否使用了正确的HTTPS协议
- 验证环境变量是否正确设置

### 4. 首次请求很慢
**原因**: 这是免费版的正常现象（冷启动）

**解决方案**:
- 演示前5-10分钟访问一次后端预热
- 在前端添加loading动画和提示

---

## 🔄 更新部署

代码更新后，Render会**自动重新部署**:
```bash
git add .
git commit -m "Fix backend issues"
git push origin main
```

Render检测到推送后会自动开始重新构建。

---

## 📊 监控和日志

### 查看日志
1. 登录Render Dashboard
2. 选择你的服务
3. 点击 **Logs** 标签
4. 实时查看运行日志

### 查看性能
1. 在Dashboard点击 **Metrics**
2. 查看CPU、内存使用情况
3. 查看请求响应时间

---

## 💰 费用说明

**完全免费**，无需绑定信用卡。

免费版包括:
- 每月750小时运行时间
- 512MB内存
- 0.1 CPU
- 100GB带宽

对于演示demo来说完全够用！

---

## 🎓 演示最佳实践

### 准备工作
1. **提前部署**: 至少在演示前1天完成部署
2. **测试完整流程**: 部署后完整测试一次
3. **准备Plan B**: 如果Render出问题，可以本地运行备用

### 演示当天
1. **预热后端**: 演示前10分钟访问后端API
2. **准备Demo数据**: 选择稳定的股票代码 (如 600519 茅台)
3. **网络检查**: 确保演示环境网络稳定

### 演示技巧
1. **说明冷启动**: 如果首次加载慢，向评委说明这是免费服务的特性
2. **突出功能**: 强调11个Agent的协作分析过程
3. **准备截图**: 提前准备好成功运行的截图作为备份

---

## 📞 获取帮助

- Render文档: https://render.com/docs
- 硅基流动API文档: https://siliconflow.cn/zh-cn/siliconcloud
- GitHub Issues: 在项目仓库提issue

---

**部署成功后，请将后端URL提供给前端开发者！**

Good luck with your presentation! 🎉

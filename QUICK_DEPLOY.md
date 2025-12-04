# ⚡ 5分钟部署指南

## 🎯 目标

将你的 AI 股票分析工具部署到互联网，获得一个**公开访问链接**！

## 📋 前提条件

- ✅ GitHub 账号
- ✅ 代码已完成
- ✅ 有一个可用的 API 密钥

## 🚀 部署步骤

### 1️⃣ 推送代码到 GitHub（2分钟）

```bash
# 初始化 Git
git init
git add .
git commit -m "feat: ready for deployment"

# 在 GitHub 创建新仓库
# 访问 https://github.com/new
# 仓库名: stock-analysis-agent
# 设为公开（Public）

# 推送代码
git remote add origin https://github.com/你的用户名/stock-analysis-agent.git
git branch -M main
git push -u origin main
```

### 2️⃣ 部署到 Streamlit Cloud（2分钟）

1. **访问**: https://share.streamlit.io
2. **登录**: 使用 GitHub 账号
3. **新建应用**: 点击 "New app"
4. **选择仓库**: `你的用户名/stock-analysis-agent`
5. **主文件**: `ui/streamlit_app.py`
6. **点击**: "Deploy!"

### 3️⃣ 配置 API 密钥（1分钟）

部署前在 "Advanced settings" 添加 Secrets：

```toml
api-key = "你的API密钥"
base-url = "https://api.siliconflow.cn/v1"
```

---

## ✅ 完成！

**你的应用链接：**
```
https://你的应用名.streamlit.app
```

现在可以分享这个链接给任何人使用！

---

## 🎨 自定义应用名称

在 Streamlit Cloud 设置中可以修改应用URL：

```
https://stock-analysis.streamlit.app
https://ai-stocks.streamlit.app
https://你想要的名称.streamlit.app
```

---

## 🔄 更新应用

修改代码后：

```bash
git add .
git commit -m "update: improve features"
git push
```

Streamlit Cloud 会自动检测并重新部署（约1-2分钟）！

---

## 💡 常见问题

### Q: 部署失败？
A: 检查 Logs，通常是依赖问题或 Secrets 配置错误

### Q: 应用很慢？
A: 免费版资源有限，考虑优化代码或升级套餐

### Q: 应用休眠了？
A: 7天无访问会休眠，访问链接即可唤醒

---

## 📚 详细文档

查看 [DEPLOY_STREAMLIT_CLOUD.md](DEPLOY_STREAMLIT_CLOUD.md) 了解更多详情！

---

**祝你部署顺利！** 🎉



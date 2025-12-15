# 前端部署说明（无需环境变量）

## ✅ 简化配置

**好消息**：前端不需要配置文件！

用户直接在前端界面的**设置面板**中输入：
- ✅ API 地址（后端URL）
- ✅ API 密钥
- ✅ 模型选择

---

## 🚀 部署步骤

### Vercel 部署

1. 访问 https://vercel.com
2. 用GitHub登录
3. **New Project** → 选择仓库
4. **Root Directory**: `frontend`
5. **Framework**: Vite (自动检测)
6. 点击 **Deploy**

**完成！** 不需要任何环境变量配置。

---

### Cloudflare Pages 部署

1. 访问 https://pages.cloudflare.com
2. 连接GitHub
3. 选择仓库
4. **Build directory**: `frontend`
5. **Build command**: `npm run build`
6. **Output directory**: `dist`
7. 部署

---

## 💡 用户使用方式

### 第一次访问
1. 打开前端网站
2. 点击**设置图标⚙️**
3. 输入配置：
   ```
   API 地址: https://你的Railway后端.railway.app
   API 密钥: sk-你的密钥
   模型: Qwen 2.5 7B
   ```
4. 关闭设置
5. 输入股票代码开始分析

### 后续使用
浏览器会记住设置（localStorage），下次直接用。

---

## 📝 告诉用户的信息

**部署完成后，告诉用户**：

1. **前端地址**: `https://你的项目.vercel.app` 或 `xxx.pages.dev`
2. **后端地址**: `https://你的后端.railway.app`
3. **使用说明**: 
   - 首次打开前端，点击设置⚙️
   - 输入后端地址（第2项）
   - 输入API密钥
   - 开始使用

---

## ✅ 优势

- ✅ **无需配置文件** - 非常简洁
- ✅ **用户自主控制** - 可以随时切换后端
- ✅ **灵活部署** - 前后端完全独立
- ✅ **无需重新部署** - 换后端URL只需在设置里改

---

## 🎯 总结

**前端部署超简单**：
1. 推送代码到GitHub
2. 在Vercel/Cloudflare连接仓库
3. 选择`frontend`目录
4. 部署
5. 完成！

用户使用时在设置里填写后端URL即可。

**这是最灵活的方案！** 🚀

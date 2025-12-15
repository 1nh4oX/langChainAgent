# 前端 Vercel 部署说明

> **注意**: 本文档是给前端开发者的配置指南，**不涉及前端代码修改**，只说明需要的配置和注意事项。

---

## ✅ Vercel 部署可行性

**结论**: 前端**可以**部署到Vercel，这是标准的React/Vue/HTML静态网站部署方案。

Vercel非常适合前端部署:
- ✅ 全球CDN加速
- ✅ 自动HTTPS
- ✅ 免费额度充足
- ✅ 自动部署（Git推送即部署）

---

## 🎯 前端需要配置的内容

### 1. API Endpoint配置

**关键点**: 前端需要将API请求地址改为Render后端的URL

**示例配置**:
```javascript
// 开发环境
const API_BASE_URL = 'http://localhost:8000'

// 生产环境（Vercel部署后）
const API_BASE_URL = 'https://你的后端URL.onrender.com'
```

**建议**: 使用环境变量管理API地址

---

### 2. 环境变量设置（如果需要）

如果前端需要将API Key传递给后端:

**在Vercel Dashboard设置**:
1. 进入项目设置
2. 点击 **Environment Variables**
3. 添加:
```
VITE_API_BASE_URL = https://你的后端URL.onrender.com
```

**在前端代码中使用**:
```javascript
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
```

---

### 3. CORS问题

**好消息**: 后端已经配置好CORS，允许所有Vercel域名:

```python
# 后端已配置
allow_origins=[
    "https://*.vercel.app",  # 允许所有Vercel部署
    "*"  # 开发阶段允许所有
]
```

**前端无需额外配置CORS**。

---

## 🚀 Vercel 部署步骤

### 方法一: 通过GitHub自动部署（推荐）

#### 步骤1: 准备代码
```bash
cd frontend  # 进入前端目录
# 确保以下文件存在:
# - package.json
# - vercel.json (可选但推荐)
```

#### 步骤2: 推送到GitHub
```bash
git add .
git commit -m "Prepare frontend for Vercel deployment"
git push origin main
```

#### 步骤3: 连接Vercel
1. 访问 https://vercel.com
2. 点击 **New Project**
3. 导入GitHub仓库
4. 选择 `frontend` 目录作为Root Directory

#### 步骤4: 配置项目
```
Project Name: langchain-agent-frontend
Framework Preset: (自动检测，如React/Vue/Vite)
Root Directory: frontend
Build Command: npm run build (或 yarn build)
Output Directory: dist (或 build)
```

#### 步骤5: 添加环境变量
在Vercel项目设置中添加:
```
VITE_API_BASE_URL = https://后端URL.onrender.com
```

#### 步骤6: 部署
点击 **Deploy**，等待1-3分钟。

---

### 方法二: 使用 Vercel CLI

```bash
# 安装Vercel CLI
npm install -g vercel

# 在前端目录下
cd frontend

# 登录Vercel
vercel login

# 部署
vercel --prod
```

---

## 📋 前端检查清单

在部署前，请确认以下内容:

### 必须修改
- [ ] API endpoint地址改为Render后端URL
- [ ] package.json 中的构建命令正确
- [ ] 环境变量配置（如果使用）

### 推荐优化
- [ ] 添加loading状态提示（后端冷启动时）
- [ ] 添加错误处理（网络失败时）
- [ ] 添加超时处理（首次请求可能较慢）

### 配置文件示例
- [ ] vercel.json 文件（如果需要特殊配置）

---

## 📄 vercel.json 配置示例

如果前端是SPA (单页应用)，需要配置路由:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600"
        }
      ]
    }
  ]
}
```

---

## 🔧 API调用示例

**前端调用后端的示例代码**:

```javascript
// 配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 调用分析API
async function analyzeStock(symbol, apiKey) {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      symbol: symbol,
      api_key: apiKey,  // 如果前端持有API key
      model: "Qwen/Qwen2.5-7B-Instruct",
      debate_threshold: 3.0,
      max_rounds: 2
    })
  })
  
  // 流式处理响应
  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    
    const chunk = decoder.decode(value)
    const lines = chunk.split('\n')
    
    for (const line of lines) {
      if (line.trim()) {
        const data = JSON.parse(line)
        console.log(data)  // 处理实时数据
      }
    }
  }
}
```

---

## ⚠️ 注意事项

### 1. API Key管理

**最佳实践**: 
- ❌ 不要把API Key硬编码在前端代码中
- ✅ 让用户在设置页面输入API Key
- ✅ API Key存储在localStorage（仅用于demo）
- ✅ 每次请求时传递给后端

**示例**:
```javascript
// 用户设置页面
const apiKey = localStorage.getItem('api-key')

// 调用API时传递
fetch('/api/analyze', {
  body: JSON.stringify({
    api_key: apiKey,  // 从localStorage获取
    // ...其他参数
  })
})
```

### 2. 后端冷启动处理

Render免费版会休眠，前端需要处理首次加载慢的情况:

```javascript
// 添加超时和loading提示
const [isLoading, setIsLoading] = useState(false)
const [loadingMessage, setLoadingMessage] = useState('')

async function analyzeStock() {
  setIsLoading(true)
  setLoadingMessage('正在唤醒后端服务...')
  
  // 设置超时提示
  const timer = setTimeout(() => {
    setLoadingMessage('后端正在冷启动，预计需要30-60秒，请稍候...')
  }, 5000)
  
  try {
    await fetch(...)
    clearTimeout(timer)
  } catch (error) {
    // 错误处理
  } finally {
    setIsLoading(false)
  }
}
```

### 3. 错误处理

```javascript
try {
  const response = await fetch(`${API_BASE_URL}/api/analyze`, {...})
  
  if (!response.ok) {
    throw new Error(`API错误: ${response.status}`)
  }
  
  // 处理响应
} catch (error) {
  console.error('API调用失败:', error)
  
  // 友好的错误提示
  if (error.message.includes('Failed to fetch')) {
    alert('无法连接到后端服务，请检查网络或稍后重试')
  } else {
    alert(`分析失败: ${error.message}`)
  }
}
```

---

## 🧪 本地测试

部署前，先在本地测试前端连接Render后端:

```bash
# 1. 修改API endpoint为Render URL
# 2. 本地启动前端
npm run dev

# 3. 测试功能
# 4. 确认无误后再部署到Vercel
```

---

## 📊 部署后验证

部署成功后，访问Vercel提供的URL，测试:

1. **基础功能**:
   - [ ] 页面正常加载
   - [ ] 样式显示正确
   - [ ] 路由跳转正常

2. **API连接**:
   - [ ] 可以连接到Render后端
   - [ ] 股票分析功能正常
   - [ ] 实时数据流显示正常

3. **错误处理**:
   - [ ] 网络错误有友好提示
   - [ ] API错误有明确说明
   - [ ] 冷启动有loading提示

---

## 🔄 自动部署

配置完成后，每次推送代码到GitHub，Vercel会**自动重新部署**:

```bash
git add .
git commit -m "Update frontend"
git push origin main
```

Vercel会自动检测更新并部署，无需手动操作。

---

## 💡 优化建议

### 性能优化
1. 启用Vercel的Edge Network加速
2. 配置合适的Cache-Control headers
3. 压缩静态资源

### 用户体验优化
1. 添加骨架屏（Skeleton）显示
2. 添加请求进度条
3. 优化首屏加载速度

### SEO优化（可选）
1. 添加meta标签
2. 配置sitemap
3. 启用预渲染

---

## 📞 需要后端提供的信息

**前端开发者需要从后端获取**:

1. ✅ Render后端URL (例如: `https://xxx.onrender.com`)
2. ✅ API endpoint列表:
   - `POST /api/analyze` - 股票分析
   - `GET /api/health` - 健康检查
3. ✅ API请求格式和参数说明
4. ✅ 响应数据格式

**后端已提供**: 在`/api/docs`查看完整API文档

---

## 🎯 总结

**前端Vercel部署要点**:
1. ✅ 可以部署，无问题
2. ⚙️ 需要配置后端URL
3. 🔑 需要处理API Key
4. ⏱️ 需要处理后端冷启动
5. 🛡️ 需要添加错误处理

**如果有问题，联系后端开发者获取帮助！**

Good luck! 🚀

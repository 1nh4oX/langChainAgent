# 🚀 完整部署指南（含 API 密钥管理）

## 🔐 API 密钥安全说明

**重要：永远不要把 API 密钥上传到 GitHub！**

`.gitignore` 已配置：
```
.env
.env.local
.streamlit/secrets.toml
```

这些文件会被自动忽略，不会上传。

---

## 🎯 三种部署方案

### 方案 A：自己使用（Streamlit Secrets）⭐

**特点：**
- ✅ 最安全
- ✅ 最方便
- ❌ 只有你能用

**步骤：**

1. 上传代码到 GitHub（不包含 `.env`）
2. 部署到 Streamlit Cloud
3. 在 Streamlit Cloud 配置 Secrets

**详见下方 "方案 A 详细步骤"**

---

### 方案 B：公开分享（用户自己输入 API）⭐⭐⭐

**特点：**
- ✅ 任何人都能用
- ✅ 用户使用自己的 API
- ✅ 完全公开，无需担心 API 泄露

**使用：**

```bash
streamlit run ui/streamlit_app_with_login.py
```

**特色：**
- 侧边栏配置页面
- API 测试功能
- 只在 session 中保存（不持久化）
- 提供免费 API 获取链接

**详见下方 "方案 B 详细步骤"**

---

### 方案 C：混合模式（最灵活）⭐⭐⭐⭐⭐

**特点：**
- ✅ 如果有 Streamlit Secrets，自动使用
- ✅ 如果没有，让用户输入
- ✅ 适合所有场景

**说明：**

`streamlit_app_with_login.py` 已实现混合模式！

```python
# 自动检测
if hasattr(st, 'secrets') and 'api-key' in st.secrets:
    # 使用 Streamlit Secrets
    api_key = st.secrets['api-key']
else:
    # 让用户输入
    api_key_input = st.text_input("API Key", type="password")
```

---

## 📝 方案 A 详细步骤（自己用）

### 1. 准备代码

```bash
# 确认 .env 在 .gitignore 中
cat .gitignore | grep .env

# 应该看到：
# .env
# .env.local
```

### 2. 上传到 GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push
```

**✅ .env 文件不会被上传！**

### 3. 部署到 Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 点击 "New app"
3. 选择你的 GitHub 仓库
4. 设置：
   - **Main file:** `ui/streamlit_app.py`
   - **Python version:** 3.9+

### 4. 配置 Secrets

在 Streamlit Cloud 应用设置中：

```toml
# .streamlit/secrets.toml
api-key = "你的API密钥"
base-url = "https://api.siliconflow.cn/v1"
model = "Qwen/Qwen2.5-7B-Instruct"
```

### 5. 部署完成

获得链接：`https://your-app.streamlit.app`

---

## 📝 方案 B 详细步骤（公开分享）

### 1. 修改主文件

在 Streamlit Cloud 部署时：

- **Main file:** `ui/streamlit_app_with_login.py`

### 2. 上传到 GitHub

```bash
git add .
git commit -m "Add public version with API input"
git push
```

### 3. 部署

1. Streamlit Cloud 部署
2. **不需要配置 Secrets！**
3. 用户自己输入 API

### 4. 使用流程

**用户角度：**

1. 打开网站
2. 看到提示："请在侧边栏配置 API"
3. 在侧边栏输入：
   - API Key
   - Base URL
   - Model
4. 点击 "Test & Save"
5. 测试通过后开始使用

**优势：**
- 完全公开
- 无需担心 API 泄露
- 用户用自己的额度

---

## 🆓 提供给用户的免费 API 指南

在 `streamlit_app_with_login.py` 中已包含：

```python
st.sidebar.markdown("""
**Recommended:**
- [SiliconFlow](https://siliconflow.cn) - 免费额度
- [Zhipu AI](https://open.bigmodel.cn) - 免费tokens
- [Moonshot](https://platform.moonshot.cn) - 新用户礼包
""")
```

---

## 🎨 UI 对比

### streamlit_app.py（方案 A）

```
┌──────────────────────┐
│ 📊 AI Stock Analysis │
├──────────────────────┤
│ 💡 Quick Examples    │
│ [Ex1] [Ex2] [Ex3]... │
│                      │
│ 🔍 Your Question     │
│ [输入框]             │
│ [Analyze] [Clear]    │
└──────────────────────┘

✅ 直接使用（Secrets 已配置）
```

### streamlit_app_with_login.py（方案 B/C）

```
┌─────────┬────────────────┐
│ ⚙️ API  │ 📊 AI Stock   │
│ Config  │ Analysis      │
├─────────┼────────────────┤
│ 🔑 API  │ 💡 Examples   │
│ Key:    │ [Ex1] [Ex2]   │
│ [输入]  │               │
│         │ 🔍 Question   │
│ Base    │ [输入框]      │
│ URL:    │               │
│ [输入]  │ [Analyze]     │
│         │               │
│ Model:  │               │
│ [输入]  │               │
│         │               │
│ [Test]  │               │
└─────────┴────────────────┘

✅ 用户输入 API 后使用
```

---

## 🔄 本地测试

### 测试方案 A（Secrets）

```bash
# 创建 .streamlit/secrets.toml
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
api-key = "your-key"
base-url = "https://api.siliconflow.cn/v1"
model = "Qwen/Qwen2.5-7B-Instruct"
EOF

# 运行
streamlit run ui/streamlit_app.py
```

### 测试方案 B（用户输入）

```bash
# 直接运行
streamlit run ui/streamlit_app_with_login.py

# 在侧边栏输入 API
```

---

## 📊 方案选择建议

| 场景 | 推荐方案 | 文件 |
|------|---------|------|
| **个人使用** | A | `streamlit_app.py` + Secrets |
| **组员协作** | C | `streamlit_app_with_login.py` + Secrets |
| **公开分享** | B | `streamlit_app_with_login.py` |
| **教学演示** | B | `streamlit_app_with_login.py` |
| **商业应用** | C | `streamlit_app_with_login.py` + 后端 API |

---

## 🎯 推荐：方案 C（混合模式）

**为什么？**

1. **灵活性最高：**
   - 你自己用：配置 Secrets，自动加载
   - 分享给他人：他们输入自己的 API

2. **一套代码两种用法：**
   ```python
   # 自动检测
   if hasattr(st, 'secrets') and 'api-key' in st.secrets:
       use_secrets()
   else:
       user_input_api()
   ```

3. **安全且方便：**
   - 你的 API 在 Secrets 中（安全）
   - 用户的 API 在 session 中（临时）

---

## 🛡️ 安全检查清单

部署前确认：

- [ ] `.env` 在 `.gitignore` 中
- [ ] `.streamlit/secrets.toml` 在 `.gitignore` 中
- [ ] GitHub 仓库中没有 `.env` 文件
- [ ] GitHub 仓库中没有 `secrets.toml` 文件
- [ ] 代码中没有硬编码的 API 密钥

**检查命令：**

```bash
# 检查是否有泄露
git log --all --full-history --source -S 'sk-' 
git log --all --full-history --source -S 'api-key'

# 如果不小心上传了，立即：
# 1. 删除密钥
# 2. 重新生成新密钥
# 3. 使用 git filter-branch 清理历史
```

---

## 📦 完整部署流程（推荐）

### 1. 准备

```bash
# 确认忽略文件正确
cat .gitignore | grep -E "\.env|secrets"

# 清理敏感文件（如果存在）
rm .env  # 本地保留，不上传
rm .streamlit/secrets.toml  # 本地保留，不上传
```

### 2. 提交代码

```bash
git add .
git commit -m "feat: add API configuration support"
git push origin main
```

### 3. 部署到 Streamlit Cloud

```
Repository: your-repo
Branch: main
Main file: ui/streamlit_app_with_login.py  ← 混合模式
```

### 4A. 如果你要自己用

配置 Streamlit Cloud Secrets：
```toml
api-key = "your-key"
base-url = "https://api.siliconflow.cn/v1"
model = "Qwen/Qwen2.5-7B-Instruct"
```

### 4B. 如果要公开分享

不配置 Secrets，用户自己输入！

### 5. 测试

- ✅ 打开网站
- ✅ (如果有 Secrets) 直接可用
- ✅ (如果没有 Secrets) 提示输入 API
- ✅ 输入 API → 测试 → 开始使用

---

## 🎉 总结

### 最佳实践

1. **使用 `streamlit_app_with_login.py`** - 混合模式
2. **本地开发：** 使用 `.streamlit/secrets.toml`
3. **个人部署：** 配置 Streamlit Cloud Secrets
4. **公开分享：** 不配置 Secrets，让用户输入

### 文件说明

| 文件 | 用途 | 部署方式 |
|------|------|---------|
| `streamlit_app.py` | 需要 Secrets | 个人使用 |
| `streamlit_app_cn.py` | 中文版，需要 Secrets | 个人使用 |
| `streamlit_app_with_login.py` | 混合模式 | **推荐**⭐ |

### 推荐配置

```yaml
# Streamlit Cloud 部署配置
repository: your-username/langChainAgent
branch: main
main_file: ui/streamlit_app_with_login.py
python_version: 3.9

# Secrets（可选，适合自己用）
secrets:
  api-key: "your-key"
  base-url: "https://api.siliconflow.cn/v1"
  model: "Qwen/Qwen2.5-7B-Instruct"
```

---

**现在你可以安全地部署了！** 🚀

有任何问题随时问我！


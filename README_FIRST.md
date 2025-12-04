# 🚀 开始使用 - 超简单！

## ⚡ 1分钟启动

### 第1步：安装依赖

```bash
pip install streamlit langchain langchain-openai python-dotenv akshare pandas
```

### 第2步：配置API

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env，填入你的API密钥
api-key=你的密钥
base-url=https://api.siliconflow.cn/v1
```

### 第3步：启动UI

```bash
streamlit run ui/streamlit_app.py
```

### 第4步：开始使用

浏览器自动打开 `http://localhost:8501`

1. 点击 "Example 1-5" 任意按钮
2. 或输入你的问题（中文/英文都可以）
3. 点击 "🚀 Analyze"
4. 查看结果！

---

## 🎯 关键说明

### ✅ 已解决的问题

1. **编码错误** - 使用英文界面，支持中文查询
2. **按钮不工作** - 已修复，点击后自动填充
3. **UI 复杂** - 重新设计，极简风格

### 🌟 核心特性

- ✅ **英文界面** - 零编码问题
- ✅ **中文查询** - 完全支持中文输入
- ✅ **中文回答** - AI 自动识别语言
- ✅ **示例按钮** - 一键填充查询
- ✅ **历史记录** - 自动保存所有分析

---

## 📝 使用示例

### 点击示例

点击 "Example 1" → 自动填充 → 点击分析

### 中文查询

```
分析贵州茅台（600519）的技术指标和最新新闻
```

### 英文查询

```
Analyze technical indicators and news of Kweichow Moutai (600519)
```

**都可以！AI 会智能识别！**

---

## 🌐 部署到线上（可选）

5分钟获得公开访问链接：

查看 `QUICK_DEPLOY.md` 完整教程

---

## 🐛 遇到问题？

### 编码错误？
```bash
# 使用安全启动
python run_ui_safe.py
```

### 按钮不工作？
```bash
# 清除浏览器缓存后重试
```

### API 错误？
```bash
# 检查 .env 配置
cat .env
```

---

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| **README_FIRST.md** | 👈 **从这里开始** |
| `PROBLEM_SOLVED.md` | 问题解决详情 |
| `RUN_UI.md` | 3个UI版本对比 |
| `QUICK_DEPLOY.md` | 在线部署指南 |
| `README.md` | 完整项目文档 |

---

## 🎉 就这么简单！

```bash
streamlit run ui/streamlit_app.py
```

**打开浏览器，点击示例，开始分析！** 🚀

---

**保证可用，有问题随时反馈！** ✅



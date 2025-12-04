# 🎨 Stock Analysis Agent - Web UI

现代化的股票分析 Agent 网页界面，设计灵感来自 Kaggle、X (Twitter)、Threads 等现代社交平台。

## ✨ 设计特点

- 🎨 **现代卡片式设计** - 清晰的视觉层次，优雅的交互体验
- 🌈 **渐变色彩** - 紫色渐变主题，专业而不失活力
- 📱 **响应式布局** - 完美适配各种屏幕尺寸
- ⚡ **流畅动画** - 悬停效果、加载动画，提升用户体验
- 📊 **数据可视化** - 直观的指标展示，一目了然

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install streamlit
```

或更新 requirements.txt 后安装：

```bash
pip install -r requirements.txt
```

### 2. 运行 UI

```bash
# 方式1: 直接运行
streamlit run ui/streamlit_app.py

# 方式2: 指定端口
streamlit run ui/streamlit_app.py --server.port 8080

# 方式3: 后台运行
nohup streamlit run ui/streamlit_app.py &
```

### 3. 访问界面

浏览器自动打开，或访问：
```
http://localhost:8501
```

## 📖 功能说明

### 主要功能

1. **智能对话** - 输入股票分析需求，AI 自动选择工具并分析
2. **配置调整** - 侧边栏可调整模型、温度、思考次数等参数
3. **快速示例** - 点击侧边栏示例快速开始
4. **历史记录** - 自动保存所有分析历史，支持展开查看
5. **实时指标** - 显示思考次数、结果长度、分析效率等

### 配置选项

| 配置 | 说明 | 默认值 |
|------|------|--------|
| 模型选择 | 选择使用的LLM模型 | Qwen2.5-7B |
| 温度参数 | 控制输出随机性（0-1） | 0.3 |
| 最大思考次数 | Agent最多调用工具次数 | 10 |
| 显示执行详情 | 是否显示详细执行过程 | 关闭 |

## 🎨 设计元素

### 颜色方案

```css
主色调: 紫色渐变 (#667eea → #764ba2)
背景色: 白色 (#ffffff)
卡片阴影: rgba(0,0,0,0.07)
文字颜色: 深灰 (#2d3748)
辅助文字: 浅灰 (#718096)
```

### 组件样式

- **英雄区域** - 渐变文字标题，突出品牌
- **卡片设计** - 圆角、阴影、悬停效果
- **按钮样式** - 渐变背景，悬停上浮
- **输入框** - 大圆角，聚焦高亮
- **结果展示** - 左侧彩条，渐变背景

## 📱 界面截图

```
┌─────────────────────────────────────────┐
│  📊 AI 股票分析助手                      │
│  基于 LangChain 的智能分析系统           │
├─────────────────────────────────────────┤
│                                          │
│  🔍 [输入您的分析需求...]                │
│                                          │
│     [🚀 分析]  [🗑️]                     │
│                                          │
├─────────────────────────────────────────┤
│  📊 本次分析                             │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐           │
│  │ 10 │ │256 │ │ 5  │ │ 25 │           │
│  │思考│ │字数│ │总数│ │效率│           │
│  └────┘ └────┘ └────┘ └────┘           │
│                                          │
│  ✨ 分析结果                             │
│  ┌──────────────────────────────────┐  │
│  │ 根据最近10个交易日的数据分析...    │  │
│  │ ...                               │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

## 🛠️ 自定义配置

### Streamlit 配置

创建 `.streamlit/config.toml`：

```toml
[theme]
primaryColor = "#667eea"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#2d3748"
font = "sans serif"

[server]
port = 8501
headless = false
```

### 修改样式

编辑 `streamlit_app.py` 中的 CSS：

```python
st.markdown("""
<style>
    /* 在这里修改样式 */
    .hero-title {
        color: #your-color;
    }
</style>
""", unsafe_allow_html=True)
```

## 📊 性能优化

### 缓存配置

Streamlit 自带缓存机制：

```python
@st.cache_resource
def load_agent():
    return StockAnalysisAgent()

# 使用缓存的 Agent
agent = load_agent()
```

### 大数据处理

处理大量历史记录时：

```python
# 只保留最近 N 条记录
MAX_HISTORY = 50
if len(st.session_state.history) > MAX_HISTORY:
    st.session_state.history = st.session_state.history[:MAX_HISTORY]
```

## 🚀 部署建议

### 本地开发

```bash
streamlit run ui/streamlit_app.py --server.runOnSave true
```

### 生产部署

**Streamlit Cloud（推荐）:**
1. 推送代码到 GitHub
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 连接仓库并部署

**Docker 部署:**

```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "ui/streamlit_app.py"]
```

**Heroku 部署:**

创建 `Procfile`:
```
web: streamlit run ui/streamlit_app.py --server.port $PORT
```

## 🐛 常见问题

### Q: 界面显示异常？
A: 清除浏览器缓存，或使用无痕模式打开。

### Q: 样式不生效？
A: 确保 CSS 在 `<style>` 标签内，使用 `unsafe_allow_html=True`。

### Q: 运行缓慢？
A: 检查是否有大量历史记录，考虑限制保存数量。

### Q: 无法连接？
A: 检查防火墙设置，确保 8501 端口未被占用。

## 📚 参考资源

- [Streamlit 官方文档](https://docs.streamlit.io/)
- [Streamlit 组件库](https://streamlit.io/components)
- [CSS 渐变生成器](https://cssgradient.io/)
- [配色方案](https://coolors.co/)

## 🎯 未来改进

- [ ] 添加暗色主题切换
- [ ] 集成数据可视化图表（K线图）
- [ ] 支持导出分析报告（PDF/Word）
- [ ] 多语言支持
- [ ] 语音输入功能
- [ ] 实时消息推送

## 📝 更新日志

### v1.0.0 (2025-12-03)
- ✨ 初始版本发布
- 🎨 现代化卡片式设计
- 📊 完整的分析功能
- 📱 响应式布局
- ⚡ 流畅的交互体验

---

**提示**: 第一次运行可能需要几秒钟初始化，之后会很快！

**问题反馈**: 如遇到问题，请查看 GitHub Issues 或提交新 Issue。


